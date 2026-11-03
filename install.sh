#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
case "${1:-}" in
  --print-env) printf 'export CODEX_HOME=%q\n' "$root"; exit 0 ;;
  --help|-h)
    printf '%s\n' 'Usage: ./install.sh [--print-env]' \
      'Link this checkout to ~/.codex and expose its skills. No downloads or account setup.' \
      'Existing unrelated directories and configuration are preserved.' \
      'For the current shell: eval "$(./install.sh --print-env)"'
    exit 0 ;;
  '') ;;
  *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
esac
if (( $# > 0 )); then printf '%s\n' 'Unexpected arguments.' >&2; exit 2; fi
fail() { printf '%s\n' "$*" >&2; exit 1; }
same_directory() { [[ -d "$1" ]] && [[ "$(cd -- "$1" && pwd -P)" == "$2" ]]; }
home_link="$HOME/.codex"
skills="$HOME/.agents/skills"
[[ -d "$root/skills" && -f "$root/config.template.toml" ]] || fail 'Incomplete coding checkout.'
if [[ -e "$home_link" || -L "$home_link" ]]; then
  same_directory "$home_link" "$root" || fail 'Existing ~/.codex points elsewhere. Preserve it and choose its migration explicitly.'
fi
# Preflight skill conflicts before creating the home link or configuration.
if [[ -e "$skills" || -L "$skills" ]]; then
  [[ -d "$skills" ]] || fail 'Existing ~/.agents/skills is not an available directory.'
  if ! same_directory "$skills" "$root/skills"; then
    for definition in "$root"/skills/*/SKILL.md; do
      [[ -f "$definition" ]] || continue
      source="${definition%/SKILL.md}"
      destination="$skills/${source##*/}"
      if [[ -e "$destination" || -L "$destination" ]]; then
        same_directory "$destination" "$source" || fail "Existing skill preserved: $destination"
      fi
    done
  fi
fi
if [[ ! -e "$home_link" && ! -L "$home_link" ]]; then ln -s "$root" "$home_link"; fi
if [[ ! -e "$root/config.toml" && ! -L "$root/config.toml" ]]; then
  (umask 077; cp "$root/config.template.toml" "$root/config.toml")
fi
if [[ ! -e "$skills" && ! -L "$skills" ]]; then
  mkdir -p "$HOME/.agents"
  ln -s "$root/skills" "$skills"
elif ! same_directory "$skills" "$root/skills"; then
  for definition in "$root"/skills/*/SKILL.md; do
    [[ -f "$definition" ]] || continue
    source="${definition%/SKILL.md}"
    destination="$skills/${source##*/}"
    if [[ ! -e "$destination" && ! -L "$destination" ]]; then ln -s "$source" "$destination"; fi
  done
fi
printf 'Coding harness ready: %s\n' "$root"
printf '%s\n' 'Codex uses ~/.codex by default. Optional current-shell export: eval "$(./install.sh --print-env)"'
