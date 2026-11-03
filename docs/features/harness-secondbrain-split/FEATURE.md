# Separate coding harness and second brain

The owner authorized splitting this checkout into a coding-only `dot-codex` repository and a sibling `secondbrain` repository. Existing research, analysis, presentations and local deliverables move to the explicitly selected ObsidianVault. Preserve pre-existing source changes, private runtime state and account connections.

## Acceptance

- H1: A fresh coding checkout activates through `install.sh` using filesystem links and a template configuration, without services, account login or network access. Repeating installation preserves user configuration and other skills. An existing conflicting home or skill is preserved and reported. An explicit environment command supplies a shell-safe `CODEX_HOME` export.
- H2: Coding source and its inventory contain the coding workflow and development tools. Second-brain services, deployment setup, personal skills and their feature records belong to the sibling repository. Each inventory resolves its owned skills locally. Existing staged changes are retained in a recovery snapshot before relocation; no commit or push is part of this change.
- H3: The second-brain entrypoint and backend CLI run from its repository without the coding checkout. Profile activation and native/container launch configuration select its private Codex home and do not replace the coding home, copy credentials or enable accounts/schedules.
- H4: Existing deliverables and their assets are transferred byte-for-byte to ObsidianVault with a private manifest and recovery snapshot. Default instructions direct future research, analysis and presentation deliverables there. Product documentation, acceptance tests and reusable skill assets remain with their source.
- H5: The secondbrain root has one public launcher, `secondbrain.sh`. Runtime templates live under `deployments/templates/`, and its capability inventory lives at `skills/manifest.toml`. The YAML/state-CLI runtime, duplicate shell alias, and superseded native-service setup flow are removed. Current setup, source export, container staging, profile activation and personal workflows use only the supported SQLite/MCP runtime. Historical evidence is retained as history rather than exposed as supported operation. The owner explicitly requested this simplification without legacy support.

## Boundary

Verification uses temporary homes and local commands. It does not reconnect accounts, deploy containers, provision resources, restart existing services, or establish live provider readiness. Existing private runtime files remain at their original locations unless individually identified as deliverables. Historical completion records remain history; this migration does not re-prove every older feature.
