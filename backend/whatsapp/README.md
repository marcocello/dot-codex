# Optional WhatsApp bot

This is the Baileys and Python live bot imported from `whatsapp-bot`. Searchable WhatsApp history is collected through wacli in `backend/context`. This component remains a separately enabled bot policy.

From the checkout root:

```bash
./secondbrain.sh setup --component whatsapp
./secondbrain.sh whatsapp --plan
./secondbrain.sh whatsapp
```

Automatic replies are disabled by default. To enable the retained Python greeting explicitly, run `./secondbrain.sh whatsapp --enable-replies`. It replies to new incoming personal/group messages with `🤖 hey I am the AI assistant of Marco`. The default policy ignores own messages. A send event does not establish delivery or a read receipt.

The wrapper defaults credentials to `~/projects/.secondbrain/baileys`. Override `WHATSAPP_AUTH_DIR` for another private session. Direct `npm start` uses `XDG_STATE_HOME/dot-codex/whatsapp`, falling back to `~/.local/state/dot-codex/whatsapp`. Keep one listener per auth directory. First startup displays a QR for WhatsApp's Linked devices screen. Pairing requires the account owner's phone. Credentials are separate from wacli.

Node.js 24 and Python 3.10+ are required. Component-local operation is also available:

```bash
cd backend/whatsapp
npm ci
npm run check
npm start
# Explicit direct enablement:
WHATSAPP_AUTO_REPLY=1 npm start
```

Set `WHATSAPP_PYTHON` to select an interpreter. The Python worker receives normalized text/captions, message content, identifiers, and direction. It returns `reply` or `ignore`; Node owns transport and sends. Decisions have a five-second timeout. Failed or uncertain sends are not replayed automatically. Worker restart and reconnect preserve the original behavior.

Terminal events contain metadata only. The listener filters history, status/channel updates, protocol housekeeping, and process-local duplicates. It does not persist history or download media. Restart can expose a repeated notification because deduplication is bounded and process-local. Production credential storage and a durable bot queue remain outside this retained development component.

`npm run check` verifies TypeScript and dependencies without connecting. Live pairing and receipt require account-owner verification. See the [platform guide](../../docs/harness/secondbrain-platform.md).
