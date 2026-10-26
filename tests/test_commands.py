"""Behavioral tests for basic commands."""

import unittest
from src.shell import Shell
from src.vfs import VFS


class CommandTests(unittest.TestCase):
    """Exercise command modes, errors and session state."""

    def setUp(self):
        """Load an independent in-memory filesystem per test."""
        self.shell = Shell(vfs=VFS("examples/vfs/deep.xml"))

    def test_listing_and_navigation(self):
        """List flags, quoted paths and relative paths work together."""
        self.assertNotIn(".hidden", self.shell.execute("ls"))
        self.assertIn("0644 .hidden", self.shell.execute("ls -al"))
        self.shell.execute("cd /home/student/docs")
        self.assertEqual(self.shell.execute('ls "with spaces.txt"'),
                         "with spaces.txt")
        self.shell.execute("cd ..")
        self.assertEqual(self.shell.cwd, "/home/student")
        self.shell.execute("cd")
        self.assertEqual(self.shell.cwd, "/")

    def test_date_calendar_clear(self):
        """Calendar includes leap day and clear sets a one-shot signal."""
        self.assertRegex(self.shell.execute("date +%Y-%m-%d"),
                         r"^\d{4}-\d{2}-\d{2}$")
        self.assertIn("29", self.shell.execute("cal 2 2024"))
        self.assertIn("December", self.shell.execute("cal 2026"))
        self.assertNotEqual(self.shell.execute("cal"), "")
        self.shell.execute("clear")
        self.assertTrue(self.shell.clear_requested)
        self.shell.execute("ls")
        self.assertFalse(self.shell.clear_requested)

    def test_errors_leave_cwd_unchanged(self):
        """Malformed arguments fail without corrupting session state."""
        for line in ["cd /motd", "cd /missing", "cd a b", "ls -z",
                     "ls a b", "date bad", "clear extra", "cal 13 2026",
                     "cal 0", "cal bad", "cal 1 2 3"]:
            with self.subTest(line=line):
                self.assertTrue(self.shell.execute(line).startswith("Error:"))
                self.assertEqual(self.shell.cwd, "/")
