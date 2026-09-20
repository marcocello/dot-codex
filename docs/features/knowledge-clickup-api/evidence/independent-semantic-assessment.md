# Independent routing assessment

Author: /root/clickup_api_proof. Assessed the implemented integration skill, shared contract, capture skill and Second Brain reference, review skill and harness routing pointer on 2026-09-19 against the frozen PROOF journeys. This is semantic instruction assessment, not a live autonomous-agent conversation or live ClickUp account test.

| Journey / paraphrases | Result and grounding |
| --- | --- |
| No file: “save this task”, “track this idea”, “what needs attention?” | Pass at instruction boundary: capture's Second Brain reference and review both invoke knowledge-config, retain the request, ask on SETUP_REQUIRED and resume. Integration explicitly forbids sending the user away to invoke another skill. Executable proof independently confirms the missing-file signal. |
| File with saved profiles but no default: “use my Second Brain” | Pass: setup offers saved profile names, asks once, keeps question pending, saves chosen default and verifies resolve/access before resume. No arbitrary account discovery is promoted into a default. |
| Explicit disabled default: “capture this next step” | Pass: none is configured, suppresses setup/provider access, returns unsaved proposal. Executable proof confirms persisted none resolution. |
| Broken TOML or unknown explicit selection | Pass: integration and workflows require precise repair, not automatic reselection or fallback. Executable proof distinguishes errors from SETUP_REQUIRED. |
| “Append this to my journal file” / “archive this article in Zotero” | Pass: standalone mode routing remains explicit; integration, shared contract and harness pointer exclude it from setup. |
| “Use profile personal for this review” followed by ordinary review | Pass: precedence is explicit operation/chat selection then saved default; resolve override does not persist changes. New invocation reads the configuration rather than relying on remembered service. |
| One integration skill, capture/review retained | Pass: knowledge-config owns setup, canonical resolver and provider references/direct scripts. Capture owns classification/matching/authorization; review owns review depth/read-only boundaries. Provider-specific instructions live under integration. |
| Missing ClickUp credential, wrong account or inaccessible list | Pass: asks only for private reference, never token text; verifies actual account and destination before content; leaves original operation pending/unsaved on blocked access. No transport fallback. |

No blocking instruction ambiguity found in these accepted journeys. Actual model compliance across fresh sessions and real ClickUp credential/permission behavior remain unverified and must not be reported as observed live success. Setup necessarily pauses for the user's answer; elapsed time is not a selection.
