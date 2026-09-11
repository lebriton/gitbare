import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import gitbare as cli


class GitbareTestCase(unittest.TestCase):
    def setUp(self):
        self._old_cwd = os.getcwd()
        self._old_config = os.environ.get("GITBARE_CONFIG")
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "config")
        os.environ["GITBARE_CONFIG"] = self.config_path
        self.workdir = os.path.join(self.tmpdir, "work")
        self.bare_dir = os.path.join(self.tmpdir, "bare.git")
        os.makedirs(self.workdir)
        subprocess.run(["git", "init", "--bare", "-q", self.bare_dir], check=True)

    def tearDown(self):
        os.chdir(self._old_cwd)
        if self._old_config is None:
            os.environ.pop("GITBARE_CONFIG", None)
        else:
            os.environ["GITBARE_CONFIG"] = self._old_config
        shutil.rmtree(self.tmpdir)

    def chdir(self, path: str) -> None:
        os.chdir(path)


class ConfigTests(GitbareTestCase):
    def test_config_path_uses_environment(self):
        self.assertEqual(cli.config_path(), self.config_path)

    def test_load_config_missing_file_is_empty(self):
        self.assertEqual(cli.load_config().sections(), [])

    def test_load_config_preserves_path_case(self):
        with open(self.config_path, "w", encoding="utf-8") as handle:
            handle.write("[bare]\n/Home/User/Project = /Home/User/project.git\n")
        mapping = cli.load_config()[cli.BARE_SECTION]
        self.assertEqual(mapping["/Home/User/Project"], "/Home/User/project.git")


class LinkTests(GitbareTestCase):
    def test_link_writes_mapping(self):
        self.chdir(self.workdir)
        self.assertEqual(cli.cmd_link([self.bare_dir]), 0)
        mapping = cli.load_config()[cli.BARE_SECTION]
        self.assertEqual(mapping[os.path.realpath(self.workdir)], self.bare_dir)

    def test_link_resolves_relative_bare_path(self):
        self.chdir(self.workdir)
        relative = os.path.relpath(self.bare_dir, self.workdir)
        self.assertEqual(cli.cmd_link([relative]), 0)
        mapping = cli.load_config()[cli.BARE_SECTION]
        self.assertEqual(mapping[os.path.realpath(self.workdir)], self.bare_dir)

    def test_link_overwrites_existing_mapping(self):
        self.chdir(self.workdir)
        cli.cmd_link([self.bare_dir])
        other_bare = os.path.join(self.tmpdir, "other.git")
        subprocess.run(["git", "init", "--bare", "-q", other_bare], check=True)
        cli.cmd_link([other_bare])
        mapping = cli.load_config()[cli.BARE_SECTION]
        self.assertEqual(mapping[os.path.realpath(self.workdir)], other_bare)


class UnlinkTests(GitbareTestCase):
    def test_unlink_current_directory(self):
        self.chdir(self.workdir)
        cli.cmd_link([self.bare_dir])
        self.assertEqual(cli.cmd_unlink([]), 0)
        self.assertNotIn(cli.BARE_SECTION, cli.load_config())

    def test_unlink_explicit_workdir(self):
        self.chdir(self.workdir)
        cli.cmd_link([self.bare_dir])
        other = os.path.join(self.tmpdir, "other")
        os.makedirs(other)
        self.assertEqual(cli.cmd_unlink([other]), 1)
        self.assertEqual(cli.cmd_unlink([self.workdir]), 0)

    def test_unlink_without_mapping_fails(self):
        self.chdir(self.workdir)
        self.assertEqual(cli.cmd_unlink([]), 1)

    def test_unlink_wrong_explicit_workdir_fails(self):
        self.chdir(self.workdir)
        cli.cmd_link([self.bare_dir])
        other = os.path.join(self.tmpdir, "other")
        os.makedirs(other)
        self.assertEqual(cli.cmd_unlink([other]), 1)


class MappingTests(GitbareTestCase):
    def link_current(self) -> None:
        self.chdir(self.workdir)
        self.assertEqual(cli.cmd_link([self.bare_dir]), 0)

    def test_find_mapping_exact(self):
        self.link_current()
        self.assertEqual(
            cli.find_mapping(cli.load_config()), os.path.realpath(self.workdir)
        )

    def test_find_mapping_missing_section(self):
        self.chdir(self.workdir)
        self.assertIsNone(cli.find_mapping(cli.load_config()))

    def test_find_mapping_no_match(self):
        self.link_current()
        other = os.path.join(self.tmpdir, "other")
        os.makedirs(other)
        self.chdir(other)
        self.assertIsNone(cli.find_mapping(cli.load_config()))

    def test_find_mapping_parent_directory(self):
        self.link_current()
        nested = os.path.join(self.workdir, "nested", "deeper")
        os.makedirs(nested)
        self.chdir(nested)
        self.assertEqual(
            cli.find_mapping(cli.load_config()), os.path.realpath(self.workdir)
        )


class RunGitTests(GitbareTestCase):
    def test_run_git_no_mapping(self):
        self.chdir(self.workdir)
        self.assertEqual(cli.run_git(["status"]), 1)

    def test_run_git_passthrough_exit_code(self):
        self.chdir(self.workdir)
        cli.cmd_link([self.bare_dir])
        bare = cli.load_config()[cli.BARE_SECTION][os.path.realpath(self.workdir)]
        cmd = [
            "git",
            "--git-dir=" + bare,
            "--work-tree=" + self.workdir,
            "rev-parse",
            "--is-bare-repository",
        ]
        self.assertEqual(cli.run_git(cmd[2:]), 0)

    def test_end_to_end_commit(self):
        self.chdir(self.workdir)
        cli.cmd_link([self.bare_dir])
        self.assertEqual(cli.run_git(["config", "user.name", "Test User"]), 0)
        self.assertEqual(cli.run_git(["config", "user.email", "test@example.com"]), 0)
        with open(
            os.path.join(self.workdir, "file.txt"), "w", encoding="utf-8"
        ) as handle:
            handle.write("hello gitbare\n")
        self.assertEqual(cli.run_git(["add", "file.txt"]), 0)
        self.assertEqual(cli.run_git(["commit", "-m", "first commit"]), 0)
        result = subprocess.run(
            ["git", "--git-dir=" + self.bare_dir, "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertTrue(result.stdout.strip())


class MainTests(GitbareTestCase):
    def test_main_git_passthrough(self):
        self.chdir(self.workdir)
        cli.main(["link", self.bare_dir])
        self.assertEqual(cli.main(["status"]), 0)

    def test_main_link_then_unlink(self):
        self.chdir(self.workdir)
        self.assertEqual(cli.main(["link", self.bare_dir]), 0)
        self.assertEqual(cli.main(["unlink"]), 0)

    def test_main_no_args_prints_help(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(cli.main([]), 0)
        self.assertIn("gitbare", buffer.getvalue())

    def test_main_verbose_git_passthrough(self):
        self.chdir(self.workdir)
        cli.main(["link", self.bare_dir])
        self.assertEqual(cli.main(["-v", "status"]), 0)

    def test_main_unknown_command_uses_git(self):
        self.chdir(self.workdir)
        cli.main(["link", self.bare_dir])
        self.assertEqual(cli.main(["not-a-git-command"]), 1)


if __name__ == "__main__":
    unittest.main()
