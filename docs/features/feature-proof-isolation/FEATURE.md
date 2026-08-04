# Feature Proof Isolation

## Goal
Keep one feature's executable proof from becoming a historical sweep of other feature proofs while preserving the integration signal required by prerequisites.

## Behavior
- A feature proof owns its executable claim and does not import or execute another feature's complete proof.
- Prerequisite behavior may be used as setup.
- The active proof may exercise the smallest necessary integration canary through the prerequisite's normal public behavior.

## Constraints
- Do not add a dependency graph, proof registry, hashes, receipts, or historical completion sweep.
- Do not forbid focused integration checks merely because they cross modules.

## Non-Goals
- Preventing all shared test helpers or fixtures.
- Replacing feature proof with isolated unit tests.

