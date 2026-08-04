# UI Proof Realism

## Goal
Make UI proof fail when real user interaction, rendered resources, or application-backed domain behavior is broken.

## Behavior
- Interaction claims use genuine browser/user actions against rendered controls; handler calls and synthetic DOM dispatch are insufficient.
- Resource claims observe loaded, decoded, and visible content; a URL or source attribute is insufficient.
- Domain-behavior claims cross the real protected application API and its normal authorization path when relevant.
- Fixtures and API stubs may prove presentation-only states; unsafe outer providers may still be faked.

## Constraints
- Keep the rules in the UI proof profile used by proof authoring.
- Do not require live unsafe providers when an outer-edge fake preserves the application boundary.

## Non-Goals
- Mandating screenshots for every UI feature.
- Replacing repository-specific browser tooling.

