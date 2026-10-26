"""GUI integration test, skipped on hosts without a display."""

import tkinter as tk
import unittest

from src.gui import Terminal
from src.shell import Shell
from src.vfs import VFS


class GuiTests(unittest.TestCase):
    """Check the actual Tk widget state after command submission."""

    def test_interactive_terminal(self):
        """Title, quoted input, errors, clearing and exit work in Tk."""
        shell = Shell(vfs=VFS("examples/vfs/deep.xml"))
        try:
            terminal = Terminal(shell, shell.vfs.name)
        except tk.TclError as error:
            self.skipTest(str(error))
        terminal.root.withdraw()
        self.assertIn("Variant 20", terminal.root.title())
        terminal.entry.insert(0, 'ls "/home/student/docs/with spaces.txt"')
        terminal.submit()
        self.assertIn("with spaces.txt", terminal.output.get("1.0", "end"))
        terminal.run_line("unknown")
        self.assertIn("Error:", terminal.output.get("1.0", "end"))
        terminal.run_line("clear")
        self.assertEqual(terminal.output.get("1.0", "end").strip(), "")
        terminal.run_line("exit")
        self.assertFalse(shell.running)
