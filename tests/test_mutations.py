"""Mutation correctness and persistence isolation tests."""

from pathlib import Path
import unittest

from src.mutations import apply_mode
from src.shell import Shell
from src.vfs import VFS


class MutationTests(unittest.TestCase):
    """Test state changes, rejected moves and source immutability."""

    def setUp(self):
        """Load an isolated fixture and keep its original bytes."""
        self.path = Path("examples/vfs/deep.xml")
        self.original = self.path.read_bytes()
        self.shell = Shell(vfs=VFS(self.path))

    def tearDown(self):
        """Every test must leave the source XML untouched."""
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_modes(self):
        """Support octal, symbolic and recursive chmod."""
        self.assertEqual(apply_mode(0o644, "u+x,g=r,o="), 0o740)
        self.assertEqual(apply_mode(0o777, "a-w"), 0o555)
        self.assertEqual(self.shell.execute("chmod -R 700 /home"), "")
        node = self.shell.vfs.node("/home/student/docs/notes.txt")
        self.assertEqual(node.mode, 0o700)
        self.assertIn("Error:", self.shell.execute("chmod 999 /home"))

    def test_rename_ancestor_updates_cwd(self):
        """Moving an ancestor preserves current directory identity."""
        self.shell.execute("cd /home/student/docs")
        self.assertEqual(self.shell.execute("mv /home/student /tmp"), "")
        self.assertEqual(self.shell.cwd, "/tmp/student/docs")
        self.assertIn("notes.txt", self.shell.execute("ls"))

    def test_move_and_overwrite_file(self):
        """Moving to directories and replacing files preserves content."""
        self.assertEqual(self.shell.execute("mv /motd /tmp"), "")
        self.assertEqual(self.shell.execute("mv /tmp/motd /.hidden"), "")
        self.assertIn(b"Welcome", self.shell.vfs.node("/.hidden").data)
        self.assertNotIn("motd", self.shell.vfs.root.children)

    def test_invalid_moves_are_atomic(self):
        """Rejected moves do not remove or duplicate filesystem entries."""
        before = repr(self.shell.vfs.root)
        for line in ["mv / /tmp", "mv /home /home/student",
                     "mv /motd /motd", "mv /absent /tmp",
                     "mv /motd /absent/name", "mv /motd /motd/new",
                     'mv /motd ""', "mv /home /motd", "mv"]:
            with self.subTest(line=line):
                self.assertIn("Error:", self.shell.execute(line))
                self.assertEqual(repr(self.shell.vfs.root), before)
