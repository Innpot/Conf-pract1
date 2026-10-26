"""VFS loading, path traversal and data decoding checks."""

from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from src.vfs import VFS, parse_node


class VFSTests(unittest.TestCase):
    """Check all fixture sizes and invalid XML structures."""

    def test_fixtures(self):
        """Minimal, flat and deep filesystems load without extraction."""
        base = Path("examples/vfs")
        self.assertEqual(VFS(base / "minimal.xml").root.children, {})
        flat = VFS(base / "files.xml")
        self.assertEqual(flat.node("/binary.bin").data, b"\0\1\2\xff")
        self.assertIn("Welcome", flat.motd())
        deep = VFS(base / "deep.xml")
        self.assertEqual(deep.resolve("../docs", "/home/student/empty"),
                         "/home/student/docs")
        self.assertEqual(deep.resolve("../../.."), "/")
        with self.assertRaises(ValueError):
            deep.resolve("/motd/..")

    def test_invalid_nodes(self):
        """Reject duplicate names, unsafe paths and invalid content."""
        invalid = [
            '<vfs><file name=".." /></vfs>',
            '<vfs><dir name="a"/><file name="a"/></vfs>',
            '<file encoding="base64">?</file>',
            '<file mode="888"/>',
            '<unknown/>',
            '<file><dir name="a"/></file>',
        ]
        for xml in invalid:
            with self.subTest(xml=xml), self.assertRaises(ValueError):
                parse_node(ET.fromstring(xml))
