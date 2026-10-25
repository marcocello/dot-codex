#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SELF="$SCRIPT_DIR/$(basename "${BASH_SOURCE[0]}")"
TF_DIR="$ROOT/deployments/prod/tf"
VPN_SSH_ALIAS="${CODEX_VM_VPN_SSH_ALIAS:-codex-on-vm-vpn}"
OPENVPN_PROFILE_PATH="${CODEX_VM_OPENVPN_PROFILE_PATH:-$HOME/.config/codex-on-vm/openvpn/codex-on-vm.ovpn}"
DRY_RUN=0
USE_COLOR=1
PREPARATION_CONFIRMED=0
ACTION_CANCELLED=0

if [[ ! -t 1 || -n "${NO_COLOR:-}" ]]; then
  USE_COLOR=0
fi

fail() {
  printf 'Codex VM: %s\n' "$1" >&2
  exit 1
}

paint() {
  local code="$1"
  shift
  if [[ "$USE_COLOR" == "1" ]]; then
    printf '\033[%sm%s\033[0m' "$code" "$*"
  else
    printf '%s' "$*"
  fi
}

headline() {
  printf '\n'
  paint '1;36' "$1"
  printf '\n'
}

stage() {
  printf '\n'
  paint '1;34' "==> $1"
  printf '\n'
}

success() {
  paint '1;32' "Done:"
  printf ' %s\n' "$1"
}

warning() {
  paint '1;33' "Note:"
  printf ' %s\n' "$1"
}

print_command() {
  printf '    $'
  printf ' %q' "$@"
  printf '\n'
}

run_command() {
  if [[ "$DRY_RUN" == "1" ]]; then
    print_command "$@"
    return 0
  fi
  "$@"
}

run_stage() {
  local label="$1"
  local status
  shift
  stage "$label"
  set +e
  "$@"
  status=$?
  set -e
  if [[ "$status" != "0" ]]; then
    paint '1;31' "Failed:"
    printf ' %s (exit %s)\n' "$label" "$status" >&2
    return "$status"
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    success "$label planned"
  else
    success "$label"
  fi
}

extract_embedded_helper() {
  local helper="$1"
  local target="$2"
  local begin_marker="__CODEX_VM_HELPER_BEGIN__ $helper"
  local end_marker="__CODEX_VM_HELPER_END__ $helper"

  awk -v begin_marker="$begin_marker" -v end_marker="$end_marker" '
    $0 == begin_marker {
      found = 1
      capture = 1
      next
    }
    $0 == end_marker {
      if (capture) {
        closed = 1
        exit
      }
    }
    capture {
      print
    }
    END {
      if (!found || !closed) {
        exit 1
      }
    }
  ' "$SELF" >"$target" ||
    fail "could not extract embedded helper: $helper"
}

materialize_helpers() {
  local target="$1"
  local helper

  [[ "$target" == /* ]] || fail "embedded helper target must be an absolute path"
  [[ -d "$ROOT/deployments" ]] || fail "missing deployment tree: $ROOT/deployments"

  if [[ -e "$target" || -L "$target" ]]; then
    [[ -d "$target" && ! -L "$target" ]] ||
      fail "embedded helper target already exists and is not a directory: $target"
    [[ -z "$(find "$target" -mindepth 1 -maxdepth 1 -print -quit)" ]] ||
      fail "embedded helper target must be empty: $target"
  else
    mkdir -m 0700 -p "$target"
  fi

  chmod 0700 "$target"
  mkdir -m 0700 -p "$target/scripts" "$target/vm-scripts"
  ln -s "$ROOT/deployments" "$target/deployments"

  for helper in \
    prepare-machine.sh \
    codex-pair.sh \
    dot-codex-bootstrap.sh \
    telegram-to-agents-bootstrap.sh \
    openvpn-setup.sh \
    remote-control-recover.sh; do
    extract_embedded_helper "$helper" "$target/scripts/$helper"
  done

  for helper in \
    ensure-codex-remote-control.sh \
    ensure-ssh-keys.sh \
    fetch-verified-artifact.sh \
    install-verified-codex.sh \
    configure-codex-openvpn.sh \
    prepare-codex-vm.sh \
    prepare-persistent-codex-home.sh; do
    extract_embedded_helper "$helper" "$target/vm-scripts/$helper"
  done

  chmod 0700 "$target/scripts/"*.sh
  chmod 0700 "$target/vm-scripts/"*.sh
}

run_embedded_payload() {
  local payload="$1"
  local runtime_root
  shift

  case "$payload" in
    ensure-codex-remote-control.sh) ;;
    ensure-ssh-keys.sh) ;;
    fetch-verified-artifact.sh) ;;
    install-verified-codex.sh) ;;
    configure-codex-openvpn.sh) ;;
    prepare-codex-vm.sh) ;;
    prepare-persistent-codex-home.sh) ;;
    *) fail "unknown embedded VM payload: $payload" ;;
  esac

  (
    set -euo pipefail
    umask 077
    runtime_root="$(mktemp -d "${TMPDIR:-/tmp}/codex-vm.XXXXXX")"
    trap 'rm -rf "$runtime_root"' EXIT INT TERM
    materialize_helpers "$runtime_root"
    "$runtime_root/vm-scripts/$payload" "$@"
  )
}

run_helper() {
  local helper="$1"
  local runtime_root
  shift

  case "$helper" in
    prepare-machine.sh) ;;
    codex-pair.sh) ;;
    dot-codex-bootstrap.sh) ;;
    telegram-to-agents-bootstrap.sh) ;;
    openvpn-setup.sh) ;;
    remote-control-recover.sh) ;;
    *) fail "unknown embedded helper: $helper" ;;
  esac

  if [[ "$DRY_RUN" == "1" ]]; then
    printf '    embedded helper: %s' "$helper"
    if [[ $# -gt 0 ]]; then
      printf ' %q' "$@"
    fi
    printf '\n'
    return 0
  fi

  if [[ "${CODEX_VM_TEST_MODE:-0}" == "1" && -n "${CODEX_VM_TEST_HELPER_DIR:-}" ]]; then
    [[ "$CODEX_VM_TEST_HELPER_DIR" == /* ]] ||
      fail "CODEX_VM_TEST_HELPER_DIR must be an absolute path"
    [[ -x "$CODEX_VM_TEST_HELPER_DIR/$helper" ]] ||
      fail "missing executable test helper: $CODEX_VM_TEST_HELPER_DIR/$helper"
    "$CODEX_VM_TEST_HELPER_DIR/$helper" "$@"
    return
  fi

  (
    set -euo pipefail
    umask 077
    runtime_root="$(mktemp -d "${TMPDIR:-/tmp}/codex-vm.XXXXXX")"
    trap 'rm -rf "$runtime_root"' EXIT INT TERM
    materialize_helpers "$runtime_root"
    "$runtime_root/scripts/$helper" "$@"
  )
}

require_macos() {
  [[ "$(uname -s)" == "Darwin" ]] || fail "this command is for macOS"
}

require_commands() {
  local command
  for command in "$@"; do
    command -v "$command" >/dev/null || fail "missing required command: $command"
  done
}

print_usage() {
  cat <<'EOF'
Codex VM

Usage:
  scripts/codex-vm.sh [--dry-run] [--no-color] <command> [arguments]
  scripts/codex-vm.sh

Commands:
  setup                     Set up or repair Codex after manual Terraform apply
  sign-in                   Sign in to Codex
  pair                      Pair a device with the signed-in Codex account
  dot-codex                 Clone or update dot-codex from GitHub
  telegram-to-agents        Install or update telegram-to-agents on the VM
  vpn-setup [--rotate]      Repair or intentionally rotate private OpenVPN access
  menu                      Open the interactive menu
  help                      Show this help

Options:
  --dry-run                 Print mutating commands without running them
  --no-color                Disable ANSI colors

Examples:
  scripts/codex-vm.sh setup
  scripts/codex-vm.sh sign-in
  scripts/codex-vm.sh pair
  scripts/codex-vm.sh dot-codex
  scripts/codex-vm.sh telegram-to-agents
  scripts/codex-vm.sh vpn-setup

Connect the Mac OpenVPN client before sign-in, pairing, dot-codex, telegram-to-agents, or VPN maintenance.
If preparation is required, interactive commands ask before running setup.
Non-interactive commands stop and instruct you to run setup explicitly.
EOF
}

check_openvpn_connection() {
  [[ $# -eq 0 ]] || fail "OpenVPN connection check accepts no positional arguments"
  [[ -n "$VPN_SSH_ALIAS" && "$VPN_SSH_ALIAS" != -* && "$VPN_SSH_ALIAS" != *[[:space:]]* ]] ||
    fail "CODEX_VM_VPN_SSH_ALIAS is invalid"
  [[ "$OPENVPN_PROFILE_PATH" == /* && "$OPENVPN_PROFILE_PATH" != *$'\n'* && "$OPENVPN_PROFILE_PATH" != *$'\r'* ]] ||
    fail "CODEX_VM_OPENVPN_PROFILE_PATH must be an absolute path without control characters"

  stage "Check OpenVPN connection"
  printf '    SSH alias: %s\n' "$VPN_SSH_ALIAS"
  printf '    Profile: %s\n' "$OPENVPN_PROFILE_PATH"
  if [[ "$DRY_RUN" == "1" ]]; then
    success "OpenVPN connection check planned"
    return 0
  fi

  require_commands ssh
  if ssh -o BatchMode=yes -o ConnectTimeout=5 "$VPN_SSH_ALIAS" true >/dev/null 2>&1; then
    success "OpenVPN is connected"
    return 0
  fi
  if [[ -f "$OPENVPN_PROFILE_PATH" ]]; then
    fail "OpenVPN is not connected. Use $OPENVPN_PROFILE_PATH; import it into the Mac OpenVPN client, connect it, and retry"
  fi
  fail "OpenVPN is not connected and the profile is missing at $OPENVPN_PROFILE_PATH; restore or configure the profile, import it into the Mac OpenVPN client, connect it, and retry"
}

delegate_prepared_no_args() {
  local label="$1"
  local helper="$2"
  shift 2
  [[ $# -eq 0 ]] || fail "$label accepts no positional arguments"
  ensure_vm_prepared || return $?
  [[ "$ACTION_CANCELLED" == "0" ]] || return 0
  check_openvpn_connection || return $?
  headline "$label"
  run_stage "$label" run_helper "$helper"
}

account_action() {
  local mode="$1"
  local label="$2"
  shift 2
  [[ $# -eq 0 ]] || fail "$label accepts no positional arguments"
  ensure_vm_prepared || return $?
  [[ "$ACTION_CANCELLED" == "0" ]] || return 0
  check_openvpn_connection || return $?
  headline "$label"
  run_stage "$label" run_helper codex-pair.sh "$mode"
}

setup_machine() {
  [[ $# -eq 0 ]] || fail "Set up or repair Codex on the VM accepts no positional arguments"
  headline "Set up or repair Codex on the VM"
  run_stage "Set up or repair Codex on the VM" run_helper prepare-machine.sh || return $?
  PREPARATION_CONFIRMED=1
}

openvpn_setup() {
  [[ $# -le 1 ]] || fail "vpn-setup accepts only the optional --rotate flag"
  if [[ $# -eq 1 && "$1" != "--rotate" ]]; then
    fail "vpn-setup accepts only the optional --rotate flag"
  fi
  ensure_vm_prepared || return $?
  [[ "$ACTION_CANCELLED" == "0" ]] || return 0
  check_openvpn_connection || return $?
  headline "Repair or rotate OpenVPN"
  run_stage "Repair or rotate OpenVPN" run_helper openvpn-setup.sh "$@"
}

read_preparation_target() {
  local connection
  connection="$(terraform "-chdir=$TF_DIR" output -json connection)" ||
    fail "could not read Terraform connection output; run terraform apply first"
  CONNECTION="$connection" python3 - <<'PY'
import json
import os
import re

try:
    value = json.loads(os.environ["CONNECTION"])
except (json.JSONDecodeError, TypeError) as error:
    raise SystemExit(f"Terraform connection output is not valid JSON: {error}")

keys = (
    "subscription_id",
    "resource_group_name",
    "vm_name",
    "workspace_mount_path",
    "codex_version",
)
patterns = (
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
    r"[A-Za-z0-9._()/-]{1,90}",
    r"[A-Za-z0-9-]{1,64}",
    r"/[^\t\r\n]+",
    r"[0-9]+\.[0-9]+\.[0-9]+",
)
try:
    fields = [str(value[key]) for key in keys]
except (KeyError, TypeError) as error:
    raise SystemExit(f"Terraform connection output is missing {error}")
for key, field, pattern in zip(keys, fields, patterns):
    if re.fullmatch(pattern, field) is None:
        raise SystemExit(f"Terraform connection output contains an unsafe {key}")
print("\t".join(fields))
PY
}

vm_is_prepared() {
  local values subscription_id resource_group vm_name workspace_mount codex_version
  local active_subscription check_script response
  local progress_interval progress_pid elapsed check_status

  require_commands terraform az python3
  printf '    Terraform: read current VM target\n'
  values="$(read_preparation_target)" || return $?
  IFS=$'\t' read -r \
    subscription_id resource_group vm_name workspace_mount codex_version <<<"$values"

  printf '    Azure: verify active subscription\n'
  active_subscription="$(az account show --query id --output tsv)" ||
    fail "could not read the active Azure subscription"
  [[ "$active_subscription" == "$subscription_id" ]] ||
    fail "Azure CLI is using subscription $active_subscription, expected $subscription_id"

  check_script="$(
    CODEX_VERSION="$codex_version" WORKSPACE_MOUNT="$workspace_mount" python3 - <<'PY'
import os
import shlex

version = shlex.quote(f"codex_version={os.environ['CODEX_VERSION']}")
mount = shlex.quote(f"workspace_mount={os.environ['WORKSPACE_MOUNT']}")
telegram = shlex.quote("telegram_to_agents_prerequisites=1")
print("marker=/var/lib/codex-on-vm/prepared")
print(
    'if test -r "$marker"'
    f" && grep -Fqx -- {version} \"$marker\""
    f" && grep -Fqx -- {mount} \"$marker\""
    f" && grep -Fqx -- {telegram} \"$marker\"; then"
)
print("  printf 'CODEX_ON_VM_PREPARED=1\\n'")
print("fi")
PY
  )"

  progress_interval="${CODEX_VM_PREPARATION_PROGRESS_SECONDS:-10}"
  case "$progress_interval" in
    '' | *[!0-9]* | 0*) fail "CODEX_VM_PREPARATION_PROGRESS_SECONDS must be a positive integer without leading zeroes" ;;
  esac

  printf '    Azure: inspect preparation marker on %s\n' "$vm_name"
  printf '    Azure: Run Command can take a minute; progress will remain visible here.\n'
  python3 -u - "$progress_interval" <<'PY' &
import sys
import time

interval = int(sys.argv[1])
elapsed = 0
while True:
    time.sleep(interval)
    elapsed += interval
    print(f"    Azure: still checking VM preparation ({elapsed}s elapsed)", flush=True)
PY
  progress_pid=$!

  check_status=0
  response="$(az vm run-command invoke \
    --subscription "$subscription_id" \
    --resource-group "$resource_group" \
    --name "$vm_name" \
    --command-id RunShellScript \
    --scripts "$check_script" \
    --output json \
    --only-show-errors)" || check_status=$?

  kill "$progress_pid" >/dev/null 2>&1 || true
  wait "$progress_pid" 2>/dev/null || true

  if [[ "$check_status" != "0" ]]; then
    warning "Azure Run Command could not inspect the preparation marker."
    return "$check_status"
  fi
  printf '    Azure: preparation response received\n'

  RESPONSE="$response" python3 - <<'PY'
import json
import os

try:
    value = json.loads(os.environ["RESPONSE"])
except (json.JSONDecodeError, TypeError):
    raise SystemExit(1)

messages = []
for item in value.get("value", []):
    if isinstance(item, dict):
        messages.append(str(item.get("message", "")))
if any(
    line.strip() == "CODEX_ON_VM_PREPARED=1"
    for message in messages
    for line in message.splitlines()
):
    raise SystemExit(0)
raise SystemExit(1)
PY
}

ensure_vm_prepared() {
  local answer
  ACTION_CANCELLED=0

  if [[ "$PREPARATION_CONFIRMED" == "1" ]]; then
    return 0
  fi

  stage "Check VM preparation"
  if [[ "$DRY_RUN" == "1" ]]; then
    printf '    Terraform: read current VM target\n'
    printf '    Azure: verify active subscription\n'
    printf '    Azure: inspect the preparation marker with Run Command\n'
    printf '    Marker: /var/lib/codex-on-vm/prepared\n'
    printf '    Setup requires confirmation when the current marker is missing or stale.\n'
    PREPARATION_CONFIRMED=1
    success "VM preparation check planned"
    return 0
  fi

  if vm_is_prepared; then
    PREPARATION_CONFIRMED=1
    success "VM preparation is current"
    return 0
  fi

  if [[ ! -t 0 || ! -t 1 ]]; then
    fail "VM setup is required before this command; run scripts/codex-vm.sh setup first"
  fi

  warning "Codex is not set up for the current VM configuration."
  printf 'Run setup now? [y/N] '
  if ! IFS= read -r answer </dev/tty; then
    printf '\n'
    warning "Action cancelled."
    ACTION_CANCELLED=1
    return 0
  fi
  case "$answer" in
    y | Y | [yY][eE][sS])
      setup_machine || return $?
      ;;
    *)
      warning "Action cancelled."
      ACTION_CANCELLED=1
      ;;
  esac
}

show_menu() {
  local choice action
  [[ $# -eq 0 ]] || fail "menu accepts no positional arguments"
  [[ -t 0 && -t 1 ]] || fail "the interactive menu requires a terminal; run help for explicit commands"

  headline "Codex VM operator console"
  printf '\n'
  paint '1;33' "Choose one action"
  printf '\n  1) Set up or repair Codex on the VM\n'
  printf '  2) Sign in to Codex\n'
  printf '  3) Pair a device\n'
  printf '  4) Clone or update dot-codex from GitHub\n'
  printf '  5) Install or update telegram-to-agents\n'
  printf '  6) Repair OpenVPN\n\n'
  printf 'Choose an action: '
  IFS= read -r choice </dev/tty || return 0
  case "$choice" in
    1) action=setup ;;
    2) action=sign-in ;;
    3) action=pair ;;
    4) action=dot-codex ;;
    5) action=telegram-to-agents ;;
    6) action=vpn-setup ;;
    *) fail "unknown menu selection '$choice'; choose 1, 2, 3, 4, 5, or 6" ;;
  esac

  dispatch "$action"
}

dispatch() {
  local command_name="$1"
  shift
  case "$command_name" in
    help)
      [[ $# -eq 0 ]] || fail "help accepts no positional arguments"
      print_usage
      return 0
      ;;
    setup | sign-in | pair | dot-codex | telegram-to-agents | vpn-setup | menu)
      ;;
    *) fail "unknown command '$command_name'; run scripts/codex-vm.sh help" ;;
  esac

  require_macos
  case "$command_name" in
    setup) setup_machine "$@" ;;
    sign-in) account_action sign-in "Sign in to Codex" "$@" ;;
    pair) account_action pair "Pair a device" "$@" ;;
    dot-codex) delegate_prepared_no_args "Clone or update dot-codex from GitHub" dot-codex-bootstrap.sh "$@" ;;
    telegram-to-agents) delegate_prepared_no_args "Install or update telegram-to-agents" telegram-to-agents-bootstrap.sh "$@" ;;
    vpn-setup) openvpn_setup "$@" ;;
    menu) show_menu "$@" ;;
  esac
}

main() {
  local command_name

  if [[ "${1:-}" == "__export-helpers" ]]; then
    [[ $# -eq 2 ]] || fail "__export-helpers requires one absolute target directory"
    materialize_helpers "$2"
    return 0
  fi

  if [[ "${1:-}" == "__extract-helpers" ]]; then
    [[ "${CODEX_VM_TEST_MODE:-0}" == "1" ]] ||
      fail "__extract-helpers is available only in test mode"
    [[ $# -eq 2 ]] ||
      fail "__extract-helpers requires one absolute target directory"
    materialize_helpers "$2"
    return 0
  fi

  if [[ "${1:-}" == "__terraform-ensure-ssh-keys" ]]; then
    [[ $# -eq 1 ]] ||
      fail "__terraform-ensure-ssh-keys accepts no positional arguments"
    run_embedded_payload ensure-ssh-keys.sh
    return 0
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run) DRY_RUN=1 ;;
      --no-color) USE_COLOR=0 ;;
      --help | -h)
        print_usage
        return 0
        ;;
      --) shift; break ;;
      -*) fail "unknown option '$1'; run scripts/codex-vm.sh help" ;;
      *) break ;;
    esac
    shift
  done

  if [[ $# -eq 0 ]]; then
    command_name=menu
  else
    command_name="$1"
    shift
  fi
  dispatch "$command_name" "$@"
}

main "$@"
exit $?

__CODEX_VM_HELPER_BEGIN__ prepare-machine.sh
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="$ROOT/deployments/prod/tf"
VM_SCRIPT_DIR="$ROOT/vm-scripts"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() {
  printf 'Machine preparation failed: %s\n' "$1" >&2
  exit 1
}

write_private_file() {
  local target="$1"
  local temporary
  mkdir -p "$(dirname "$target")"
  temporary="$(mktemp "$(dirname "$target")/.codex-on-vm.XXXXXX")"
  cat >"$temporary"
  chmod 0600 "$temporary"
  mv -f "$temporary" "$target"
}

[[ $# -eq 0 ]] || fail "this command accepts no positional arguments"
[[ "$(uname -s)" == "Darwin" ]] || fail "this helper is for macOS"
for command in az python3 terraform; do
  command -v "$command" >/dev/null || fail "missing required command: $command"
done

for script in \
  fetch-verified-artifact.sh \
  install-verified-codex.sh \
  prepare-persistent-codex-home.sh \
  configure-codex-openvpn.sh \
  ensure-codex-remote-control.sh \
  prepare-codex-vm.sh; do
  [[ -r "$VM_SCRIPT_DIR/$script" ]] || fail "missing VM preparation script: $VM_SCRIPT_DIR/$script"
done

CONNECTION="$(terraform -chdir="$TF_DIR" output -json connection)"
IFS=$'\t' read -r \
  SUBSCRIPTION_ID \
  RESOURCE_GROUP \
  VM_NAME \
  SSH_FQDN \
  SSH_USERNAME \
  WORKSPACE_MOUNT_PATH \
  WORKSPACE_DISK_LUN \
  CODEX_VERSION \
  CODEX_PACKAGE_URL \
  CODEX_PACKAGE_SHA256 \
  MAC_PRIVATE_KEY_PATH \
  SSH_HOST_CONFIG_PATH \
  SSH_KNOWN_HOSTS_PATH \
  OPENVPN_PORT \
  OPENVPN_NETWORK \
  OPENVPN_NETMASK \
  OPENVPN_SERVER_ADDRESS \
  OPENVPN_SSH_ALIAS <<<"$(CONNECTION="$CONNECTION" python3 - <<'PY'
import json
import os
import re

value = json.loads(os.environ["CONNECTION"])
keys = (
    "subscription_id",
    "resource_group_name",
    "vm_name",
    "ssh_fqdn",
    "ssh_username",
    "workspace_mount_path",
    "workspace_disk_lun",
    "codex_version",
    "codex_package_url",
    "codex_package_sha256",
    "mac_private_key_path",
    "ssh_host_config_path",
    "ssh_known_hosts_path",
    "openvpn_port",
    "openvpn_network",
    "openvpn_netmask",
    "openvpn_server_address",
    "openvpn_ssh_alias",
)
fields = [str(value[key]) for key in keys]
patterns = (
    r"[0-9a-fA-F-]{36}",
    r"[A-Za-z0-9._()/-]{1,90}",
    r"[A-Za-z0-9-]{1,64}",
    r"[A-Za-z0-9.-]{1,253}",
    r"[a-z_][a-z0-9_-]{0,31}",
    r"/[^\t\r\n]+",
    r"[0-9]+",
    r"[0-9]+\.[0-9]+\.[0-9]+",
    r"https://[^\t\r\n]+",
    r"[0-9a-f]{64}",
    r"/[^\t\r\n]+",
    r"/[^\t\r\n]+",
    r"/[^\t\r\n]+",
    r"[0-9]{1,5}",
    r"[0-9.]{7,15}",
    r"[0-9.]{7,15}",
    r"[0-9.]{7,15}",
    r"[A-Za-z0-9._-]{1,64}",
)
for key, field, pattern in zip(keys, fields, patterns):
    if re.fullmatch(pattern, field) is None:
        raise SystemExit(f"Terraform connection output contains an unsafe {key}")
print("\t".join(fields))
PY
)"

[[ "$(az account show --query id --output tsv)" == "$SUBSCRIPTION_ID" ]] ||
  fail "Azure CLI is using a different subscription"

printf 'Preparing VM %s in resource group %s from this Mac.\n' "$VM_NAME" "$RESOURCE_GROUP"
agent_ready=0
for _attempt in $(seq 1 60); do
  if [[ "$(az vm get-instance-view \
    --subscription "$SUBSCRIPTION_ID" \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --query "instanceView.vmAgent.statuses[?code=='ProvisioningState/succeeded'].code | [0]" \
    --output tsv \
    --only-show-errors 2>/dev/null || true)" == "ProvisioningState/succeeded" ]]; then
    agent_ready=1
    break
  fi
  sleep 10
done
[[ "$agent_ready" == "1" ]] || fail "Azure VM agent did not become ready"

REMOTE_PAYLOAD="$TMP/prepare-codex-vm-payload.sh"
VM_SCRIPT_DIR="$VM_SCRIPT_DIR" \
  SSH_USERNAME="$SSH_USERNAME" \
  WORKSPACE_MOUNT_PATH="$WORKSPACE_MOUNT_PATH" \
  WORKSPACE_DISK_LUN="$WORKSPACE_DISK_LUN" \
  CODEX_VERSION="$CODEX_VERSION" \
  CODEX_PACKAGE_URL="$CODEX_PACKAGE_URL" \
  CODEX_PACKAGE_SHA256="$CODEX_PACKAGE_SHA256" \
  OPENVPN_PORT="$OPENVPN_PORT" \
  OPENVPN_NETWORK="$OPENVPN_NETWORK" \
  OPENVPN_NETMASK="$OPENVPN_NETMASK" \
  OPENVPN_SERVER_ADDRESS="$OPENVPN_SERVER_ADDRESS" \
  python3 >"$REMOTE_PAYLOAD" <<'PY'
import base64
import hashlib
import os
import pathlib
import shlex

source_dir = pathlib.Path(os.environ["VM_SCRIPT_DIR"])
files = (
    ("fetch-verified-artifact.sh", "/usr/local/sbin/fetch-verified-artifact"),
    ("install-verified-codex.sh", "/usr/local/sbin/install-verified-codex"),
    ("configure-codex-openvpn.sh", "/usr/local/sbin/configure-codex-openvpn"),
    ("prepare-persistent-codex-home.sh", "/usr/local/sbin/prepare-persistent-codex-home"),
    ("ensure-codex-remote-control.sh", "/usr/local/sbin/ensure-codex-remote-control"),
    ("prepare-codex-vm.sh", "/usr/local/sbin/prepare-codex-vm"),
)

print("""#!/usr/bin/env bash
set -euo pipefail
VM_ROOT="${CODEX_VM_ROOT:-}"
install_checked() {
  local logical_target="$1"
  local expected_sha="$2"
  local encoded="$3"
  local target="${VM_ROOT}${logical_target}"
  local temporary actual_sha
  temporary="$(mktemp)"
  printf '%s' "$encoded" | base64 --decode >"$temporary"
  actual_sha="$(sha256sum "$temporary" | awk '{print $1}')"
  [[ "$actual_sha" == "$expected_sha" ]] || {
    printf 'VM preparation payload checksum mismatch for %s\\n' "$logical_target" >&2
    exit 1
  }
  install -d -m 0755 "$(dirname "$target")"
  if [[ ! -f "$target" ]] || ! cmp -s "$temporary" "$target"; then
    if [[ "${CODEX_VM_TEST_MODE:-0}" == "1" ]]; then
      install -m 0755 "$temporary" "$target"
    else
      install -o root -g root -m 0755 "$temporary" "$target"
    fi
  fi
  cmp -s "$temporary" "$target" || {
    printf 'VM preparation payload reconciliation failed for %s\\n' "$logical_target" >&2
    exit 1
  }
  rm -f "$temporary"
}
""")

for source_name, target in files:
    content = (source_dir / source_name).read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    encoded = base64.b64encode(content).decode("ascii")
    print(f"install_checked {shlex.quote(target)} {shlex.quote(digest)} {shlex.quote(encoded)}")

arguments = (
    os.environ["SSH_USERNAME"],
    os.environ["WORKSPACE_MOUNT_PATH"],
    os.environ["WORKSPACE_DISK_LUN"],
    os.environ["CODEX_VERSION"],
    os.environ["CODEX_PACKAGE_URL"],
    os.environ["CODEX_PACKAGE_SHA256"],
    os.environ["OPENVPN_PORT"],
    os.environ["OPENVPN_NETWORK"],
    os.environ["OPENVPN_NETMASK"],
    os.environ["OPENVPN_SERVER_ADDRESS"],
)
quoted = " ".join(shlex.quote(value) for value in arguments)
print(f'exec "$VM_ROOT/usr/local/sbin/prepare-codex-vm" {quoted}')
PY
chmod 0600 "$REMOTE_PAYLOAD"

RUN_RESPONSE="$TMP/run-command.json"
if ! az vm run-command invoke \
  --subscription "$SUBSCRIPTION_ID" \
  --resource-group "$RESOURCE_GROUP" \
  --name "$VM_NAME" \
  --command-id RunShellScript \
  --scripts @"$REMOTE_PAYLOAD" \
  --output json \
  --only-show-errors >"$RUN_RESPONSE"; then
  fail "Azure Run Command preparation failed"
fi

if ! SSH_HOST_PUBLIC_KEY="$(python3 - "$RUN_RESPONSE" <<'PY'
import json
import pathlib
import re
import sys

value = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
messages = "\n".join(str(item.get("message", "")) for item in value.get("value", []))
if "CODEX_ON_VM_PREPARED=1" not in messages:
    raise SystemExit("remote preparation readiness marker is missing")
match = re.search(r"^SSH_HOST_PUBLIC_KEY=(ssh-ed25519 [A-Za-z0-9+/=]+)$", messages, re.MULTILINE)
if match is None:
    raise SystemExit("remote Ed25519 host key read-back is missing")
print(match.group(1))
PY
  )"; then
  python3 - "$RUN_RESPONSE" <<'PY' >&2
import json
import pathlib
import sys

value = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
messages = "\n".join(str(item.get("message", "")) for item in value.get("value", []))
if messages:
    print("Azure Run Command output (bounded tail):")
    print(messages[-4096:])
PY
  fail "remote preparation read-back failed"
fi

printf '%s %s\n' "$SSH_FQDN" "$SSH_HOST_PUBLIC_KEY" |
  write_private_file "$SSH_KNOWN_HOSTS_PATH"
cat <<EOF | write_private_file "$SSH_HOST_CONFIG_PATH"
Host $OPENVPN_SSH_ALIAS
  HostName $OPENVPN_SERVER_ADDRESS
  HostKeyAlias $SSH_FQDN
  User $SSH_USERNAME
  IdentityFile $MAC_PRIVATE_KEY_PATH
  IdentitiesOnly yes
  StrictHostKeyChecking yes
  UserKnownHostsFile $SSH_KNOWN_HOSTS_PATH
EOF

printf 'Machine preparation completed through Azure Run Command.\n'
printf '  VM: %s\n' "$VM_NAME"
printf '  Projects: %s\n' "$WORKSPACE_MOUNT_PATH"
printf '  SSH host config: %s\n' "$SSH_HOST_CONFIG_PATH"
printf '  Next: connect OpenVPN, then run scripts/codex-vm.sh sign-in\n'
__CODEX_VM_HELPER_END__ prepare-machine.sh

__CODEX_VM_HELPER_BEGIN__ codex-pair.sh
#!/usr/bin/env bash
set -euo pipefail

SSH_ALIAS="${CODEX_VM_VPN_SSH_ALIAS:-codex-on-vm-vpn}"
ACTION="${1:-}"

fail() {
  printf 'Codex account action failed: %s\n' "$1" >&2
  exit 1
}

trap 'exit 130' INT TERM

[[ $# -eq 1 ]] || fail "expected one action: sign-in or pair"
case "$ACTION" in
  sign-in | pair) ;;
  *) fail "unknown action '$ACTION'; expected sign-in or pair" ;;
esac
[[ "$(uname -s)" == "Darwin" ]] || fail "this helper is for macOS"
[[ -n "$SSH_ALIAS" && "$SSH_ALIAS" != -* && "$SSH_ALIAS" != *[[:space:]]* ]] ||
  fail "CODEX_VM_VPN_SSH_ALIAS is invalid"
command -v ssh >/dev/null || fail "missing required command: ssh"
ssh -o BatchMode=yes -o ConnectTimeout=5 "$SSH_ALIAS" true >/dev/null 2>&1 ||
  fail "OpenVPN is not connected; connect the Mac OpenVPN client and retry"

case "$ACTION" in
  sign-in)
    REMOTE_SIGN_IN='CODEX_BIN="$HOME/.codex/packages/standalone/current/codex"; test -x "$CODEX_BIN" || { printf "Managed Codex is missing; run scripts/codex-vm.sh setup locally first.\n" >&2; exit 1; }; "$CODEX_BIN" login status >/dev/null 2>&1 || exec "$CODEX_BIN" login --device-auth'
    ssh -t "$SSH_ALIAS" "$REMOTE_SIGN_IN"
    ;;
  pair)
    REMOTE_REQUIRE_LOGIN='CODEX_BIN="$HOME/.codex/packages/standalone/current/codex"; test -x "$CODEX_BIN" || { printf "Managed Codex is missing; run scripts/codex-vm.sh setup locally first.\n" >&2; exit 1; }; "$CODEX_BIN" login status >/dev/null 2>&1 || { printf "Codex is not logged in; run scripts/codex-vm.sh sign-in from the Mac checkout.\n" >&2; exit 1; }'
    ssh "$SSH_ALIAS" "$REMOTE_REQUIRE_LOGIN"
    REMOTE_PAIR='CODEX_BIN="$HOME/.codex/packages/standalone/current/codex"; "$CODEX_BIN" remote-control start; "$CODEX_BIN" remote-control pair'
    ssh "$SSH_ALIAS" "$REMOTE_PAIR"
    ;;
esac

case "$ACTION" in
  sign-in) printf 'Codex sign-in was launched from this Mac over OpenVPN.\n' ;;
  pair) printf 'Codex device pairing was launched from this Mac over OpenVPN.\n' ;;
esac
__CODEX_VM_HELPER_END__ codex-pair.sh

__CODEX_VM_HELPER_BEGIN__ dot-codex-bootstrap.sh
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SSH_ALIAS="${CODEX_VM_VPN_SSH_ALIAS:-codex-on-vm-vpn}"
REPOSITORY_URL="${DOT_CODEX_REPOSITORY_URL:-https://github.com/marcocello/dot-codex}"
REMOTE_DIR="${DOT_CODEX_REMOTE_DIR:-}"
REMOTE_RECOVERY_HELPER="${DOT_CODEX_REMOTE_RECOVERY_HELPER:-/usr/local/sbin/ensure-codex-remote-control}"
REMOTE_CONTROL_RETRY_SECONDS="${DOT_CODEX_REMOTE_CONTROL_RETRY_SECONDS:-2}"
STEP_NUMBER=0
CURRENT_PHASE="initialization"

fail() {
  printf 'Dot Codex bootstrap failed: %s\n' "$1" >&2
  exit 1
}

step() {
  STEP_NUMBER=$((STEP_NUMBER + 1))
  CURRENT_PHASE="$1"
  printf '\n[%d/6] %s\n' "$STEP_NUMBER" "$CURRENT_PHASE"
}

note() {
  printf '  - %s\n' "$1"
}

cleanup_on_exit() {
  local status=$?
  trap - EXIT
  if [[ "$status" != "0" ]]; then
    printf '\n[FAILED] %s\n' "$CURRENT_PHASE" >&2
  fi
  exit "$status"
}

trap cleanup_on_exit EXIT
trap 'exit 130' INT TERM

step "Validate local inputs and helper availability"
[[ "$#" == "0" ]] || fail "this command accepts no positional arguments"
[[ "$(uname -s)" == "Darwin" ]] || fail "this helper is for macOS"
[[ -n "$REPOSITORY_URL" ]] || fail "DOT_CODEX_REPOSITORY_URL must not be empty"
[[ "$REPOSITORY_URL" != *$'\n'* && "$REPOSITORY_URL" != *$'\r'* && "$REPOSITORY_URL" != *$'\t'* ]] || fail "repository URL must not contain control characters"
[[ -n "$SSH_ALIAS" && "$SSH_ALIAS" != -* ]] || fail "CODEX_VM_VPN_SSH_ALIAS is invalid"
[[ "$SSH_ALIAS" != *$'\n'* && "$SSH_ALIAS" != *$'\r'* && "$SSH_ALIAS" != *$'\t'* && "$SSH_ALIAS" != *' '* ]] || fail "SSH alias must not contain whitespace"
[[ "$REMOTE_RECOVERY_HELPER" == /* ]] || fail "DOT_CODEX_REMOTE_RECOVERY_HELPER must be an absolute remote path"
[[ "$REMOTE_RECOVERY_HELPER" != *$'\n'* && "$REMOTE_RECOVERY_HELPER" != *$'\r'* && "$REMOTE_RECOVERY_HELPER" != *$'\t'* ]] || fail "remote recovery-helper path must not contain control characters"
[[ "$REMOTE_CONTROL_RETRY_SECONDS" =~ ^[0-9]+$ ]] || fail "DOT_CODEX_REMOTE_CONTROL_RETRY_SECONDS must be an integer"
((REMOTE_CONTROL_RETRY_SECONDS <= 30)) || fail "DOT_CODEX_REMOTE_CONTROL_RETRY_SECONDS must be between 0 and 30"
if [[ -n "$REMOTE_DIR" ]]; then
  [[ "$REMOTE_DIR" == /* ]] || fail "DOT_CODEX_REMOTE_DIR must be an absolute remote path"
  [[ "$REMOTE_DIR" != *$'\n'* && "$REMOTE_DIR" != *$'\r'* && "$REMOTE_DIR" != *$'\t'* ]] || fail "remote path must not contain control characters"
fi

command -v ssh >/dev/null || fail "missing required command: ssh"
[[ -x "$ROOT/scripts/remote-control-recover.sh" ]] || fail "missing Remote Control recovery helper"
note "Repository: $REPOSITORY_URL"
note "VM SSH alias: $SSH_ALIAS"
note "Remote clone: ${REMOTE_DIR:-\$HOME/projects/dot-codex}"
note "Local validation passed."

step "Verify OpenVPN SSH access"
ssh -o BatchMode=yes -o ConnectTimeout=5 "$SSH_ALIAS" true >/dev/null 2>&1 ||
  fail "OpenVPN is not connected; connect the Mac OpenVPN client and retry"
note "The VM is reachable through OpenVPN."

step "Reconcile and repair current Remote Control"
note "Checking Codex login before any daemon recovery."
printf -v REMOTE_PREFLIGHT_COMMAND 'bash -s -- %q' "packages/standalone/current/codex"
ssh "$SSH_ALIAS" "$REMOTE_PREFLIGHT_COMMAND" <<'REMOTE_PREFLIGHT'
set -euo pipefail
MANAGED_RELATIVE_PATH="$1"
CODEX_BIN="$HOME/.codex/$MANAGED_RELATIVE_PATH"
[[ -x "$CODEX_BIN" ]] || {
  printf 'Remote bootstrap preflight failed: managed Codex is missing at %s\n' "$CODEX_BIN" >&2
  exit 1
}
"$CODEX_BIN" login status >/dev/null 2>&1 || {
  printf 'Remote bootstrap preflight failed: Codex is not logged in; run scripts/codex-vm.sh sign-in from the Mac checkout\n' >&2
  exit 1
}
printf '  [remote] Codex login is ready.\n'
REMOTE_PREFLIGHT
note "Using Azure Run Command to install the checked-in recovery helper when needed."
if "$ROOT/scripts/remote-control-recover.sh"; then
  note "Pre-migration Remote Control recovery completed."
else
  note "Pre-migration recovery did not complete; the SSH phase will diagnose login and retry safely."
fi

step "Bootstrap or repair dot-codex on the VM"
printf -v REMOTE_COMMAND \
  'bash -s -- %q %q %q %q' \
  "$REPOSITORY_URL" \
  "$REMOTE_DIR" \
  "$REMOTE_RECOVERY_HELPER" \
  "$REMOTE_CONTROL_RETRY_SECONDS"
ssh "$SSH_ALIAS" "$REMOTE_COMMAND" <<'REMOTE_SCRIPT'
set -euo pipefail

REPOSITORY_URL="$1"
REMOTE_DIR_OVERRIDE="$2"
RECOVERY_HELPER="$3"
RETRY_SECONDS="$4"
DOT_CODEX_DIR="${REMOTE_DIR_OVERRIDE:-$HOME/projects/dot-codex}"
CODEX_LINK="$HOME/.codex"
MANAGED_RELATIVE_PATH="packages/standalone/current/codex"
BACKUP_PATH=""
MOVED_OLD_CODEX=0
CREATED_LINK=0
DAEMON_STOPPED=0

fail() {
  printf 'Remote Dot Codex bootstrap failed: %s\n' "$1" >&2
  exit 1
}

remote_note() {
  printf '  [remote] %s\n' "$1"
}

remote_control_connected_once() {
  local attempt="$1"
  local bin output status timed_out environment_id
  bin="$CODEX_LINK/$MANAGED_RELATIVE_PATH"
  if ! output="$("$bin" remote-control start --json 2>&1)"; then
    remote_note "Remote Control check $attempt: start command failed."
    return 1
  fi
  status="$(jq -r '.status // "unknown"' <<<"$output" 2>/dev/null || printf 'invalid-json')"
  timed_out="$(jq -r 'if has("timedOut") then (.timedOut | tostring) else "unknown" end' <<<"$output" 2>/dev/null || printf 'invalid-json')"
  environment_id="$(jq -r '.environmentId // ""' <<<"$output" 2>/dev/null || true)"
  remote_note "Remote Control check $attempt: status=$status timedOut=$timed_out."
  jq -e '
    .status == "connected" and
    .timedOut == false and
    (.environmentId | type == "string" and length > 0) and
    (.daemon.status | type == "string" and length > 0)
  ' <<<"$output" >/dev/null 2>&1 && [[ -n "$environment_id" ]]
}

wait_for_remote_control() {
  local phase="$1"
  local attempt
  for attempt in 1 2 3; do
    if remote_control_connected_once "$phase.$attempt"; then
      return 0
    fi
    if [[ "$attempt" != "3" && "$RETRY_SECONDS" != "0" ]]; then
      remote_note "Waiting ${RETRY_SECONDS}s before the next connection check."
      sleep "$RETRY_SECONDS"
    fi
  done
  return 1
}

repair_remote_control() {
  local context="$1"
  local bin
  bin="$CODEX_LINK/$MANAGED_RELATIVE_PATH"
  [[ -x "$bin" ]] || {
    remote_note "Managed Codex executable is missing at $bin."
    return 1
  }
  "$bin" login status >/dev/null 2>&1 || {
    remote_note "Codex login is missing; run scripts/codex-vm.sh sign-in from the Mac checkout"
    return 1
  }
  remote_note "Checking Remote Control for $context."
  if wait_for_remote_control "start"; then
    remote_note "Remote Control is connected."
    return 0
  fi
  remote_note "Supported start did not connect; invoking $RECOVERY_HELPER."
  if ! "$RECOVERY_HELPER"; then
    remote_note "The VM recovery helper returned failure; checking connection once more."
  fi
  if wait_for_remote_control "repair"; then
    remote_note "Remote Control recovered and is connected."
    return 0
  fi
  remote_note "Remote Control is not connected after bounded repair attempts."
  return 1
}

rollback_on_exit() {
  local status=$?
  trap - EXIT
  set +e
  if [[ "$status" != "0" && "$MOVED_OLD_CODEX" == "1" ]]; then
    remote_note "Rolling back the Codex-home migration."
    if [[ "$CREATED_LINK" == "1" && -L "$CODEX_LINK" ]]; then
      rm -- "$CODEX_LINK"
    fi
    if [[ ! -e "$CODEX_LINK" && ! -L "$CODEX_LINK" && ( -e "$BACKUP_PATH" || -L "$BACKUP_PATH" ) ]]; then
      mv -- "$BACKUP_PATH" "$CODEX_LINK"
    fi
  fi
  if [[ "$status" != "0" && "$DAEMON_STOPPED" == "1" && -x "$CODEX_LINK/$MANAGED_RELATIVE_PATH" ]]; then
    remote_note "Attempting Remote Control recovery on the restored Codex home."
    repair_remote_control "the restored Codex home" ||
      printf 'Remote Dot Codex bootstrap rollback warning: the prior Remote Control connection did not recover\n' >&2
  fi
  exit "$status"
}

next_backup_path() {
  local base candidate suffix
  base="$HOME/.codex.backup.$(date +%Y%m%d-%H%M%S)"
  candidate="$base"
  suffix=0
  while [[ -e "$candidate" || -L "$candidate" ]]; do
    suffix=$((suffix + 1))
    candidate="$base.$suffix"
  done
  printf '%s\n' "$candidate"
}

trap rollback_on_exit EXIT
trap 'exit 130' INT TERM

for command in git jq readlink sleep tar; do
  command -v "$command" >/dev/null || fail "missing required command: $command"
done
[[ "$DOT_CODEX_DIR" == /* ]] || fail "remote clone path must be absolute"
[[ "$DOT_CODEX_DIR" != "$CODEX_LINK" ]] || fail "remote clone path must differ from ~/.codex"
[[ "$RECOVERY_HELPER" == /* && -x "$RECOVERY_HELPER" ]] || fail "VM recovery helper is unavailable or not executable at $RECOVERY_HELPER"
[[ "$RETRY_SECONDS" =~ ^[0-9]+$ ]] || fail "remote retry delay must be an integer"
((RETRY_SECONDS <= 30)) || fail "remote retry delay must be between 0 and 30"

if [[ -e "$DOT_CODEX_DIR" || -L "$DOT_CODEX_DIR" ]]; then
  remote_note "Inspecting existing clone at $DOT_CODEX_DIR."
  [[ -d "$DOT_CODEX_DIR" && ! -L "$DOT_CODEX_DIR" ]] || fail "clone target exists but is not a real directory: $DOT_CODEX_DIR"
  [[ "$(git -C "$DOT_CODEX_DIR" rev-parse --is-inside-work-tree 2>/dev/null)" == "true" ]] ||
    fail "clone target is not a Git worktree: $DOT_CODEX_DIR"
  CLONE_ROOT="$(git -C "$DOT_CODEX_DIR" rev-parse --show-toplevel)"
  [[ "$(readlink -f "$CLONE_ROOT")" == "$(readlink -f "$DOT_CODEX_DIR")" ]] ||
    fail "clone target is nested inside a different Git worktree: $DOT_CODEX_DIR"
  ACTUAL_ORIGIN="$(git -C "$DOT_CODEX_DIR" remote get-url origin 2>/dev/null)" ||
    fail "clone target has no origin remote"
  [[ "$ACTUAL_ORIGIN" == "$REPOSITORY_URL" ]] ||
    fail "clone origin is $ACTUAL_ORIGIN, expected $REPOSITORY_URL"
  [[ -z "$(git -C "$DOT_CODEX_DIR" status --porcelain --untracked-files=normal)" ]] ||
    fail "clone has local worktree or index changes: $DOT_CODEX_DIR"
  CURRENT_BRANCH="$(git -C "$DOT_CODEX_DIR" symbolic-ref --quiet --short HEAD)" ||
    fail "clone is detached"
  UPSTREAM="$(git -C "$DOT_CODEX_DIR" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null)" ||
    fail "branch $CURRENT_BRANCH has no upstream"
  [[ "$UPSTREAM" == origin/* ]] || fail "branch $CURRENT_BRANCH does not track origin"
  ORIGINAL_HEAD="$(git -C "$DOT_CODEX_DIR" rev-parse HEAD)"
  remote_note "Fetching origin before the default rebase."
  git -C "$DOT_CODEX_DIR" fetch --prune origin
  FORK_POINT="$(git -C "$DOT_CODEX_DIR" merge-base --fork-point "$UPSTREAM" "$ORIGINAL_HEAD" 2>/dev/null)" ||
    fail "could not determine a reflog-aware fork point for $CURRENT_BRANCH and $UPSTREAM"
  git -C "$DOT_CODEX_DIR" merge-base --is-ancestor "$FORK_POINT" "$ORIGINAL_HEAD" ||
    fail "reflog-aware fork point is not an ancestor of the original branch"
  remote_note "Rebasing VM-only commits after the reflog-aware fork point onto $UPSTREAM."
  if ! git -C "$DOT_CODEX_DIR" rebase --onto "$UPSTREAM" "$FORK_POINT" "$CURRENT_BRANCH"; then
    ABSOLUTE_GIT_DIR="$(git -C "$DOT_CODEX_DIR" rev-parse --absolute-git-dir)"
    if [[ -d "$ABSOLUTE_GIT_DIR/rebase-merge" || -d "$ABSOLUTE_GIT_DIR/rebase-apply" ]]; then
      remote_note "Rebase did not apply cleanly; aborting it."
      git -C "$DOT_CODEX_DIR" rebase --abort ||
        fail "rebase failed and automatic abort could not restore the original branch"
    fi
    [[ "$(git -C "$DOT_CODEX_DIR" symbolic-ref --quiet --short HEAD 2>/dev/null)" == "$CURRENT_BRANCH" ]] ||
      fail "rebase failed and did not restore branch $CURRENT_BRANCH"
    [[ "$(git -C "$DOT_CODEX_DIR" rev-parse HEAD)" == "$ORIGINAL_HEAD" ]] ||
      fail "rebase failed and did not restore the original branch commit"
    [[ -z "$(git -C "$DOT_CODEX_DIR" status --porcelain --untracked-files=normal)" ]] ||
      fail "rebase failed and did not restore a clean worktree"
    fail "rebase conflicted; original branch restored"
  fi
  git -C "$DOT_CODEX_DIR" merge-base --is-ancestor "$UPSTREAM" HEAD ||
    fail "rebase completed without placing $UPSTREAM behind the local branch"
else
  remote_note "Clone is missing; cloning $REPOSITORY_URL."
  git clone -- "$REPOSITORY_URL" "$DOT_CODEX_DIR"
fi

if [[ -L "$CODEX_LINK" ]] &&
  [[ "$(readlink -f "$CODEX_LINK")" == "$(readlink -f "$DOT_CODEX_DIR")" ]]; then
  remote_note "Symlink already correct; no backup or migration needed."
  repair_remote_control "the existing dot-codex home" ||
    fail "Remote Control is not connected after bounded repair attempts"
  printf 'Remote Dot Codex clone and symlink are ready at %s.\n' "$DOT_CODEX_DIR"
  ls -ld "$CODEX_LINK"
  exit 0
fi

if [[ -x "$CODEX_LINK/$MANAGED_RELATIVE_PATH" ]]; then
  remote_note "Checking Codex login before changing the active home."
  "$CODEX_LINK/$MANAGED_RELATIVE_PATH" login status >/dev/null 2>&1 ||
    fail "Codex is not logged in; run scripts/codex-vm.sh sign-in from the Mac checkout"
  remote_note "Stopping the managed daemon before migration."
  "$CODEX_LINK/$MANAGED_RELATIVE_PATH" app-server daemon stop
  DAEMON_STOPPED=1
fi

if [[ -e "$CODEX_LINK" || -L "$CODEX_LINK" ]]; then
  BACKUP_PATH="$(next_backup_path)"
  remote_note "Moving the previous Codex home to $BACKUP_PATH."
  mv -- "$CODEX_LINK" "$BACKUP_PATH"
  MOVED_OLD_CODEX=1
  if [[ -d "$BACKUP_PATH" ]]; then
    remote_note "Migrating VM-local ignored state while preserving Git-owned files."
    (
      cd "$BACKUP_PATH"
      tar --exclude='.git' -cf - .
    ) | (
      cd "$DOT_CODEX_DIR"
      tar -xf -
    )
    git -C "$DOT_CODEX_DIR" restore --source=HEAD --staged --worktree -- .
  fi
fi

remote_note "Creating ~/.codex -> $DOT_CODEX_DIR."
ln -s -- "$DOT_CODEX_DIR" "$CODEX_LINK"
CREATED_LINK=1
[[ -L "$CODEX_LINK" ]] || fail "~/.codex was not created as a symlink"
[[ "$(readlink -f "$CODEX_LINK")" == "$(readlink -f "$DOT_CODEX_DIR")" ]] ||
  fail "~/.codex does not resolve to $DOT_CODEX_DIR"

repair_remote_control "the migrated dot-codex home" ||
  fail "Remote Control is not connected after bounded repair attempts"

printf 'Remote Dot Codex clone is ready at %s.\n' "$DOT_CODEX_DIR"
if [[ -n "$BACKUP_PATH" ]]; then
  printf 'Previous ~/.codex preserved at %s.\n' "$BACKUP_PATH"
fi
ls -ld "$CODEX_LINK"
REMOTE_SCRIPT

step "Verify Remote Control"
"$ROOT/scripts/remote-control-recover.sh" ||
  fail "final Remote Control verification failed; run scripts/codex-vm.sh setup after checking VM login and network access"
printf 'Remote Control verified connected.\n'

step "Complete"
printf 'Dot Codex bootstrap and repair completed successfully.\n'
printf '  Clone: %s\n' "${REMOTE_DIR:-\$HOME/projects/dot-codex}"
printf '  Symlink: \$HOME/.codex -> %s\n' "${REMOTE_DIR:-\$HOME/projects/dot-codex}"
printf '  SSH: VPN-only\n'
printf '  Remote Control: connected\n'
__CODEX_VM_HELPER_END__ dot-codex-bootstrap.sh

__CODEX_VM_HELPER_BEGIN__ telegram-to-agents-bootstrap.sh
#!/usr/bin/env bash
set -euo pipefail

SSH_ALIAS="${CODEX_VM_VPN_SSH_ALIAS:-codex-on-vm-vpn}"
REPOSITORY_URL="${TELEGRAM_TO_AGENTS_REPOSITORY_URL:-https://github.com/marcocello/dot-codex}"
REMOTE_DIR="${TELEGRAM_TO_AGENTS_REMOTE_DIR:-}"

fail() {
  printf 'telegram-to-agents installation failed: %s\n' "$1" >&2
  exit 1
}

note() {
  printf '  - %s\n' "$1"
}

[[ $# -eq 0 ]] || fail "this command accepts no positional arguments"
[[ "$(uname -s)" == "Darwin" ]] || fail "this helper is for macOS"
[[ -n "$REPOSITORY_URL" ]] || fail "TELEGRAM_TO_AGENTS_REPOSITORY_URL must not be empty"
[[ "$REPOSITORY_URL" != *$'\n'* && "$REPOSITORY_URL" != *$'\r'* && "$REPOSITORY_URL" != *$'\t'* ]] ||
  fail "repository URL must not contain control characters"
[[ -n "$SSH_ALIAS" && "$SSH_ALIAS" != -* ]] || fail "CODEX_VM_VPN_SSH_ALIAS is invalid"
[[ "$SSH_ALIAS" != *$'\n'* && "$SSH_ALIAS" != *$'\r'* && "$SSH_ALIAS" != *$'\t'* && "$SSH_ALIAS" != *' '* ]] ||
  fail "SSH alias must not contain whitespace"
if [[ -n "$REMOTE_DIR" ]]; then
  [[ "$REMOTE_DIR" == /* ]] || fail "TELEGRAM_TO_AGENTS_REMOTE_DIR must be an absolute remote path"
  [[ "$REMOTE_DIR" != *$'\n'* && "$REMOTE_DIR" != *$'\r'* && "$REMOTE_DIR" != *$'\t'* ]] ||
    fail "remote path must not contain control characters"
fi
command -v ssh >/dev/null || fail "missing required command: ssh"

note "Repository: $REPOSITORY_URL"
note "VM SSH alias: $SSH_ALIAS"
note "Remote clone: ${REMOTE_DIR:-\$HOME/projects/dot-codex}"

ssh -o BatchMode=yes -o ConnectTimeout=5 "$SSH_ALIAS" true >/dev/null 2>&1 ||
  fail "OpenVPN is not connected; connect the Mac OpenVPN client and retry"

printf -v REMOTE_COMMAND 'bash -s -- %q %q' "$REPOSITORY_URL" "$REMOTE_DIR"
REMOTE_OUTPUT=""
REMOTE_STATUS=0
REMOTE_OUTPUT="$(ssh "$SSH_ALIAS" "$REMOTE_COMMAND" <<'REMOTE_SCRIPT'
set -euo pipefail

REPOSITORY_URL="$1"
REMOTE_DIR_OVERRIDE="$2"
CHECKOUT="${REMOTE_DIR_OVERRIDE:-$HOME/projects/dot-codex}"
PACKAGE="$CHECKOUT/backend/telegram"
VENV="$CHECKOUT/.venv"
CLI="$VENV/bin/telegram-to-agents"
CLI_LINK="$HOME/.local/bin/telegram-to-agents"
CONFIG="$HOME/.telegram-to-agents/config/config.json"
SERVICE="telegram-to-agents.service"

fail() {
  printf 'Remote telegram-to-agents installation failed: %s\n' "$1" >&2
  exit 1
}

remote_note() {
  printf '  [remote] %s\n' "$1"
}

for command in git python3 readlink systemctl; do
  command -v "$command" >/dev/null || fail "missing required command: $command"
done
[[ "$CHECKOUT" == /* ]] || fail "remote clone path must be absolute"

if [[ -e "$CHECKOUT" || -L "$CHECKOUT" ]]; then
  remote_note "Inspecting existing checkout at $CHECKOUT."
  [[ -d "$CHECKOUT" && ! -L "$CHECKOUT" ]] ||
    fail "clone target exists but is not a real directory: $CHECKOUT"
  [[ "$(git -C "$CHECKOUT" rev-parse --is-inside-work-tree 2>/dev/null)" == "true" ]] ||
    fail "clone target is not a Git worktree: $CHECKOUT"
  CLONE_ROOT="$(git -C "$CHECKOUT" rev-parse --show-toplevel)"
  [[ "$(readlink -f "$CLONE_ROOT")" == "$(readlink -f "$CHECKOUT")" ]] ||
    fail "clone target is nested inside a different Git worktree: $CHECKOUT"
  ACTUAL_ORIGIN="$(git -C "$CHECKOUT" remote get-url origin 2>/dev/null)" ||
    fail "clone target has no origin remote"
  [[ "$ACTUAL_ORIGIN" == "$REPOSITORY_URL" ]] ||
    fail "clone origin is $ACTUAL_ORIGIN, expected $REPOSITORY_URL"
  [[ -z "$(git -C "$CHECKOUT" status --porcelain --untracked-files=normal)" ]] ||
    fail "clone has local worktree or index changes: $CHECKOUT"
  CURRENT_BRANCH="$(git -C "$CHECKOUT" symbolic-ref --quiet --short HEAD)" ||
    fail "clone is detached"
  UPSTREAM="$(git -C "$CHECKOUT" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null)" ||
    fail "branch $CURRENT_BRANCH has no upstream"
  [[ "$UPSTREAM" == origin/* ]] || fail "branch $CURRENT_BRANCH does not track origin"
  remote_note "Fetching and fast-forwarding $CURRENT_BRANCH from $UPSTREAM."
  git -C "$CHECKOUT" fetch --prune origin
  git -C "$CHECKOUT" merge-base --is-ancestor HEAD "$UPSTREAM" ||
    fail "branch $CURRENT_BRANCH contains local commits or has diverged from $UPSTREAM"
  git -C "$CHECKOUT" merge --ff-only "$UPSTREAM" ||
    fail "branch $CURRENT_BRANCH has diverged from $UPSTREAM; resolve it manually"
else
  remote_note "Cloning $REPOSITORY_URL into $CHECKOUT."
  mkdir -p "$(dirname "$CHECKOUT")"
  git clone -- "$REPOSITORY_URL" "$CHECKOUT"
fi

remote_note "Creating or refreshing the checkout virtual environment."
python3 -m venv "$VENV"
[[ -f "$PACKAGE/pyproject.toml" ]] || fail "bundled Telegram package is missing; update dot-codex first"
"$VENV/bin/python" -m pip install --upgrade "$PACKAGE"
[[ -x "$CLI" ]] || fail "installed CLI is missing at $CLI"

mkdir -p "$(dirname "$CLI_LINK")"
if [[ -e "$CLI_LINK" || -L "$CLI_LINK" ]]; then
  [[ -L "$CLI_LINK" && "$(readlink -f "$CLI_LINK")" == "$(readlink -f "$CLI")" ]] ||
    fail "CLI path exists and does not point to this checkout: $CLI_LINK"
else
  ln -s -- "$CLI" "$CLI_LINK"
fi

if [[ ! -f "$CONFIG" ]]; then
  remote_note "Current configuration is missing; interactive onboarding is required."
  printf 'TELEGRAM_TO_AGENTS_ONBOARDING_REQUIRED=1\n'
  exit 0
fi

if systemctl --user cat "$SERVICE" >/dev/null 2>&1; then
  remote_note "Restarting the existing telegram-to-agents service."
  "$CLI" restart
  systemctl --user is-active "$SERVICE" >/dev/null 2>&1 ||
    fail "$SERVICE is not active after restart"
  remote_note "$SERVICE is active."
else
  remote_note "Package updated; no installed telegram-to-agents user service was found."
fi

printf 'Remote telegram-to-agents installation is ready at %s.\n' "$CHECKOUT"
REMOTE_SCRIPT
)" || REMOTE_STATUS=$?
printf '%s\n' "$REMOTE_OUTPUT"
[[ "$REMOTE_STATUS" == "0" ]] || exit "$REMOTE_STATUS"

if grep -Fx 'TELEGRAM_TO_AGENTS_ONBOARDING_REQUIRED=1' <<<"$REMOTE_OUTPUT" >/dev/null; then
  note "Starting interactive telegram-to-agents onboarding on the VM."
  ssh -t "$SSH_ALIAS" '$HOME/.local/bin/telegram-to-agents onboarding' ||
    fail "interactive onboarding did not complete"
fi

printf 'telegram-to-agents installation/update completed successfully.\n'
printf '  Clone: %s\n' "${REMOTE_DIR:-\$HOME/projects/dot-codex}"
printf '  CLI: \$HOME/.local/bin/telegram-to-agents\n'
printf '  SSH: VPN-only\n'
__CODEX_VM_HELPER_END__ telegram-to-agents-bootstrap.sh

__CODEX_VM_HELPER_BEGIN__ openvpn-setup.sh
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="$ROOT/deployments/prod/tf"
VM_CONFIGURATOR="$ROOT/vm-scripts/configure-codex-openvpn.sh"
ROTATE=0
BOOTSTRAP=0
LOCAL_PROMOTED=0
LOCAL_WAS_PRESENT=0
REMOTE_COMMITTED=0
REMOTE_STAGE=""
LOCAL_BACKUP=""
OLD_CA_FINGERPRINT=""
NEW_CA_FINGERPRINT=""
TMP="$(mktemp -d "${TMPDIR:-/tmp}/codex-openvpn.XXXXXX")"

fail() {
  printf 'OpenVPN setup failed: %s\n' "$1" >&2
  exit 1
}

cleanup() {
  local status=$?
  local inspect_command remote_ca_fingerprint restore_local=0
  trap - EXIT
  set +e
  if [[ "$status" != "0" && "$LOCAL_PROMOTED" == "1" && "$REMOTE_COMMITTED" != "1" ]]; then
    remote_ca_fingerprint=""
    printf -v inspect_command 'remote_ca=%q; if [[ -n "${CODEX_VM_ROOT:-}" ]]; then remote_ca="${CODEX_VM_ROOT}${remote_ca}"; fi; if sudo test -f "$remote_ca"; then sudo openssl x509 -in "$remote_ca" -noout -fingerprint -sha256; else printf "MISSING\\n"; fi' \
      "$WORKSPACE_MOUNT/.codex-on-vm/openvpn/server/ca.crt"
    remote_ca_fingerprint="$(ssh "$VPN_SSH_ALIAS" "$inspect_command" 2>/dev/null || true)"
    if [[ -n "$NEW_CA_FINGERPRINT" && "$remote_ca_fingerprint" == "$NEW_CA_FINGERPRINT" ]]; then
      REMOTE_COMMITTED=1
      printf 'OpenVPN setup recovery: the replacement is active remotely; keeping the matching local credentials.\n' >&2
    elif [[ -n "$OLD_CA_FINGERPRINT" && "$remote_ca_fingerprint" == "$OLD_CA_FINGERPRINT" ]]; then
      restore_local=1
    elif [[ -z "$OLD_CA_FINGERPRINT" && "$remote_ca_fingerprint" == "MISSING" ]]; then
      restore_local=1
    else
      printf 'OpenVPN setup recovery warning: remote trust could not be identified; keeping the new local credentials and any prior backup for a safe retry.\n' >&2
    fi
  fi
  if [[ -n "$REMOTE_STAGE" ]]; then
    printf -v cleanup_command 'rm -rf -- %q' "$REMOTE_STAGE"
    ssh "$VPN_SSH_ALIAS" "$cleanup_command" >/dev/null 2>&1 || true
  fi
  if [[ "$restore_local" == "1" ]]; then
    rm -rf -- "$LOCAL_ROOT"
    if [[ "$LOCAL_WAS_PRESENT" == "1" && -n "$LOCAL_BACKUP" && -d "$LOCAL_BACKUP" ]]; then
      mv "$LOCAL_BACKUP" "$LOCAL_ROOT" || true
      LOCAL_BACKUP=""
    fi
  fi
  rm -rf -- "$TMP"
  exit "$status"
}

trap cleanup EXIT
trap 'exit 130' INT TERM

[[ $# -le 1 ]] || fail "expected only the optional --rotate flag"
if [[ $# -eq 1 ]]; then
  case "$1" in
    --rotate) ROTATE=1 ;;
    --bootstrap) BOOTSTRAP=1 ;;
    *) fail "unknown option '$1'; expected --rotate or --bootstrap" ;;
  esac
fi
[[ "$(uname -s)" == "Darwin" ]] || fail "this helper is for macOS"
for command in cmp install openssl python3 scp ssh tar terraform; do
  command -v "$command" >/dev/null || fail "missing required command: $command"
done
[[ -r "$VM_CONFIGURATOR" ]] || fail "OpenVPN VM configurator is unavailable"

CONNECTION="$(terraform -chdir="$TF_DIR" output -json connection)"
IFS=$'\t' read -r \
  SSH_FQDN SSH_USERNAME WORKSPACE_MOUNT \
  MAC_PRIVATE_KEY SSH_CONFIG KNOWN_HOSTS \
  VPN_PORT VPN_NETWORK VPN_NETMASK VPN_SERVER_ADDRESS VPN_SSH_ALIAS \
  LOCAL_ROOT CLIENT_PROFILE <<<"$(CONNECTION="$CONNECTION" python3 - <<'PY'
import json
import os
import re

value = json.loads(os.environ["CONNECTION"])
keys = (
    "ssh_fqdn",
    "ssh_username",
    "workspace_mount_path",
    "mac_private_key_path",
    "ssh_host_config_path",
    "ssh_known_hosts_path",
    "openvpn_port",
    "openvpn_network",
    "openvpn_netmask",
    "openvpn_server_address",
    "openvpn_ssh_alias",
    "openvpn_local_root_path",
    "openvpn_client_profile_path",
)
patterns = (
    r"[A-Za-z0-9.-]{1,253}",
    r"[a-z_][a-z0-9_-]{0,31}",
    r"/[^\t\r\n]+",
    r"/[^\t\r\n]+",
    r"/[^\t\r\n]+",
    r"/[^\t\r\n]+",
    r"[0-9]{1,5}",
    r"[0-9.]{7,15}",
    r"[0-9.]{7,15}",
    r"[0-9.]{7,15}",
    r"[A-Za-z0-9._-]{1,64}",
    r"/[^\t\r\n]+",
    r"/[^\t\r\n]+",
)
fields = [str(value[key]) for key in keys]
for key, field, pattern in zip(keys, fields, patterns):
    if re.fullmatch(pattern, field) is None:
        raise SystemExit(f"Terraform connection output contains an unsafe {key}")
if not fields[-1].startswith(fields[-2] + "/"):
    raise SystemExit("OpenVPN client profile must be inside the local OpenVPN root")
print("\t".join(fields))
PY
)"

[[ "$VPN_PORT" -ge 1 && "$VPN_PORT" -le 65535 ]] || fail "OpenVPN port is invalid"
[[ -f "$KNOWN_HOSTS" ]] || fail "SSH host trust is missing; run scripts/codex-vm.sh setup"
[[ -f "$MAC_PRIVATE_KEY" ]] || fail "Mac SSH private key is missing; run scripts/codex-vm.sh setup"
if [[ "$BOOTSTRAP" != "1" ]]; then
  ssh -o BatchMode=yes -o ConnectTimeout=5 "$VPN_SSH_ALIAS" true >/dev/null 2>&1 ||
    fail "OpenVPN is not connected; connect the Mac OpenVPN client and retry"
fi

required_files="ca.crt ca.key server.crt server.key client.crt client.key tls-crypt.key server.conf codex-on-vm.ovpn"
local_complete=1
if [[ -d "$LOCAL_ROOT" ]]; then
  LOCAL_WAS_PRESENT=1
  for required in $required_files; do
    if [[ ! -f "$LOCAL_ROOT/$required" ]]; then
      local_complete=0
    fi
  done
  [[ "$local_complete" == "1" ]] || fail "local OpenVPN state is partial; restore or remove it explicitly before retrying"
  OLD_CA_FINGERPRINT="$(openssl x509 -in "$LOCAL_ROOT/ca.crt" -noout -fingerprint -sha256)" ||
    fail "local OpenVPN CA certificate is invalid"
elif [[ -e "$LOCAL_ROOT" || -L "$LOCAL_ROOT" ]]; then
  fail "local OpenVPN root is not a directory: $LOCAL_ROOT"
else
  local_complete=0
fi

if [[ "$local_complete" != "1" && "$ROTATE" != "1" && "$BOOTSTRAP" != "1" ]]; then
  fail "existing OpenVPN trust is missing at $LOCAL_ROOT; restore it or run scripts/codex-vm.sh vpn-setup --rotate to intentionally create replacement trust"
fi

validate_local_credentials() {
  local target="$1"
  local name key_pub cert_pub
  openssl verify -purpose sslserver -CAfile "$target/ca.crt" "$target/server.crt" >/dev/null ||
    fail "server certificate verification failed"
  openssl verify -purpose sslclient -CAfile "$target/ca.crt" "$target/client.crt" >/dev/null ||
    fail "client certificate verification failed"
  for name in ca server client; do
    key_pub="$TMP/$name-key.pub"
    cert_pub="$TMP/$name-cert.pub"
    openssl pkey -in "$target/$name.key" -pubout -out "$key_pub" >/dev/null 2>&1 ||
      fail "$name private key is invalid"
    openssl x509 -in "$target/$name.crt" -pubkey -noout >"$cert_pub" ||
      fail "$name certificate is invalid"
    cmp -s "$key_pub" "$cert_pub" || fail "$name certificate does not match its private key"
  done
  python3 - "$target" <<'PY'
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
profile = (root / "codex-on-vm.ovpn").read_text(encoding="utf-8")
for tag, name in (("ca", "ca.crt"), ("cert", "client.crt"), ("key", "client.key"), ("tls-crypt", "tls-crypt.key")):
    match = re.search(rf"<{re.escape(tag)}>\n(.*?)</{re.escape(tag)}>", profile, re.DOTALL)
    if match is None or match.group(1).strip() != (root / name).read_text(encoding="utf-8").strip():
        raise SystemExit(f"client profile has mismatched inline {tag} material")
PY
}

generate_credentials() {
  local target="$1"
  install -d -m 0700 "$target"
  openssl genrsa -out "$target/ca.key" 3072 >/dev/null 2>&1
  openssl req -x509 -new -sha256 -days 3650 \
    -key "$target/ca.key" \
    -out "$target/ca.crt" \
    -subj '/CN=codex-on-vm-openvpn-ca' >/dev/null 2>&1

  openssl genrsa -out "$target/server.key" 3072 >/dev/null 2>&1
  openssl req -new -sha256 \
    -key "$target/server.key" \
    -out "$TMP/server.csr" \
    -subj '/CN=codex-on-vm-server' >/dev/null 2>&1
  cat >"$TMP/server.ext" <<EOF
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:$SSH_FQDN
EOF
  openssl x509 -req -sha256 -days 825 \
    -in "$TMP/server.csr" \
    -CA "$target/ca.crt" \
    -CAkey "$target/ca.key" \
    -set_serial 1001 \
    -extfile "$TMP/server.ext" \
    -out "$target/server.crt" >/dev/null 2>&1

  openssl genrsa -out "$target/client.key" 3072 >/dev/null 2>&1
  openssl req -new -sha256 \
    -key "$target/client.key" \
    -out "$TMP/client.csr" \
    -subj '/CN=codex-on-vm-mac' >/dev/null 2>&1
  cat >"$TMP/client.ext" <<'EOF'
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=clientAuth
EOF
  openssl x509 -req -sha256 -days 825 \
    -in "$TMP/client.csr" \
    -CA "$target/ca.crt" \
    -CAkey "$target/ca.key" \
    -set_serial 1002 \
    -extfile "$TMP/client.ext" \
    -out "$target/client.crt" >/dev/null 2>&1

  python3 >"$target/tls-crypt.key" <<'PY'
import secrets

value = secrets.token_hex(256)
print("-----BEGIN OpenVPN Static key V1-----")
for index in range(0, len(value), 32):
    print(value[index:index + 32])
print("-----END OpenVPN Static key V1-----")
PY

  cat >"$target/server.conf" <<EOF
port $VPN_PORT
proto udp
dev tun
topology subnet
server $VPN_NETWORK $VPN_NETMASK
ca /etc/openvpn/server/ca.crt
cert /etc/openvpn/server/server.crt
key /etc/openvpn/server/server.key
dh none
ecdh-curve prime256v1
tls-crypt /etc/openvpn/server/tls-crypt.key
tls-version-min 1.2
remote-cert-tls client
verify-client-cert require
data-ciphers AES-256-GCM:CHACHA20-POLY1305:AES-128-GCM
data-ciphers-fallback AES-256-GCM
auth SHA256
keepalive 10 120
explicit-exit-notify 1
persist-key
persist-tun
user nobody
group nogroup
verb 3
EOF

  {
    cat <<EOF
client
dev tun
proto udp
remote $SSH_FQDN $VPN_PORT
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
verify-x509-name codex-on-vm-server name
tls-version-min 1.2
data-ciphers AES-256-GCM:CHACHA20-POLY1305:AES-128-GCM
data-ciphers-fallback AES-256-GCM
auth SHA256
auth-nocache
verb 3
<ca>
EOF
    cat "$target/ca.crt"
    printf '</ca>\n<cert>\n'
    cat "$target/client.crt"
    printf '</cert>\n<key>\n'
    cat "$target/client.key"
    printf '</key>\n<tls-crypt>\n'
    cat "$target/tls-crypt.key"
    printf '</tls-crypt>\n'
  } >"$target/codex-on-vm.ovpn"
  chmod 0600 "$target"/*

}

SOURCE_ROOT="$LOCAL_ROOT"
if [[ "$local_complete" != "1" || "$ROTATE" == "1" ]]; then
  STAGED_ROOT="$TMP/credentials"
  generate_credentials "$STAGED_ROOT"
  install -d -m 0700 "$(dirname "$LOCAL_ROOT")"
  if [[ "$LOCAL_WAS_PRESENT" == "1" ]]; then
    LOCAL_BACKUP="${LOCAL_ROOT}.backup-$(date -u +%Y%m%dT%H%M%SZ)-$$"
    [[ ! -e "$LOCAL_BACKUP" ]] || fail "local OpenVPN backup path already exists"
    mv "$LOCAL_ROOT" "$LOCAL_BACKUP"
  fi
  mv "$STAGED_ROOT" "$LOCAL_ROOT"
  LOCAL_PROMOTED=1
  SOURCE_ROOT="$LOCAL_ROOT"
fi
validate_local_credentials "$SOURCE_ROOT"
NEW_CA_FINGERPRINT="$(openssl x509 -in "$SOURCE_ROOT/ca.crt" -noout -fingerprint -sha256)"

SERVER_BUNDLE="$TMP/server-bundle.tar"
tar -C "$SOURCE_ROOT" -cf "$SERVER_BUNDLE" \
  ca.crt server.crt server.key tls-crypt.key server.conf
chmod 0600 "$SERVER_BUNDLE"

if [[ "$BOOTSTRAP" == "1" ]]; then
  [[ -n "${SECOND_BRAIN_SETUP_SCRIPTS:-}" && -f "$SECOND_BRAIN_SETUP_SCRIPTS/setup_azure.py" ]] ||
    fail "protected bootstrap requires the unified secondbrain setup entry point"
  printf '%s' "$CONNECTION" >"$TMP/connection.json"
  chmod 0600 "$TMP/connection.json"
  PYTHONPATH="$SECOND_BRAIN_SETUP_SCRIPTS${PYTHONPATH:+:$PYTHONPATH}" \
    python3 - "$TMP/connection.json" "$VM_CONFIGURATOR" "$SERVER_BUNDLE" <<'PY'
import json
from pathlib import Path
import sys
from setup_azure import bootstrap_vpn
from setup_support import SetupError
try:
    bootstrap_vpn(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]), Path(sys.argv[3]))
except SetupError as error:
    print(str(error), file=sys.stderr)
    raise SystemExit(1)
PY
  REMOTE_COMMITTED=1
  printf 'OpenVPN reconciled through Azure protected parameters. Profile: %s\n' "$CLIENT_PROFILE"
  exit 0
fi

REMOTE_STAGE="$(ssh "$VPN_SSH_ALIAS" 'umask 077; mktemp -d /tmp/codex-on-vm-openvpn.XXXXXX')"
[[ "$REMOTE_STAGE" =~ ^/tmp/codex-on-vm-openvpn\.[A-Za-z0-9]+$ ]] ||
  fail "remote OpenVPN staging path is invalid"
scp "$VM_CONFIGURATOR" "$SERVER_BUNDLE" "$VPN_SSH_ALIAS:$REMOTE_STAGE/"
printf -v install_command \
  'sudo bash %q %q %q %q %q %q %q %q' \
  "$REMOTE_STAGE/configure-codex-openvpn.sh" \
  "$SSH_USERNAME" \
  "$WORKSPACE_MOUNT" \
  "$VPN_PORT" \
  "$VPN_NETWORK" \
  "$VPN_NETMASK" \
  "$VPN_SERVER_ADDRESS" \
  "$REMOTE_STAGE/server-bundle.tar"
ssh "$VPN_SSH_ALIAS" "$install_command"
REMOTE_COMMITTED=1

write_private_file() {
  local target="$1"
  local temporary
  install -d -m 0700 "$(dirname "$target")"
  temporary="$(mktemp "$(dirname "$target")/.codex-on-vm.XXXXXX")"
  cat >"$temporary"
  chmod 0600 "$temporary"
  mv -f "$temporary" "$target"
}

cat <<EOF | write_private_file "$SSH_CONFIG"
Host $VPN_SSH_ALIAS
  HostName $VPN_SERVER_ADDRESS
  HostKeyAlias $SSH_FQDN
  User $SSH_USERNAME
  IdentityFile $MAC_PRIVATE_KEY
  IdentitiesOnly yes
  StrictHostKeyChecking yes
  UserKnownHostsFile $KNOWN_HOSTS
EOF

printf 'OpenVPN server and Mac profile were reconciled over the connected VPN.\n'
printf '  Profile: %s\n' "$CLIENT_PROFILE"
printf '  SSH after connecting: ssh %s\n' "$VPN_SSH_ALIAS"
if [[ -n "$LOCAL_BACKUP" ]]; then
  printf '  Previous credentials: %s\n' "$LOCAL_BACKUP"
fi
__CODEX_VM_HELPER_END__ openvpn-setup.sh

__CODEX_VM_HELPER_BEGIN__ remote-control-recover.sh
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="$ROOT/deployments/prod/tf"
HELPER_PATH="$ROOT/vm-scripts/ensure-codex-remote-control.sh"

fail() {
  printf 'Remote Control recovery failed: %s\n' "$1" >&2
  exit 1
}

for command in az python3 terraform; do
  command -v "$command" >/dev/null || fail "missing required command: $command"
done
[[ -f "$HELPER_PATH" && -r "$HELPER_PATH" ]] || fail "missing VM recovery helper: $HELPER_PATH"

CONNECTION="$(terraform -chdir="$TF_DIR" output -json connection)"
IFS=$'\t' read -r SUBSCRIPTION_ID RESOURCE_GROUP VM_NAME SSH_USERNAME <<<"$(CONNECTION="$CONNECTION" python3 - <<'PY'
import json
import os
import re

value = json.loads(os.environ["CONNECTION"])
fields = [value[key] for key in ("subscription_id", "resource_group_name", "vm_name", "ssh_username")]
patterns = [
    r"[0-9a-fA-F-]{36}",
    r"[A-Za-z0-9._()/-]{1,90}",
    r"[A-Za-z0-9-]{1,64}",
    r"[a-z_][a-z0-9_-]{0,31}",
]
if any(re.fullmatch(pattern, field) is None for pattern, field in zip(patterns, fields)):
    raise SystemExit("Terraform connection output contains an unsafe recovery identifier")
print("\t".join(fields))
PY
)"

[[ "$(az account show --query id --output tsv)" == "$SUBSCRIPTION_ID" ]] || fail "Azure CLI is using a different subscription"

REMOTE_SCRIPT="$(HELPER_PATH="$HELPER_PATH" SSH_USERNAME="$SSH_USERNAME" python3 - <<'PY'
import base64
import hashlib
import os
import pathlib
import shlex

helper = pathlib.Path(os.environ["HELPER_PATH"]).read_bytes()
encoded_helper = base64.b64encode(helper).decode("ascii")
expected_sha = hashlib.sha256(helper).hexdigest()
username = os.environ["SSH_USERNAME"]
target = "/usr/local/sbin/ensure-codex-remote-control"
home = f"/home/{username}"
quote = shlex.quote

print(
    f"""#!/bin/sh
set -eu
target={quote(target)}
expected_sha={quote(expected_sha)}
tmp="$(mktemp)"
trap 'rm -f "$tmp"' 0 HUP INT TERM
printf '%s' {quote(encoded_helper)} | base64 --decode >"$tmp"
actual_sha="$(sha256sum "$tmp" | awk '{{print $1}}')"
if [ "$actual_sha" != "$expected_sha" ]; then
  printf 'VM recovery helper payload checksum mismatch\\n' >&2
  exit 1
fi
if ! cmp -s "$tmp" "$target"; then
  install -o root -g root -m 0755 "$tmp" "$target"
fi
if ! cmp -s "$tmp" "$target"; then
  printf 'VM recovery helper reconciliation failed\\n' >&2
  exit 1
fi
runuser -u {quote(username)} -- env HOME={quote(home)} CODEX_HOME={quote(f"{home}/.codex")} "$target"
"""
)
PY
)"
az vm run-command invoke \
  --subscription "$SUBSCRIPTION_ID" \
  --resource-group "$RESOURCE_GROUP" \
  --name "$VM_NAME" \
  --command-id RunShellScript \
  --scripts "$REMOTE_SCRIPT" \
  --only-show-errors >/dev/null

printf 'Remote Control recovery completed through Azure Run Command; SSH remained closed.\n'
__CODEX_VM_HELPER_END__ remote-control-recover.sh
__CODEX_VM_HELPER_BEGIN__ ensure-codex-remote-control.sh
#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CODEX_BIN="$CODEX_HOME/packages/standalone/current/codex"
DAEMON_DIR="$CODEX_HOME/app-server-daemon"
APP_PID_FILE="$DAEMON_DIR/app-server.pid"
UPDATER_PID_FILE="$DAEMON_DIR/app-server-updater.pid"
HEALTH_STATE="${CODEX_RECOVERY_HEALTH_STATE:-$CODEX_HOME/codex-on-vm/remote-control-health.json}"
FAILURE_THRESHOLD="${CODEX_RECOVERY_FAILURE_THRESHOLD:-5}"
BACKOFF_BASE_SECONDS="${CODEX_RECOVERY_BACKOFF_BASE_SECONDS:-300}"
BACKOFF_MAX_SECONDS="${CODEX_RECOVERY_BACKOFF_MAX_SECONDS:-3600}"
STABILIZE_SECONDS="${CODEX_RECOVERY_STABILIZE_SECONDS:-2}"
PS_BIN="${CODEX_RECOVERY_PS:-/usr/bin/ps}"
KILL_BIN="${CODEX_RECOVERY_KILL:-/bin/kill}"
SLEEP_BIN="${CODEX_RECOVERY_SLEEP:-/usr/bin/sleep}"
CMP_BIN="${CODEX_RECOVERY_CMP:-/usr/bin/cmp}"
PROC_ROOT="${CODEX_RECOVERY_PROC_ROOT:-/proc}"
PROCESS_USER="$(id -un)"
CONSECUTIVE_FAILURES=0
LAST_RESTART_EPOCH=0
RESTART_ATTEMPTS=0
NOW_EPOCH=0

fail() {
  printf 'Codex Remote Control recovery failed: %s\n' "$1" >&2
  exit 1
}

require_nonnegative_integer() {
  local name="$1"
  local value="$2"
  [[ "$value" =~ ^[0-9]+$ ]] || fail "$name must be a non-negative integer"
}

load_health_state() {
  local values
  [[ -f "$HEALTH_STATE" ]] || return 0
  if ! values="$(jq -er '
    select(
      (.consecutiveFailures | type == "number" and . >= 0 and floor == .) and
      (.lastRestartEpoch | type == "number" and . >= 0 and floor == .) and
      (.restartAttempts | type == "number" and . >= 0 and floor == .)
    )
    | [.consecutiveFailures, .lastRestartEpoch, .restartAttempts]
    | @tsv
  ' "$HEALTH_STATE")"; then
    printf 'Ignoring invalid Remote Control health state at %s.\n' "$HEALTH_STATE" >&2
    return 0
  fi
  IFS=$'\t' read -r CONSECUTIVE_FAILURES LAST_RESTART_EPOCH RESTART_ATTEMPTS <<<"$values"
}

write_health_state() {
  local state_dir temporary
  state_dir="$(dirname "$HEALTH_STATE")"
  mkdir -p "$state_dir"
  temporary="$(mktemp "$state_dir/.health-state.XXXXXX")"
  if ! jq -n \
    --argjson consecutiveFailures "$CONSECUTIVE_FAILURES" \
    --argjson lastRestartEpoch "$LAST_RESTART_EPOCH" \
    --argjson restartAttempts "$RESTART_ATTEMPTS" \
    '{
      consecutiveFailures: $consecutiveFailures,
      lastRestartEpoch: $lastRestartEpoch,
      restartAttempts: $restartAttempts
    }' >"$temporary"; then
    rm -f "$temporary"
    return 1
  fi
  chmod 0600 "$temporary"
  mv "$temporary" "$HEALTH_STATE"
}

reset_health_state() {
  CONSECUTIVE_FAILURES=0
  LAST_RESTART_EPOCH=0
  RESTART_ATTEMPTS=0
  write_health_state
}

daemon_ready() {
  local output managed_codex_path
  output="$("$CODEX_BIN" app-server daemon version)" || return 1
  managed_codex_path="$(jq -er '
    select(
      .status == "running" and
      (.appServerVersion | type == "string" and length > 0) and
      (.managedCodexPath | type == "string" and length > 0)
    )
    | .managedCodexPath
  ' <<<"$output")" || return 1
  [[ "$managed_codex_path" -ef "$CODEX_BIN" ]]
}

daemon_stable() {
  daemon_ready || return 1
  "$SLEEP_BIN" "$STABILIZE_SECONDS"
  daemon_ready
}

remote_control_connected() {
  local output
  if ! output="$("$CODEX_BIN" remote-control start --json 2>&1)"; then
    [[ -z "$output" ]] || printf '%s\n' "$output" >&2
    return 1
  fi
  printf '%s\n' "$output"
  jq -e '
    select(
      .mode == "daemon" and
      .status == "connected" and
      .timedOut == false and
      (.environmentId | type == "string" and length > 0) and
      (.daemon | type == "object") and
      (.daemon.status | type == "string" and length > 0)
    )
  ' <<<"$output" >/dev/null
}

finish_connected() {
  local message="$1"
  reset_health_state || fail "could not persist connected health state"
  printf '%s\n' "$message"
}

record_connection_failure() {
  CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
  write_health_state || fail "could not persist Remote Control failure state"
}

restart_backoff_seconds() {
  local delay attempt
  delay="$BACKOFF_BASE_SECONDS"
  for ((attempt = 1; attempt < RESTART_ATTEMPTS; attempt++)); do
    if ((delay >= BACKOFF_MAX_SECONDS / 2)); then
      delay="$BACKOFF_MAX_SECONDS"
      break
    fi
    delay=$((delay * 2))
  done
  ((delay <= BACKOFF_MAX_SECONDS)) || delay="$BACKOFF_MAX_SECONDS"
  printf '%s\n' "$delay"
}

restart_is_due() {
  local delay elapsed
  ((CONSECUTIVE_FAILURES >= FAILURE_THRESHOLD)) || return 1
  ((LAST_RESTART_EPOCH == 0)) && return 0
  delay="$(restart_backoff_seconds)"
  ((NOW_EPOCH >= LAST_RESTART_EPOCH)) || return 1
  elapsed=$((NOW_EPOCH - LAST_RESTART_EPOCH))
  ((elapsed >= delay))
}

record_restart_attempt() {
  LAST_RESTART_EPOCH="$NOW_EPOCH"
  RESTART_ATTEMPTS=$((RESTART_ATTEMPTS + 1))
  write_health_state || fail "could not persist Remote Control restart state"
}

record_value() {
  local path="$1"
  local field="$2"
  [[ -f "$path" ]] || return 1
  jq -er --arg field "$field" '.[$field]' "$path"
}

process_value() {
  local pid="$1"
  local field="$2"
  "$PS_BIN" -p "$pid" -o "$field" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

same_executable_content() {
  local candidate="$1"
  [[ -x "$candidate" && -x "$CODEX_BIN" ]] || return 1
  [[ "$candidate" -ef "$CODEX_BIN" ]] || "$CMP_BIN" -s "$candidate" "$CODEX_BIN"
}

verified_stale_processes() {
  local updater_args updater_executable
  UPDATER_PID="$(record_value "$UPDATER_PID_FILE" pid)" || return 1
  UPDATER_STARTED="$(record_value "$UPDATER_PID_FILE" processStartTime)" || return 1
  APP_PID="$(record_value "$APP_PID_FILE" pid)" || return 1
  APP_STARTED="$(record_value "$APP_PID_FILE" processStartTime)" || return 1
  [[ "$UPDATER_PID" =~ ^[0-9]+$ && "$UPDATER_PID" -gt 1 ]] || return 1
  [[ "$APP_PID" =~ ^[0-9]+$ && "$APP_PID" -gt 1 ]] || return 1
  [[ "$(process_value "$UPDATER_PID" user=)" == "$PROCESS_USER" ]] || return 1
  [[ "$(process_value "$UPDATER_PID" lstart=)" == "$UPDATER_STARTED" ]] || return 1
  updater_args="$(process_value "$UPDATER_PID" args=)" || return 1
  updater_executable="${updater_args% app-server daemon pid-update-loop}"
  [[ -n "$updater_executable" && "$updater_executable" != "$updater_args" ]] || return 1
  same_executable_content "$updater_executable" || return 1
  same_executable_content "$PROC_ROOT/$UPDATER_PID/exe" || return 1
  [[ "$(process_value "$APP_PID" user=)" == "$PROCESS_USER" ]] || return 1
  [[ "$(process_value "$APP_PID" lstart=)" == "$APP_STARTED" ]] || return 1
  [[ "$(process_value "$APP_PID" stat=)" == Z* ]] || return 1
  [[ "$(process_value "$APP_PID" ppid=)" == "$UPDATER_PID" ]] || return 1
}

terminate_verified_stale_parent() {
  verified_stale_processes || return 1
  "$KILL_BIN" -TERM "$UPDATER_PID"
  for _attempt in {1..10}; do
    if ! process_value "$UPDATER_PID" user= >/dev/null 2>&1 && \
      ! process_value "$APP_PID" user= >/dev/null 2>&1; then
      return 0
    fi
    "$SLEEP_BIN" 1
  done
  return 1
}

recover_after_restart() {
  if remote_control_connected && daemon_stable; then
    finish_connected "Codex Remote Control recovered after a bounded daemon restart."
    return 0
  fi
  daemon_ready && return 1
  recover_verified_stale
}

recover_verified_stale() {
  if terminate_verified_stale_parent && remote_control_connected && daemon_stable; then
    finish_connected "Codex Remote Control recovered from a verified stale updater."
    return 0
  fi
  return 1
}

handle_remote_degradation() {
  local delay
  record_connection_failure
  if ((CONSECUTIVE_FAILURES < FAILURE_THRESHOLD)); then
    fail "relay connection is degraded ($CONSECUTIVE_FAILURES/$FAILURE_THRESHOLD); the healthy local daemon was left running"
  fi
  if ! restart_is_due; then
    delay="$(restart_backoff_seconds)"
    fail "relay connection remains degraded; restart backoff is active for up to $delay seconds"
  fi
  record_restart_attempt
  if "$CODEX_BIN" app-server daemon restart && recover_after_restart; then
    return 0
  fi
  fail "bounded daemon restart did not restore a connected Remote Control session"
}

command -v jq >/dev/null || fail "jq is unavailable"
[[ -x "$CMP_BIN" ]] || fail "cmp is unavailable at $CMP_BIN"
[[ -x "$CODEX_BIN" ]] || fail "managed Codex install is unavailable at $CODEX_BIN"
require_nonnegative_integer CODEX_RECOVERY_FAILURE_THRESHOLD "$FAILURE_THRESHOLD"
require_nonnegative_integer CODEX_RECOVERY_BACKOFF_BASE_SECONDS "$BACKOFF_BASE_SECONDS"
require_nonnegative_integer CODEX_RECOVERY_BACKOFF_MAX_SECONDS "$BACKOFF_MAX_SECONDS"
require_nonnegative_integer CODEX_RECOVERY_STABILIZE_SECONDS "$STABILIZE_SECONDS"
((FAILURE_THRESHOLD > 0)) || fail "CODEX_RECOVERY_FAILURE_THRESHOLD must be greater than zero"
((BACKOFF_BASE_SECONDS > 0)) || fail "CODEX_RECOVERY_BACKOFF_BASE_SECONDS must be greater than zero"
((BACKOFF_MAX_SECONDS >= BACKOFF_BASE_SECONDS)) ||
  fail "CODEX_RECOVERY_BACKOFF_MAX_SECONDS must not be less than the base"
if [[ -n "${CODEX_RECOVERY_NOW_EPOCH:-}" ]]; then
  require_nonnegative_integer CODEX_RECOVERY_NOW_EPOCH "$CODEX_RECOVERY_NOW_EPOCH"
  NOW_EPOCH="$CODEX_RECOVERY_NOW_EPOCH"
else
  NOW_EPOCH="$(date +%s)"
fi
umask 077
load_health_state

if remote_control_connected && daemon_stable; then
  finish_connected "Codex Remote Control is connected."
  exit 0
fi

if daemon_ready; then
  handle_remote_degradation
  exit 0
fi

record_restart_attempt
if "$CODEX_BIN" app-server daemon restart; then
  recover_after_restart && exit 0
else
  recover_verified_stale && exit 0
fi
fail "supported lifecycle recovery failed and the stale process state was not safe to terminate"
__CODEX_VM_HELPER_END__ ensure-codex-remote-control.sh

__CODEX_VM_HELPER_BEGIN__ ensure-ssh-keys.sh
#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'SSH key bootstrap failed: %s\n' "$1" >&2
  exit 1
}

for command in python3 ssh-keygen; do
  command -v "$command" >/dev/null || fail "missing required command: $command"
done

INPUT="$(cat)"
MAC_PRIVATE_KEY="$(INPUT="$INPUT" python3 - <<'PY'
import json
import os

value = json.loads(os.environ["INPUT"])
if set(value) != {"mac_private_key_path"}:
    raise SystemExit("expected only mac_private_key_path")
path = value["mac_private_key_path"]
if not path.startswith("/") or "\n" in path or "\t" in path:
    raise SystemExit("key path must be absolute and contain no control characters")
print(path)
PY
)"
PUBLIC_KEY="$MAC_PRIVATE_KEY.pub"

install -d -m 0700 "$(dirname "$MAC_PRIVATE_KEY")"
if [[ -f "$PUBLIC_KEY" && ! -f "$MAC_PRIVATE_KEY" ]]; then
  fail "public key exists without its private key: $PUBLIC_KEY"
fi
if [[ ! -f "$MAC_PRIVATE_KEY" ]]; then
  ssh-keygen -q -t ed25519 -a 100 -N "" -C "codex-on-vm-mac" -f "$MAC_PRIVATE_KEY"
fi
if [[ ! -f "$PUBLIC_KEY" ]]; then
  ssh-keygen -y -f "$MAC_PRIVATE_KEY" >"$PUBLIC_KEY"
fi

chmod 0600 "$MAC_PRIVATE_KEY"
chmod 0644 "$PUBLIC_KEY"
DERIVED_PUBLIC="$(ssh-keygen -y -f "$MAC_PRIVATE_KEY" | awk '{print $1 " " $2}')"
STORED_PUBLIC="$(awk '{print $1 " " $2}' "$PUBLIC_KEY")"
[[ "$DERIVED_PUBLIC" == "$STORED_PUBLIC" ]] || fail "public key does not match private key: $PUBLIC_KEY"

MAC_PUBLIC_KEY="$PUBLIC_KEY" python3 - <<'PY'
import json
import os

with open(os.environ["MAC_PUBLIC_KEY"], encoding="utf-8") as handle:
    mac = handle.read().strip()
print(json.dumps({"mac_public_key": mac}, sort_keys=True))
PY
__CODEX_VM_HELPER_END__ ensure-ssh-keys.sh

__CODEX_VM_HELPER_BEGIN__ fetch-verified-artifact.sh
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  printf 'usage: %s <https-url> <sha256> <output-path>\n' "$0" >&2
  exit 64
fi

URL="$1"
EXPECTED_SHA256="$2"
OUTPUT_PATH="$3"

[[ "$URL" == https://* ]] || {
  printf 'verified artifact URL must use HTTPS\n' >&2
  exit 65
}
[[ "$EXPECTED_SHA256" =~ ^[0-9a-f]{64}$ ]] || {
  printf 'expected SHA-256 must be 64 lowercase hexadecimal characters\n' >&2
  exit 65
}

for command in curl awk; do
  command -v "$command" >/dev/null || {
    printf 'missing required command: %s\n' "$command" >&2
    exit 69
  }
done

OUTPUT_DIR="$(dirname "$OUTPUT_PATH")"
if [[ ! -d "$OUTPUT_DIR" ]]; then
  install -d -m 0700 "$OUTPUT_DIR"
fi
TEMP_PATH="$(mktemp "${OUTPUT_PATH}.tmp.XXXXXX")"
trap 'rm -f "$TEMP_PATH"' EXIT

curl --proto '=https' --tlsv1.2 --fail --silent --show-error --location --output "$TEMP_PATH" "$URL"
if command -v sha256sum >/dev/null 2>&1; then
  ACTUAL_SHA256="$(sha256sum "$TEMP_PATH" | awk '{print $1}')"
elif command -v shasum >/dev/null 2>&1; then
  ACTUAL_SHA256="$(shasum -a 256 "$TEMP_PATH" | awk '{print $1}')"
else
  printf 'missing SHA-256 command: sha256sum or shasum\n' >&2
  exit 69
fi

[[ "$ACTUAL_SHA256" == "$EXPECTED_SHA256" ]] || {
  printf 'artifact SHA-256 mismatch for %s\n' "$URL" >&2
  exit 66
}

chmod 0600 "$TEMP_PATH"
mv -f "$TEMP_PATH" "$OUTPUT_PATH"
trap - EXIT
__CODEX_VM_HELPER_END__ fetch-verified-artifact.sh

__CODEX_VM_HELPER_BEGIN__ install-verified-codex.sh
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 6 ]]; then
  printf 'usage: %s <package-url> <sha256> <version> <codex-home> <bin-dir> <verified-fetch-command>\n' "$0" >&2
  exit 64
fi

PACKAGE_URL="$1"
PACKAGE_SHA256="$2"
VERSION="$3"
CODEX_HOME="$4"
BIN_DIR="$5"
FETCH_COMMAND="$6"
TARGET="x86_64-unknown-linux-musl"
STANDALONE_ROOT="$CODEX_HOME/packages/standalone"
RELEASES_DIR="$STANDALONE_ROOT/releases"
RELEASE_DIR="$RELEASES_DIR/$VERSION-$TARGET"
CURRENT_LINK="$STANDALONE_ROOT/current"

[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
  printf 'Codex version must use x.y.z format\n' >&2
  exit 65
}
[[ -x "$FETCH_COMMAND" ]] || {
  printf 'verified fetch command is not executable: %s\n' "$FETCH_COMMAND" >&2
  exit 69
}
for command in tar awk grep; do
  command -v "$command" >/dev/null || {
    printf 'missing required command: %s\n' "$command" >&2
    exit 69
  }
done

TEMP_DIR="$(mktemp -d)"
STAGE_DIR="$RELEASES_DIR/.staging.$VERSION-$TARGET.$$"
TEMP_CURRENT="$STANDALONE_ROOT/.current.$$"
TEMP_BIN="$BIN_DIR/.codex.$$"
cleanup() {
  rm -rf "$TEMP_DIR" "$STAGE_DIR"
  rm -f "$TEMP_CURRENT" "$TEMP_BIN"
}
trap cleanup EXIT

ARCHIVE="$TEMP_DIR/codex-package.tar.gz"
"$FETCH_COMMAND" "$PACKAGE_URL" "$PACKAGE_SHA256" "$ARCHIVE"

while IFS= read -r member; do
  normalized="${member#./}"
  [[ -n "$normalized" ]] || continue
  case "$normalized" in
    /*|../*|*/../*|*/..)
      printf 'unsafe archive member: %s\n' "$member" >&2
      exit 66
      ;;
  esac
done < <(tar -tzf "$ARCHIVE")

install -d -m 0755 "$RELEASES_DIR" "$BIN_DIR"
mkdir -p "$STAGE_DIR"
tar -xzf "$ARCHIVE" -C "$STAGE_DIR"
for required in bin/codex bin/codex-code-mode-host codex-path/rg codex-resources/bwrap codex-package.json; do
  [[ -f "$STAGE_DIR/$required" ]] || {
    printf 'Codex package is missing %s\n' "$required" >&2
    exit 66
  }
done
chmod 0755 "$STAGE_DIR/bin/codex" "$STAGE_DIR/bin/codex-code-mode-host" "$STAGE_DIR/codex-path/rg" "$STAGE_DIR/codex-resources/bwrap"
INSTALLED_VERSION="$("$STAGE_DIR/bin/codex" --version | awk '{print $NF}')"
[[ "$INSTALLED_VERSION" == "$VERSION" ]] || {
  printf 'Codex package version mismatch: expected %s, got %s\n' "$VERSION" "$INSTALLED_VERSION" >&2
  exit 66
}
ln -s bin/codex "$STAGE_DIR/codex"

if [[ -e "$RELEASE_DIR" || -L "$RELEASE_DIR" ]]; then
  EXISTING_VERSION="$("$RELEASE_DIR/bin/codex" --version 2>/dev/null | awk '{print $NF}' || true)"
  [[ "$EXISTING_VERSION" == "$VERSION" ]] || {
    printf 'existing release directory has an unexpected version: %s\n' "$RELEASE_DIR" >&2
    exit 73
  }
  rm -rf "$STAGE_DIR"
else
  mv "$STAGE_DIR" "$RELEASE_DIR"
fi

ln -s "$RELEASE_DIR" "$TEMP_CURRENT"
mv -f "$TEMP_CURRENT" "$CURRENT_LINK"
ln -s "$CURRENT_LINK/bin/codex" "$TEMP_BIN"
mv -f "$TEMP_BIN" "$BIN_DIR/codex"
"$BIN_DIR/codex" --version >/dev/null
__CODEX_VM_HELPER_END__ install-verified-codex.sh

__CODEX_VM_HELPER_BEGIN__ configure-codex-openvpn.sh
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 6 && $# -ne 7 ]]; then
  printf 'usage: %s <admin-user> <projects-mount> <port> <network> <netmask> <server-address> [server-bundle]\n' "$0" >&2
  exit 64
fi

ADMIN_USER="$1"
MOUNT_PATH="$2"
VPN_PORT="$3"
VPN_NETWORK="$4"
VPN_NETMASK="$5"
VPN_SERVER_ADDRESS="$6"
BUNDLE_PATH="${7:-}"
VM_ROOT="${CODEX_VM_ROOT:-}"
TEST_MODE="${CODEX_VM_TEST_MODE:-0}"
SERVICE="openvpn-server@codex-vm.service"
PERSISTENT_ROOT=""
RUNTIME_ROOT=""
STAGE_ROOT=""
BUNDLE_STAGE_ROOT=""
PREVIOUS_PERSISTENT=""
TRANSACTION_ACTIVE=0
TRANSACTION_COMMITTED=0

fail() {
  printf 'OpenVPN VM configuration failed: %s\n' "$1" >&2
  exit 1
}

root_path() {
  printf '%s%s\n' "$VM_ROOT" "$1"
}

cleanup() {
  local status=$?
  set +e
  [[ -z "$STAGE_ROOT" ]] || rm -rf -- "$STAGE_ROOT"
  [[ -z "$BUNDLE_STAGE_ROOT" ]] || rm -rf -- "$BUNDLE_STAGE_ROOT"
  if [[ "$status" != "0" && "$TRANSACTION_ACTIVE" == "1" && "$TRANSACTION_COMMITTED" != "1" ]]; then
    rm -rf -- "$PERSISTENT_ROOT"
    if [[ -n "$PREVIOUS_PERSISTENT" && -d "$PREVIOUS_PERSISTENT" ]]; then
      mv "$PREVIOUS_PERSISTENT" "$PERSISTENT_ROOT"
      PREVIOUS_PERSISTENT=""
      install_material_tree_runtime "$PERSISTENT_ROOT" "$RUNTIME_ROOT" >/dev/null 2>&1 || true
      systemctl restart "$SERVICE" >/dev/null 2>&1 || true
    else
      rm -rf -- "$RUNTIME_ROOT"
      systemctl disable --now "$SERVICE" >/dev/null 2>&1 || true
    fi
  fi
  if [[ -n "$BUNDLE_PATH" ]]; then
    rm -f -- "$BUNDLE_PATH"
  fi
  exit "$status"
}

trap cleanup EXIT
trap 'exit 130' INT TERM

[[ "$ADMIN_USER" =~ ^[a-z_][a-z0-9_-]{0,31}$ ]] || fail "admin user is invalid"
[[ "$MOUNT_PATH" == /* && "$MOUNT_PATH" != *$'\n'* && "$MOUNT_PATH" != *$'\r'* && "$MOUNT_PATH" != *$'\t'* ]] ||
  fail "projects mount is invalid"
[[ "$VPN_PORT" =~ ^[0-9]+$ ]] || fail "OpenVPN port is invalid"
((VPN_PORT >= 1 && VPN_PORT <= 65535)) || fail "OpenVPN port is outside 1-65535"
[[ -z "$VM_ROOT" || "$TEST_MODE" == "1" ]] || fail "CODEX_VM_ROOT is available only in test mode"
if [[ -n "$BUNDLE_PATH" ]]; then
  [[ "$BUNDLE_PATH" == /* && "$BUNDLE_PATH" != *$'\n'* && "$BUNDLE_PATH" != *$'\r'* && "$BUNDLE_PATH" != *$'\t'* ]] ||
    fail "server bundle path is invalid"
  [[ -f "$BUNDLE_PATH" ]] || fail "server bundle is missing"
fi
python3 - "$VPN_NETWORK" "$VPN_NETMASK" "$VPN_SERVER_ADDRESS" <<'PY'
import ipaddress
import sys

network = ipaddress.IPv4Network((sys.argv[1], sys.argv[2]), strict=True)
server = ipaddress.IPv4Address(sys.argv[3])
if network.prefixlen != 24:
    raise SystemExit("OpenVPN network must be a /24")
if server != next(network.hosts()):
    raise SystemExit("OpenVPN server address must be the first usable network address")
PY

MOUNT_PHYSICAL="$(root_path "$MOUNT_PATH")"
[[ -d "$MOUNT_PHYSICAL" ]] || fail "projects mount is unavailable"
if [[ "$TEST_MODE" != "1" ]]; then
  mountpoint -q "$MOUNT_PHYSICAL" || fail "projects filesystem is not mounted"
fi
PERSISTENT_ROOT="$MOUNT_PHYSICAL/.codex-on-vm/openvpn/server"
RUNTIME_ROOT="$(root_path /etc/openvpn/server)"
if [[ -z "$BUNDLE_PATH" && ! -d "$PERSISTENT_ROOT" ]]; then
  printf 'Persistent OpenVPN material is not present; skipping service restoration.\n'
  exit 0
fi
for command in cmp openssl openvpn python3 systemctl tar; do
  command -v "$command" >/dev/null || fail "missing required command: $command"
done

validate_server_material() {
  local source="$1"
  local key_pub cert_pub
  for required in ca.crt server.crt server.key tls-crypt.key server.conf; do
    [[ -f "$source/$required" ]] || fail "server material is missing $required"
  done
  [[ ! -e "$source/ca.key" && ! -e "$source/client.key" && ! -e "$source/client.crt" ]] ||
    fail "server material contains client or CA private state"
  openssl verify -CAfile "$source/ca.crt" "$source/server.crt" >/dev/null ||
    fail "server certificate verification failed"
  key_pub="$(mktemp)"
  cert_pub="$(mktemp)"
  openssl pkey -in "$source/server.key" -pubout -out "$key_pub" >/dev/null 2>&1 ||
    fail "server private key is invalid"
  openssl x509 -in "$source/server.crt" -pubkey -noout >"$cert_pub" ||
    fail "server certificate is invalid"
  cmp -s "$key_pub" "$cert_pub" || fail "server certificate does not match its private key"
  rm -f "$key_pub" "$cert_pub"
  grep -Fqx -- "port $VPN_PORT" "$source/server.conf" || fail "server configuration has the wrong port"
  grep -Fqx -- 'proto udp' "$source/server.conf" || fail "server configuration must use UDP"
  grep -Fqx -- "server $VPN_NETWORK $VPN_NETMASK" "$source/server.conf" ||
    fail "server configuration has the wrong tunnel network"
  grep -Fqx -- 'verify-client-cert require' "$source/server.conf" ||
    fail "server configuration does not require client certificates"
  grep -Fqx -- 'remote-cert-tls client' "$source/server.conf" ||
    fail "server configuration does not require client certificate usage"
  grep -Fqx -- 'tls-version-min 1.2' "$source/server.conf" ||
    fail "server configuration has no TLS minimum"
  grep -Fqx -- 'tls-crypt /etc/openvpn/server/tls-crypt.key' "$source/server.conf" ||
    fail "server configuration does not use tls-crypt"
  if grep -Eiq '^[[:space:]]*(push[[:space:]]+")?(redirect-gateway|dhcp-option|comp-lzo|compress|client-to-client)' "$source/server.conf"; then
    fail "server configuration expands routing or weakens tunnel isolation"
  fi
}

install_material_tree() {
  local source="$1"
  local target="$2"
  local next="${target}.next.$$"
  rm -rf -- "$next"
  install -d -m 0700 "$next"
  install -m 0644 "$source/ca.crt" "$next/ca.crt"
  install -m 0644 "$source/server.crt" "$next/server.crt"
  install -m 0600 "$source/server.key" "$next/server.key"
  install -m 0600 "$source/tls-crypt.key" "$next/tls-crypt.key"
  install -m 0644 "$source/server.conf" "$next/codex-vm.conf"
  rm -rf -- "$target"
  mv "$next" "$target"
}

activate_persistent_material() {
  validate_server_material_runtime "$PERSISTENT_ROOT"
  install -d -m 0755 "$(dirname "$RUNTIME_ROOT")"
  install_material_tree_runtime "$PERSISTENT_ROOT" "$RUNTIME_ROOT"
  systemctl daemon-reload || return 1
  systemctl enable "$SERVICE" || return 1
  systemctl restart "$SERVICE" || return 1
  systemctl is-active --quiet "$SERVICE" || return 1
}

validate_server_material_runtime() {
  local source="$1"
  [[ -f "$source/codex-vm.conf" ]] || fail "persistent OpenVPN configuration is missing"
  STAGE_ROOT="$(mktemp -d)"
  install -m 0644 "$source/ca.crt" "$STAGE_ROOT/ca.crt"
  install -m 0644 "$source/server.crt" "$STAGE_ROOT/server.crt"
  install -m 0600 "$source/server.key" "$STAGE_ROOT/server.key"
  install -m 0600 "$source/tls-crypt.key" "$STAGE_ROOT/tls-crypt.key"
  install -m 0644 "$source/codex-vm.conf" "$STAGE_ROOT/server.conf"
  validate_server_material "$STAGE_ROOT"
  rm -rf -- "$STAGE_ROOT"
  STAGE_ROOT=""
}

install_material_tree_runtime() {
  local source="$1"
  local target="$2"
  STAGE_ROOT="$(mktemp -d)"
  install -m 0644 "$source/ca.crt" "$STAGE_ROOT/ca.crt"
  install -m 0644 "$source/server.crt" "$STAGE_ROOT/server.crt"
  install -m 0600 "$source/server.key" "$STAGE_ROOT/server.key"
  install -m 0600 "$source/tls-crypt.key" "$STAGE_ROOT/tls-crypt.key"
  install -m 0644 "$source/codex-vm.conf" "$STAGE_ROOT/server.conf"
  install_material_tree "$STAGE_ROOT" "$target"
  rm -rf -- "$STAGE_ROOT"
  STAGE_ROOT=""
}

if [[ -z "$BUNDLE_PATH" ]]; then
  activate_persistent_material || fail "restored OpenVPN service did not become active"
  printf 'OPENVPN_SERVER_READY=1\n'
  exit 0
fi

BUNDLE_STAGE_ROOT="$(mktemp -d)"
bundle_members="$(tar -tf "$BUNDLE_PATH" | sed 's#^\./##' | LC_ALL=C sort)"
expected_members="$(printf '%s\n' ca.crt server.conf server.crt server.key tls-crypt.key | LC_ALL=C sort)"
[[ "$bundle_members" == "$expected_members" ]] || fail "server bundle contains unexpected paths"
tar -xf "$BUNDLE_PATH" -C "$BUNDLE_STAGE_ROOT"
rm -f -- "$BUNDLE_PATH"
BUNDLE_PATH=""
validate_server_material "$BUNDLE_STAGE_ROOT"

install -d -m 0700 "$(dirname "$PERSISTENT_ROOT")"
if [[ -d "$PERSISTENT_ROOT" ]]; then
  PREVIOUS_PERSISTENT="${PERSISTENT_ROOT}.previous.$$"
  [[ ! -e "$PREVIOUS_PERSISTENT" ]] || fail "OpenVPN transaction backup already exists"
  mv "$PERSISTENT_ROOT" "$PREVIOUS_PERSISTENT"
fi
TRANSACTION_ACTIVE=1
install_material_tree "$BUNDLE_STAGE_ROOT" "$PERSISTENT_ROOT"

if ! activate_persistent_material; then
  rm -rf -- "$PERSISTENT_ROOT" "$RUNTIME_ROOT"
  if [[ -n "$PREVIOUS_PERSISTENT" && -d "$PREVIOUS_PERSISTENT" ]]; then
    mv "$PREVIOUS_PERSISTENT" "$PERSISTENT_ROOT"
    if ! activate_persistent_material; then
      TRANSACTION_ACTIVE=0
      PREVIOUS_PERSISTENT=""
      fail "OpenVPN replacement and rollback both failed"
    fi
    PREVIOUS_PERSISTENT=""
  else
    systemctl disable --now "$SERVICE" >/dev/null 2>&1 || true
  fi
  TRANSACTION_ACTIVE=0
  fail "OpenVPN replacement did not become active; previous configuration was restored"
fi

if [[ -n "$PREVIOUS_PERSISTENT" ]]; then
  rm -rf -- "$PREVIOUS_PERSISTENT"
  PREVIOUS_PERSISTENT=""
fi
TRANSACTION_COMMITTED=1
TRANSACTION_ACTIVE=0
printf 'OPENVPN_SERVER_READY=1\n'
__CODEX_VM_HELPER_END__ configure-codex-openvpn.sh

__CODEX_VM_HELPER_BEGIN__ prepare-codex-vm.sh
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 10 ]]; then
  printf 'usage: %s <admin-user> <projects-mount> <disk-lun> <codex-version> <package-url> <package-sha256> <openvpn-port> <openvpn-network> <openvpn-netmask> <openvpn-server-address>\n' "$0" >&2
  exit 64
fi

ADMIN_USER="$1"
MOUNT_PATH="$2"
DISK_LUN="$3"
CODEX_VERSION="$4"
CODEX_PACKAGE_URL="$5"
CODEX_PACKAGE_SHA256="$6"
OPENVPN_PORT="$7"
OPENVPN_NETWORK="$8"
OPENVPN_NETMASK="$9"
OPENVPN_SERVER_ADDRESS="${10}"
VM_ROOT="${CODEX_VM_ROOT:-}"
TEST_MODE="${CODEX_VM_TEST_MODE:-0}"
DATA_DISK="${CODEX_VM_DATA_DISK:-/dev/disk/azure/data/by-lun/$DISK_LUN}"

fail() {
  printf 'Codex VM preparation failed: %s\n' "$1" >&2
  exit 1
}

root_path() {
  printf '%s%s\n' "$VM_ROOT" "$1"
}

device_exists() {
  if [[ "$TEST_MODE" == "1" ]]; then
    [[ -e "$1" ]]
  else
    [[ -b "$1" ]]
  fi
}

install_owned_dir() {
  local mode="$1"
  local path="$2"
  if [[ "$TEST_MODE" == "1" ]]; then
    install -d -m "$mode" "$path"
  else
    install -d -o "$ADMIN_USER" -g "$ADMIN_USER" -m "$mode" "$path"
  fi
}

write_if_changed() {
  local mode="$1"
  local target="$2"
  local temporary
  install -d -m 0755 "$(dirname "$target")"
  temporary="$(mktemp)"
  cat >"$temporary"
  if [[ ! -f "$target" ]] || ! cmp -s "$temporary" "$target"; then
    if [[ "$TEST_MODE" == "1" ]]; then
      install -m "$mode" "$temporary" "$target"
    else
      install -o root -g root -m "$mode" "$temporary" "$target"
    fi
  fi
  rm -f "$temporary"
}

install_packages() {
  local attempt
  for attempt in $(seq 1 12); do
    if DEBIAN_FRONTEND=noninteractive apt-get update &&
      DEBIAN_FRONTEND=noninteractive apt-get install -y \
        apparmor-profiles \
        apparmor-utils \
        azure-vm-utils \
        bubblewrap \
        ca-certificates \
        curl \
        e2fsprogs \
        fail2ban \
        git \
        jq \
        openvpn \
        parted \
        python3-venv \
        unattended-upgrades; then
      return
    fi
    sleep 10
  done
  fail "Ubuntu package installation did not converge"
}

restore_openvpn() {
  local configurator
  configurator="$(root_path /usr/local/sbin/configure-codex-openvpn)"
  [[ -x "$configurator" ]] || fail "OpenVPN configurator is unavailable"
  CODEX_VM_ROOT="$VM_ROOT" CODEX_VM_TEST_MODE="$TEST_MODE" \
    "$configurator" \
    "$ADMIN_USER" \
    "$MOUNT_PATH" \
    "$OPENVPN_PORT" \
    "$OPENVPN_NETWORK" \
    "$OPENVPN_NETMASK" \
    "$OPENVPN_SERVER_ADDRESS"
}

configure_apparmor() {
  local source target
  source="$(root_path /usr/share/apparmor/extra-profiles/bwrap-userns-restrict)"
  target="$(root_path /etc/apparmor.d/bwrap-userns-restrict)"
  command -v bwrap >/dev/null || fail "bubblewrap is unavailable after package installation"
  command -v apparmor_parser >/dev/null || fail "AppArmor parser is unavailable"
  [[ -f "$source" ]] || fail "Ubuntu bubblewrap AppArmor profile is unavailable"
  install -d -m 0755 "$(dirname "$target")"
  if [[ "$TEST_MODE" == "1" ]]; then
    install -m 0644 "$source" "$target"
  else
    install -o root -g root -m 0644 "$source" "$target"
  fi
  apparmor_parser -r "$target"
}

prepare_workspace_disk() {
  local partition filesystem_device filesystem_type filesystem_uuid created_partition attempt
  for attempt in $(seq 1 120); do
    device_exists "$DATA_DISK" && break
    sleep 5
  done
  device_exists "$DATA_DISK" || fail "managed data disk is unavailable at $DATA_DISK"

  partition="$(lsblk -nrpo NAME,TYPE "$DATA_DISK" | awk '$2 == "part" { print $1; exit }')"
  created_partition=0
  if [[ -n "$partition" ]]; then
    filesystem_device="$partition"
  elif [[ -n "$(blkid -s TYPE -o value "$DATA_DISK" 2>/dev/null || true)" ]]; then
    filesystem_device="$DATA_DISK"
  else
    [[ -z "$(wipefs --no-act "$DATA_DISK" 2>/dev/null)" ]] || fail "unformatted disk contains unexpected signatures"
    parted "$DATA_DISK" --script mklabel gpt mkpart primary ext4 0% 100%
    partprobe "$DATA_DISK"
    udevadm settle
    partition="$(lsblk -nrpo NAME,TYPE "$DATA_DISK" | awk '$2 == "part" { print $1; exit }')"
    device_exists "$partition" || fail "partition creation did not produce a device"
    filesystem_device="$partition"
    created_partition=1
  fi

  filesystem_type="$(blkid -s TYPE -o value "$filesystem_device" 2>/dev/null || true)"
  if [[ -z "$filesystem_type" ]]; then
    [[ "$created_partition" == "1" ]] || fail "refusing to format a pre-existing untyped device"
    mkfs.ext4 -L codex-workspace "$filesystem_device"
    filesystem_type=ext4
  fi
  [[ "$filesystem_type" == "ext4" ]] || fail "workspace filesystem must be ext4"
  filesystem_uuid="$(blkid -s UUID -o value "$filesystem_device")"
  [[ -n "$filesystem_uuid" ]] || fail "workspace filesystem has no UUID"

  MOUNT_PHYSICAL="$(root_path "$MOUNT_PATH")"
  FSTAB_PATH="$(root_path /etc/fstab)"
  install_owned_dir 0770 "$MOUNT_PHYSICAL"
  install -d -m 0755 "$(dirname "$FSTAB_PATH")"
  touch "$FSTAB_PATH"
  sed -i.bak "\\|[[:space:]]$MOUNT_PATH[[:space:]]|d" "$FSTAB_PATH"
  rm -f "$FSTAB_PATH.bak"
  printf 'UUID=%s %s ext4 defaults,nofail,x-systemd.device-timeout=2min 0 2\n' \
    "$filesystem_uuid" "$MOUNT_PATH" >>"$FSTAB_PATH"
  mountpoint -q "$MOUNT_PHYSICAL" || mount "$MOUNT_PHYSICAL"
  [[ "$(findmnt -n -o FSTYPE "$MOUNT_PHYSICAL")" == "ext4" ]] || fail "workspace mount read-back failed"
  if [[ "$TEST_MODE" != "1" ]]; then
    chown "$ADMIN_USER:$ADMIN_USER" "$MOUNT_PHYSICAL"
  fi
  chmod 0770 "$MOUNT_PHYSICAL"
}

configure_runtime_files() {
  local admin_home_logical
  admin_home_logical="/home/$ADMIN_USER"
  write_if_changed 0644 "$(root_path /etc/systemd/system/codex-remote-control-bootstrap.service)" <<EOF
[Unit]
Description=Bootstrap the managed Codex Remote Control daemon after boot
Wants=network-online.target
After=network-online.target
RequiresMountsFor=$MOUNT_PATH
ConditionFileIsExecutable=$admin_home_logical/.codex/packages/standalone/current/codex

[Service]
Type=oneshot
KillMode=process
User=$ADMIN_USER
Group=$ADMIN_USER
Environment=HOME=$admin_home_logical
Environment=CODEX_HOME=$admin_home_logical/.codex
ExecStart=$admin_home_logical/.codex/packages/standalone/current/codex app-server daemon bootstrap --remote-control
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

  write_if_changed 0644 "$(root_path /etc/systemd/system/codex-remote-control-health.service)" <<EOF
[Unit]
Description=Ensure the managed Codex Remote Control daemon is ready
Wants=network-online.target
After=network-online.target codex-remote-control-bootstrap.service
RequiresMountsFor=$MOUNT_PATH
ConditionFileIsExecutable=$admin_home_logical/.codex/packages/standalone/current/codex

[Service]
Type=oneshot
KillMode=process
User=$ADMIN_USER
Group=$ADMIN_USER
Environment=HOME=$admin_home_logical
Environment=CODEX_HOME=$admin_home_logical/.codex
ExecStart=/usr/local/sbin/ensure-codex-remote-control
TimeoutStartSec=240
EOF

  write_if_changed 0644 "$(root_path /etc/systemd/system/codex-remote-control-health.timer)" <<'EOF'
[Unit]
Description=Check the managed Codex Remote Control daemon every minute

[Timer]
OnBootSec=2min
OnUnitInactiveSec=1min
Persistent=true
RandomizedDelaySec=10s
Unit=codex-remote-control-health.service

[Install]
WantedBy=timers.target
EOF

  write_if_changed 0644 "$(root_path /etc/ssh/sshd_config.d/60-codex-hardening.conf)" <<EOF
PubkeyAuthentication yes
AuthenticationMethods publickey
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitEmptyPasswords no
PermitRootLogin no
AllowUsers $ADMIN_USER
MaxAuthTries 3
LoginGraceTime 30
MaxStartups 10:30:60
X11Forwarding no
GatewayPorts no
PermitTunnel no
AllowTcpForwarding local
EOF

  write_if_changed 0644 "$(root_path /etc/fail2ban/jail.d/sshd.local)" <<'EOF'
[sshd]
enabled = true
backend = systemd
port = 22
maxretry = 5
findtime = 10m
bantime = 1h
EOF
}

run_as_admin() {
  if [[ "$TEST_MODE" == "1" ]]; then
    "$@"
  else
    runuser -u "$ADMIN_USER" -- "$@"
  fi
}

install_codex() {
  local home_helper installer fetcher managed_codex
  home_helper="$(root_path /usr/local/sbin/prepare-persistent-codex-home)"
  installer="$(root_path /usr/local/sbin/install-verified-codex)"
  fetcher="$(root_path /usr/local/sbin/fetch-verified-artifact)"
  ADMIN_HOME_PHYSICAL="$(root_path "/home/$ADMIN_USER")"
  install_owned_dir 0700 "$ADMIN_HOME_PHYSICAL"
  ADMIN_CODEX_HOME="$(CODEX_VM_TEST_MODE="$TEST_MODE" "$home_helper" "$ADMIN_USER" "$ADMIN_HOME_PHYSICAL" "$MOUNT_PHYSICAL")"
  ADMIN_BIN_DIR="$MOUNT_PHYSICAL/.local/bin"
  install_owned_dir 0755 "$MOUNT_PHYSICAL/.local"
  install_owned_dir 0755 "$ADMIN_BIN_DIR"

  run_as_admin env HOME="$ADMIN_HOME_PHYSICAL" CODEX_HOME="$ADMIN_CODEX_HOME" \
    "$installer" "$CODEX_PACKAGE_URL" "$CODEX_PACKAGE_SHA256" "$CODEX_VERSION" \
    "$ADMIN_CODEX_HOME" "$ADMIN_BIN_DIR" "$fetcher"
  managed_codex="$ADMIN_CODEX_HOME/packages/standalone/current/codex"
  [[ -x "$managed_codex" ]] || fail "managed Codex executable is missing"
  [[ "$(run_as_admin "$managed_codex" --version | awk '{print $NF}')" == "$CODEX_VERSION" ]] ||
    fail "managed Codex version read-back failed"

  install -d -m 0755 "$(root_path /usr/local/bin)"
  ln -sfn "$ADMIN_BIN_DIR/codex" "$(root_path /usr/local/bin/codex)"
  [[ "$(run_as_admin "$(root_path /usr/local/bin/codex)" --version | awk '{print $NF}')" == "$CODEX_VERSION" ]] ||
    fail "published Codex version read-back failed"

  if ! run_as_admin env HOME="$ADMIN_HOME_PHYSICAL" CODEX_HOME="$ADMIN_CODEX_HOME" \
    "$managed_codex" app-server daemon bootstrap --remote-control; then
    run_as_admin env HOME="$ADMIN_HOME_PHYSICAL" CODEX_HOME="$ADMIN_CODEX_HOME" \
      "$managed_codex" app-server daemon bootstrap
  fi
}

finish_preparation() {
  local marker host_key_file host_key managed_codex attempt health_ready
  systemctl daemon-reload
  systemctl enable codex-remote-control-bootstrap.service codex-remote-control-health.timer
  systemctl enable --now fail2ban unattended-upgrades
  systemctl start codex-remote-control-health.timer
  managed_codex="$ADMIN_CODEX_HOME/packages/standalone/current/codex"
  if run_as_admin env HOME="$ADMIN_HOME_PHYSICAL" CODEX_HOME="$ADMIN_CODEX_HOME" \
    "$managed_codex" login status >/dev/null 2>&1; then
    systemctl start codex-remote-control-bootstrap.service
    health_ready=0
    for attempt in 1 2 3 4 5; do
      if systemctl start codex-remote-control-health.service; then
        health_ready=1
        break
      fi
      ((attempt == 5)) || sleep 5
    done
    ((health_ready == 1)) ||
      fail "Remote Control did not become connected after authenticated systemd activation"
  fi
  install -d -m 0755 "$(root_path /run/sshd)"
  sshd -t
  if systemctl is-active --quiet ssh; then
    systemctl reload ssh
  elif systemctl is-active --quiet ssh.socket; then
    :
  else
    systemctl enable --now ssh
  fi

  marker="$(root_path /var/lib/codex-on-vm/prepared)"
  install -d -m 0755 "$(dirname "$marker")"
  printf 'codex_version=%s\nworkspace_mount=%s\ntelegram_to_agents_prerequisites=1\n' \
    "$CODEX_VERSION" "$MOUNT_PATH" >"$marker"

  host_key_file="$(root_path /etc/ssh/ssh_host_ed25519_key.pub)"
  [[ -f "$host_key_file" ]] || ssh-keygen -A
  host_key="$(awk 'NF >= 2 && $1 == "ssh-ed25519" { print $1 " " $2; found = 1; exit } END { if (!found) exit 1 }' "$host_key_file")"
  printf 'CODEX_ON_VM_PREPARED=1\n'
  printf 'SSH_HOST_PUBLIC_KEY=%s\n' "$host_key"
}

[[ -n "$ADMIN_USER" && "$ADMIN_USER" =~ ^[a-z_][a-z0-9_-]{0,31}$ ]] || fail "admin user is invalid"
[[ "$MOUNT_PATH" == /* ]] || fail "projects mount must be absolute"
[[ "$DISK_LUN" =~ ^[0-9]+$ ]] || fail "disk LUN must be a non-negative integer"
[[ "$CODEX_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail "Codex version must use x.y.z format"
[[ "$CODEX_PACKAGE_URL" == https://* ]] || fail "Codex package URL must use HTTPS"
[[ "$CODEX_PACKAGE_SHA256" =~ ^[0-9a-f]{64}$ ]] || fail "Codex package digest is invalid"
[[ "$OPENVPN_PORT" =~ ^[0-9]+$ ]] || fail "OpenVPN port is invalid"
[[ "$OPENVPN_NETWORK" =~ ^[0-9.]+$ ]] || fail "OpenVPN network is invalid"
[[ "$OPENVPN_NETMASK" =~ ^[0-9.]+$ ]] || fail "OpenVPN netmask is invalid"
[[ "$OPENVPN_SERVER_ADDRESS" =~ ^[0-9.]+$ ]] || fail "OpenVPN server address is invalid"
[[ -z "$VM_ROOT" || "$TEST_MODE" == "1" ]] || fail "CODEX_VM_ROOT is available only in test mode"

install_packages
configure_apparmor
prepare_workspace_disk
restore_openvpn
configure_runtime_files
install_codex
finish_preparation
__CODEX_VM_HELPER_END__ prepare-codex-vm.sh

__CODEX_VM_HELPER_BEGIN__ prepare-persistent-codex-home.sh
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  printf 'usage: %s <admin-user> <admin-home> <projects-mount>\n' "$0" >&2
  exit 64
fi

ADMIN_USER="$1"
ADMIN_HOME="$2"
MOUNT_PATH="$3"
CODEX_LINK="$ADMIN_HOME/.codex"
PERSISTENT_CODEX_HOME="$MOUNT_PATH/.codex"
DOT_CODEX_HOME="$MOUNT_PATH/dot-codex"

fail() {
  printf 'persistent Codex home preparation failed: %s\n' "$1" >&2
  exit 1
}

[[ -n "$ADMIN_USER" ]] || fail "admin user is empty"
[[ "$ADMIN_HOME" == /* && -d "$ADMIN_HOME" ]] || fail "admin home is unavailable: $ADMIN_HOME"
[[ "$MOUNT_PATH" == /* && -d "$MOUNT_PATH" ]] || fail "projects mount is unavailable: $MOUNT_PATH"
TEST_MODE="${CODEX_VM_TEST_MODE:-0}"
if [[ "$TEST_MODE" == "1" ]]; then
  ADMIN_GROUP="$(id -gn)"
else
  ADMIN_GROUP="$(id -gn "$ADMIN_USER")" || fail "admin user is unavailable: $ADMIN_USER"
fi

if [[ -d "$DOT_CODEX_HOME" && ! -L "$DOT_CODEX_HOME" && -d "$DOT_CODEX_HOME/.git" ]]; then
  ADMIN_CODEX_HOME="$DOT_CODEX_HOME"
else
  ADMIN_CODEX_HOME="$PERSISTENT_CODEX_HOME"
  if [[ -e "$ADMIN_CODEX_HOME" || -L "$ADMIN_CODEX_HOME" ]]; then
    [[ -d "$ADMIN_CODEX_HOME" && ! -L "$ADMIN_CODEX_HOME" ]] ||
      fail "persistent Codex home is not a real directory: $ADMIN_CODEX_HOME"
  fi
fi

if [[ -L "$CODEX_LINK" ]]; then
  EXISTING_TARGET="$(readlink -f "$CODEX_LINK")" ||
    fail "existing Codex link has no resolvable target: $CODEX_LINK"
  SELECTED_TARGET="$(readlink -f "$ADMIN_CODEX_HOME")" ||
    fail "selected Codex home is unavailable: $ADMIN_CODEX_HOME"
  [[ "$EXISTING_TARGET" == "$SELECTED_TARGET" ]] ||
    fail "existing Codex link resolves to $EXISTING_TARGET, expected $SELECTED_TARGET"
elif [[ -e "$CODEX_LINK" ]]; then
  fail "refusing to overwrite the real Codex home at $CODEX_LINK"
fi

if [[ "$TEST_MODE" == "1" ]]; then
  install -d -m 0700 "$ADMIN_CODEX_HOME"
else
  install -d -o "$ADMIN_USER" -g "$ADMIN_GROUP" -m 0700 "$ADMIN_CODEX_HOME"
fi
if [[ ! -L "$CODEX_LINK" ]]; then
  ln -s -- "$ADMIN_CODEX_HOME" "$CODEX_LINK"
  if [[ "$TEST_MODE" != "1" ]]; then
    chown -h "$ADMIN_USER:$ADMIN_GROUP" "$CODEX_LINK"
  fi
fi

printf '%s\n' "$ADMIN_CODEX_HOME"
__CODEX_VM_HELPER_END__ prepare-persistent-codex-home.sh
