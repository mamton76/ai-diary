#!/usr/bin/env python3
"""
AI Diary — Google Drive client

Small wrapper around Google Drive API v3 for file-based AI Diary workflows.

Responsibilities:
- OAuth authentication
- folder lookup / creation
- listing children with pagination
- uploading text/JSON files
- downloading text/raw files
- moving/copying files between Drive folders

This module deliberately does NOT know anything about diary workflow rules.
"""

from __future__ import annotations

import io
import json
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload


DRIVE_FOLDER_MIME = "application/vnd.google-apps.folder"
GOOGLE_APPS_PREFIX = "application/vnd.google-apps."
DEFAULT_SCOPES = ["https://www.googleapis.com/auth/drive"]


def drive_query_literal(value: str) -> str:
    """Escape a string for use as a single-quoted Google Drive API query literal."""
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


@dataclass(frozen=True)
class DriveFile:
    id: str
    name: str
    mime_type: str
    created_time: str | None = None
    modified_time: str | None = None
    parents: list[str] | None = None
    size: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "DriveFile":
        return cls(
            id=data["id"],
            name=data["name"],
            mime_type=data["mimeType"],
            created_time=data.get("createdTime"),
            modified_time=data.get("modifiedTime"),
            parents=data.get("parents"),
            size=data.get("size"),
        )

    @property
    def is_folder(self) -> bool:
        return self.mime_type == DRIVE_FOLDER_MIME

    @property
    def is_google_native(self) -> bool:
        return self.mime_type.startswith(GOOGLE_APPS_PREFIX)


class DriveClient:
    def __init__(
        self,
        credentials_file: Path,
        token_file: Path,
        scopes: list[str] | None = None,
    ) -> None:
        self.credentials_file = Path(credentials_file).expanduser()
        self.token_file = Path(token_file).expanduser()
        self.scopes = scopes or DEFAULT_SCOPES
        self.service = self._build_service()

    def _build_service(self):
        creds: Credentials | None = None

        if self.token_file.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_file), self.scopes)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        if not creds or not creds.valid:
            if not self.credentials_file.exists():
                raise FileNotFoundError(
                    f"Google OAuth credentials file not found: {self.credentials_file}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file),
                self.scopes,
            )
            creds = flow.run_local_server(port=0)

        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.token_file.write_text(creds.to_json(), encoding="utf-8")

        return build("drive", "v3", credentials=creds)

    # Metadata / listing

    def get_file(
        self,
        file_id: str,
        fields: str = "id,name,mimeType,createdTime,modifiedTime,parents,size",
    ) -> DriveFile:
        data = (
            self.service.files()
            .get(fileId=file_id, fields=fields, supportsAllDrives=True)
            .execute()
        )
        return DriveFile.from_api(data)

    def list_children(
        self,
        folder_id: str,
        *,
        name: str | None = None,
        mime_type: str | None = None,
        include_trashed: bool = False,
        page_size: int = 1000,
    ) -> list[DriveFile]:
        clauses = [f"{drive_query_literal(folder_id)} in parents"]

        if not include_trashed:
            clauses.append("trashed = false")

        if name is not None:
            clauses.append(f"name = {drive_query_literal(name)}")

        if mime_type is not None:
            clauses.append(f"mimeType = {drive_query_literal(mime_type)}")

        query = " and ".join(clauses)

        files: list[DriveFile] = []
        page_token: str | None = None

        while True:
            response = (
                self.service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id,name,mimeType,createdTime,modifiedTime,parents,size)",
                    pageSize=page_size,
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )

            files.extend(DriveFile.from_api(item) for item in response.get("files", []))
            page_token = response.get("nextPageToken")

            if not page_token:
                return files

    # Folders

    def find_child_folder(self, parent_id: str, name: str) -> DriveFile | None:
        matches = self.list_children(parent_id, name=name, mime_type=DRIVE_FOLDER_MIME)
        return matches[0] if matches else None

    def create_folder(self, parent_id: str, name: str) -> DriveFile:
        metadata = {
            "name": name,
            "mimeType": DRIVE_FOLDER_MIME,
            "parents": [parent_id],
        }

        data = (
            self.service.files()
            .create(body=metadata, fields="id,name,mimeType,parents", supportsAllDrives=True)
            .execute()
        )

        return DriveFile.from_api(data)

    def ensure_folder(self, parent_id: str, name: str) -> DriveFile:
        existing = self.find_child_folder(parent_id, name)
        if existing:
            return existing
        return self.create_folder(parent_id, name)

    def ensure_path(self, root_id: str, parts: Iterable[str]) -> DriveFile:
        current = self.get_file(root_id)

        for part in parts:
            if not part:
                continue
            current = self.ensure_folder(current.id, part)

        return current

    # Upload / update

    def upload_text(
        self,
        parent_id: str,
        name: str,
        text: str,
        *,
        mime_type: str = "text/plain",
    ) -> DriveFile:
        metadata = {
            "name": name,
            "parents": [parent_id],
        }
        media = MediaIoBaseUpload(
            io.BytesIO(text.encode("utf-8")),
            mimetype=mime_type,
            resumable=False,
        )

        data = (
            self.service.files()
            .create(
                body=metadata,
                media_body=media,
                fields="id,name,mimeType,parents",
                supportsAllDrives=True,
            )
            .execute()
        )

        return DriveFile.from_api(data)

    def upsert_text(
        self,
        parent_id: str,
        name: str,
        text: str,
        *,
        mime_type: str = "text/plain",
    ) -> DriveFile:
        existing = self.list_children(parent_id, name=name)

        media = MediaIoBaseUpload(
            io.BytesIO(text.encode("utf-8")),
            mimetype=mime_type,
            resumable=False,
        )

        if existing:
            data = (
                self.service.files()
                .update(
                    fileId=existing[0].id,
                    media_body=media,
                    body={"name": name},
                    fields="id,name,mimeType,parents",
                    supportsAllDrives=True,
                )
                .execute()
            )
            return DriveFile.from_api(data)

        return self.upload_text(parent_id, name, text, mime_type=mime_type)

    def upload_json(self, parent_id: str, name: str, data: dict[str, Any]) -> DriveFile:
        return self.upload_text(
            parent_id,
            name,
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            mime_type="application/json",
        )

    def upsert_json(self, parent_id: str, name: str, data: dict[str, Any]) -> DriveFile:
        return self.upsert_text(
            parent_id,
            name,
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            mime_type="application/json",
        )

    def upload_local_file(self, parent_id: str, path: Path, name: str | None = None) -> DriveFile:
        path = Path(path)
        mime_type, _ = mimetypes.guess_type(path.name)
        media = MediaFileUpload(str(path), mimetype=mime_type or "application/octet-stream")

        metadata = {
            "name": name or path.name,
            "parents": [parent_id],
        }

        data = (
            self.service.files()
            .create(
                body=metadata,
                media_body=media,
                fields="id,name,mimeType,parents",
                supportsAllDrives=True,
            )
            .execute()
        )

        return DriveFile.from_api(data)

    # Download / export

    def download_bytes(self, file_id: str) -> bytes:
        request = self.service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        return buffer.getvalue()

    def export_google_native_as_text(self, file_id: str) -> str:
        request = self.service.files().export_media(
            fileId=file_id,
            mimeType="text/plain",
        )
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        return buffer.getvalue().decode("utf-8", errors="replace")

    def download_text(self, file: DriveFile) -> str:
        if file.is_google_native:
            return self.export_google_native_as_text(file.id)

        return self.download_bytes(file.id).decode("utf-8", errors="replace")

    # Move / copy

    def copy_file(self, file_id: str, parent_id: str, *, name: str | None = None) -> DriveFile:
        source = self.get_file(file_id)
        metadata = {
            "name": name or source.name,
            "parents": [parent_id],
        }

        data = (
            self.service.files()
            .copy(
                fileId=file_id,
                body=metadata,
                fields="id,name,mimeType,parents",
                supportsAllDrives=True,
            )
            .execute()
        )

        return DriveFile.from_api(data)

    def move_file(self, file_id: str, new_parent_id: str, *, old_parent_ids: list[str] | None = None) -> DriveFile:
        source = self.get_file(file_id)

        parents_to_remove = old_parent_ids if old_parent_ids is not None else (source.parents or [])
        remove_parents = ",".join(parents_to_remove)

        data = (
            self.service.files()
            .update(
                fileId=file_id,
                addParents=new_parent_id,
                removeParents=remove_parents,
                fields="id,name,mimeType,parents",
                supportsAllDrives=True,
            )
            .execute()
        )

        return DriveFile.from_api(data)

