#!/usr/bin/env python3
"""Task registrar tests: no network, no token, no real user data."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("register_task.py")
SPEC = importlib.util.spec_from_file_location("register_task", SCRIPT)
REG = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(REG)


class RegistrarTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        base = self.root / REG.TASKS_ROOT
        (base / "active").mkdir(parents=True)
        (base / "completed" / "TASK-0001_initial").mkdir(parents=True)
        (base / "registry.json").write_text(json.dumps({"schema_version": 1, "requests": [
            {"request_key":"bootstrap-pr-13","id":"TASK-0002","slug":"review-file-format-save",
             "title":"Existing Claude task","source":"PR #13","status":"reserved-in-open-pr"}
        ]}), encoding="utf-8")

    def call(self, key="request-abc", title="New task", slug="agent-team-mvp"):
        return REG.allocate(self.root, key, slug, title, "test-agent",
                            timestamp="2026-11-16T00:00:00+01:00")

    def test_skips_reserved_pr_id(self):
        task_id, created = self.call()
        self.assertEqual((task_id, created), ("TASK-0003", True))
        path = self.root / REG.TASKS_ROOT / "active" / "TASK-0003_agent-team-mvp" / "task.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("**Status:** draft", text)
        self.assertIn("**Created:** `2026-11-16T00:00:00+01:00`", text)
        self.assertIn("Создание этой записи", text)
        REG.validate(self.root)

    def test_retry_is_idempotent(self):
        self.call()
        self.assertEqual(self.call(), ("TASK-0003", False))
        self.assertEqual(len(REG.load_registry(self.root)["requests"]), 2)

    def test_duplicate_request_key_changed_content_rejected(self):
        self.call()
        with self.assertRaises(REG.RegistrationError):
            self.call(title="Different title")

    def test_new_task_after_commit_uses_next(self):
        self.call()
        self.assertEqual(self.call(key="request-def"), ("TASK-0004", True))

    def test_existing_folder_duplicate_id_rejected(self):
        (self.root / REG.TASKS_ROOT / "active" / "TASK-0001_duplicate").mkdir()
        with self.assertRaises(REG.RegistrationError):
            REG.validate(self.root)

    def test_registry_slug_conflict_rejected(self):
        (self.root / REG.TASKS_ROOT / "active" / "TASK-0002_wrong-slug").mkdir()
        with self.assertRaises(REG.RegistrationError):
            REG.validate(self.root)

    def test_invalid_slug_and_key_rejected(self):
        with self.assertRaises(REG.RegistrationError):
            self.call(slug="../escape")
        with self.assertRaises(REG.RegistrationError):
            self.call(key="bad key")

    def test_invalid_title_rejected(self):
        with self.assertRaises(REG.RegistrationError):
            self.call(title="multi\nline")
            
    def test_new_task_refuses_to_auto_start(self):
        self.call()
        task = self.root / REG.TASKS_ROOT / "active" / "TASK-0003_agent-team-mvp" / "task.md"
        self.assertIn("**Status:** draft", task.read_text())


if __name__ == "__main__":
    unittest.main()
