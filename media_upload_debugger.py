#!/usr/bin/env python3
"""
media_upload_debugger.py – Self-contained CLI script to diagnose the Supabase
media-upload pipeline used by CursorDesktopNotes.

USAGE
-----
python media_upload_debugger.py <file1> [<file2> ...] \
       --bucket racing-notes-media \
       [--insert-db] [--note-id NOTE_UUID]

The script will:
1. Connect to Supabase using environment variables SUPABASE_URL and
   SUPABASE_ANON_KEY (override with CLI flags if desired).
2. Upload each supplied file to the given storage bucket under a timestamped
   path ("debug/YYYY/MM/DD/<uuid4>_<filename>") with upsert=True so re-runs
   do not error if the path already exists.
3. Fetch and print the public URL.
4. If --insert-db is supplied it will add a record to the "media" table.  You
   can optionally supply an existing NOTE_UUID with --note-id – if omitted a
   throw-away note is created so foreign-key constraints pass.

This script is deliberately dependency-free beyond ``supabase-py`` and the
standard library so it can be executed inside any venv/container.
"""
from __future__ import annotations

import argparse
import os
import sys
import mimetypes
from datetime import datetime
from pathlib import Path
from uuid import uuid4, UUID

try:
    from supabase import create_client  # type: ignore
except ImportError:
    print("❌  supabase-py is not installed.  Run `pip install supabase` first.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def guess_content_type(file_path: Path) -> str:
    """Return a best-effort MIME type, defaulting to application/octet-stream."""
    ctype, _ = mimetypes.guess_type(file_path.as_posix())
    return ctype or "application/octet-stream"


def format_size(num_bytes: int) -> str:
    return f"{num_bytes / (1024 * 1024):.2f} MB"

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Debug Supabase storage uploads")
    p.add_argument("files", nargs="+", type=str, help="Path(s) to the file(s) to upload")
    p.add_argument("--bucket", default="racing-notes-media", help="Target storage bucket")
    p.add_argument("--url", help="Supabase project URL (defaults to env SUPABASE_URL)")
    p.add_argument("--key", help="Supabase anon key (defaults to env SUPABASE_ANON_KEY)")
    p.add_argument("--insert-db", action="store_true", help="Insert a test record into the media table after upload")
    p.add_argument("--note-id", type=str, help="Existing note UUID for --insert-db. If omitted, a placeholder note is created.")
    return p.parse_args()

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    supabase_url = args.url or os.getenv("SUPABASE_URL")
    supabase_key = args.key or os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        print("❌  SUPABASE_URL and SUPABASE_ANON_KEY must be provided (env or flag).")
        sys.exit(1)

    client = create_client(supabase_url, supabase_key)
    storage = client.storage.from_(args.bucket)

    print(f"🔗  Connected to Supabase project: {supabase_url}")
    print(f"📦  Using bucket: {args.bucket}\n")

    for raw_path in args.files:
        file_path = Path(raw_path).expanduser().resolve()
        if not file_path.exists():
            print(f"❌  File not found: {file_path}")
            continue

        timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H%M%S")
        storage_path = f"debug/{timestamp}_{uuid4().hex}_{file_path.name}"
        mime_type = guess_content_type(file_path)

        print("──" * 40)
        print(f"⬆️  Uploading {file_path.name} ({format_size(file_path.stat().st_size)})")
        print(f"    → {storage_path}  [content-type: {mime_type}]")

        with file_path.open("rb") as fobj:
            response = storage.upload(
                path=storage_path,
                file=fobj,
                file_options={"content-type": mime_type}
            )

        # The SDK returns a StorageResponse or dict depending on version
        error = getattr(response, "error", None)
        if error:
            print(f"❌  Upload failed: {error}")
            continue

        public_url_resp = storage.get_public_url(storage_path)
        public_url: str | None = None
        if isinstance(public_url_resp, dict):
            public_url = public_url_resp.get("publicURL") or public_url_resp.get("publicUrl")
        elif hasattr(public_url_resp, "data"):
            data_field = getattr(public_url_resp, "data", None)
            if isinstance(data_field, dict):
                public_url = data_field.get("publicURL") or data_field.get("publicUrl")
        else:
            public_url = str(public_url_resp)

        if not public_url:
            print("❌  Could not retrieve public URL – check bucket policy")
            continue

        print(f"✅  Uploaded successfully: {public_url}")

        if args.insert_db:
            note_id = args.note_id
            if note_id is None:
                # Create a throw-away note to satisfy FK constraint
                note_payload = {
                    "body": "Debug note from media_upload_debugger",
                    "category": "General",
                    "created_by": "media_debugger",
                }
                note_resp = client.table("note").insert(note_payload).execute()
                if not note_resp.data:
                    print("❌  Failed to create placeholder note – cannot insert media record.")
                    continue
                note_id = note_resp.data[0]["id"]
                print(f"📝  Placeholder note created: {note_id}")

            media_payload = {
                "note_id": str(note_id),
                "file_url": public_url,
                "media_type": "image" if mime_type.startswith("image/") else "video" if mime_type.startswith("video/") else "csv",
                "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                "filename": file_path.name,
            }
            media_resp = client.table("media").insert(media_payload).execute()
            if media_resp.data:
                print(f"📥  Media record inserted with id: {media_resp.data[0]['id']}")
            else:
                err = getattr(media_resp, "error", "unknown")
                print(f"❌  Media insert failed: {err}")

    print("\n🏁  Debug session complete.")


if __name__ == "__main__":
    main() 