---
name: laravel-feature-builder
description: Use when building or fixing Laravel features, including routes, controllers, requests, models, policies, jobs, queues, APIs, admin flows, migrations, and PHPUnit or Pest coverage.
---

# Laravel Feature Builder

Use this skill for Laravel application work where framework conventions should guide the implementation.

## Goals

- preserve Laravel idioms
- place logic at the right layer
- keep changes testable
- avoid breaking existing config and environment assumptions

## Workflow

1. Inspect `composer.json`, Laravel version, PHP version, and `php artisan about`.
2. Use `prepare-environment` for Composer, `.env`, app key, and local test setup rules.
3. Trace the request or job path before editing.
4. Reuse the project’s existing patterns for validation, authorization, and persistence.
5. Prefer feature tests for user-visible behavior and unit tests for isolated logic.
6. Run the smallest meaningful test or artisan verification flow.

## Preferred Patterns

- Form Requests for validation when the app already uses them
- policies or gates for authorization
- service classes only when they clarify non-trivial logic
- queued jobs for slow side effects
- resources or transformers for API shaping when already present

## Check Before Shipping

- routes and middleware
- model events and observers
- queue side effects
- cache invalidation
- storage paths
- env-driven config
- database migrations and rollback safety

## Avoid

- moving the codebase toward a new architecture without need
- putting heavy business logic directly in controllers
- silent schema changes without tests or migration review
