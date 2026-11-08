"""Integration tests for both workflows using real adapters and fake Google APIs."""
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from fake_google import FakeGoogle, MediaDownload
from gcal_client import CalendarClient
from gcal_to_inbox import IMPORT_LOG_FILE, package_folder_name, run_workflow, short_hash
from input_to_entry_2 import InboxToEntryDriveWorkflow
from mamton_drive_client import DriveClient


class CalendarDriveEntryTest(unittest.TestCase):
    def setUp(self):
        self.enterContext(redirect_stdout(io.StringIO()))
        self.enterContext(patch("mamton_drive_client.MediaIoBaseDownload", MediaDownload))
        self.enterContext(patch("socket.socket.connect", side_effect=AssertionError("Network access")))
        for target in ("mamton_drive_client.build", "gcal_client.build", "gcal_to_inbox.gapi_build"):
            self.enterContext(patch(target, side_effect=AssertionError("Real Google service requested")))
        self.reset_services()

    def reset_services(self):
        self.google = FakeGoogle()
        self.event = self.make_event("test-event")
        self.google.calendars["incoming"][self.event["id"]] = self.event

    @staticmethod
    def make_event(event_id):
        start = datetime.now(timezone.utc).replace(microsecond=0)
        return {
            "id": event_id,
            "summary": "Synthetic diary entry",
            "description": "This is fixture text.",
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": (start + timedelta(hours=1)).isoformat()},
        }

    def drive(self):
        with patch.object(DriveClient, "_build_service", return_value=self.google):
            return DriveClient(Path("unused-credentials"), Path("unused-token"))

    def import_calendar(self, **kwargs):
        return run_workflow(
            self.drive(), CalendarClient(self.google), "root", "Inbox", "Processed",
            inbox_calendar_id="incoming", processed_calendar_id="processed", **kwargs,
        )

    def create_entries(self, **kwargs):
        return InboxToEntryDriveWorkflow(
            self.drive(), root_folder_id="root", **kwargs,
        ).run()

    def files_named(self, name):
        return [node for node in self.google.nodes.values() if node["name"] == name]

    def unique_file(self, name):
        files = self.files_named(name)
        self.assertEqual(len(files), 1, name)
        return files[0]

    def json_at(self, path):
        node = self.google.nodes["root"]
        for name in path.split("/"):
            matches = [child for child in self.google.children(node["id"]) if child["name"] == name]
            self.assertEqual(len(matches), 1, path)
            node = matches[0]
        return json.loads(node["data"])

    def assert_committed(self, result=None):
        entry = json.loads(self.unique_file("ENTRY.json")["data"])
        entry_date = self.event["start"]["dateTime"][:10]
        self.assertEqual(entry["time"]["entryDate"], entry_date)
        self.assertEqual(entry["title"], self.event["summary"])
        self.assertEqual(entry["source"]["external"]["eventId"], self.event["id"])
        processing = self.json_at(entry["source"]["rawInputRefs"][0])
        self.assertEqual(processing["createdEntities"][0]["id"], entry["id"])
        entry_path = processing["createdEntities"][0]["path"]
        self.assertEqual(self.json_at(entry_path), entry)
        folder = entry_path.rsplit("/", 1)[0]
        revision = self.json_at(f"{folder}/revisions/000_raw/revision.json")
        self.assertEqual(revision["entryId"], entry["id"])
        links = self.json_at(f"{folder}/links/source_raw_inputs.json")
        self.assertEqual(links["rawSources"][0]["rawInputId"], processing["rawInputId"])
        for name in ("MESSAGE.json", "source_event.json", "raw_text.md"):
            self.assertEqual(len(self.files_named(name)), 2, name)
        self.assertEqual(self.json_at(f'{processing["sourceArchivePath"]}/source_event.json'), self.event)
        self.assertIn(b"This is fixture text.", self.unique_file("text.md")["data"])
        if result is not None:
            self.assertEqual(entry["id"], result.entry_id)

    def test_normal_path_and_clean_rerun(self):
        imported, = self.import_calendar()
        self.assertTrue(imported.success)
        self.assertTrue(imported.moved)
        self.assertEqual(self.google.calendars["incoming"], {})
        self.assertIn("test-event", self.google.calendars["processed"])
        saved, = self.create_entries()
        self.assertEqual(saved.status, "success")
        self.assert_committed(saved)
        changes = self.google.mutations.copy()
        self.assertEqual(self.import_calendar(), [])
        self.assertEqual(self.create_entries(), [])
        self.assertEqual(self.google.mutations, changes)

    def test_partial_calendar_package_is_repaired_before_move(self):
        for name in ("raw_text.md", "source_event.json", "MESSAGE.json"):
            for phase in ("before", "after"):
                with self.subTest(name=name, phase=phase):
                    self.reset_services()
                    self.google.failure = ("create", name, phase)
                    failed, = self.import_calendar()
                    self.assertFalse(failed.success)
                    self.assertIn("test-event", self.google.calendars["incoming"])
                    self.assertEqual(self.create_entries(), [])
                    recovered, = self.import_calendar()
                    self.assertTrue(recovered.moved)
                    saved, = self.create_entries()
                    self.assertEqual(saved.status, "success")
                    self.assert_committed(saved)

    def test_interrupted_package_publication_recovers(self):
        for phase in ("before", "after"):
            with self.subTest(phase=phase):
                self.reset_services()
                now = datetime.now(timezone.utc)
                events = CalendarClient(self.google).list_events(
                    "incoming", now - timedelta(days=1), now + timedelta(days=1),
                )
                folder_name = package_folder_name(events[0], "incoming")
                self.google.failure = ("move", folder_name, phase)
                failed, = self.import_calendar()
                self.assertFalse(failed.success)
                self.assertIn("test-event", self.google.calendars["incoming"])
                if phase == "before":
                    self.assertEqual(self.create_entries(), [])
                recovered, = self.import_calendar()
                self.assertTrue(recovered.moved)
                saved, = self.create_entries()
                self.assert_committed(saved)

    def test_missing_source_snapshot_is_not_consumed_and_is_repaired(self):
        self.google.failure = ("calendar_move", "test-event", "before")
        self.import_calendar()
        snapshot = self.unique_file("source_event.json")
        del self.google.nodes[snapshot["id"]]
        self.assertEqual(self.create_entries(), [])
        recovered, = self.import_calendar()
        self.assertTrue(recovered.moved)
        saved, = self.create_entries()
        self.assert_committed(saved)

    def test_interrupted_entry_save_resumes_without_duplicates(self):
        for operation, name in [
            ("copy", "source_event.json"),
            ("create", "entry.md"),
            ("create", "revision.json"),
            ("create", "text.md"),
            ("create", "source_raw_inputs.json"),
            ("create", "PROCESSING_RESULT.json"),
            ("create", "ENTRY.json"),
            ("move", None),
        ]:
            for phase in ("before", "after"):
                with self.subTest(operation=operation, name=name, phase=phase):
                    self.reset_services()
                    imported, = self.import_calendar()
                    self.google.failure = (operation, name or imported.folder_name, phase)
                    failed, = self.create_entries()
                    self.assertEqual(failed.status, "failed")
                    if operation == "move" or (name, phase) == ("ENTRY.json", "after"):
                        entry = self.unique_file("ENTRY.json")
                        self.json_at(json.loads(entry["data"])["source"]["rawInputRefs"][0])
                    else:
                        self.assertEqual(self.files_named("ENTRY.json"), [])
                    results = self.create_entries()
                    if (operation, phase) == ("move", "after"):
                        self.assertEqual(results, [])
                    else:
                        saved, = results
                        self.assertEqual(saved.status, "success")
                    self.assert_committed()
                    self.assertEqual(self.create_entries(), [])

    def test_rescheduled_redelivery_with_no_index_uses_existing_legacy_archive(self):
        self.google.failure = ("create", IMPORT_LOG_FILE, "before")
        imported, = self.import_calendar()
        date = self.event["start"]["dateTime"][:10]
        legacy_hash = short_hash(f'incoming|test-event|{self.event["start"]["dateTime"]}')
        package = self.unique_file(imported.folder_name)
        package["name"] = f"{date}__google_calendar__event_{legacy_hash}"
        message = self.unique_file("MESSAGE.json")
        data = json.loads(message["data"])
        data["id"] = f"raw_gcal_event_{legacy_hash}"
        message["data"] = json.dumps(data).encode()
        original, = self.create_entries()
        self.assert_committed(original)
        self.assertEqual(self.files_named(IMPORT_LOG_FILE), [])

        replay = dict(self.google.calendars["processed"].pop("test-event"))
        replay["start"] = {"dateTime": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()}
        replay["end"] = {"dateTime": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()}
        self.google.calendars["incoming"]["test-event"] = replay
        imported, = self.import_calendar()
        self.assertTrue(imported.skipped)
        self.assertTrue(imported.moved)
        self.assertEqual(self.create_entries(), [])
        self.assert_committed(original)

    def test_calendar_move_failure_retries_after_drive_package_is_archived(self):
        for phase in ("before", "after"):
            with self.subTest(phase=phase):
                self.reset_services()
                self.google.failure = ("calendar_move", "test-event", phase)
                imported, = self.import_calendar()
                self.assertFalse(imported.success)
                saved, = self.create_entries()
                results = self.import_calendar()
                if phase == "before":
                    retried, = results
                    self.assertTrue(retried.skipped)
                    self.assertTrue(retried.moved)
                else:
                    self.assertEqual(results, [])
                self.assertIn("test-event", self.google.calendars["processed"])
                self.assert_committed(saved)

    def test_multiple_events_are_imported_across_api_pages(self):
        for event_id in ("another-event", "third-event"):
            self.google.calendars["incoming"][event_id] = self.make_event(event_id)
        self.assertEqual(sum(result.moved for result in self.import_calendar()), 3)
        saved = self.create_entries()
        self.assertEqual([result.status for result in saved], ["success"] * 3)
        self.assertEqual(len({result.entry_id for result in saved}), 3)
        self.assertEqual(len(self.files_named("ENTRY.json")), 3)

    def test_empty_event_is_stored_for_review_without_entry(self):
        self.event["summary"] = ""
        self.event["description"] = ""
        imported, = self.import_calendar()
        self.assertTrue(imported.moved)
        self.assertEqual(imported.status, "needs_review")
        message = self.json_at(f"inbox/needs_review/{imported.folder_name}/MESSAGE.json")
        self.assertTrue(message["ai"]["needsReview"])
        self.assertEqual(self.create_entries(), [])

    def test_dry_runs_do_not_mutate_google_services(self):
        self.import_calendar(dry_run=True)
        self.assertEqual(self.google.mutations, [])
        self.import_calendar()
        changes = self.google.mutations.copy()
        result, = self.create_entries(dry_run=True)
        self.assertEqual(result.status, "dry_run")
        self.assertEqual(self.google.mutations, changes)


if __name__ == "__main__":
    unittest.main()
