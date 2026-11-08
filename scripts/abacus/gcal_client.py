#!/usr/bin/env python3
"""
AI Diary — Google Calendar client

Small wrapper around Google Calendar API v3 for the Google Calendar → file inbox
adapter.

Responsibilities:
- OAuth credential loading / refresh
- listing calendars
- listing events from a calendar
- resolving calendar name → calendar id
- moving events between calendars via Calendar API events.move

This module does NOT know anything about diary workflow rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# MVP scope choice: broad scopes, because the existing Drive client and this Calendar
# adapter share the same token. Later these can be narrowed.
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
]

# Backwards-compatible alias used by the existing script.
CALENDAR_SCOPES = GOOGLE_SCOPES


def get_credentials(credentials_path: str | Path, token_path: str | Path) -> Credentials:
    """
    Load or refresh OAuth credentials.

    MVP assumption: google_token.json normally already exists and has both Drive and
    Calendar scopes. If it is missing or invalid, this falls back to local browser
    OAuth via run_local_server(). For a headless VPS, create the token locally first
    and copy it to the server as a secret.
    """
    credentials_path = Path(credentials_path)
    token_path = Path(token_path)

    creds: Credentials | None = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), GOOGLE_SCOPES)
        # A token can be valid but not contain the newly requested Calendar scope.
        if not creds.has_scopes(GOOGLE_SCOPES):
            creds = None

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds

    if creds and creds.valid:
        return creds

    # No usable token. This is intentionally not the deprecated OOB flow.
    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), GOOGLE_SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


@dataclass(frozen=True)
class CalendarEvent:
    id: str
    ical_uid: str
    summary: str
    description: str
    start_dt: str          # raw string from API: dateTime or date
    end_dt: str            # raw string from API: dateTime or date
    created: str | None
    updated: str | None
    html_link: str | None
    raw: dict[str, Any]    # full API response snapshot


@dataclass
class CalendarClient:
    service: Any           # googleapiclient Resource

    def list_calendars(self) -> list[dict[str, Any]]:
        """Return all calendars in the user's calendar list."""
        result: list[dict[str, Any]] = []
        page_token: str | None = None

        while True:
            resp = self.service.calendarList().list(pageToken=page_token).execute()
            result.extend(resp.get("items", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                return result

    def find_calendar_id(self, name: str) -> str | None:
        """Find a calendar id by exact display name."""
        for calendar in self.list_calendars():
            if calendar.get("summary") == name:
                return calendar.get("id")
        return None

    def list_events(
        self,
        calendar_id: str,
        time_min: datetime,
        time_max: datetime,
    ) -> list[CalendarEvent]:
        """List non-deleted events in a calendar within the given UTC time range."""
        result: list[CalendarEvent] = []
        page_token: str | None = None

        time_min_str = time_min.strftime("%Y-%m-%dT%H:%M:%SZ")
        time_max_str = time_max.strftime("%Y-%m-%dT%H:%M:%SZ")

        while True:
            resp = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min_str,
                    timeMax=time_max_str,
                    singleEvents=True,
                    orderBy="startTime",
                    showDeleted=False,
                    pageToken=page_token,
                )
                .execute()
            )

            for item in resp.get("items", []):
                result.append(_parse_event(item))

            page_token = resp.get("nextPageToken")
            if not page_token:
                return result

    def move_event(self, from_calendar_id: str, event_id: str, to_calendar_id: str) -> dict[str, Any]:
        """Move an event from one calendar to another via Calendar API events.move."""
        return (
            self.service.events()
            .move(
                calendarId=from_calendar_id,
                eventId=event_id,
                destination=to_calendar_id,
            )
            .execute()
        )


def build_calendar_client(credentials_path: str | Path, token_path: str | Path) -> CalendarClient:
    """Build a CalendarClient using credentials loaded from disk."""
    creds = get_credentials(credentials_path, token_path)
    service = build("calendar", "v3", credentials=creds)
    return CalendarClient(service=service)


def build_calendar_client_from_creds(creds: Any) -> CalendarClient:
    """Build a CalendarClient from already-loaded Credentials."""
    service = build("calendar", "v3", credentials=creds)
    return CalendarClient(service=service)


def _parse_event(item: dict[str, Any]) -> CalendarEvent:
    start = item.get("start", {})
    end = item.get("end", {})

    return CalendarEvent(
        id=item["id"],
        ical_uid=item.get("iCalUID", ""),
        summary=item.get("summary", ""),
        description=item.get("description", ""),
        start_dt=start.get("dateTime") or start.get("date", ""),
        end_dt=end.get("dateTime") or end.get("date", ""),
        created=item.get("created"),
        updated=item.get("updated"),
        html_link=item.get("htmlLink"),
        raw=item,
    )

