"""Command-line settings and startup script processing."""

import argparse
from pathlib import Path


def parse_args(argv=None):
    """Read physical VFS, XML log and startup script paths."""
    parser = argparse.ArgumentParser(description="Variant 20 GUI shell")
    parser.add_argument("--vfs", default="examples/vfs/deep.xml")
    parser.add_argument("--log", default="logs/events.xml")
    parser.add_argument("--script")
    return parser.parse_args(argv)


def script_lines(path):
    """Read UTF-8 commands, ignoring empty lines and full-line comments."""
    if not path:
        return []
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    return [line for line in lines if line.strip()
            and not line.lstrip().startswith("#")]


def run_script(lines, shell, callback):
    """Execute commands in order, continuing after command errors."""
    for line in lines:
        if not shell.running:
            break
        callback(line)


def validate_paths(args):
    """Prevent the log or its temporary file from overwriting input."""
    log = Path(args.log).resolve()
    temporary = log.with_suffix(log.suffix + ".tmp")
    inputs = [Path(args.vfs).resolve()]
    if args.script:
        inputs.append(Path(args.script).resolve())
    if log in inputs or temporary in inputs:
        raise ValueError("log paths must differ from VFS and script paths")
