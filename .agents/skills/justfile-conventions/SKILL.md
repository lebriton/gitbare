---
name: justfile-conventions
description: 'Justfile conventions. Use when writing or reviewing Justfiles.'
---

# Justfile Conventions

Every Justfile has its tasks sorted in alphabetical order.

## Task Ordering

When writing a Justfile, sort tasks alphabetically by name.

```just
build:
    cargo build

check:
    cargo clippy

test:
    cargo test
```
