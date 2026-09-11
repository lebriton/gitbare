# Agents

## Workflow

- Pre-commit hooks must all pass on every commit. Never use `--no-verify` or `-n` to skip hooks, unless explicitly insisted by the user.
- Never commit, push, or execute any git command that modifies local or remote state unless the user explicitly asks for it. You must ask for approval every single time before running any such command.
- Use `--ff-only` for all merges. Use `--rebase` for all pulls. No merge commits or non-ff rebases allowed.

## Language

- All comments in code and all commit messages must be written in English only. French is not allowed.

## Documentation

- Documentation must be stored in `docs/*.md` files.
- Each documentation file must be linked in the README under the `# Documentation` section.
- Links in the `# Documentation` section must be sorted alphabetically.
