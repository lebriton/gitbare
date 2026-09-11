<p align="center">
  <img src="" alt="Logo" width="200" />
</p>

<h1 align="center">gitbare</h1>

<p align="center">
  <strong>Bare Git repositories, without the bare experience.</strong>
</p>

<p align="center">
  <i>A single portable .py, powered by Python's standard library only.</i>
</p>

<br>

# What it does

`gitbare` wraps `git` so you can work with bare repositories as easily as with
normal ones. Link a working directory to a bare repository once, then run
plain `git` commands through `gitbare` — the matching `--git-dir` and
`--work-tree` options are injected for you.

```bash
gitbare link --init ~/bare/project.git   # once, from your working directory
gitbare status                           # git --git-dir=... --work-tree=...
gitbare add .
gitbare commit -m "Deployable state"
gitbare push origin main
```

# Why this project

It started with a specific problem: PHP projects served from `/var/www`. A
normal clone keeps a `.git` directory next to the files, and when those files
are served over HTTP a misconfigured or compromised webserver can expose it —
leaking the entire history: sources, credentials, everything. Apache/nginx
rules help, but a second line of defense is better.

A bare repository holds no working tree, so there is nothing to serve or
browse from the web root. Backing a project with a bare repo means even the
worst misconfiguration has no `.git` directory to stumble into.

`gitbare` was vibe-coded quickly to make that setup painless — treat it as a
handy convenience tool, not a hardened piece of software.

# Configuration

Mappings live in `~/.gitbare`:

```ini
[bare]
/var/www/project = /home/user/bare/project.git
/home/user/dotfiles = /home/user/dotfiles.git
```

`gitbare` looks up the current directory — walking up through parent
directories if needed — and runs git against the mapped bare repository. If no
mapping matches, it errors out; it never falls back to plain `git`.

# Commands

- `link <bare> [--init]` — map the current directory to the bare repository;
  `--init` creates it when missing.
- `unlink [dir]` — remove the mapping for a directory (default: current).
- `-v`, `--verbose` — print the resolved mapping and the git command being run.
- Anything else is forwarded to `git` unchanged.

# Installation

Download and install as a single command.

**wget:**

```bash
mkdir -p ~/.local/bin
wget -qO ~/.local/bin/gitbare https://raw.githubusercontent.com/lebriton/gitbare/main/src/gitbare.py
chmod +x ~/.local/bin/gitbare
```

**curl:**

```bash
mkdir -p ~/.local/bin
curl -fsSL https://raw.githubusercontent.com/lebriton/gitbare/main/src/gitbare.py -o ~/.local/bin/gitbare
chmod +x ~/.local/bin/gitbare
```

Make sure `~/.local/bin` is in your `PATH`.

# License

[MIT](LICENSE).

<br>

<p align="center">
  <sub>Made with determination.</sub>
</p>
