1. Specification

- Users must have export permission before an export starts.
- When a user selects at most 500 orders, the export must contain only those selected orders.
- The worker should retry a transient failure after 30 seconds.
- The export may return a cached response. Whether “may” grants permission or describes a possibility is unspecified. Cache behavior remains unverified.
- If the caller lacks export permission, the streaming API must return status `403`.
- The export should be fast and handle permanent failures gracefully. The performance target and observable permanent-failure behavior remain undecided.

2. Proof plan

Starting state: A user has export permission. Orders A, B, and C are available, with normal identifiers and distinct amounts. Record those identifiers and amounts to distinguish the orders. The public interface is a browser.

Assumptions to resolve before execution: The browser supports selecting orders and starting an export. The export result can be inspected independently. Confirm the actual controls, result format, and observation method. Record the target runtime and any real or fake external dependencies; none are specified.

After resolving those assumptions:

1. Use the confirmed browser controls to select A and B, leaving C unselected.
2. Start the export through the confirmed browser action.
3. Inspect the complete export result through the confirmed independent observation method.
4. Compare the exported orders with the recorded identities of A, B, and C.

Pass if the export contains A and B and excludes C and all other orders. The plan does not assume a CSV file or a download.

This case checks selection of two orders. It does not establish the 500-order boundary, permission rejection, retry timing, cache behavior, performance, or permanent-failure behavior. The plan has not been executed.
