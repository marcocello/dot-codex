# Runtime consolidation proof

Run `proof/run.sh` from this checkout. The local Python test starts the public platform CLI in subprocesses. It verifies the setup plan without creating a virtual environment or invoking providers, reads VM help, extracts and syntax-checks every embedded helper, checks the bundled Telegram package entry point and native gateway regressions, and checks optional bot configuration. Provider commands are not executed against Azure or WhatsApp.

The VM bootstrap test executes the extracted production shell against a local Git origin with simulated SSH and package installation. It observes the bundled package path, first-use onboarding, retained executable link, and subsequent service restart. Telegram distributions are built and checked alongside its existing synthetic Telegram/native-harness acceptance. The bot proof starts real npm/Python processes with synthetic WhatsApp transport and temporary authentication, including default-disabled replies, explicit greeting sends, failures, reconnect, and shutdown.

Live Telegram delivery, Azure deployment, VPN access, pairing, service startup, and reboot recovery remain operator activation checks. The proof does not claim those effects.
