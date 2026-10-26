"""Basic shell commands operating on virtual paths."""

import calendar
from datetime import datetime
import posixpath


def check_count(args, minimum, maximum, usage):
    """Validate positional argument count."""
    if not minimum <= len(args) <= maximum:
        raise ValueError(f"usage: {usage}")


def listing_arguments(args):
    """Separate ls flags from its optional positional path."""
    flags = set()
    paths = []
    options = True
    for arg in args:
        if options and arg == "--":
            options = False
        elif options and arg.startswith("-") and arg != "-":
            flags.update(arg[1:])
        else:
            paths.append(arg)
    if flags - {"a", "l"}:
        raise ValueError("ls: supported options are -a and -l")
    check_count(paths, 0, 1, "ls [-a] [-l] [--] [path]")
    return flags, paths


def list_directory(shell, args):
    """List one path, optionally including dotfiles and mode metadata."""
    flags, paths = listing_arguments(args)
    path = shell.vfs.resolve(paths[0] if paths else ".", shell.cwd)
    node = shell.vfs.node(path)
    entries = node.children if node.directory else {
        posixpath.basename(path): node
    }
    rows = []
    for name, child in sorted(entries.items()):
        if node.directory and name.startswith(".") and "a" not in flags:
            continue
        label = name + ("/" if child.directory else "")
        if "l" in flags:
            label = f"{child.mode:04o} {label}"
        rows.append(label)
    return "\n".join(rows)


def change_directory(shell, args):
    """Change directory; no argument selects the virtual root."""
    check_count(args, 0, 1, "cd [path]")
    path = shell.vfs.resolve(args[0] if args else "/", shell.cwd)
    if not shell.vfs.node(path).directory:
        raise ValueError(f"cd: not a directory: {path}")
    shell.cwd = path
    return ""


def clear_screen(shell, args):
    """Ask the GUI to clear the transcript."""
    check_count(args, 0, 0, "clear")
    shell.clear_requested = True
    return ""


def show_date(shell, args):
    """Display local date/time, optionally using a strftime format."""
    check_count(args, 0, 1, "date [+FORMAT]")
    if args and not args[0].startswith("+"):
        raise ValueError("usage: date [+FORMAT]")
    pattern = args[0][1:] if args else "%Y-%m-%d %H:%M:%S %z"
    return datetime.now().astimezone().strftime(pattern)


def show_calendar(shell, args):
    """Show this month, a whole year, or a given month and year."""
    check_count(args, 0, 2, "cal [[month] year]")
    today = datetime.now()
    cal = calendar.TextCalendar(firstweekday=calendar.MONDAY)
    if not args:
        return cal.formatmonth(today.year, today.month).rstrip()
    year = int(args[-1])
    if not datetime.min.year <= year <= datetime.max.year:
        raise ValueError("cal: year must be between 1 and 9999")
    if len(args) == 1:
        return cal.formatyear(year).rstrip()
    month = int(args[0])
    if month not in range(1, len(calendar.month_name)):
        raise ValueError("cal: month must be between 1 and 12")
    return cal.formatmonth(year, month).rstrip()


COMMANDS = {
    "ls": list_directory,
    "cd": change_directory,
    "clear": clear_screen,
    "date": show_date,
    "cal": show_calendar,
}
