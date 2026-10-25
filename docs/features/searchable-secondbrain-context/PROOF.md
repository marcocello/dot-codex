# Context retrieval proof

Run `proof/run.sh` after local setup and installation of the test extra. The proof uses disposable workspaces. CLI subprocesses read a synthetic wacli archive through the real adapter and its content-free journal contract. Tests exercise allowlisted chats, inbound/outbound messages, retry, restart, checkpoint failures, deletion, source disable, changed scope, and source erasure. The archive is independently read back to detect writes.

The Graph adapter talks HTTP to a local provider fixture using Microsoft's documented delta envelopes. The real worker and SQLite store handle identity, pagination, retries, deleted entries, and independent sources. The fixture replaces Microsoft authentication and Graph only; it cannot verify tenant consent or actual mailbox completeness.

The semantic journey uses real FastEmbed inference and persistent local Qdrant. The first run downloads its public model. MCP proof starts the real stdio server, initializes a protocol client, lists tools, searches, and reads a cited document. Only read tools are exposed. Assertions read the durable store and returned source references independently of ingestion.

Live Microsoft authentication, real wacli pairing and synchronized history, selected account/chat verification, VM supervision, and relevance over the user's actual multilingual corpus remain activation checks. Retrieved source content is untrusted evidence throughout.
