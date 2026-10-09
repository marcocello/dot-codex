1. Specification

- Users must have export permission before an export starts.
- When a user selects at most 500 orders, the export must contain only those selected orders.
- The worker should retry a transient failure after 30 seconds.
- The export may return a cached response. Cache behavior remains unverified.
- If the caller lacks export permission, the streaming API must return status `403`.
- The export should be fast and handle permanent failures gracefully. The performance target and observable permanent-failure behavior remain undecided.

2. Proof plan

Starting state: A user with export permission opens the browser. Orders A, B, and C are available, with normal identifiers and distinct amounts. Record their identifiers and amounts before export. The target runtime and external dependencies are unspecified; record them before execution.

Select A and B in the browser, leaving C unselected. Choose Export. Independently read the downloaded export file and compare its order identifiers and amounts with the starting records.

Pass if the file contains A and B with their recorded amounts and excludes C and all other orders. This plan checks the selected-order result for two orders. It does not establish the 500-order boundary, permission rejection, retry timing, cache behavior, performance, or permanent-failure behavior. The plan has not been executed.

3. User status

The unit tests passed with a fake payment provider. The staging browser export downloaded a CSV containing only A and B. Production deployment is still pending.

A separate log contained exactly `upstream timed out`. We suspect the provider, but the cause is unconfirmed. Your authorization is required before the next deployment action.

4. Technical instruction

Start the streaming worker with `python worker.py --timeout 30`. Keep the established timeout of 30 seconds.

The request field is `retry_after_ms`. The observed literal error is `Cannot acquire lock; retry later`.

5. Risposta in italiano

L’export dalla CLI locale ha prodotto il CSV atteso. Il provider reale non era disponibile, quindi resta da verificare. Il deployment richiede la tua autorizzazione, che non hai ancora dato.
