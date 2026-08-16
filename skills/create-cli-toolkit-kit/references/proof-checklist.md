# CLI Toolkit Kit Proof Checklist

## Build and provenance

- Build twice; bytes and SHA-256 match.
- Original source digest and licensing status are recorded.
- Every selected input and transformed output is hash-correlated.
- Archive contains only the intended manifest, code, and resources.
- Source comments/resources with customer-history sentinels are absent when classified private.

## Activation safety

- Real Portal protected upload and production runtime activation both accept the candidate.
- Traversal, alias, duplicate, symlink, executable mode, native binary, installer, missing entrypoint, JSON entrypoint, malformed JSON, non-finite JSON, corruption, unsupported compression, and size limits reject without catalog mutation.
- Upload never imports code, executes hooks, or installs dependencies.

## Real invocation

- Use disposable PostgreSQL and the real Portal API/MCP transport.
- Use the production runtime implementation and built image.
- Invoke the uploaded archive, not an in-test reimplementation.
- Verify exact dynamic `tools/list` schemas.
- Verify success/refusal/unavailable/failure projections.
- Verify Portal activity/events and runtime receipt reach the same terminal identity.
- Replay the same client request and prove no second process.
- Reuse the same client request with different input and prove conflict.

## Data and output safety

- Mount labelled fixture data read-only using the production path.
- Run as the production execution UID and prove write denial plus unchanged digest.
- Remove the mount and prove safe `unavailable` output.
- Seed forbidden customer-history values that the engine could naturally emit; assert they are absent everywhere external.
- Assert errors never expose traceback, SQL, paths, environment variables, credentials, or raw source/data.

## Deployment

- Built runtime image imports exact pinned dependencies.
- Compose and Kubernetes declare the same fixed data root read-only.
- Runtime has private service discovery and no public ingress.
- Deployment pipeline builds and substitutes the runtime image.
- Document how operators populate/refresh data separately from Admin kit upload.

## Completion

For tracked work, retain an official realistic proof PASS and obtain a fresh read-only evaluator PASS on the unchanged candidate before marking the feature done.
