"""XML-backed filesystem whose state is held entirely in memory."""

import base64
from dataclasses import dataclass, field
import posixpath
import re
import xml.etree.ElementTree as ET


@dataclass
class Node:
    """Represent a directory or binary file and its permission bits."""

    directory: bool
    mode: int
    data: bytes = b""
    children: dict = field(default_factory=dict)


def parse_node(element):
    """Validate and recursively decode a VFS node."""
    directory = element.tag in {"vfs", "dir"}
    if element.tag not in {"vfs", "dir", "file"}:
        raise ValueError(f"invalid VFS element: {element.tag}")
    mode = element.get("mode", "755" if directory else "644")
    if not re.fullmatch(r"[0-7]{3,4}", mode):
        raise ValueError(f"invalid permission mode: {mode}")
    node = Node(directory, int(mode, 8))
    if directory:
        for child in element:
            name = child.get("name", "")
            if not name or name in {".", ".."} or "/" in name:
                raise ValueError(f"invalid VFS name: {name!r}")
            if name in node.children:
                raise ValueError(f"duplicate VFS name: {name}")
            node.children[name] = parse_node(child)
    else:
        if len(element):
            raise ValueError("file cannot contain child elements")
        encoding = element.get("encoding", "utf-8")
        text = element.text or ""
        if encoding == "base64":
            node.data = base64.b64decode("".join(text.split()),
                                        validate=True)
        elif encoding == "utf-8":
            node.data = text.encode("utf-8")
        else:
            raise ValueError(f"unsupported encoding: {encoding}")
    return node


class VFS:
    """Resolve virtual paths without accessing host filesystem paths."""

    def __init__(self, path=None):
        """Load XML once or create an empty in-memory filesystem."""
        self.name = "VFS"
        self.root = Node(True, 0o755)
        if path is not None:
            element = ET.parse(path).getroot()
            if element.tag != "vfs":
                raise ValueError("VFS root must be <vfs>")
            self.name = element.get("name", str(path))
            self.root = parse_node(element)

    def resolve(self, path, cwd="/"):
        """Resolve dot components and verify intermediate directories."""
        if not path:
            raise ValueError("empty path")
        parts = [] if path.startswith("/") else cwd.strip("/").split("/")
        parts = [part for part in parts if part]
        for part in path.split("/"):
            current = self.node("/" + "/".join(parts))
            if not current.directory:
                raise ValueError(f"not a directory: {part or path}")
            if part == "..":
                parts = parts[:-1]
            elif part not in {"", "."}:
                parts.append(part)
        result = "/" + "/".join(parts)
        self.node(result)
        return result

    def node(self, path):
        """Look up an already canonical absolute path."""
        node = self.root
        for part in filter(None, path.split("/")):
            if not node.directory:
                raise ValueError(f"not a directory: {path}")
            if part not in node.children:
                raise ValueError(f"no such file or directory: {path}")
            node = node.children[part]
        return node

    def motd(self):
        """Return optional root message of the day as UTF-8 text."""
        node = self.root.children.get("motd")
        if node is None or node.directory:
            return ""
        return node.data.decode("utf-8", errors="replace")
