"""Configuration, startup script and XML journal checks."""

from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from src.config import parse_args, run_script, script_lines, validate_paths
from src.event_log import EventLog
from src.shell import Shell


class ConfigTests(unittest.TestCase):
    """Verify settings and observable command execution."""

    def test_input_paths_are_protected(self):
        """Log files must never overwrite VFS or startup input."""
        for options in [["--vfs", "same.xml", "--log", "same.xml"],
                        ["--script", "a.xml.tmp", "--log", "a.xml"]]:
            with self.subTest(options=options):
                with self.assertRaises(ValueError):
                    validate_paths(parse_args(options))

    def test_invalid_log_is_preserved(self):
        """Malformed XML is reported instead of silently replaced."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "log.xml"
            path.write_text("broken", encoding="utf-8")
            with self.assertRaises(ET.ParseError):
                EventLog(path)
            self.assertEqual(path.read_text(encoding="utf-8"), "broken")

    def test_parameters(self):
        """All physical paths may contain spaces."""
        args = parse_args(["--vfs", "a b", "--log", "c d",
                           "--script", "e f"])
        self.assertEqual((args.vfs, args.log, args.script),
                         ("a b", "c d", "e f"))

    def test_script_and_log(self):
        """Errors do not stop scripts; exit does; XML escapes input."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            script = path / "start.txt"
            script.write_text('# comment\nunknown\nls "<&"\nexit\nls',
                              encoding="utf-8")
            log = path / "events.xml"
            shell = Shell(EventLog(log))
            results = []
            run_script(script_lines(script), shell,
                       lambda line: results.append(shell.execute(line)))
            self.assertEqual(len(results), 3)
            events = ET.parse(log).getroot()
            self.assertEqual(len(events), 3)
            self.assertEqual(events[1].findtext("command"), 'ls "<&"')
            self.assertTrue(events[0].get("user"))
            self.assertTrue(events[0].get("timestamp"))
            EventLog(log).record("date")
            self.assertEqual(len(ET.parse(log).getroot()), 4)
