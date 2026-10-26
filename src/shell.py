"""Command parsing and execution independent of the GUI."""

import shlex


class Shell:
    """Maintain an interactive shell session."""

    def __init__(self, logger=None):
        """Create an active session."""
        self.running = True
        self.cwd = "/"
        self.clear_requested = False
        self.logger = logger

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
        """Execute prototype commands."""
        if command in {"ls", "cd"}:
            return f"{command}: {args!r}"
        raise ValueError(f"unknown command: {command}")
