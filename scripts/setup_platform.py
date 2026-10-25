#!/usr/bin/env python3
"""Guided, resumable installation of the complete second-brain environment."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import sys

from setup_support import SetupError, ask, save_json, setup_lock, yes

ROOT = Path(__file__).resolve().parents[1]


def plan(mode):
    print(f"Secondbrain setup: {mode}\n")
    if mode == "azure":
        print("Mac prerequisites → Azure login/subscription → state storage → Terraform plan/approval/apply")
        print("Azure agent: persistent disk + pinned Codex + SSH host trust → protected VPN bootstrap")
        print("Connect the generated VPN profile → verified SSH → the same host setup")
    print((ROOT / "scripts/setup-plan.txt").read_text(), end="")


def collect(previous, options):
    allowed = {"mode", "destination", "telegram", "baileys", "remote_control", "memory", "outlook", "whatsapp", "azure", "since", "mail", "chats"}
    if not isinstance(previous, dict) or not set(previous) <= allowed:
        raise SetupError("Setup choices contain unsupported fields; credentials belong in the private credential files")
    for key, fields in (("memory", {"backend", "index", "namespace", "cloud", "region"}),
                        ("mail", {"account", "client_id", "tenant_id", "folders"}),
                        ("azure", {"subscription", "owner", "resource_group", "storage_account", "container", "key", "location"})):
        if key in previous and (not isinstance(previous[key], dict) or not set(previous[key]) <= fields):
            raise SetupError(f"Unsupported {key} configuration fields; do not put credentials in setup choices")
    value = dict(previous)
    interactive = not options.non_interactive
    if not value or options.reconfigure:
        mode = options.mode or (ask("Setup target (host = Ubuntu VM; azure = provision from this Mac)", "azure" if platform.system() == "Darwin" else "host",
                                    interactive=interactive))
        value["mode"] = mode
        if mode == "azure":
            cloud = dict(value.get("azure", {}))
            # Offer the existing backend identity before proposing a new state location.
            import tomllib
            backend = ROOT / "deployments/prod/tf/backend.hcl"
            variables = ROOT / "deployments/prod/tf/terraform.tfvars"
            if backend.is_file():
                try:
                    existing = tomllib.loads(backend.read_text())
                    for source, target in (("resource_group_name", "resource_group"), ("storage_account_name", "storage_account"), ("container_name", "container"), ("key", "key")):
                        if source in existing:
                            cloud.setdefault(target, existing[source])
                except tomllib.TOMLDecodeError:
                    raise SetupError("Existing backend.hcl uses a custom format; provide its identity in --config") from None
            if variables.is_file():
                try:
                    existing = tomllib.loads(variables.read_text())
                    for source, target in (("subscription_id", "subscription"), ("owner", "owner")):
                        if source in existing:
                            cloud.setdefault(target, existing[source])
                except tomllib.TOMLDecodeError:
                    raise SetupError("Existing terraform.tfvars uses a custom format; provide its identity in --config") from None
            for key, label, default in (
                ("subscription", "Azure subscription UUID", ""),
                ("owner", "Resource owner tag", os.environ.get("USER", "operator")),
                ("resource_group", "Terraform state resource group", "secondbrain-state"),
                ("storage_account", "Globally unique state storage account (lowercase letters/digits)", ""),
                ("container", "State container", "tfstate"),
                ("key", "Terraform state key", "secondbrain.tfstate"),
                ("location", "State storage Azure location", "austriaeast")):
                cloud[key] = ask(label, cloud.get(key, default), interactive=interactive)
            value["azure"] = cloud
        else:
            value["destination"] = ask("Persistent harness checkout", value.get("destination", str(Path.home() / "projects/dot-codex")), interactive=interactive)
            value["telegram"] = yes("Enable the Telegram agent gateway?", value.get("telegram", True), interactive=interactive)
            value["baileys"] = yes("Enable the optional Baileys WhatsApp reply bot?", value.get("baileys", False), interactive=interactive)
            value["remote_control"] = yes("Enable Codex Remote Control at boot?", value.get("remote_control", True), interactive=interactive)
            memory = dict(value.get("memory", {"backend": "qdrant"}))
            memory["backend"] = ask("Memory backend (qdrant/pinecone)", memory.get("backend", "qdrant"), interactive=interactive)
            if memory["backend"] == "pinecone":
                memory["index"] = ask("Pinecone index name", memory.get("index", "secondbrain"), interactive=interactive)
                memory["namespace"] = ask("Dedicated namespace for THIS workspace", memory.get("namespace", "secondbrain-" + os.urandom(8).hex()), interactive=interactive)
            value["memory"] = memory
            value["outlook"] = yes("Connect one Outlook mailbox?", value.get("outlook", True), interactive=interactive)
            value["whatsapp"] = yes("Collect selected WhatsApp chats using wacli?", value.get("whatsapp", True), interactive=interactive)
    if options.mode:
        value["mode"] = options.mode
    if value.get("mode") not in {"host", "azure"}:
        raise SetupError("Configure mode as host or azure")
    if value["mode"] == "host":
        required = {"destination", "telegram", "baileys", "remote_control", "memory", "outlook", "whatsapp"}
        if not required <= set(value):
            raise SetupError("Incomplete host configuration; run setup interactively with --reconfigure")
        if value["memory"].get("backend") not in {"qdrant", "pinecone"}:
            raise SetupError("Memory backend must be qdrant or pinecone")
        if value["memory"]["backend"] == "pinecone" and not all(value["memory"].get(key) for key in ("index", "namespace")):
            raise SetupError("Pinecone setup choices need index and namespace")
        for name in ("telegram", "baileys", "remote_control", "outlook", "whatsapp"):
            if type(value[name]) is not bool:
                raise SetupError(f"Configuration {name} must be a boolean")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("host", "azure"))
    parser.add_argument("--plan", "--dry-run", action="store_true", help="Read-only plan; never install, log in or provision")
    parser.add_argument("--config", type=Path, help="Saved non-secret setup choices as JSON")
    parser.add_argument("--state", type=Path, default=Path(os.environ.get("SECOND_BRAIN_STATE", str(Path.home() / "projects/.secondbrain"))))
    parser.add_argument("--non-interactive", "--no-prompt", action="store_true", help="Require saved choices and existing authentication")
    parser.add_argument("--reconfigure", action="store_true", help="Review setup choices; preserve existing context scopes")
    args = parser.parse_args(argv)
    if args.plan:
        plan(args.mode or "host")
        return 0
    if args.non_interactive:
        os.environ["SECOND_BRAIN_NO_PROMPT"] = "1"
    os.umask(0o077)
    try:
        state = args.state.expanduser().absolute()
        choices = args.config.expanduser() if args.config else state / "setup.json"
        if args.non_interactive and not choices.is_file():
            raise SetupError("Non-interactive setup needs an existing --config or saved setup.json")
        previous = json.loads(choices.read_text()) if choices.is_file() else {}
        selected = collect(previous, args)
        with setup_lock(state):
            save_json(state / "setup.json", selected)
            selected["_review_sources"] = args.reconfigure
            if selected["mode"] == "azure":
                from setup_azure import setup
            else:
                from setup_host import setup
            return setup(ROOT, state, selected, interactive=not args.non_interactive)
    except (SetupError, OSError, ValueError) as error:
        print(f"Setup: {error}", file=sys.stderr)
        return 2
    except (KeyboardInterrupt, EOFError):
        print("\nSetup interrupted. Repeat the same command to recheck and resume.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
