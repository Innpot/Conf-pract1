"""Application entry point."""

from src.gui import Terminal
from src.shell import Shell
from src.config import parse_args, run_script, script_lines, validate_paths
from src.event_log import EventLog
from src.vfs import VFS
import sys
import xml.etree.ElementTree as ET


def main():
    """Run the graphical shell."""
    args = parse_args()
    print(f"vfs={args.vfs!r}, log={args.log!r}, script={args.script!r}")
    try:
        validate_paths(args)
        lines = script_lines(args.script)
        vfs = VFS(args.vfs)
        shell = Shell(EventLog(args.log), vfs)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"Startup error: {error}", file=sys.stderr)
        return 1
    terminal = Terminal(shell, vfs.name)
    terminal.write(f"Configuration: {vars(args)}")
    if vfs.motd():
        terminal.write(vfs.motd())
    terminal.root.after(0, lambda: run_script(
        lines, shell, terminal.run_line
    ))
    terminal.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
