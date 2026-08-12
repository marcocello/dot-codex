---
name: launch-photo-drop
description: Launch and manage a temporary mobile-friendly event photo and video portal with shareable ngrok URLs, QR access, original-quality host storage, live status, and graceful shutdown.
---

# Launch Photo Drop

Use the bundled application in `assets/app`. Never scaffold or rewrite an application when invoking this skill.

## Bundled runtime contract

- Every start invocation boots the backend and the prebuilt frontend together from this skill's `assets/app`; do not generate code, select another frontend, or start a separate development server.
- The backend serves the bundled original Photo Drop frontend at the public guest URL and the bundled host dashboard at the loopback-only admin URL.
- Guests always receive the warm, card-based Photo Drop upload UI bundled with this skill: deep-green type and action, coral accent, one prominent multi-file picker, localized upload states, and a live shared gallery of completed event photos. Do not substitute the fluorescent Shared Album reference UI. Their browser resolves English, Italian, Spanish, French, German, or Portuguese from `navigator.languages`, with English fallback.
- Device-language selection happens inside the bundled frontend on each guest device. Codex does not choose or translate the portal language when starting an event.

## Start an event

1. Resolve this skill directory and use its `scripts/` paths absolutely.
2. Check for an existing event:

   ```bash
   python3 <skill-dir>/scripts/status_event.py
   ```

   If it is active, return its URLs and destination. Do not replace it silently. If its session is ended, `start_event.py` safely retires the old process before starting another event.
3. Resolve event settings:
   - Derive a concise human event title from the request. Exclude the skill invocation, start/launch wording, duration, destination/provider details, and generic `photo drop` wording.
   - Preserve meaningful names and punctuation, normalize spacing around `&`, and apply obvious human capitalization. Example: `Use $launch-photo-drop to start a 6-hour Rob&mary wedding photo drop` becomes `Rob & Mary Wedding`.
   - If no meaningful event phrase remains, use `Photo Drop`. Do not invent people, places, or an event type.
   - Use the destination supplied by the user.
   - If absent, default to `~/Pictures/Photo Drop/<YYYY-MM-DD-HHMM>` and tell the user the exact path before starting.
   - Default to 12 hours unless the user specifies a duration.
   - Honor quota or free-space-reserve requests through the start script flags.
4. Check ngrok authentication before launching:
   - The skill uses only the official ngrok Python SDK; it does not require or discover an ngrok executable.
   - This requires the agent authtoken shown in the ngrok dashboard, not the REST API key. First check all supported sources without revealing the value:

     ```bash
     python3 <skill-dir>/scripts/configure_ngrok.py --check
     ```

   - The check reports `environment`, `photo_drop`, or `ngrok_config`. Reuse a standard installed ngrok credential automatically; do not ask the user to configure a duplicate. The resolver recognizes ngrok's standard macOS, Linux, and Windows v2/v3 config locations without invoking the ngrok executable, and never copies or changes that config.
   - Only if the check reports missing, guide the user to open `https://dashboard.ngrok.com/get-started/your-authtoken`, copy the agent authtoken, and run this exact command in a terminal they control:

     ```bash
     python3 <skill-dir>/scripts/configure_ngrok.py
     ```

     The helper uses a hidden prompt and stores the token under the private Codex state directory with owner-only permissions. Never ask the user to paste the secret into chat, pass it on a command line, or show it in tool output. Pause the launch until the user confirms configuration is complete, then rerun `--check` and continue.
   - Precedence is inherited `NGROK_AUTHTOKEN`, Photo Drop's private credential, then standard installed-ngrok config. Do not edit shell startup files automatically.
   - To remove the Photo Drop-owned credential when the user requests it, run `python3 <skill-dir>/scripts/configure_ngrok.py --delete`. Never delete or rewrite the installed ngrok config.
   - Do not use the proof tunnel fake for a real event.
5. Prepare the isolated runtime:

   ```bash
   python3 <skill-dir>/scripts/setup_runtime.py
   ```

   This is idempotent and also runs automatically inside `start_event.py`. It creates or repairs a venv under `${CODEX_HOME:-~/.codex}/state/launch-photo-drop`, installs only the bundled declared Python packages with that venv's pip, and verifies FastAPI, Uvicorn, and the ngrok SDK. It never performs a global install or invokes a system package manager. Python 3.12 or newer with `venv` support is the host prerequisite.
6. A direct request to start or launch an event authorizes creation of its temporary public tunnel. For preparatory requests, do not publish until the user explicitly asks to start.
7. Start the event:

   ```bash
   python3 <skill-dir>/scripts/start_event.py \
     --destination <absolute-folder> \
     --event-name "<derived-title>" \
     --ttl-hours <hours>
   ```

   The script creates the destination when needed, starts the bundled service in a managed background process, waits for full readiness, and prints one JSON result.
8. Return these fields prominently:
   - `guest_url`: share this with guests; it contains the upload page and QR destination.
   - `admin_url`: open only on the host laptop to see the QR, activity, totals, and stop control.
   - `destination`: finalized originals arrive here.
   - `event_name`: the title shown on the host dashboard and guest upload page.
   - `expires_at` and `provider`.
   Remind the user to keep the laptop awake and connected while collecting uploads.

Never describe the local admin URL as public. Never expose application state, generated storage names, or local paths to guests.

## Check an event

Run:

```bash
python3 <skill-dir>/scripts/status_event.py
```

Report whether the process and session are active, stopping, or ended, plus the existing URLs and destination. Do not start a replacement unless requested.

## Stop an event

Run:

```bash
python3 <skill-dir>/scripts/stop_event.py
```

This sends a graceful shutdown to the recorded Photo Drop process so the public tunnel is disabled before the listeners exit. Report the retained destination. Never signal an unrelated PID or delete uploaded media.

## Operational behavior

- The backend uses the ngrok Python SDK to expose only the loopback guest listener and closes its listener handle on stop. The host admin listener remains local.
- The backend listens separately for public guest uploads and loopback-only administration.
- The bundled guest portal uses the original Photo Drop mobile design and resolves English, Italian, Spanish, French, German, or Portuguese from the device language, falling back to English.
- Files stream directly to the chosen destination without resizing or recompression.
- Finalized files keep their sanitized original basename; collisions insert `_001`, `_002`, and later suffixes before the extension without overwriting existing host files.
- Everyone with the active event URL can view completed image uploads in the shared gallery. The gallery never lists videos, filenames, host paths, pre-existing folder files, other sessions, partial uploads, or failed uploads, and closes with the event.
- Runtime metadata, logs, and the venv live outside the skill under the Codex state directory; uploaded media never does.
