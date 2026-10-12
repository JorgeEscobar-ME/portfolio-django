import json
import re
import tempfile
from datetime import datetime, timezone
from io import BytesIO, StringIO
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

from django.conf import settings
from django.core.management import call_command
from django.core.serializers import deserialize
from django.core.serializers.base import DeserializationError
from django.db import transaction


ARCHIVE_VERSION = 1
MAX_ARCHIVE_SIZE = 100 * 1024 * 1024
MAX_ARCHIVE_FILES = 5000
DATABASE_EXCLUDES = [
    "admin.logentry",
    "auth.permission",
    "contenttypes",
    "sessions",
]
_SAFE_ARCHIVE_COMPONENT = re.compile(r"^[\w .@+-]+$", re.UNICODE)


class BackupValidationError(Exception):
    pass


def create_backup():
    fixture_output = StringIO()
    call_command(
        "dumpdata",
        database="default",
        natural_foreign=True,
        exclude=DATABASE_EXCLUDES,
        stdout=fixture_output,
        verbosity=0,
    )
    fixture = fixture_output.getvalue().encode("utf-8")
    media_root = Path(settings.MEDIA_ROOT)
    media_files = []
    total_size = len(fixture)
    if media_root.exists():
        for path in media_root.rglob("*"):
            if path.is_file():
                if path.is_symlink():
                    raise BackupValidationError(
                        "Media symlinks cannot be included in a backup."
                    )
                relative_path = path.relative_to(media_root).as_posix()
                _validate_media_path(relative_path)
                size = path.stat().st_size
                total_size += size
                media_files.append((path, relative_path, size))
    if len(media_files) + 2 > MAX_ARCHIVE_FILES:
        raise BackupValidationError(
            f"Backup exceeds the {MAX_ARCHIVE_FILES} file limit."
        )
    if total_size > MAX_ARCHIVE_SIZE:
        raise BackupValidationError(
            "Database and media exceed the 100 MiB backup limit."
        )

    archive_buffer = BytesIO()
    with ZipFile(archive_buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps({
            "format": "portfolio-django-backup",
            "version": ARCHIVE_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }))
        archive.writestr("data.json", fixture)
        for path, relative_path, _ in media_files:
            archive.write(path, f"media/{relative_path}")
    if archive_buffer.tell() > MAX_ARCHIVE_SIZE:
        raise BackupValidationError(
            "Compressed backup exceeds the 100 MiB download limit."
        )
    archive_buffer.seek(0)
    return archive_buffer


def inspect_backup(uploaded_file):
    if uploaded_file.size > MAX_ARCHIVE_SIZE:
        raise BackupValidationError("Backup file exceeds the 100 MiB upload limit.")
    try:
        archive = ZipFile(uploaded_file)
    except BadZipFile as error:
        raise BackupValidationError("The selected file is not a valid ZIP backup.") from error

    with archive:
        entries = archive.infolist()
        if len(entries) > MAX_ARCHIVE_FILES:
            raise BackupValidationError(
                f"Backup exceeds the {MAX_ARCHIVE_FILES} file limit."
            )
        if sum(entry.file_size for entry in entries) > MAX_ARCHIVE_SIZE:
            raise BackupValidationError("Uncompressed backup exceeds the 100 MiB limit.")
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)):
            raise BackupValidationError("Backup contains duplicate file names.")
        if "manifest.json" not in names or "data.json" not in names:
            raise BackupValidationError("Backup is missing its manifest or database data.")
        media_names = []
        for entry in entries:
            if entry.is_dir():
                continue
            if entry.filename in {"manifest.json", "data.json"}:
                continue
            if not entry.filename.startswith("media/"):
                raise BackupValidationError("Backup contains an unexpected file.")
            relative_path = entry.filename[len("media/"):]
            _validate_media_path(relative_path)
            media_names.append(entry.filename)

        try:
            if archive.testzip() is not None:
                raise BackupValidationError("Backup contains a corrupted file.")
        except BadZipFile as error:
            raise BackupValidationError("Backup contains a corrupted file.") from error

        try:
            manifest = json.loads(archive.read("manifest.json"))
            fixture = archive.read("data.json")
            fixture_objects = json.loads(fixture)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise BackupValidationError("Backup metadata or database data is invalid.") from error
        if (
            not isinstance(manifest, dict)
            or manifest.get("format") != "portfolio-django-backup"
            or manifest.get("version") != ARCHIVE_VERSION
        ):
            raise BackupValidationError("Backup format or version is not supported.")
        if not isinstance(fixture_objects, list):
            raise BackupValidationError("Database data must be a Django fixture list.")
        if not any(
            item.get("model") == "auth.user"
            and item.get("fields", {}).get("is_superuser") is True
            for item in fixture_objects
            if isinstance(item, dict)
        ):
            raise BackupValidationError(
                "Backup must include a superuser so you can continue to access Admin."
            )
        try:
            list(
                deserialize(
                    "json",
                    fixture,
                    using="default",
                    handle_forward_references=True,
                )
            )
        except (DeserializationError, ValueError, LookupError) as error:
            raise BackupValidationError(
                f"Database fixture cannot be restored: {error}"
            ) from error
        media_files = [
            (name, archive.read(name))
            for name in media_names
        ]
    return fixture, media_files


def restore_backup(fixture, media_files):
    fixture_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".json",
            prefix="portfolio-backup-",
            delete=False,
        ) as fixture_file:
            fixture_file.write(fixture)
            fixture_path = fixture_file.name
        with transaction.atomic(using="default"):
            call_command("flush", database="default", interactive=False, verbosity=0)
            call_command(
                "loaddata",
                fixture_path,
                database="default",
                verbosity=0,
            )
    finally:
        if fixture_path:
            Path(fixture_path).unlink(missing_ok=True)

    _restore_media_files(media_files)


def _restore_media_files(media_files):
    root = Path(settings.MEDIA_ROOT).resolve()
    for archive_name, contents in media_files:
        relative_path = archive_name[len("media/"):]
        _validate_media_path(relative_path)
        destination = (root / Path(*PurePosixPath(relative_path).parts)).resolve()
        if not destination.is_relative_to(root):
            raise BackupValidationError("Backup media path escapes the media directory.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(contents)


def _validate_media_path(path):
    pure_path = PurePosixPath(path)
    if (
        not path
        or pure_path.is_absolute()
        or any(part in {"", ".", ".."} for part in pure_path.parts)
        or any(not _SAFE_ARCHIVE_COMPONENT.fullmatch(part) for part in pure_path.parts)
    ):
        raise BackupValidationError("Backup contains an unsafe media file path.")
