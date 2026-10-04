# Interactive checks

For a web app, prefer the available browser tools or its existing browser test runner. Open the actual served app, perform the user's action, and inspect the visible result and persisted state. Check the important failure path and a narrow viewport when relevant. A successful HTTP request or screenshot alone does not prove an interaction. Use stable labels or roles, wait for observable state, and preserve a failed draft when testing recovery.

For a CLI, run the built or installed command from a temporary working directory. Check a real operation and its output or saved effect, not only `--help`. This catches accidental dependencies on the source checkout.

For a TUI, use an available PTY or a private tmux socket. If tmux is installed, this pattern isolates the test terminal; substitute the actual authorized application command:

```sh
check_dir="$(mktemp -d)"
tmux -S "$check_dir/socket" new-session -d -s app -x 100 -y 30 -c /path/to/test-workspace
tmux -S "$check_dir/socket" send-keys -t app -l '/absolute/path/to/application'
tmux -S "$check_dir/socket" send-keys -t app Enter
tmux -S "$check_dir/socket" capture-pane -t app -p
```

Wait for readiness, exercise the relevant input, and capture the resulting screen. Startup is not proof that the interaction completed. Limit waits, check the actual exit or response, and distinguish a model/API call from a local interface check. Stop only the session you created with `tmux -S "$check_dir/socket" kill-server` when finished. Never send keys to a user's existing terminal or kill a shared tmux server.
