#!/usr/bin/env python3
"""Tests for portable presentation gallery export."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("build_preview_site.py")
SPEC = importlib.util.spec_from_file_location("build_preview_site", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PreviewSiteTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.tasks = self.base / "tasks"
        self.out = self.base / "output"
        self.manifest = self.base / "allowlist.json"
        p = self.tasks / "active" / "TASK-0001_demo-preview" / "presentation"
        p.mkdir(parents=True)
        (p / "index.html").write_text("<h1>Demo</h1>", encoding="utf-8")
        (p / "assets").mkdir()
        (p / "assets" / "style.css").write_text("body{}", encoding="utf-8")

    def manifest_ids(self, ids):
        self.manifest.write_text(json.dumps({"schema_version":1,"public_task_ids":ids}),encoding="utf-8")

    def test_build_allowlisted_task_only(self):
        self.manifest_ids(["TASK-0001"])
        self.assertEqual(MODULE.build(self.tasks, self.manifest, self.out),["TASK-0001"])
        self.assertTrue((self.out / "TASK-0001" / "index.html").exists())
        self.assertTrue((self.out / "TASK-0001" / "assets" / "style.css").exists())
        self.assertIn('TASK-0001/index.html', (self.out / "index.html").read_text())

    def test_unlisted_task_not_published(self):
        self.manifest_ids([])
        self.assertEqual(MODULE.build(self.tasks, self.manifest, self.out),[])
        self.assertFalse((self.out / "TASK-0001").exists())

    def test_missing_task_fails_closed(self):
        self.manifest_ids(["TASK-9999"])
        with self.assertRaises(ValueError):
            MODULE.build(self.tasks, self.manifest, self.out)

    def test_unsafe_file_fails_closed(self):
        p = self.tasks / "active" / "TASK-0001_demo-preview" / "presentation"
        (p / "private.key").write_text("fake secret",encoding="utf-8")
        self.manifest_ids(["TASK-0001"])
        with self.assertRaises(ValueError):
            MODULE.build(self.tasks, self.manifest, self.out)


if __name__ == "__main__":
    unittest.main()
