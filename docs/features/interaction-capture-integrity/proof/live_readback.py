"""Verify recovery against an explicit, local snapshot of unavailable app entries."""
import importlib.util,json,sys
from pathlib import Path
root=Path.cwd()
path=root/"skills/harness-capture-interactions/scripts/capture_interactions.py"
spec=importlib.util.spec_from_file_location("capture_verify",path)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
missing=json.loads(Path(sys.argv[1]).read_text())
ids=sorted({t["id"] for t in missing})
index=json.loads((root/"docs/interactions/index.json").read_text())
indexed={r["task_id"]:r for r in index["records"]}
completed=messages=partial=0
with m.AppServerClient("codex") as client:
 for identity in ids:
  record=json.loads((root/"docs/interactions/threads"/(identity+".json")).read_text())
  assert record["task"]["id"]==identity
  assert record["capture"]["source_format"]=="app-server-paginated"
  expected=[];cursor=None
  while True:
   params={"threadId":identity,"itemsView":"full","sortDirection":"asc","limit":100}
   if cursor:params["cursor"]=cursor
   page=client.request("thread/turns/list",params)
   for turn in page["data"]:
    assert turn.get("itemsView","full")=="full"
    visible=False
    for item in turn["items"]:
     if item["type"]=="agentMessage" and item.get("phase") in {None,"commentary","final","final_answer"}:
      visible=visible or bool(item.get("text","").strip())
     elif item["type"]=="userMessage":
      for part in item["content"]:
       if part["type"]=="text":visible=visible or bool(m.without_injected_context(part["text"]).strip())
       elif part["type"] in {"image","localImage"}:visible=True
    if turn["status"]=="completed" and visible:expected.append(turn["id"])
   cursor=page.get("nextCursor")
   if not cursor:break
  assert [t["id"] for t in record["turns"]]==expected, identity
  n=sum(len(t["messages"]) for t in record["turns"])
  assert indexed[identity]["turn_count"]==len(expected)
  assert indexed[identity]["message_count"]==n
  assert all(t["messages"] and t["status"]=="complete" for t in record["turns"])
  completed+=len(expected);messages+=n
  partial+=record["capture"]["state"]=="partial"
print(f"Recovered chats verified against full app history: {len(ids)}")
print(f"Persisted completed turns: {completed}; human-visible messages: {messages}; partial records: {partial}")
print("All recovered chats are indexed; completed-turn IDs match the live app API; incomplete dialogue is excluded.")
