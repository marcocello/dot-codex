---
name: create-cli-toolkit-kit
description: Create, adapt, validate, and prove provider-Admin Python kits for TWYD CLI Toolkit Runtime from CLIs, repositories, or ZIPs, including schemas, adapters, pinned dependencies, provenance, and realistic Admin-to-MCP proof.
---

# Create CLI Toolkit Kit

Build a deterministic MCP tool package. Keep reasoning in the MCP client, authorization and audit in Portal, and Python execution in the private CLI Toolkit Runtime.

## Start With Repository Authority

1. Read `AGENTS.md` and the relevant `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/TESTING.md`, and feature package.
2. Inspect the current `backend/cli_toolkit_runtime/runtime.py` and Portal integration before assuming archive or schema support.
3. For customer quotation engines under `business_logic_modules/`, also use the repository's business-module integration skill.
4. Treat a new customer kit, runtime dependency, resource type, data mount, or output policy as standard or sensitive feature work. Define or update one `FEATURE_DIR` and prove the complete boundary.

Read [references/runtime-contract.md](references/runtime-contract.md) for the current package and execution constraints. Read [references/proof-checklist.md](references/proof-checklist.md) before authoring proof.

## Analyze the Source Before Packaging

Record:

- original path, digest, Git history/upstream, and license status;
- public CLI/API entrypoints and exact required/optional inputs;
- import closure for each proposed tool;
- runtime dependencies and versions;
- required files, databases, secrets, and mutable state;
- customer-derived facts that could leak through code comments, resources, logs, errors, warnings, or raw engine output.

Reject the shortcut of uploading the whole repository. Select the smallest executable closure. Do not invent a license, provenance, missing price, default, or customer fact.

## Decide the Public Tool Contract

For every tool, define:

- one stable name and purpose;
- an exact schema-expressible input object with closed fields, enums, and bounds;
- one exact output envelope with explicit success, refusal, unavailable, and failure behavior;
- an allowlisted safe projection of engine output;
- fixed handling for missing deployment data;
- whether resources or databases are package-owned or deployment-owned.

If the runtime schema subset cannot express an invariant, validate it inside the isolated adapter and state that boundary. Do not claim pre-process rejection for adapter-only validation.

## Build the Integration

Prefer this shape:

```text
business_logic_modules/<kit-slug>/
├── source/                 # preserved selected source or imported subtree
├── <tool>_adapter.py       # TWYD-owned stdin/stdout boundary
├── kit_manifest.json
├── build_kit.py            # deterministic archive and provenance checks
├── SOURCE.md
├── SOURCE_RECEIPT.json
└── dist/<kit-id>-<version>.zip
```

Keep imported business logic separate from TWYD adaptation. If source bytes are transformed for packaging, retain the original selected bytes and record both input and output hashes plus the named transformation.

### Adapter Rules

- Read exactly one JSON value from stdin and emit exactly one JSON value to stdout.
- Accept no caller path, command, argv, environment, credential, runtime identity, or permission choice.
- Call the engine's public function directly; do not invoke its argparse CLI when a library boundary exists.
- Rebuild output from an explicit allowlist. Never return raw engine objects.
- Normalize unexpected exceptions and `SystemExit` to bounded safe failures without traceback, SQL, paths, environment values, secrets, or source data.
- Use deployment-owned absolute data roots and read-only database modes. Never search the filesystem or fall back to bundled customer data.
- Make missing/unreadable/incompatible data `unavailable`, never a guessed or zero quote.
- Prevent runtime library thread pools from exceeding process limits through runtime-owned environment configuration when required.

### Builder Rules

- Produce the same bytes for the same inputs: sorted members, fixed timestamps, fixed modes, strict JSON, and no mutable build metadata.
- Package only declared `.py` entrypoints/imports and approved bounded `.json` resources supported by the current runtime.
- Exclude installers, native binaries, executable modes, symlinks, hidden paths, databases, raw datasets, tests, notebooks, reports, and documentation.
- Never install dependencies during upload. Pin necessary packages in the controlled runtime image and verify imports there.
- Generate a source receipt covering original digest, selected inputs, transformations, resources, adapter, manifest, builder, dependency pins, and final archive.

## Validate Before Upload

Run the bundled static validator:

```bash
python scripts/validate_kit.py path/to/kit.zip
```

Then cross both real validation boundaries: Portal's protected Admin upload route and the production runtime activation route. Static validation is not feature proof.

## Prove the Journey

Prove the actual sequence:

1. build twice and compare bytes/digests;
2. start disposable PostgreSQL and the production Toolkit Runtime image;
3. configure the runtime through protected Portal Admin APIs;
4. upload the archive, authorize its exact version for a Team, and publish a safe option;
5. create a bound Coworker, enable MCP, initialize Streamable HTTP, list tools, and call the tool;
6. verify the real uploaded adapter subprocess result, Portal activity/events, runtime receipt, and idempotent replay;
7. verify invalid schema input starts no process;
8. verify corrupt/oversized/traversal/symlink/executable/native/installer/resource-entrypoint archives fail without catalog mutation;
9. verify missing data is safe and deployment data remains byte-identical/read-only as the actual execution UID;
10. verify forbidden customer-history sentinels cannot appear in archive bytes, catalog, stdout, MCP result, or errors.

Use realistic fixture data labelled as proof data. Never represent a fixture database as production pricing accuracy.

## Handoff

Report:

- uploadable archive path, kit id/version, tools, and SHA-256;
- source/provenance and license status;
- runtime image dependency and deployment-data requirements;
- exact Admin → Team → Coworker → MCP setup steps;
- official proof run and fresh final-review verdict for standard or sensitive work;
- known gaps, especially missing production data, unproved pricing accuracy, hostile-code isolation, or live-cluster deployment.

Do not populate production data, deploy, upload to a live Admin portal, or mutate external services without explicit authorization.
