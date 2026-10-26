"""In-memory chmod and mv implementations."""

import posixpath
import re

from src.commands import check_count


def apply_mode(current, specification):
    """Apply octal permissions or symbolic u/g/o/a clauses."""
    if re.fullmatch(r"[0-7]{3,4}", specification):
        return int(specification, 8)
    for clause in specification.split(","):
        match = re.fullmatch(r"([ugoa]*)([+=-])([rwx]*)", clause)
        if match is None:
            raise ValueError(f"chmod: invalid mode: {specification}")
        who, operator, permissions = match.groups()
        who = "ugo" if not who or "a" in who else who
        bits = sum(value for key, value in {"r": 4, "w": 2, "x": 1}.items()
                   if key in permissions)
        for subject in set(who):
            shift = {"u": 6, "g": 3, "o": 0}[subject]
            mask = bits << shift
            if operator == "=":
                current = (current & ~(0o7 << shift)) | mask
            elif operator == "+":
                current |= mask
            else:
                current &= ~mask
    return current


def change_mode(shell, args):
    """Change one node's permissions, optionally recursively."""
    recursive = bool(args and args[0] == "-R")
    values = args[1:] if recursive else args
    check_count(values, 2, 2, "chmod [-R] MODE path")
    mode, path = values
    apply_mode(0, mode)
    node = shell.vfs.node(shell.vfs.resolve(path, shell.cwd))
    pending = [node]
    while pending:
        current = pending.pop()
        current.mode = apply_mode(current.mode, mode)
        if recursive:
            pending.extend(current.children.values())
    return ""


def destination_path(shell, target, source):
    """Resolve an existing destination or a new name in an existing dir."""
    parent_text, name = posixpath.split(target)
    if name in {"", ".", ".."}:
        resolved = shell.vfs.resolve(target, shell.cwd)
    else:
        parent = shell.vfs.resolve(parent_text or ".", shell.cwd)
        if not shell.vfs.node(parent).directory:
            raise ValueError("mv: destination parent is not a directory")
        resolved = posixpath.join(parent, name)
    parent = shell.vfs.node(posixpath.dirname(resolved) or "/")
    node = shell.vfs.root if resolved == "/" else parent.children.get(
        posixpath.basename(resolved)
    )
    if node is not None and node.directory:
        resolved = posixpath.join(resolved, posixpath.basename(source))
    return resolved


def validate_move(shell, source, destination, node):
    """Reject cycles, type conflicts and nonempty directory replacement."""
    if source == "/":
        raise ValueError("mv: cannot move root")
    if source == destination:
        raise ValueError("mv: source and destination are the same")
    if node.directory and destination.startswith(source + "/"):
        raise ValueError("mv: cannot move a directory into itself")
    parent = shell.vfs.node(posixpath.dirname(destination))
    existing = parent.children.get(posixpath.basename(destination))
    if existing is not None:
        if existing.directory != node.directory:
            raise ValueError("mv: source and destination types differ")
        if existing.directory and existing.children:
            raise ValueError("mv: destination directory is not empty")


def move(shell, args):
    """Rename or move a file/directory and update cwd if necessary."""
    check_count(args, 2, 2, "mv source destination")
    source = shell.vfs.resolve(args[0], shell.cwd)
    if not args[1]:
        raise ValueError("mv: empty destination")
    node = shell.vfs.node(source)
    destination = destination_path(shell, args[1], source)
    validate_move(shell, source, destination, node)
    old_parent = shell.vfs.node(posixpath.dirname(source))
    new_parent = shell.vfs.node(posixpath.dirname(destination))
    new_parent.children[posixpath.basename(destination)] = node
    del old_parent.children[posixpath.basename(source)]
    if shell.cwd == source or shell.cwd.startswith(source + "/"):
        shell.cwd = destination + shell.cwd[len(source):]
    return ""


MUTATIONS = {"chmod": change_mode, "mv": move}
