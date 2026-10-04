# Save and reopen owner contacts

Accepted from README: maintain an owner's durable contact list through the public CLI.

- AC1: Add a contact, exit, and list it in a new CLI invocation using the same database.
- AC2: Reject a duplicate email within the same owner, keeping prior records intact.
- AC3: Owner lists are isolated; two different owners may each store the same email.

The caller supplies the authenticated owner. Login/authentication is outside this library contract. No external services.
