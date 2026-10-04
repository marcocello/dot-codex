# Export download integration findings

The narrow outcome is: a customer starts an export from a newly connected account with no previous exports, sees progress, and can download that export after completion. This is a planning deliverable only; no feature, provider call, or acceptance execution was performed.

## Evidence and integration mismatch

- `README.md` says the portal stores only `account_id`, has no available credentials or network service, and will use the bundled client.
- `docs/api.md` documents creation returning `export_id` and `status_url`, followed by status polling with `pending`, `ready`, or `failed`. Its suggestion to render `download_path` directly is incomplete.
- The pinned 2.4.0 source in `vendor/archivebox.py`, `ArchiveBox.download`, explicitly says download paths require the account bearer token and are never suitable for browser links. It resolves paths against the configured provider endpoint and retrieves bytes through the server transport. Prefixing the example path with the endpoint does not solve authentication.
- `ArchiveBox.share_export(export_id, ttl_seconds=300)` POSTs to `/exports/{export_id}/shares` and extracts the response `url`. This is a separate operation returning a public, expiring URL. Its source comment explicitly says new exports have no shares by default. `ready` alone therefore does not establish that a customer can download from a browser.

The supplied documentation and code are all available evidence. The source resolves the local client contract, but cannot establish actual provider permissions, response behavior, or live download success. Investigation commands and actual stdout/stderr are retained in `tool-events.log`.

## Recommended narrow implementation plan

Use the bundled share operation if expiring public links are acceptable for these exports. The 300-second client default is a provisional engineering choice, not user approval of public sharing. A public URL permits anyone possessing it to access the export until expiry; customer authentication on the portal alone does not restrict that URL. The request does not establish whether that disclosure model is acceptable. Resolve this consequential choice before freezing dependent acceptance or implementation. If links must remain restricted to the authenticated customer, use a protected portal download route that checks account/export ownership and streams `client.download(download_path)` from the server instead; do not silently switch to public shares.

For the public-link option, the smallest complete slice is:

1. Resolve the connected account through the authenticated portal session. Establish a server-side provider transport, endpoint, and authorized credentials using the connection's supported credential mechanism. An `account_id` alone cannot authorize provider requests. Never place the account bearer token in a browser URL or client-side code.
2. On the customer's export action, call `create_export(account_id)` and durably associate the returned `export_id` and `status_url` with that account/customer. Start with an empty export history; do not require an existing export or pre-created share.
3. Poll the saved status through the backend with bounded retries/backoff. Show pending while pending, and an explicit failure with an intentional retry action when failed. Reloading the portal must resume observation of the same saved export rather than create another export automatically.
4. On ready, call `share_export(export_id)` server-side. Store the URL and locally tracked expiry information with the correct export; only then render the download action. A share failure is a link-generation failure, not an export-generation failure. Retry link generation without creating a second export. Do not fall back to exposing `download_path`.
5. Refresh an expired share through a deliberate authenticated download/refresh action. Fetch the current link near download time, rather than assuming a share created at export completion remains usable indefinitely. Treat local expiry tracking as an approximation until provider expiry semantics are verified. Avoid an uncontrolled share-creation loop during polling; serialize link creation for the same export where practical.

The portal's actual framework, persistence, connection credential store, and worker/polling infrastructure are absent. Reuse them when available rather than invent a new stack. Schedule exports, export history management, notifications, and permanent public sharing are outside this slice.

## Acceptance plan

The acceptance target is the actual portal in a browser, its authenticated backend and persistence, the pinned ArchiveBox client, and eventually an authorized provider sandbox. An independent acceptance author should implement the proof before feature implementation; this task supplies a plan, not executable independent proof.

Start with an authenticated newly connected account containing only its current persisted account identity and no export/share records. Supply provider credentials through the normal connection mechanism, not through prefilled export results. Activate the real export UI. The producer is the portal's protected create route, provider state owns export completion, portal persistence owns customer association, and the browser is the final consumer. Observe saved state through normal reload/read-back and inspect the actual downloaded file independently.

| Scenario | Required observation / defect caught |
| --- | --- |
| First export, pending to ready | Create returns a new ID; status polling reaches ready; share creation uses that same ID; browser follows the returned share URL and downloads a valid archive with expected meaningful contents. Catches omitted share creation and a link that returns 401 or an empty/error payload. |
| Pending and provider failure | No download action before usable link creation; failure is visible and no share is requested for failed exports. Catches premature success. |
| Share failure and retry | Export remains identifiable as completed, link failure is visible, retry creates a usable link without creating another export. Catches swallowed failure and duplicate export generation. |
| Expiry | Expired links are refreshed through the chosen protected action; the replacement download works. Verify provider enforcement in the sandbox rather than inferring it from local timestamps. |
| Reload and repeated polling | Same account/export state survives reload; polling does not continuously mint shares or create duplicate exports. |
| Ownership | A second customer cannot request, inspect, or refresh another customer's export through portal routes. For public shares, separately document that possession of the URL grants access until expiry. |
| Missing/revoked provider access | A fresh connection without usable credentials or sharing permission shows an actionable failure and no fabricated link. |

Local deterministic acceptance may fake only the unavailable provider transport. Its state machine should begin with no exports or shares, reject unauthenticated raw downloads, and issue a share only after the real application calls the share endpoint. Exercise real portal routes, persistence, client methods, browser navigation, and downloaded contents; never fake the portal's ready-to-link logic or preseed its final URL. A local pass proves application behavior against that declared provider model, not provider compatibility. Static inspection, HTTP 200 alone, or a screenshot of a link cannot prove the requested outcome.

## Remaining limits and readiness

No credentials, provider sandbox, runnable portal, or test infrastructure are supplied. Live service contact is forbidden for this task. Thus provider share permissions, actual TTL/expiry behavior, response constraints, rate limits, retry/idempotency behavior, and real archive contents remain unverified. No performance or reliability claim is made.

Before delivery work: the product/data owner must settle public-link acceptability or select the protected streaming route; the connection/integration owner must provide a sanctioned sandbox and credential setup without exposing secrets. In that sandbox, the acceptance author must start from a new account, create an export through the normal portal path, observe provider readiness, obtain a link through the selected mechanism, and validate the resulting downloaded archive. Confirm required share permission and expiry behavior if the public-link option is selected. These are explicit prerequisites, not a reason to implement or contact a live service now. The feature is not implementation-ready under the supplied proof contract because no executable independent acceptance or verified external boundary exists yet.
