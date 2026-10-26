"""Persistent XML command event journal."""

from datetime import datetime
import getpass
from pathlib import Path
import xml.etree.ElementTree as ET


class EventLog:
    """Append timestamped command invocations to a valid XML document."""

    def __init__(self, path):
        """Open an existing journal or create its parent directory."""
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.root = ET.Element("events")
        if self.path.exists():
            self.root = ET.parse(self.path).getroot()
            if self.root.tag != "events":
                raise ValueError("log root must be <events>")
        self.user = getpass.getuser()
        self.save()

    def record(self, command):
        """Record raw input, including malformed and unknown commands."""
        event = ET.SubElement(self.root, "event", {
            "timestamp": datetime.now().astimezone().isoformat(),
            "user": self.user,
        })
        ET.SubElement(event, "command").text = command
        self.save()

    def save(self):
        """Write XML through a temporary sibling to avoid partial files."""
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        ET.ElementTree(self.root).write(
            temporary, encoding="utf-8", xml_declaration=True
        )
        temporary.replace(self.path)
