#!/usr/bin/env python3
"""Tests for task discussion bundle generation; standard library only."""

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_discussions.py")
SPEC = importlib.util.spec_from_file_location("build_discussions", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class BuildDiscussionsTest(unittest.TestCase):
    def test_order_and_source_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "02_b.md").write_text("# B\n", encoding="utf-8")
            (p / "01_a.md").write_text("# A\n", encoding="utf-8")
            result = MODULE.render([p / "02_b.md", p / "01_a.md"])
            self.assertEqual(
                result,
                "<!-- Source: threads/01_a.md -->\n\n# A\n\n---\n\n"
                "<!-- Source: threads/02_b.md -->\n\n# B\n",
            )

    def test_check_detects_stale_and_write_recovers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            discussion = root / "active" / "TASK-0002_demo" / "discussion"
            threads = discussion / "threads"
            threads.mkdir(parents=True)
            (threads / "01_a.md").write_text("# A\n", encoding="utf-8")
            self.assertEqual(MODULE.process(root, write=False), 1)
            self.assertEqual(MODULE.process(root, write=True), 0)
            self.assertEqual(MODULE.process(root, write=False), 0)
            self.assertEqual(
                (discussion / "00_all.md").read_text(encoding="utf-8"),
                "<!-- Source: threads/01_a.md -->\n\n# A\n",
            )


if __name__ == "__main__":
    unittest.main()
