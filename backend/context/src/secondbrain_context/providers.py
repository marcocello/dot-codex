"""Read-only source adapters. Imported text is data and never controls execution."""
from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import sqlite3
import subprocess
from urllib.parse import quote, urlencode, urlparse

import httpx

from .config import ContextError, instant, require


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        if tag in ("p", "br", "div", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain_body(body):
    content = body.get("content", "")
    require(isinstance(content, str), "Microsoft returned an invalid message body")
    if body.get("contentType", "").lower() != "html":
        return content
    parser = PlainText()
    parser.feed(content)
    return "".join(parser.parts)


class GraphClient:
    """Endpoint injection is for local protocol tests; production always uses Microsoft Graph."""
    def __init__(self, token, base_url="https://graph.microsoft.com/v1.0"):
        self.token = token
        self.base = base_url.rstrip("/")
        self.client = httpx.Client(timeout=30, follow_redirects=False)

    def close(self):
        self.client.close()

    def validate_url(self, url):
        expected, actual = urlparse(self.base), urlparse(url)
        require(actual.scheme == expected.scheme and actual.netloc == expected.netloc
                and actual.path.startswith(expected.path + "/")
                and not actual.username and not actual.password and not actual.fragment,
                "Microsoft returned a continuation outside its configured Graph endpoint")

    def get(self, url):
        self.validate_url(url)
        try:
            response = self.client.get(url, headers={
                "Authorization": f"Bearer {self.token()}",
                "Prefer": 'IdType="ImmutableId", outlook.body-content-type="text", odata.maxpagesize=100',
            })
        except httpx.HTTPError:
            raise ContextError("Microsoft Graph connection failed; retry without advancing the checkpoint") from None
        if response.status_code == 410:
            raise ContextError("Microsoft delta checkpoint expired; disable and forget this source, then resync")
        if response.status_code == 429:
            raise ContextError("Microsoft Graph throttled the read; retry later from the saved checkpoint")
        require(response.status_code == 200,
                f"Microsoft Graph read failed (HTTP {response.status_code}); check consent and account access")
        require(len(response.content) <= 16 * 1024 * 1024, "Microsoft returned an oversized page")
        try:
            result = response.json()
        except ValueError:
            raise ContextError("Microsoft returned invalid JSON") from None
        require(isinstance(result, dict), "Microsoft returned an invalid response")
        return result

    def verify_account(self, expected):
        profile = self.get(self.base + "/me?$select=id,mail,userPrincipalName")
        candidates = {str(profile.get(key) or "").casefold() for key in ("mail", "userPrincipalName")}
        require(expected.casefold() in candidates, "Signed-in Microsoft account differs from the selected mailbox")
        require(isinstance(profile.get("id"), str) and bool(profile["id"]), "Microsoft account identity is missing")
        return profile["id"]

    def initial_url(self, folder, since):
        params = {"$select": "id,subject,body,from,receivedDateTime,sentDateTime,lastModifiedDateTime,webLink",
                  "$filter": f"receivedDateTime ge {since}"}
        return self.base + f"/me/mailFolders/{quote(folder, safe='')}/messages/delta?" + urlencode(params)


def graph_item(message, source, folder):
    require(isinstance(message, dict), "Microsoft returned an invalid message record")
    identity = message.get("id")
    require(isinstance(identity, str) and bool(identity), "Microsoft returned a message without an identity")
    native = json.dumps([folder, identity])
    if "@removed" in message:
        return {"native_id": native, "deleted": True}
    occurred = message.get("receivedDateTime") or message.get("sentDateTime")
    require(occurred is not None, "Microsoft returned a message without a date")
    instant(occurred)
    # A folder delta can include read-state events outside its original date filter.
    if instant(occurred) < instant(source.scope["since"]):
        return None
    sender_record = message.get("from") or {}
    require(isinstance(sender_record, dict) and isinstance(sender_record.get("emailAddress", {}), dict),
            "Microsoft returned an invalid sender")
    sender = sender_record.get("emailAddress", {}).get("address", "")
    require(isinstance(sender, str) and isinstance(message.get("body") or {}, dict),
            "Microsoft returned invalid message content")
    body = plain_body(message.get("body") or {})
    require(len(body) <= 250000, "Microsoft message exceeds the retained-text limit; narrow the source scope")
    return {"native_id": native, "title": str(message.get("subject") or "(no subject)"),
            "text": body, "occurred_at": occurred,
            "direction": "sent" if sender.casefold() == source.scope["account"].casefold() else "received",
            "ref": {"provider": "microsoft_graph", "account": source.scope["account"],
                    "folder": folder, "message_id": identity, "sender": sender,
                    "url": message.get("webLink") or ""}}


def sync_graph(source, store, client, max_pages):
    account_id = client.verify_account(source.scope["account"])
    pages = 0
    more = False
    for folder in source.scope["folders"]:
        cursor, state = store.checkpoint(source.id, folder)
        require(not state.get("account_id") or state["account_id"] == account_id,
                "Microsoft mailbox identity changed; register a new source")
        if pages >= max_pages:
            more = True
            break
        while pages < max_pages:
            page = client.get(cursor or client.initial_url(folder, source.scope["since"]))
            messages = page.get("value")
            require(isinstance(messages, list), "Microsoft delta response has no complete message page")
            next_link, delta_link = page.get("@odata.nextLink"), page.get("@odata.deltaLink")
            require(bool(next_link) != bool(delta_link), "Microsoft delta response needs exactly one continuation")
            link = next_link or delta_link
            require(isinstance(link, str), "Microsoft returned an invalid delta link")
            client.validate_url(link)
            require(not next_link or link != cursor, "Microsoft returned a non-advancing next page")
            bootstrap = state.get("bootstrap", True)
            count = state.get("initial_count", 0) + len(messages) if bootstrap else 0
            require(not bootstrap or count < 5000,
                    "Microsoft filtered initial sync reached the 5,000-message limit; narrow since/folders and rebuild")
            items = [item for message in messages if (item := graph_item(message, source, folder)) is not None]
            state = {"account_id": account_id, "bootstrap": bootstrap and bool(next_link), "initial_count": count}
            store.apply_page(source.id, folder, cursor, link, items, state)
            cursor = link
            pages += 1
            if delta_link:
                break
        else:
            more = True
    return {"pages": pages, "more": more, "coverage": "selected folders since configured date; filtered initial delta is limited to 5,000 messages"}


def wacli_changes(source, cursor, page_size, *, checkpoint=False):
    command = [source.scope.get("binary", "wacli"), "--read-only", "--json", "--store", source.scope["store"],
               "messages", "changes"]
    command += ["--checkpoint"] if checkpoint else ["--since", cursor or "beginning", "--limit", str(page_size)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise ContextError("wacli read unavailable; install a journal-capable version and verify the selected store") from None
    require(len(result.stdout) <= 8 * 1024 * 1024, "wacli returned an oversized change page")
    require(result.returncode == 0,
            "wacli change read failed; check archive access and journal expiry. An expired journal requires a scoped rebuild")
    try:
        envelope = json.loads(result.stdout)
    except ValueError:
        raise ContextError("wacli returned invalid JSON") from None
    require(isinstance(envelope, dict) and envelope.get("success") is True, "wacli did not return a successful read")
    page = envelope.get("data")
    require(isinstance(page, dict) and isinstance(page.get("changes"), list)
            and type(page.get("has_more")) is bool and isinstance(page.get("next_checkpoint"), str)
            and isinstance(page.get("store_id"), str) and bool(page["store_id"]),
            "wacli change journal is unsupported; upgrade and migrate the archive with its owner")
    return page


def whatsapp_item(archive, source, chat, message):
    native = json.dumps([chat, message])
    row = archive.execute("SELECT chat_jid,msg_id,sender_jid,ts,display_text,text,from_me,deleted_at,payload_purged_at "
                          "FROM messages WHERE chat_jid=? AND msg_id=?", (chat, message)).fetchone()
    # A missing current row does not establish a remote deletion. Only journal delete records erase it.
    if row is None:
        return None
    if row["deleted_at"] or row["payload_purged_at"]:
        return {"native_id": native, "deleted": True}
    occurred = datetime.fromtimestamp(row["ts"], timezone.utc)
    if occurred < instant(source.scope["since"]):
        return None
    return {"native_id": native, "title": f"WhatsApp {'sent' if row['from_me'] else 'received'}",
            "text": row["display_text"] or row["text"] or "", "occurred_at": occurred.isoformat(),
            "direction": "sent" if row["from_me"] else "received",
            "ref": {"provider": "wacli", "chat_jid": chat, "message_id": message,
                    "sender": row["sender_jid"] or "", "url": ""}}


def sync_wacli(source, store, max_pages, page_size):
    path = Path(source.scope["store"]) / "wacli.db"
    require(path.is_file(), "Selected wacli archive is missing; pair and sync wacli separately")
    try:
        archive = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=10)
        archive.row_factory = sqlite3.Row
        required = {"chat_jid", "msg_id", "sender_jid", "ts", "display_text", "text", "from_me", "deleted_at", "payload_purged_at"}
        require(required <= {row[1] for row in archive.execute("PRAGMA table_info(messages)")},
                "Unsupported wacli archive schema; upgrade its owner before ingestion")
        cursor, state = store.checkpoint(source.id, "changes")
        pages = 0
        if cursor is None:
            # Anchor before scanning: later inserts, old backfills, edits, and purges
            # must replay even when their message timestamps precede the scan.
            anchor = wacli_changes(source, None, page_size, checkpoint=True)
            state = {"store_id": anchor["store_id"], "bootstrap": True, "last_rowid": 0,
                     "highwater": archive.execute("SELECT coalesce(max(rowid),0) FROM messages").fetchone()[0]}
            cursor = anchor["next_checkpoint"]
            store.apply_page(source.id, "changes", None, cursor, [], state)
        while state.get("bootstrap") and pages < max_pages:
            chats = source.scope["chats"]
            placeholders = ",".join("?" for _ in chats)
            rows = archive.execute(f"SELECT rowid,chat_jid,msg_id FROM messages WHERE rowid>? AND rowid<=? "
                                   f"AND chat_jid IN ({placeholders}) AND ts>=? ORDER BY rowid LIMIT ?",
                                   (state["last_rowid"], state["highwater"], *chats,
                                    instant(source.scope["since"]).timestamp(), page_size)).fetchall()
            items = [item for row in rows if (item := whatsapp_item(
                archive, source, row["chat_jid"], row["msg_id"])) is not None]
            state = {**state, "last_rowid": rows[-1]["rowid"] if rows else state["highwater"],
                     "bootstrap": len(rows) == page_size}
            store.apply_page(source.id, "changes", cursor, cursor, items, state)
            pages += 1
        if pages >= max_pages:
            return {"pages": pages, "more": True,
                    "coverage": "scoped initial archive scan; anchored journal replay pending"}
        while pages < max_pages:
            page = wacli_changes(source, cursor, page_size)
            require(not state.get("store_id") or state["store_id"] == page["store_id"],
                    "wacli store identity changed; register a new source")
            require(not page["has_more"] or page["next_checkpoint"] != cursor,
                    "wacli returned a non-advancing change page")
            items = []
            for change in page["changes"]:
                require(isinstance(change, dict) and change.get("operation") in {"upsert", "delete", "identity_move"},
                        "wacli returned an unsupported change")
                chat, message = change.get("chat_jid"), change.get("msg_id")
                require(isinstance(chat, str) and isinstance(message, str), "wacli change identity is missing")
                if chat in source.scope["chats"]:
                    if change["operation"] in {"delete", "identity_move"}:
                        items.append({"native_id": json.dumps([chat, message]), "deleted": True})
                    else:
                        item = whatsapp_item(archive, source, chat, message)
                        if item:
                            items.append(item)
                if change["operation"] == "identity_move" and change.get("new_chat_jid") in source.scope["chats"]:
                    item = whatsapp_item(archive, source, change["new_chat_jid"], change.get("new_msg_id") or message)
                    if item:
                        items.append(item)
            state = {"store_id": page["store_id"]}
            store.apply_page(source.id, "changes", cursor, page["next_checkpoint"], items, state)
            cursor = page["next_checkpoint"]
            pages += 1
            if not page["has_more"]:
                break
        return {"pages": pages, "more": page["has_more"], "coverage": "retained local archive only; live sync is supervised separately"}
    except sqlite3.Error:
        raise ContextError("Cannot read the selected wacli archive; verify its schema and read-only access") from None
    finally:
        if "archive" in locals():
            archive.close()
