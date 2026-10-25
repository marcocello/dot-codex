"""Mac entry mode: explicit cloud plans, agent bootstrap, then verified VPN SSH."""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import tempfile
import time
import tomllib

from setup_support import (Journal, SetupError, ask, atomic_write, command, save_json, yes)


def managed_run_command(connection, script, protected, *, runner=command):
    """Keys travel only in ARM protectedParameters, never argv/source/console/state."""
    subscription = connection["subscription_id"]
    group, vm = connection["resource_group_name"], connection["vm_name"]
    location = runner(["az", "vm", "show", "--subscription", subscription, "-g", group, "-n", vm,
                       "--query", "location", "-o", "tsv"], capture=True).stdout.strip()
    url = (f"https://management.azure.com/subscriptions/{subscription}/resourceGroups/{group}/providers/"
           f"Microsoft.Compute/virtualMachines/{vm}/runCommands/secondbrain-vpn?api-version=2024-11-01")
    with tempfile.TemporaryDirectory(prefix="secondbrain-protected-") as tmp:
        payload = Path(tmp) / "request.json"
        save_json(payload, {"location": location, "properties": {
            "source": {"script": script}, "timeoutInSeconds": 600,
            "protectedParameters": [{"name": name, "value": value} for name, value in protected.items()]}})
        runner(["az", "rest", "--method", "put", "--url", url, "--body", "@" + str(payload), "-o", "none"], capture=True)
    for _ in range(150):
        result = runner(["az", "rest", "--method", "get", "--url", url + "&$expand=instanceView"], capture=True)
        value = json.loads(result.stdout).get("properties", {})
        view = value.get("instanceView", {})
        execution = view.get("executionState")
        if execution == "Succeeded" and view.get("exitCode") == 0:
            runner(["az", "rest", "--method", "delete", "--url", url, "-o", "none"], capture=True)
            return
        if execution in {"Failed", "Canceled", "TimedOut"} or value.get("provisioningState") == "Failed":
            raise SetupError("Protected VPN bootstrap failed; local credentials retained for a safe retry")
        time.sleep(4)
    raise SetupError("VPN bootstrap has not finished; repeat setup to inspect/reconcile it")


def bootstrap_vpn(connection, configurator, bundle, *, runner=command):
    """Reconcile trust without replacing an existing CA on a restored disk."""
    import hashlib
    args = [connection[key] for key in ("ssh_username", "workspace_mount_path", "openvpn_port", "openvpn_network", "openvpn_netmask", "openvpn_server_address")]
    expected = runner(["openssl", "x509", "-in", Path(connection["openvpn_local_root_path"]) / "ca.crt", "-noout", "-fingerprint", "-sha256"], capture=True).stdout.strip()
    ca = str(Path(connection["workspace_mount_path"]) / ".codex-on-vm/openvpn/server/ca.crt")
    script = "\n".join([
        "#!/bin/bash", "set -euo pipefail", "umask 077", 'stage="$(mktemp -d /tmp/secondbrain-vpn.XXXXXX)"',
        "trap 'rm -rf -- \"$stage\"' EXIT", f"existing={shlex.quote(ca)}", f"expected={shlex.quote(expected)}",
        'if [[ "${CODEX_VM_TEST_MODE:-0}" == "1" && -n "${CODEX_VM_ROOT:-}" ]]; then existing="$CODEX_VM_ROOT$existing"; fi',
        'if [[ -f "$existing" ]] && [[ "$(openssl x509 -in "$existing" -noout -fingerprint -sha256)" != "$expected" ]]; then',
        "  echo 'Existing VPN trust differs; restore matching local credentials before retrying' >&2; exit 1", "fi",
        'printf %s "$SERVER_BUNDLE" | base64 --decode >"$stage/server-bundle.tar"',
        'printf %s "$CONFIGURATOR" | base64 --decode >"$stage/configure.sh"',
        f'echo "{hashlib.sha256(configurator.read_bytes()).hexdigest()}  $stage/configure.sh" | sha256sum --check --status',
        'bash "$stage/configure.sh" ' + shlex.join(map(str, args)) + ' "$stage/server-bundle.tar"',
        "echo SECOND_BRAIN_VPN_READY=1", ""])
    managed_run_command(connection, script, {"SERVER_BUNDLE": base64.b64encode(bundle.read_bytes()).decode(),
                                            "CONFIGURATOR": base64.b64encode(configurator.read_bytes()).decode()}, runner=runner)


def prerequisites(interactive):
    if platform.system() != "Darwin":
        raise SetupError("Azure entry mode is supported from macOS; use host mode inside Ubuntu")
    missing = [name for name in ("az", "terraform", "git", "openssl") if not shutil.which(name)]
    if missing:
        if not shutil.which("brew"):
            raise SetupError("Homebrew is required to install missing Mac tools; install it from https://brew.sh and repeat setup")
        if not interactive or not yes("Install missing Mac tools with Homebrew: " + ", ".join(missing) + "?", interactive=interactive):
            raise SetupError("Mac prerequisites remain incomplete")
        if "terraform" in missing:
            command(["brew", "tap", "hashicorp/tap"])
        packages = [{"az": "azure-cli", "terraform": "hashicorp/tap/terraform", "openssl": "openssl@3"}.get(name, name) for name in missing]
        command(["brew", "install", *packages])
    return "Mac Azure/Terraform/SSH prerequisites verified"


def cloud_state(root, selected, interactive):
    cloud = selected.get("azure", {})
    required = {"subscription", "owner", "resource_group", "storage_account", "container", "key", "location"}
    if not required <= set(cloud) or not re.fullmatch(r"[a-fA-F0-9-]{36}", cloud["subscription"]):
        raise SetupError("Azure configuration needs subscription, owner and state backend fields")
    if not re.fullmatch(r"[a-z0-9]{3,24}", cloud["storage_account"]):
        raise SetupError("State storage account must have 3–24 lowercase letters/digits")
    files = backend_files(root, cloud)
    account = command(["az", "account", "show", "-o", "json"], capture=True, check=False)
    if account.returncode:
        if not interactive:
            raise SetupError("Azure login is required; rerun interactively")
        command(["az", "login", "--use-device-code"], capture=False)
    command(["az", "account", "set", "--subscription", cloud["subscription"]])
    common = ["--subscription", cloud["subscription"], "--only-show-errors"]
    exists = command(["az", "storage", "account", "show", "-g", cloud["resource_group"], "-n", cloud["storage_account"], *common], capture=True, check=False)
    if exists.returncode:
        print(f"Create Azure state storage: {cloud['resource_group']}/{cloud['storage_account']} in {cloud['location']} (billable).")
        if not interactive or not yes("Create this state backend?", False, interactive=interactive):
            raise SetupError("State backend creation requires explicit interactive approval")
        command(["az", "group", "create", "-n", cloud["resource_group"], "-l", cloud["location"], *common], capture=True)
        command(["az", "storage", "account", "create", "-g", cloud["resource_group"], "-n", cloud["storage_account"],
                 "-l", cloud["location"], "--sku", "Standard_LRS", "--min-tls-version", "TLS1_2", "--allow-blob-public-access", "false", *common], capture=True)
        scope = f"/subscriptions/{cloud['subscription']}/resourceGroups/{cloud['resource_group']}/providers/Microsoft.Storage/storageAccounts/{cloud['storage_account']}"
        user = command(["az", "ad", "signed-in-user", "show", "--query", "id", "-o", "tsv"], capture=True).stdout.strip()
        command(["az", "role", "assignment", "create", "--assignee-object-id", user, "--assignee-principal-type", "User", "--role", "Storage Blob Data Contributor", "--scope", scope, *common], capture=True)
    ready = False
    for attempt in range(18):
        probe = command(["az", "storage", "container", "create", "--account-name", cloud["storage_account"], "--name", cloud["container"], "--auth-mode", "login", *common], capture=True, check=False)
        if not probe.returncode:
            ready = True
            break
        if attempt == 0:
            print("Waiting for state storage access. The signed-in identity needs Storage Blob Data Contributor on this account.", flush=True)
        time.sleep(5)
    if not ready:
        raise SetupError("State storage access is unavailable. Grant the signed-in identity Storage Blob Data Contributor, then repeat setup; existing resources are retained")
    for path, content in files:
        if not path.exists():
            atomic_write(path, content)
    tf = root / "deployments/prod/tf"
    command(["terraform", f"-chdir={tf}", "init", "-input=false", "-backend-config=backend.hcl"])
    return "Azure login and persistent Terraform backend verified"


def backend_files(root, cloud):
    tf = root / "deployments/prod/tf"
    values = {"resource_group_name": cloud["resource_group"], "storage_account_name": cloud["storage_account"], "container_name": cloud["container"], "key": cloud["key"], "use_azuread_auth": True}
    backend = "\n".join(f"{key} = {json.dumps(value)}" for key, value in values.items()) + "\n"
    tfvars = "\n".join(f"{key} = {json.dumps(value)}" for key, value in (("subscription_id", cloud["subscription"]), ("owner", cloud["owner"]))) + "\n"
    # A pre-existing Terraform backend defines identity. Never silently migrate its state.
    files = ((tf / "backend.hcl", backend), (tf / "terraform.tfvars", tfvars))
    for path, content in files:
        if path.exists():
            try:
                existing = tomllib.loads(path.read_text())
                desired = tomllib.loads(content)
            except tomllib.TOMLDecodeError:
                raise SetupError(f"Preserve custom {path.name}; reconcile its backend identity explicitly") from None
            identity = {"resource_group_name", "storage_account_name", "container_name", "key"} if path.name == "backend.hcl" else {"subscription_id", "owner"}
            if any(existing.get(key) != desired[key] for key in identity):
                raise SetupError(f"Existing {path.name} differs from saved setup choices; reconcile it explicitly before continuing")
    return files


def provision(root, state, interactive):
    tf = root / "deployments/prod/tf"
    plan_file = state / "azure.tfplan"
    result = command(["terraform", f"-chdir={tf}", "plan", "-input=false", "-detailed-exitcode", f"-out={plan_file}"], check=False)
    if result.returncode not in {0, 2}:
        raise SetupError("Terraform planning failed; existing state retained")
    if result.returncode == 2:
        print("This plan can create billable Azure VM, managed disks, public IP and backup resources.")
        if not interactive or not yes("Apply exactly the displayed Terraform plan?", False, interactive=interactive):
            raise SetupError("Azure plan requires explicit interactive approval")
        command(["terraform", f"-chdir={tf}", "apply", "-input=false", plan_file])
    return "Azure infrastructure reconciled against the saved Terraform state"


def connect(root, state, interactive):
    connection = json.loads(command(["terraform", f"-chdir={root / 'deployments/prod/tf'}", "output", "-json", "connection"], capture=True).stdout)
    base = ["az", "vm"]
    identity_args = ["--subscription", connection["subscription_id"], "--resource-group", connection["resource_group_name"], "--name", connection["vm_name"]]
    vm_id = command([*base, "show", *identity_args, "--query", "vmId", "-o", "tsv"], capture=True).stdout.strip()
    if not vm_id:
        raise SetupError("Azure VM identity is unavailable")
    power = command([*base, "get-instance-view", *identity_args, "--query", "instanceView.statuses[?starts_with(code, 'PowerState/')].code | [0]", "-o", "tsv"], capture=True).stdout.strip()
    if power != "PowerState/running":
        print("The Azure VM is stopped or starting; running it incurs compute charges.")
        if not interactive or not yes("Start the selected VM?", False, interactive=interactive):
            raise SetupError("VM startup requires explicit approval")
        command([*base, "start", *identity_args])
    receipt = state / "azure-machine.json"
    previous = json.loads(receipt.read_text()) if receipt.is_file() else {}
    def prepare():
        command([root / "scripts/codex-vm.sh", "setup"])
        with tempfile.TemporaryDirectory(prefix="secondbrain-vm-helpers-") as tmp:
            helpers = Path(tmp)
            command([root / "scripts/codex-vm.sh", "__export-helpers", helpers], capture=True)
            command([helpers / "scripts/openvpn-setup.sh", "--bootstrap"], env={**os.environ, "SECOND_BRAIN_SETUP_SCRIPTS": str(root / "scripts")})
        save_json(receipt, {"vm_id":vm_id, "ssh_fqdn":connection["ssh_fqdn"]})
    if previous.get("vm_id") != vm_id or not all(Path(connection[key]).is_file() for key in ("ssh_known_hosts_path", "ssh_host_config_path", "openvpn_client_profile_path")):
        prepare()
    ssh_config = Path(connection["ssh_host_config_path"])
    ssh = ["ssh", "-F", str(ssh_config), "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", connection["openvpn_ssh_alias"]]
    repaired = False
    while command([*ssh, "true"], capture=True, check=False).returncode:
        print(f"Connect this owner-only OpenVPN profile in your VPN client:\n{connection['openvpn_client_profile_path']}")
        if not interactive or not yes("VPN connected; retry the verified SSH connection?", True, interactive=interactive):
            raise SetupError("VPN connection is required; profile and cloud state retained for the next setup")
        if command([*ssh, "true"], capture=True, check=False).returncode and not repaired:
            print("Refreshing VM preparation and host trust through the Azure agent.", flush=True)
            prepare()
            repaired = True
    destination = str(Path(connection["workspace_mount_path"]) / "dot-codex")
    origin = command(["git", "-C", root, "remote", "get-url", "origin"], capture=True).stdout.strip()
    if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?", origin):
        # SSH GitHub origins are common locally; remote bootstrap uses HTTPS and operator auth.
        match = re.fullmatch(r"git@github\.com:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?:\.git)?", origin)
        if not match:
            raise SetupError("Remote bootstrap needs a GitHub HTTPS/SSH origin without embedded credentials")
        origin = "https://github.com/" + match[1]
    from setup_export import APPLY, bundle
    with tempfile.TemporaryDirectory(prefix="secondbrain-transfer-") as tmp:
        archive = bundle(root, Path(tmp))
        stage = command([*ssh, "umask 077; mktemp -d /tmp/secondbrain-source.XXXXXX"], capture=True).stdout.strip()
        if not re.fullmatch(r"/tmp/secondbrain-source\.[A-Za-z0-9]+", stage):
            raise SetupError("Remote source staging path is invalid")
        try:
            command(["scp", "-F", ssh_config, archive, connection["openvpn_ssh_alias"] + ":" + stage + "/source.tar.gz"])
            apply = "python3 -c " + shlex.quote(APPLY) + " " + shlex.join([stage + "/source.tar.gz", destination, origin,
                     str(Path(connection["workspace_mount_path"]) / ".secondbrain/source-bundle.json")])
            command([*ssh, apply])
        finally:
            command([*ssh, "rm -rf -- " + shlex.quote(stage)], capture=True, check=False)
    script = "set -euo pipefail\ncd " + shlex.quote(destination) + "\nexec ./secondbrain.sh setup --mode host" + ("" if interactive else " --non-interactive")
    # A TTY carries device codes and QR pairing directly to the operator. No credentials cross stdout capture.
    result = command(["ssh", "-t", "-F", str(ssh_config), connection["openvpn_ssh_alias"], "bash -lc " + shlex.quote(script)], check=False)
    if result.returncode:
        raise SetupError("Remote host setup remains incomplete; repeat setup to reconnect and resume")
    return "The same host setup completed through verified VPN SSH"


def setup(root, state, selected, *, interactive):
    journal = Journal(state)
    journal.phase("mac-prerequisites", lambda: prerequisites(interactive))
    journal.phase("azure-state", lambda: cloud_state(root, selected, interactive), requires=("mac-prerequisites",))
    journal.phase("azure-resources", lambda: provision(root, state, interactive), requires=("azure-state",))
    journal.phase("remote-host", lambda: connect(root, state, interactive), requires=("azure-resources",))
    failed = journal.finish()
    print(f"\n{'Setup incomplete; repeat to resume' if failed else 'Setup verified on the remote host'}")
    return 2 if failed else 0
