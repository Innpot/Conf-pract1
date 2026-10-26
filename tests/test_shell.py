"""Tests for the command parser and session lifecycle."""

import unittest

from src.shell import Shell


class ShellTests(unittest.TestCase):
    """Exercise valid and invalid input."""

    def test_empty_and_unknown(self):
        """Blank input is ignored; unknown commands are reported."""
        shell = Shell()
        self.assertEqual(shell.execute("  "), "")
        self.assertIn("unknown command", shell.execute("unknown"))

    def test_quotes(self):
        """Quoted arguments preserve spaces and malformed quotes fail."""
        shell = Shell()
        self.assertIn("a b", shell.execute('ls "a b"'))
        self.assertTrue(shell.execute('ls "').startswith("Error:"))

    def test_exit(self):
        """Exit accepts no arguments and ends the session."""
        shell = Shell()
        self.assertIn("Error:", shell.execute("exit extra"))
        self.assertTrue(shell.running)
        shell.execute("exit")
        self.assertFalse(shell.running)
