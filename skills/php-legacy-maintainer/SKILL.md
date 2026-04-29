---
name: php-legacy-maintainer
description: Use when working on plain PHP or framework-light PHP projects that need maintenance, debugging, runtime audits, Composer dependency review, PHP version compatibility checks, incremental refactors, or safe upgrade planning.
---

# PHP Legacy Maintainer

Use this skill for classic PHP applications, custom CMS codebases, or mixed legacy stacks where the right answer is careful containment rather than framework rewrites.

## Goals

- identify the real runtime shape of the app
- document PHP version, extensions, entry points, and dependencies
- make minimal safe changes
- reduce risk before larger upgrades

## Workflow

1. Inspect `composer.json`, bootstrap files, config files, and public entry points.
2. Use `prepare-environment` for PHP version, Composer, `.env`, and local validation setup.
3. Detect the actual PHP version target and required extensions.
4. Separate infrastructure problems from code defects.
5. Prefer local fixes and small abstractions over large architectural rewrites.
6. Add or improve validation where possible.

## Focus Areas

- Composer dependency conflicts
- deprecated PHP APIs
- missing extensions
- unsafe globals or include chains
- configuration sprawl
- weak error handling
- upgrade-readiness notes

## Upgrade Pattern

When the task includes a PHP upgrade:

1. inventory version constraints
2. scan for deprecated behavior
3. identify blocked packages
4. propose the smallest viable upgrade path
5. validate with targeted CLI or test flows

## Deliverables

Prefer outputs that include:

- the current-state runtime summary
- the change made
- remaining blockers or follow-up risks
