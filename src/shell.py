"""Command parsing and execution independent of the GUI."""

import shlex
from src.vfs import VFS
from src.commands import COMMANDS
from src.mutations import MUTATIONS


class Shell:
    """Maintain an interactive shell session."""

    def __init__(self, logger=None, vfs=None):
        """Create an active session."""
        self.running = True
        self.cwd = "/"
        self.clear_requested = False
        self.logger = logger
        self.vfs = vfs if vfs is not None else VFS()

    def execute(self, line):
        """Parse one command, reporting invalid syntax as text."""
        self.clear_requested = False
        try:
            if line.strip() and self.logger:
                self.logger.record(line)
            words = shlex.split(line)
            if not words:
                return ""
            command, *args = words
            if command == "exit":
                if args:
                    raise ValueError("exit: arguments are not supported")
                self.running = False
                return ""
            return self.dispatch(command, args)
        except (ValueError, OSError) as error:
            return f"Error: {error}"

    def dispatch(self, command, args):
        """Dispatch a supported command to its implementation."""
        handler = COMMANDS.get(command) or MUTATIONS.get(command)
        if handler is None:
            raise ValueError(f"unknown command: {command}")
        return handler(self, args)
