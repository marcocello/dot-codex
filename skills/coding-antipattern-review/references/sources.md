# Upstream Source Map

Use upstream repositories to generate candidates and ground terminology, not as substitutes for repository evidence. Prefer precise links to the relevant upstream path or rule. Do not vendor or reproduce whole catalogs. Recheck the live source when a rule, license, supported language, or recommended practice may have changed.

Reviewed: 2026-07-14.

## Architecture and runtime

- [MicrosoftDocs/architecture-center: `docs/antipatterns`](https://github.com/MicrosoftDocs/architecture-center/tree/main/docs/antipatterns): primary named catalog for cloud and distributed-system anti-patterns including busy database, chatty I/O, extraneous fetching, monolithic persistence, noisy neighbor, retry storm, and synchronous I/O. Use the catalog's problem, symptoms, and solution structure as a model, then verify applicability against the reviewed system.
- [mspnp/cloud-design-patterns](https://github.com/mspnp/cloud-design-patterns): companion implementations for Azure Architecture Center cloud patterns. Use for counter-pattern and remediation examples, not as evidence that a reviewed system needs the same architecture.

## Executable candidate sources

- [github/codeql](https://github.com/github/codeql): open query libraries for security, correctness, maintainability, and readability across supported languages. Use existing repository CodeQL results or relevant queries to generate candidates. The repository code is MIT-licensed; the CodeQL CLI has separate terms.
- [semgrep/semgrep-rules](https://github.com/semgrep/semgrep-rules): multi-language community rules, strongest for security and locally recognizable source patterns. Treat every match as a candidate requiring contextual confirmation. The rules use the Semgrep Rules License rather than a general permissive code license.
- [SonarSource/rspec](https://github.com/SonarSource/rspec): large cross-language specification index for Sonar static-analysis rules. Link to relevant rules when useful, but do not copy or vendor the catalog; it uses the SONAR Source-Available License.

## Code and language-specific catalogs

- [lee-dohm/code-smells](https://github.com/lee-dohm/code-smells): classical object-oriented smell vocabulary derived largely from refactoring literature. Use as secondary terminology support because the catalog is OOP-heavy and does not by itself establish harm.
- [quantifiedcode/python-anti-patterns](https://github.com/quantifiedcode/python-anti-patterns): Python anti-pattern examples and migration patterns. Use as an older secondary catalog and verify current language guidance before recommending a change.
- [lucasvegi/Elixir-Code-Smells](https://github.com/lucasvegi/Elixir-Code-Smells): research-backed Elixir-specific catalog with explicit problem, example, refactoring, and treatment sections. Use only for Elixir repositories or for catalog-structure inspiration.

## Tests and proof

- [TestSmells/TestSmellDetector](https://github.com/TestSmells/TestSmellDetector): Java/JUnit detector and example catalog for test smells. Use the taxonomy as candidate input; do not assume its language-specific thresholds transfer across stacks. The project is GPL-3.0 licensed.

## Security invariants

- [OWASP/CheatSheetSeries](https://github.com/OWASP/CheatSheetSeries): primary secure-design and implementation guidance for application-security boundaries. Use relevant cheat sheets to establish current invariants and remediation constraints. Do not claim comprehensive security coverage from this anti-pattern review.

## Source selection rules

- Prefer official vendor, project, standards, or research-maintained repositories over personal summaries.
- Prefer an executable rule only when the reviewed language and framework match its assumptions.
- Record the exact rule, path, and upstream commit when importing or adapting any content in a future revision.
- Preserve attribution and inspect the upstream license before copying code, examples, or rule definitions.
