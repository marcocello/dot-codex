#!/usr/bin/env bash
# Definitions only: secondbrain.sh owns execution and strict shell mode.
# Inspired by OpenClaw's installer structure; provider reconciliation stays in Python.

sb_error() {
    printf 'Setup: %s\n' "$*" >&2
}

sb_help() {
    cat <<'HELP'
Secondbrain setup — Ubuntu VM or macOS → Azure

  ./secondbrain.sh setup [options]       Complete installation and onboarding
  ./install.sh setup [options]           Equivalent entry
  ./secondbrain.sh                       Open the same wizard

  --mode host|azure        Target (default: host on Linux, azure on macOS)
  --plan, --dry-run         Show the complete plan without making changes
  --config PATH            Existing JSON choices; credentials stay in private files
  --state PATH             Private state (default: ~/projects/.secondbrain)
  --non-interactive,
  --no-prompt              Use saved choices/authentication; never approve cloud costs
  --reconfigure            Review choices and existing connections
  --component NAME         Dependencies only: core, context, telegram, whatsapp, all
  -h, --help               Show this help without requiring Python

Setup reuses Python 3.11–3.13, or installs it with Ubuntu apt / existing Homebrew.
Interactive setup needs a terminal. Unattended setup needs existing choices and logins.
Rerun the same command to recheck resources and resume incomplete work.

Other commands: install, vm, codex, context, telegram, whatsapp, doctor.
Existing ./install.sh harness arguments retain their meaning.
HELP
}

sb_find_python() {
    local candidate
    for candidate in python3 python3.12 python3.13 python3.11; do
        if command -v "$candidate" >/dev/null 2>&1 &&
            "$candidate" -c 'import sys; raise SystemExit(not ((3, 11) <= sys.version_info[:2] < (3, 14)))' >/dev/null 2>&1; then
            SB_PYTHON="$(command -v "$candidate")"
            return 0
        fi
    done
    return 1
}

sb_has_tty() {
    { : </dev/tty; } 2>/dev/null && { : >/dev/tty; } 2>/dev/null
}

sb_bootstrap_python() {
    local os_name="$1" unattended="$2" os_release brew_path prefix
    local -a privilege=()
    printf '\n[bootstrap] Installing compatible Python\n'
    case "$os_name" in
        Linux)
            os_release="$(cat /etc/os-release 2>/dev/null || true)"
            case $'\n'"$os_release"$'\n' in
                *$'\nID=ubuntu\n'*|*$'\nID="ubuntu"\n'*) ;;
                *) sb_error 'Automatic Python bootstrap supports Ubuntu 24.04. Install Python 3.11–3.13 and repeat setup.'; return 2 ;;
            esac
            case $'\n'"$os_release"$'\n' in
                *$'\nVERSION_ID="24.04"\n'*|*$'\nVERSION_ID=24.04\n'*) ;;
                *) sb_error 'Automatic Python bootstrap supports Ubuntu 24.04. Install Python 3.11–3.13 and repeat setup.'; return 2 ;;
            esac
            if [[ $EUID -ne 0 ]]; then
                command -v sudo >/dev/null 2>&1 || { sb_error 'Python bootstrap needs sudo. Install Python 3.11–3.13 and repeat setup.'; return 2; }
                privilege=(sudo)
                [[ $unattended != 1 ]] || privilege+=(-n)
            fi
            "${privilege[@]}" apt-get update || return $?
            "${privilege[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-venv ca-certificates || return $?
            ;;
        Darwin)
            brew_path="$(command -v brew || true)"
            if [[ -z $brew_path ]]; then
                sb_error 'Python bootstrap needs Homebrew on this Mac. Install it from https://brew.sh or provide Python 3.11–3.13, then repeat setup.'
                return 2
            fi
            HOMEBREW_NO_AUTO_UPDATE=1 NONINTERACTIVE=1 "$brew_path" install python@3.12 || return $?
            prefix="$("$brew_path" --prefix python@3.12)" || return $?
            export PATH="$prefix/bin:$PATH"
            ;;
        *) sb_error 'Python bootstrap supports Ubuntu 24.04 and macOS. Install Python 3.11–3.13 and repeat setup.'; return 2 ;;
    esac
    sb_find_python || { sb_error 'Python installation did not produce a compatible interpreter. Check PATH and repeat setup.'; return 2; }
    printf '[bootstrap] Python verified\n'
}

secondbrain_main() {
    local root="$1" operation="${2:-setup}"
    shift
    [[ $# == 0 ]] || shift
    if [[ $operation == --help || $operation == -h ]]; then
        sb_help
        return 0
    fi
    if [[ $operation != setup ]]; then
        # Other commands do not install prerequisites.
        command -v python3 >/dev/null 2>&1 || { sb_error 'Python is missing. Run ./secondbrain.sh setup first.'; return 2; }
        exec python3 "$root/scripts/secondbrain_platform.py" "$operation" "$@"
    fi

    local dry=0 unattended=0 help=0 mode="" component="" config="" state="${SECOND_BRAIN_STATE:-$HOME/projects/.secondbrain}"
    local key value os_name line bootstrap_status
    # Bash 3.2 treats an empty array as unset under nounset; keep the command here.
    local -a forwarded=(setup)
    while [[ $# -gt 0 ]]; do
        key="${1%%=*}"
        case "$key" in
            --plan|--dry-run) dry=1; forwarded+=(--plan) ;;
            --no-prompt|--non-interactive) unattended=1; forwarded+=(--non-interactive) ;;
            --reconfigure) forwarded+=(--reconfigure) ;;
            --help|-h) help=1 ;;
            --mode|--component|--config|--state)
                if [[ $1 == *=* ]]; then value="${1#*=}"; else
                    [[ $# -gt 1 && $2 != --* && -n $2 ]] || { sb_error "Missing value for $key. See ./secondbrain.sh setup --help"; return 2; }
                    shift
                    value="$1"
                fi
                [[ -n $value ]] || { sb_error "Missing value for $key"; return 2; }
                case "$key" in
                    --mode) mode="$value" ;;
                    --component) component="$value" ;;
                    --config) config="$value" ;;
                    --state) state="$value" ;;
                esac
                forwarded+=("$key" "$value")
                ;;
            *) sb_error "Unknown setup option: $key. See ./secondbrain.sh setup --help"; return 2 ;;
        esac
        if [[ $key != --mode && $key != --component && $key != --config && $key != --state && $1 == *=* ]]; then
            sb_error "Option $key does not accept a value"
            return 2
        fi
        shift
    done
    [[ -z $mode || $mode == host || $mode == azure ]] || { sb_error '--mode must be host or azure'; return 2; }
    case "$component" in ''|core|context|telegram|whatsapp|all) ;; *) sb_error 'Invalid --component'; return 2 ;; esac
    if [[ -n $component ]]; then
        for key in "${forwarded[@]}"; do
            case "$key" in --mode|--config|--state|--reconfigure)
                sb_error "$key is available only for complete setup; omit --component"
                return 2 ;;
            esac
        done
    fi
    if [[ $help == 1 ]]; then sb_help; return 0; fi

    os_name="$(uname -s)"
    if [[ -z $mode ]]; then
        if [[ $os_name == Darwin ]]; then mode=azure; else mode=host; fi
    fi
    export PYTHONDONTWRITEBYTECODE=1
    if [[ $dry == 1 && -z $component ]]; then
        printf 'Secondbrain setup: %s\nBootstrap: reuse Python 3.11–3.13 or install through apt / existing Homebrew\n\n' "$mode"
        if [[ $mode == azure ]]; then
            printf '%s\n' 'Mac prerequisites → Azure login/subscription → state storage → Terraform plan/approval/apply' \
                'Azure agent: persistent disk + pinned Codex + SSH host trust → protected VPN bootstrap' \
                'Connect the generated VPN profile → verified SSH → the same host setup'
        fi
        while IFS= read -r line || [[ -n $line ]]; do printf '%s\n' "$line"; done < "$root/scripts/setup-plan.txt"
        printf '\nDry run complete; no changes made.\n'
        return 0
    fi

    # Decide prompt authority before package installation or state creation.
    if [[ $dry != 1 && -z $component ]]; then
        if [[ $unattended == 1 ]]; then
            case "$state" in '~') state="$HOME" ;; '~/'*) state="$HOME/${state:2}" ;; esac
            [[ -n $config ]] || config="$state/setup.json"
            case "$config" in '~') config="$HOME" ;; '~/'*) config="$HOME/${config:2}" ;; esac
            [[ -f $config ]] || { sb_error 'Unattended setup needs an existing --config or saved setup.json. Run interactive setup first.'; return 2; }
        elif [[ ! -t 0 ]]; then
            sb_has_tty || { sb_error 'No interactive terminal. Run setup in a terminal, or use --no-prompt --config PATH with existing choices and logins.'; return 2; }
            exec </dev/tty
        fi
    fi
    if [[ $unattended == 1 ]]; then
        export SECOND_BRAIN_NO_PROMPT=1
        exec </dev/null
    fi
    if ! sb_find_python; then
        if [[ $dry == 1 ]]; then
            printf 'Dependency-only setup: bootstrap Python 3.11–3.13\n'
            case "$component" in core|all|context) printf '%s\n' 'Install backend/context in .venv' ;; esac
            case "$component" in core|all|telegram) printf '%s\n' 'Install backend/telegram in .venv' ;; esac
            case "$component" in all|whatsapp) printf '%s\n' 'Run npm ci in backend/whatsapp' ;; esac
            return 0
        fi
        trap 'sb_error "Python bootstrap interrupted. Repeat the same command to resume."; exit 130' INT
        trap 'sb_error "Python bootstrap terminated. Repeat the same command to resume."; exit 143' TERM
        if sb_bootstrap_python "$os_name" "$unattended"; then :; else
            bootstrap_status=$?
            sb_error "Python bootstrap failed (exit $bootstrap_status). Resolve the package-manager error and repeat the same setup command."
            return "$bootstrap_status"
        fi
        trap - INT TERM
    fi
    printf '\nSecondbrain setup\n[bootstrap] Compatible Python ready\n'
    exec "$SB_PYTHON" "$root/scripts/secondbrain_platform.py" "${forwarded[@]}"
}
