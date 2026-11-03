---
name: coding-privacy-audit
description: Audit public-repository changes before each commit, or review broader release/existing exposure for credentials, personal information, private work, and system details. Optional for private-repository commits. Cover relevant staged changes, history, and exports; report scanner use and coverage without implying cleanup authority.
---

# Repository Privacy Audit

Assess what a release would disclose and what is already exposed. A secrets scanner is one source of evidence; it cannot decide whether research, a course, a client case, or operational metadata belongs in public.

## Choose the scope

- **Before-commit audit:** Required by `coding-commit` before each actual commit in a public repository or for an intended public release. Optional for confirmed private-repository commits unless requested or a specific concern warrants review. If visibility cannot be established from available evidence, apply the public-repository check and state the uncertainty.
- Inspect the selected group's exact index content, added/modified material with enough surrounding file context, new paths, renamed/copied content, relevant generated exports or archive members, and the proposed commit message and author metadata. Preserve partial staging; do not substitute a later working-tree version for the staged version. Follow related copies or history when needed to understand the disclosure, rather than rescanning unrelated history for every commit.
- Bind the result to the selected content and message. After changes, recheck affected material before committing. An existing audit can supply evidence only where its coverage and inspected content still match. Before-commit checks do not claim a full repository/history audit or remote publication verification.
- Hold the commit for confirmed credentials, unintended private disclosures, or unresolved material publication questions in its selected scope. Do not silently modify staging or sanitize files. Report unchanged historical findings separately; they do not by themselves block a safe correction or unrelated commit. If GitGuardian is unavailable, perform local inspection and disclose the scanner gap; unavailability alone does not block a commit or require approval.
- **Full exposure audit:** For requests about the whole repository, its history, or existing publication, cover the broader surfaces below and distinguish present release risks from prior exposure.

## Establish the release boundary

- Determine the repository, intended release, actual remote, and visibility from available evidence. Private, public, and unknown are distinct. An authenticated fetch does not establish anonymous public access.
- Record the starting HEAD, refs, index, and worktree status. Preserve existing staged and unstaged work. If another task changes them during the review, identify which revision each result covers and check new content before extending the conclusion.
- Use the user's stated privacy preferences. Distinguish deliberately published maintainer identity and reusable examples from unexpected personal context. Do not require the user to enumerate every private fact before investigating.
- Keep the review read-only. Unstaging, moving files, redacting, rotating credentials, rewriting history, changing visibility, pushing, and installing hooks require applicable authorization.

## Inspect both secrets and disclosure

Review these surfaces for public repositories and proposed public releases. For a narrower request, name any omitted surfaces in the result.

1. Current tracked content, the exact index content, unstaged edits, and non-ignored untracked release candidates. Ignore rules do not protect files that are already tracked or staged. Inventory ignored private state only as needed to check that it is excluded; do not indiscriminately ingest credential stores or unrelated home directories.
2. Commits reachable through branches, tags, remote-tracking refs, other refs, and reflogs. Include removed and renamed files, original commits retained after history rewriting, commit messages, author/committer identities, and relevant ref names. Keep local snapshots, reflog-only history, branch history, and confirmed remote publication distinct.
3. Generated or copied forms of suspect content: PDF text and relevant rendered pages, screenshots, images, diagram labels/metadata, archive members, embedded files, source snapshots, and duplicate exports. A sanitized source does not establish that its PNG, PDF, or ZIP is sanitized. Do not execute archive contents or extract untrusted paths outside an isolated private directory. Name unavailable readers and uninspected formats.
4. Publication configuration: broad allowlists, artifact defaults, packaging rules, and examples or evidence that could include private deliverables in the next release.

Read [Scan playbook](references/scan-playbook.md) when selecting Git/history commands, running GitGuardian, or checking remote exposure.

### Credentials and key material

Look for API/access/refresh tokens, passwords, connection strings, credentials in URLs, cloud/service credentials, SSH and TLS private keys, PEM private-key blocks, keystores, and credential/config backups. Inspect suspicious contents, not just filenames: `.pem` can contain a public certificate, while a private key can have an unrelated extension. Distinguish usable-looking material from explicit placeholders, tests, public keys, certificates, and scanner mistakes. Do not test a candidate credential against its provider to prove it is real.

Use an available GitGuardian CLI or connector with existing authorized authentication. Do not automatically install a scanner, obtain credentials, or substitute another scanning service when GitGuardian is unavailable. Never expand the authorized data-transfer scope merely because a connector is installed. Continue local inspection when the scanner is missing or blocked, but report that automated scanning did not complete. Do not present manual checks as equivalent coverage.

Always state **GitGuardian used**, **partially used**, or **not used**, with the version/tool, scanned surfaces, completion status, and reason for any gap. Invocation alone is not a completed scan. Check scanner errors and coverage before interpreting alerts or a zero-finding result. Challenge each alert against its source context.

### Personal, work, and system information

Inspect meaning and combinations of facts, not just email/key patterns:

- Personal email addresses, phone numbers, contact/chat identifiers, private account names, home addresses, local usernames, absolute home/workspace paths, and identifying document metadata.
- Mailbox sizes, unread counts, WhatsApp/message/chat/contact counts, agenda size, storage volumes, collection scopes, retention windows, dates, activity patterns, and similar usage statistics. They disclose personal behavior even without message bodies. Check screenshots as well as machine-readable text.
- Unpublished courses, talks, research analysis, annotated source collections, proposed experiments, strategy, product plans, career dossiers, and judgments about the owner's work. Public source papers do not make the owner's selection, notes, or unpublished analysis public by intent.
- Named client/project lessons, stakeholder exchanges, internal incidents, real task requests, conversation captures, and proprietary examples. Separate synthetic evaluation cases from records of actual work; a synthetic case does not make its surrounding real project narrative anonymous.
- Real hostnames, IPs, VM/bot identities, cloud/resource identifiers, backup/database/credential locations, deployment receipts, permissions, service topology, and operational or billing history. Distinguish reusable architecture from a map of the owner's actual systems.

Reject false positives with context, including reserved example addresses, synthetic counts, loopback addresses, and intentionally public attribution. Do not infer confidentiality breaches, working relationships, credential validity, or system compromise from a name or pattern alone. If publication intent remains consequentially unclear, mark the item unresolved and ask about that boundary before recommending it for release.

## Check existing exposure without spreading it

Use local evidence first. If remote verification is in scope, prefer connected repository tools; use an unauthenticated check when the question is whether anyone can access a known URL. Avoid search-engine queries containing private strings, guessed resources, or attempts to access other accounts. Do not upload private assets to OCR, scanning, or other services without applicable authority.

Removing a file from current `main`, resetting a branch, or adding an ignore rule does not prove old commits or exports are inaccessible. Record whether a known old URL still works. A local object or reflog entry alone does not prove it was ever published. Forks, clones, pull-request refs, releases, and CI artifacts remain gaps unless inspected within scope; never promise global erasure.

## Report safely and precisely

- Keep raw evidence and requested standalone reports outside public repositories. Save deliverables in `${OBSIDIAN_VAULT:-$HOME/ObsidianVault}/Dot-codex/`, preserving topic folders and accompanying assets, unless the user selects another destination. Resolve an unavailable vault before saving; never fall back to a public repository. Use an authorized private temporary directory for intermediate inspection. Product documentation, acceptance contracts, verification evidence, and reusable source assets remain with their repository; generalize private context before including it there.
- Mask sensitive values in commentary and reports. Cite a relative repository path plus revision, line, archive member, or page instead of reproducing a secret, full personal address, private absolute path, or precise private usage statistic. Avoid echoing matching lines, secret-bearing commands, or API headers into logs. Do not commit real findings as examples in this skill.
- Lead with the release recommendation and confirmed disclosures. For each finding, explain what it reveals, evidence location, confidence, exposure state, and smallest correction. Separate staged/unpublished candidates from current public content, old public commits, local snapshots, and unverified publication.
- Include the GitGuardian status even if unavailable, false positives and their basis, exact coverage, and material gaps. Say “no genuine credentials identified in the checked scope” when justified; never guarantee that the repository has no secrets or private information.
- Recommend private storage or generalized examples for personal/research/client/operational material. Include every retained export and historical path in a cleanup proposal. Explain what remains publicly reachable and who must authorize any remote or destructive action.
- Finish with what changed, if anything, and where private evidence is available. A passing credential scan does not override a confirmed privacy finding or authorize publication.
