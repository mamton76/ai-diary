"""In-memory Google API resources with a one-shot mutation failure."""
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from itertools import count
import re
from typing import Any

from mamton_drive_client import DRIVE_FOLDER_MIME


@dataclass
class Request:
    action: Callable[[], Any]

    def execute(self):
        return deepcopy(self.action())


class MediaDownload:
    def __init__(self, stream, request):
        self.stream = stream
        self.request = request

    def next_chunk(self):
        self.stream.write(self.request.execute())
        return None, True


class FakeGoogle:
    def __init__(self):
        self.nodes = {
            "root": {"id": "root", "name": "root", "mimeType": DRIVE_FOLDER_MIME, "parents": []}
        }
        self.calendars = {"incoming": {}, "processed": {}}
        self.file_ids = count(1)
        self.failure = None
        self.mutations = []

    def files(self):
        return DriveFiles(self)

    def events(self):
        return CalendarEvents(self)

    def mutation(self, operation, name, action):
        def execute():
            self.mutations.append((operation, name))
            self.interrupt(operation, name, "before")
            result = action()
            self.interrupt(operation, name, "after")
            return result
        return Request(execute)

    def interrupt(self, operation, name, phase):
        if self.failure == (operation, name, phase):
            self.failure = None
            raise OSError(f"Simulated Google API interruption {phase} {operation}: {name}")

    def children(self, parent_id):
        return [node for node in self.nodes.values() if parent_id in node["parents"]]


class DriveFiles:
    def __init__(self, google):
        self.google = google

    def list(self, *, q, pageToken=None, **kwargs):
        parent_id, = re.findall(r"'([^']+)' in parents", q)
        results = self.google.children(parent_id)
        for field, operator, value in re.findall(r"(name|mimeType) (!?=) '([^']+)'", q):
            results = [node for node in results if (node[field] == value) == (operator == "=")]
        offset = int(pageToken or 0)
        page = {"files": results[offset:offset + 2]}
        if "nextPageToken" in kwargs["fields"] and offset + 2 < len(results):
            page["nextPageToken"] = str(offset + 2)
        return Request(lambda: page)

    def get(self, *, fileId, **kwargs):
        return Request(lambda: self.google.nodes[fileId])

    def get_media(self, *, fileId):
        return Request(lambda: self.google.nodes[fileId]["data"])

    def _store(self, metadata, data=None):
        file_id = f"file-{next(self.google.file_ids)}"
        node = {**metadata, "id": file_id}
        if data is not None:
            node["data"] = data
        self.google.nodes[file_id] = node
        return node

    def create(self, *, body, media_body=None, **kwargs):
        if media_body is None:
            action = lambda: self._store(body)
        else:
            action = lambda: self._store(
                {**body, "mimeType": media_body.mimetype()},
                media_body.getbytes(0, media_body.size()),
            )
        return self.google.mutation("create", body["name"], action)

    def copy(self, *, fileId, body, **kwargs):
        source = self.google.nodes[fileId]
        return self.google.mutation("copy", body["name"], lambda: self._store(
            {**source, **body}, source["data"],
        ))

    def update(self, *, fileId, body=None, media_body=None,
               addParents=None, removeParents=None, **kwargs):
        node = self.google.nodes[fileId]

        def action():
            node.update(body or {})
            if media_body is not None:
                node["data"] = media_body.getbytes(0, media_body.size())
            if addParents is not None:
                self.assert_valid_move(node, removeParents)
                node["parents"] = [addParents]
            return node

        operation = "move" if addParents else "update"
        return self.google.mutation(operation, node["name"], action)

    @staticmethod
    def assert_valid_move(node, remove_parents):
        if set(remove_parents.split(",")) != set(node["parents"]):
            raise ValueError("Drive move used the wrong source parents")


class CalendarEvents:
    def __init__(self, google):
        self.google = google

    def list(self, *, calendarId, timeMin, timeMax, pageToken=None, **kwargs):
        def action():
            items = self.google.calendars[calendarId].values()
            items = sorted(
                (event for event in items if event["start"].get("dateTime", event["start"].get("date")) < timeMax
                 and event["end"].get("dateTime", event["end"].get("date")) > timeMin),
                key=lambda event: event["id"],
            )
            offset = int(pageToken or 0)
            result = {"items": items[offset:offset + 1]}
            if offset + 1 < len(items):
                result["nextPageToken"] = str(offset + 1)
            return result

        return Request(action)

    def move(self, *, calendarId, eventId, destination):
        def action():
            event = self.google.calendars[calendarId].pop(eventId)
            self.google.calendars[destination][eventId] = event
            return event

        return self.google.mutation("calendar_move", eventId, action)
