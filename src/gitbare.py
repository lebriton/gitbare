#!/usr/bin/env python3

from __future__ import annotations

import argparse
import configparser
import logging
import os
import shlex
import subprocess
import sys

logger = logging.getLogger(__name__)

DESCRIPTION = (
    "Run git commands against bare repositories mapped in ~/.gitbare "
    "(override the location with the GITBARE_CONFIG environment variable)."
)

EPILOG = """\
Subcommands:
  link   <bare>    Map the current directory to a bare repository
                   (use --init to create the bare repository first).
  unlink [dir]     Remove the mapping for a directory (default: current).

Any other command is forwarded to git with the matching --git-dir and
--work-tree options injected automatically.

Examples:
  gitbare link --init ~/repos/project.git
  gitbare status
  gitbare add . && gitbare commit -m "update"
"""

CONFIG_DEFAULT = os.path.expanduser("~/.gitbare")
BARE_SECTION = "bare"
VERSION = "1.0.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitbare",
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print the resolved mapping and the git command being run.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="Print the gitbare version and exit.",
    )
    return parser


def cmd_link(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="gitbare link",
        description="Link the current directory to a bare repository.",
    )
    parser.add_argument("bare", help="Path to the bare git repository.")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create the bare repository if it does not exist.",
    )
    args = parser.parse_args(argv)

    bare = os.path.abspath(os.path.expanduser(args.bare))
    if is_bare_repo(bare):
        logger.info("%s is already a bare git repository", bare)
    elif args.init:
        if os.path.exists(bare) and (not os.path.isdir(bare) or os.listdir(bare)):
            logger.error("%s exists but is not an empty directory", bare)
            return 1
        if create_bare_repo(bare) != 0:
            return 1
        logger.info("Created bare git repository %s", bare)
    else:
        logger.warning(
            "No bare git repository found at %s (use --init to create it)", bare
        )

    workdir = os.path.realpath(os.getcwd())

    cfg = load_config()
    if BARE_SECTION not in cfg:
        cfg[BARE_SECTION] = {}
    cfg[BARE_SECTION][workdir] = bare
    save_config(cfg)

    logger.info("Linked %s -> %s", workdir, bare)
    return 0


def cmd_unlink(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="gitbare unlink",
        description="Remove a bare repository mapping.",
    )
    parser.add_argument(
        "workdir",
        nargs="?",
        help="Directory to unlink (default: current directory).",
    )
    args = parser.parse_args(argv)

    cfg = load_config()
    if BARE_SECTION not in cfg:
        logger.error("No bare repository mapping configured in %s", config_path())
        return 1
    mapping = cfg[BARE_SECTION]

    if args.workdir is not None:
        target = os.path.realpath(os.path.abspath(os.path.expanduser(args.workdir)))
        if target not in mapping:
            logger.error("No mapping found for %s", target)
            return 1
    else:
        target = find_mapping(cfg)
        if target is None:
            logger.error("No mapping found for %s", os.getcwd())
            return 1

    del mapping[target]
    if not mapping:
        del cfg[BARE_SECTION]
    save_config(cfg)
    logger.info("Unlinked %s", target)
    return 0


def config_path() -> str:
    return os.path.expanduser(os.environ.get("GITBARE_CONFIG", CONFIG_DEFAULT))


def create_bare_repo(bare: str) -> int:
    parent = os.path.dirname(bare)
    if parent:
        os.makedirs(parent, exist_ok=True)
    cmd = ["git", "init", "--bare", bare]
    logger.debug("Running: %s", " ".join(shlex.quote(part) for part in cmd))
    try:
        result = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        logger.error("git executable not found in PATH")
        return 1
    return result.returncode


def find_mapping(cfg: configparser.ConfigParser) -> str | None:
    if BARE_SECTION not in cfg:
        return None
    mapping = cfg[BARE_SECTION]
    directory = os.path.realpath(os.getcwd())
    while True:
        if directory in mapping:
            return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None


def is_bare_repo(bare: str) -> bool:
    cmd = ["git", "--git-dir=" + bare, "rev-parse", "--is-bare-repository"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        logger.error("git executable not found in PATH")
        return False
    return result.returncode == 0 and result.stdout.strip() == "true"


def load_config() -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    path = config_path()
    if os.path.exists(path):
        parser.read(path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, git_args = parser.parse_known_args(sys.argv[1:] if argv is None else argv)
    setup(args.verbose)

    if args.version:
        print(f"gitbare {VERSION}")
        return 0

    if not git_args or git_args[0] in ("-h", "--help"):
        parser.print_help()
        return 0

    command = git_args.pop(0)
    if command == "link":
        return cmd_link(git_args)
    if command == "unlink":
        return cmd_unlink(git_args)

    return run_git([command] + git_args)


def run_git(git_args: list[str]) -> int:
    cfg = load_config()
    workdir = find_mapping(cfg)
    if workdir is None:
        logger.error(
            "No bare repository mapping found for %s (check %s or use 'gitbare link')",
            os.getcwd(),
            config_path(),
        )
        return 1

    bare = cfg[BARE_SECTION][workdir]
    cmd = ["git", "--git-dir=" + bare, "--work-tree=" + workdir] + git_args
    logger.debug("Running: %s", " ".join(shlex.quote(part) for part in cmd))

    try:
        result = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        logger.error("git executable not found in PATH")
        return 1
    return result.returncode


def save_config(cfg: configparser.ConfigParser) -> None:
    path = config_path()
    parent = os.path.dirname(path) or "."
    os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        cfg.write(handle)
    os.chmod(path, 0o600)


def setup(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=level)


if __name__ == "__main__":
    sys.exit(main())
