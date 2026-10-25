# One checkout for the second-brain runtime

The operator uses this checkout to install Codex and the harness, prepare the VM, and run the Telegram gateway or optional WhatsApp bot. The existing source repositories remain untouched. The first deployment target is the existing Ubuntu/Azure design; macOS supports development and foreground execution.

## Acceptance

- R1: The checkout contains the VM console and non-secret Terraform source, the installable Telegram package with its license, and the runnable Baileys component. Imported credentials, sessions, environments, and provider state are excluded.
- R2: One documented CLI exposes local setup, diagnostics, context commands, Telegram onboarding, optional bot startup, and VM operator commands. Its plan mode performs no installation or provider mutation. Existing `install.sh` commands retain their behavior.
- R3: The VM console resolves infrastructure from this checkout and installs Telegram from its bundled package. It preserves the existing VPN-only access and explicit infrastructure-apply boundary. Executable local fixtures verify command dispatch and embedded payloads; live Azure setup remains an activation check requiring the operator's existing account and VPN.
- R4: The bundled Telegram gateway retains native harness execution and authorization behavior. The optional Baileys bot starts with automatic replies disabled unless the operator explicitly enables them. No setup command pairs WhatsApp or starts a duplicate listener implicitly.

## Decisions

Keep the working harness layout at the root. Put runtime applications under `backend/` and infrastructure under `deployments/prod/`. Keep provider credentials and memory outside tracked source. Preserve the original repositories and record import revisions. The operator retains control of paid resources, authentication, pairing, and service activation.
