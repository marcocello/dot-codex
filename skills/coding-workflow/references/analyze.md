# Analyze

Answer the user's question through investigation. Architecture deep dives, architecture improvement proposals, UI critiques, anti-pattern reviews, and harness reflection remain directly invocable capabilities.

1. Establish the question, scope, relevant repository or runtime context, and decision the analysis should support.
2. Investigate with the appropriate analytical skill. Prefer current code/runtime evidence; separate facts, assumptions, and unknowns. Use an independent reviewer only for a concrete risk or explicit request.
3. Give findings, implications, limitations, and the smallest useful recommendations. Retain relevant evidence through [evidence.md](evidence.md).

An analysis-only request does not create a feature package, start a development Goal, run unrelated suites, or implement suggestions. A request that already authorizes implementation can continue in the same task through Shape/Ship or Fix after the analysis; do not require a new task or repeat authorization. Unresolved consequential behavior choices still need conversation.
