---
name: python-cli
description: 'Python CLI scripts using argparse, standard library only.'
---

# Python CLI

## Template

```python
#!/usr/bin/env python3

import argparse
import logging
import sys

logger = logging.getLogger(__name__)

DESCRIPTION = "Short description."


def main() -> int:
    args = parse_args()
    setup(args.verbose)

    # TODO: implement

    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("name", help="Positional argument.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output.")
    return parser.parse_args(argv)


def setup(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=level)


if __name__ == "__main__":
    sys.exit(main())
```

## Conventions

- **Standard library only.** Every import comes from the stdlib — maximum portability, zero install.
- **Argparse only.** Argparse is the single source of truth for argument definition and help generation — no click, no typer.

