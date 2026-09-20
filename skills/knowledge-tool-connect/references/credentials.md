# Token intake and storage

First reuse the selected connection's existing credential. Otherwise ask whether the user has a token; if not, guide generation using the selected provider reference. Check operation support first. Offer “Puoi incollare qui il token oppure indicarmi una variabile d’ambiente o un file privato.” Chat input is supported when the user chooses it; briefly explain that the pasted value remains in conversation history. Do not refuse it or demand rotation merely because it was pasted.

## Token supplied in chat

Treat a token supplied during explicitly requested setup as authorized for that selected connection, not unrelated use. Never quote or repeat it, including partial values, in replies, receipts or errors. Default storage is the selected profile's `token` field in `${CODEX_HOME:-$HOME/.codex}/knowledge.toml`: plaintext, owner-only (0600), ignored and never committed. Use `knowledge_profile.py credentials NAME --token-stdin` with suitable secret-input/stdin tooling, or a structured private write facility with restrictive permissions established before writing. Never interpolate the value into shell commands/arguments or request payload artifacts. Existing environment/file references remain optional alternatives. Do not read unrelated credential stores.

For an existing selected reference, `credentials NAME --import-current` saves its value inline without printing it or deleting the source file. It preserves auth type and all other profile/default/transport settings. Public configuration commands redact tokens; do not feed the redacted placeholder back into configuration. Config files containing inline tokens must be owner-owned regular files with no group/world access; symlinks and special files are rejected.

For entry in the user's own interactive terminal, substitute the chosen profile name and run:

    python3 -c 'import getpass,sys; sys.stdout.write(getpass.getpass("API token (hidden): "))' | "${CODEX_HOME:-$HOME/.codex}/skills/knowledge-tool-connect/scripts/knowledge_profile.py" credentials PROFILE --token-stdin

The hidden input is piped directly to the configuration command; the command only prints redacted results. Do not run this interactive prompt through an agent tool.
If suitable storage/input tooling or filesystem permission is unavailable, say exactly what is missing and offer the private-terminal procedure below. Do not claim the token was stored/verified when it was not; do not ask the user to paste it again. Never promise to erase conversation history. No token input frontend or OAuth enrollment is implemented by the API clients themselves.

## Environment variable or private file

Offer an existing environment variable visible to the agent process, or a persistent private file outside the repository. A variable exported in another terminal may not be visible here. When helping a macOS/Linux user save a new token, offer this procedure for **their own interactive terminal**, adapting the non-secret filename to the selected account. Do not run the interactive secret prompt through an agent tool.

    python3 -c 'import getpass, os; from pathlib import Path; p=Path.home()/".config"/"knowledge-tokens"/"clickup-work"; p.parent.mkdir(parents=True,exist_ok=True,mode=0o700); token=getpass.getpass("API token (hidden): ").strip(); assert token and len(token)<=16384 and all(33<=ord(c)<=126 for c in token), "Invalid token"; fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600); f=os.fdopen(fd,"w"); f.write(token); f.close(); print("Saved token file:",p)'

This creates an owner-only file and refuses to overwrite an existing one. The token is hidden during entry and absent from shell history. For this terminal route, ask for the printed path; do not request a second copy of the token. If the file already exists, verify/use its reference or choose an account-specific path; never overwrite or rotate a credential implicitly. The API loader rejects symlinks, files owned by another user and group/world-accessible files. Do not search unrelated token stores.

For first-use discovery, use the private file or environment reference, create the verified profile, then use `credentials NAME --import-current` to store inline. Keep a reference only when the user prefers it; see [setup](setup.md). Discovery/check verifies actual account/workspace before content access. Missing credentials should produce actionable private setup guidance, not repeated demands for an already configured reference. These clients consume existing credentials; they do not implement OAuth login or provision provider tokens.
