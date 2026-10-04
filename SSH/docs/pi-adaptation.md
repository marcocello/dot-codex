# Pi → SSH

Source inspected: the local `pi/` checkout of [earendil-works/pi](https://github.com/earendil-works/pi/tree/d5629e20489ccf770ed90b5a33941cb3b7ef24d0), revision `d5629e20489ccf770ed90b5a33941cb3b7ef24d0`, on 2026-09-24. This is a selective adaptation of that checkout, not a claim about every Pi installation or the newest upstream version. Attribution is retained in [Pi-LICENSE.txt](Pi-LICENSE.txt).

Pi's useful design is a capable model with a small core, specialized instructions loaded on demand, and executable integrations kept separate from prose. SSH keeps that separation and adds the user's four pillars. A skill supplies judgment or reusable assets; it does not implement a runtime API or enforce a sandbox.

| Pi source capability | SSH adaptation | Pillar served |
| --- | --- | --- |
| Scout/planner examples and issue investigation prompt | `code-explore`: focused code map, independently checked cause, small proposal; no labels or assignments | Understand the outcome |
| Worker example and native tool loop | The base model implements directly with Codex tools; no generic worker skill or compulsory agent chain | Own the work |
| Reviewer example, PR prompt, and deslop prompt | `code-review`: evidence-backed findings; simplification only when requested | Understand and prove |
| Interactive-testing skill and release smoke tests outside the checkout | `code-verify`: real interaction, consumer read-back, persistence, and recovery | Prove the outcome |
| Release skill, changelog prompt, and wrap-up prompt | `code-release`: prepare a candidate, perform authorized publication, inspect partial failure and consumer availability | Own, prove, and leave evidence |
| Handoff extension | `code-handoff`: compact continuation context using available native tools; no automatic new task | Leave useful evidence |
| Progressive skill loading | Short Codex `SKILL.md` files with discriminating descriptions and optional references | Keep the core small |
| Existing SSH stack preference | `react-fastapi-scaffold` remains the default for new web apps | Avoid repeated routine decisions |

The source files behind this mapping are [the system prompt builder](https://github.com/earendil-works/pi/blob/d5629e20489ccf770ed90b5a33941cb3b7ef24d0/packages/coding-agent/src/core/system-prompt.ts), [skill loading documentation](https://github.com/earendil-works/pi/blob/d5629e20489ccf770ed90b5a33941cb3b7ef24d0/packages/coding-agent/docs/skills.md), [subagent examples](https://github.com/earendil-works/pi/tree/d5629e20489ccf770ed90b5a33941cb3b7ef24d0/packages/coding-agent/examples/extensions/subagent), [repository prompts](https://github.com/earendil-works/pi/tree/d5629e20489ccf770ed90b5a33941cb3b7ef24d0/.pi/prompts), [repository skills](https://github.com/earendil-works/pi/tree/d5629e20489ccf770ed90b5a33941cb3b7ef24d0/.pi/skills), and [handoff extension](https://github.com/earendil-works/pi/blob/d5629e20489ccf770ed90b5a33941cb3b7ef24d0/packages/coding-agent/examples/extensions/handoff.ts).

Codex remains responsible for tool execution, permission enforcement, sessions, model configuration, and any available delegation or compaction. SSH does not claim Pi's TypeScript extensions run inside Codex. Its plan-mode shell filter, session tree, custom providers, TUI widgets, RPC/SDK, model presets, and automatic Git checkpoints are not ported. A review skill's read-only scope is an instruction, not a security boundary.

Pi's `add-llm-provider` skill targets `packages/ai` internals and stays with Pi. Its advisory-publication prompt and release-specific versioning are also outside this general coding harness. Automatic issue assignment, PR labeling, comments, commits, pushes, issue closure, and release announcements from Pi's personal prompts are deliberately removed. These actions remain available through native tools when the user authorizes them.

No Pi process, npm package, account, provider key, or checkout is required to use the adapted skills. No model is pinned. Native delegation is optional and depends on the actual session's tools and instructions. The adaptation does not replace the user's existing harness or modify the Pi repository.
