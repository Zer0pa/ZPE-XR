# Phase 5 Release Decision

## Selected Channel

`PRIVATE_ONLY`

This means the codec is useful today for private evaluation and engineering handoff while the comparator gate remains open.

## Why

- The repo has a real Rust-backed package surface, a fresh x86_64 wheel, `twine check` PASS, and fresh-venv install/import smoke PASS.
- The repo has a real five-sequence ContactPose outward-safe bundle with a non-null Comet experiment key.
- The governing public-release comparator gate failed `0/5`.

## What Is Allowed

- private/internal package evaluation
- internal engineering handoff
- private evidence review and next-milestone planning

## What Is Not Allowed

- public PyPI upload
- public repo flip framed as release readiness
- comparator-displacement claims
- runtime-complete claims
