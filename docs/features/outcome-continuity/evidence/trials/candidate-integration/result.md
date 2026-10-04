# Export download integration findings

The customer can receive a working download link, but `download_path` must not be rendered directly. The bundled client says that path requires the account bearer token and is never suitable for browser links. A newly connected account has neither export metadata nor an existing share, so merely polling for `ready` and displaying that path would fail the requested first-use journey.

## Evidence and scope

- `README.md`: the portal stores only `account_id`; no credentials or network service are available. The bundled client matches the pinned package.
- `docs/api.md`: create returns `export_id` and `status_url`; status is `pending`, `ready`, or `failed`, with `download_path` on ready. Its instruction to render a link omits the authentication problem.
- `vendor/archivebox.py`: `download(download_path)` resolves the path against the endpoint and calls transport `get_bytes`; the source explicitly requires account bearer authentication. `share_export(export_id, ttl_seconds=300)` posts to `/exports/{id}/shares` and returns the response's `url`. Its comment describes public expiring URLs and explicitly says new exports have no shares by default.
- A network-free probe of the actual client showed create/status never invokes share creation; explicit sharing sends a 300-second TTL; download resolves a root-relative path to the endpoint's origin. Full executed investigation commands and stdout/stderr are retained in `tool-events.log`. The probe used invented transport responses solely to observe dispatch. It does not establish successful provider authentication, actual share issuance, ZIP validity, or browser delivery.

## Recommended narrow implementation

Deliver one outcome: a customer starting with a connected account and no exports requests an export, sees progress, and downloads that export from the portal once ready.

Recommendation, not a recorded user decision: use an authenticated portal download link and fetch bytes server-side through the bundled client's `download` method. This preserves customer access control without introducing public possession-based access. Assume the portal has a customer session/ownership model; no portal source was supplied to verify it. If “connected” currently means only a stored account ID, secure server-side provider credential resolution is a necessary integration prerequisite, not something the ID supplies.

1. On the ordinary export action, the backend verifies customer/account ownership, resolves the account's provider credentials, and calls `create_export(account_id)`.
2. Persist a portal export record linked to the owning customer/account, including `export_id`, `status_url`, current state, and eventual `download_path`. Start from absent records rather than seeded exports. Keep bearer credentials in the existing secure connection mechanism, never in browser links or export rows.
3. Use the existing job/polling mechanism if available to query the returned status URL. Pending shows progress, failed shows failure without a download action, and ready is recorded only with usable metadata. Preserve the record across reloads. Poll frequency and retry limits follow existing portal conventions; these conventions were not supplied.
4. Once ready, display a link to a portal-owned route identified by the portal export record. On every download, authorize ownership again, resolve the stored provider path on the server, call `download`, and return the export bytes with an appropriate download filename/content type. The route must not accept an arbitrary provider URL from the browser or redirect to the authenticated provider path. Hide/reject downloads before ready. Provider errors must produce a visible retryable failure rather than a false successful file.
5. Verify the first request end to end before adding export history, notifications, scheduling, or configurable retention. Those are outside this slice.

The public-link alternative is technically supported by the pinned client: after `ready`, explicitly call `share_export(export_id, ttl_seconds=300)` and render the returned URL, never `download_path`. No pre-existing share can be assumed. Share failure is a separate link-preparation failure, and expiration requires requesting a fresh share through an authorized portal action. A short TTL reduces exposure but does not enforce customer identity. Choose this alternative only if access by anyone possessing the URL matches the intended policy; that meaningful access change needs a product/security decision before implementation. It avoids carrying file bytes through the portal, whereas the recommended route retains authenticated access but consumes portal bandwidth. No extra sharing endpoint or SDK upgrade is needed based on the supplied source.

## Acceptance plan

Target the actual portal UI, backend, export state store, and worker/polling entry point. The provider HTTP transport is the only substituted external boundary for local acceptance. A separate acceptance author should prepare executable proof before implementation; this request only asks for the plan, so no feature package, proof runner, or acceptance pass is claimed.

| Scenario | Activation and independent read-back | Incomplete implementation caught |
| --- | --- | --- |
| Fresh connected account | Begin with only its account connection, no export rows or shares. Use the real browser export action. Provider fixture returns a newly created export, then pending, then ready. Observe outbound create/status requests, stored ownership and metadata, and UI progress. Reload and follow the visible download link. Inspect the actual downloaded ZIP and known meaningful contents. | Seeded export/share dependency; missing persistence; premature link; dead provider path; empty or wrong download |
| Protected delivery | Through the ordinary portal route, verify provider authentication is added server-side and the expected provider path is fetched. Verify no account bearer appears in the rendered URL/DOM. | Direct browser provider link; missing credential resolution; token leakage |
| Account isolation | A second customer and an unauthenticated session attempt the same portal download URL. Both are denied and no provider bytes are fetched for them. The owner succeeds. | Hidden link mistaken for authorization; cross-account downloads |
| Incomplete or failed export | Exercise pending, provider failed, and ready without a path. Observe no usable link and a truthful state. | UI treats any status response or malformed ready as success |
| Transient provider failure | Fail status once, then recover using the configured retry path. Fail a download and retry normally. Verify stable export identity, no fabricated file, and eventual correct bytes. | Retry creates replacement exports or reports an error body as the export |

The local provider fixture must follow the supplied create/status/download contract and require server-side authentication at its boundary. It may supply a small ZIP with fixed expected contents. It must not implement portal persistence, authorization, polling, or the download route. Browser tests must click real controls and inspect the downloaded artifact; an HTTP 200, visible anchor, source inspection, or direct handler call is insufficient.

If public links are chosen instead, replace protected-byte delivery assertions with explicit share creation after ready, returned-URL use, share failure recovery, expired-link regeneration, and an ordinary browser download without an account bearer. Begin with no shares. Keep portal ownership checks on share issuance and explicitly record the changed possession-based download policy. A fake cannot prove that a live URL is genuinely public or expires correctly.

## Remaining limits and next owner

No portal application, persistence schema, transport authentication implementation, job infrastructure, provider credentials, sample export data, or live service was supplied. Existing connection readiness, provider permissions, error formats, rate limits, export retention, and file sizes remain unverified. The client's `get_bytes` interface suggests buffering; large-file memory/response-time suitability cannot be established from this fixture. No latency or reliability claim is justified.

Before delivery can be accepted against a real integration, the implementation owner needs the portal source and an explicitly authorized provider sandbox with a newly connected test account. Use the same ordinary export action, observe a new ready export, and download and inspect its actual contents in the customer browser. The provider/connection owner must supply the established credential setup; this investigation grants no new live access. If public sharing is selected, additionally establish issuance, expiry, and access behavior against that sandbox.

Investigation and planning are complete. Only this findings document and the requested investigation log were written; no feature was implemented, no live service contacted, and no executable acceptance result claimed.
