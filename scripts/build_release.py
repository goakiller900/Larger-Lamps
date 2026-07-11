#!/usr/bin/env python3
"""Validate and build a deterministic Factorio release archive."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import NoReturn

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "LargerLamps-2.0"
INFO_PATH = SOURCE_DIR / "info.json"
CHANGELOG_PATH = SOURCE_DIR / "changelog.txt"
DIST_DIR = ROOT / "dist"

REQUIRED_FILES = {
    "info.json",
    "changelog.txt",
    "data.lua",
    "data-final-fixes.lua",
    "license.txt",
    "prototypes/entity.lua",
    "prototypes/item.lua",
    "prototypes/technology.lua",
}
EXCLUDED_NAMES = {
    ".DS_Store",
    "__pycache__",
}
FORBIDDEN_SOURCE_MARKERS = {
    "aai-production": "obsolete private AAI recipe category",
    "aai-industrial-assembler": "guessed AAI machine prototype",
    "aai-assembling-machine": "obsolete AAI machine prototype",
    "aai-manual-crafter": "obsolete AAI machine prototype",
    "DeadlockLargerLamp": "obsolete internal mod name",
    "game.technology_prototypes": "obsolete runtime prototype access",
    "game.recipe_prototypes": "obsolete runtime prototype access",
}
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
CHANGELOG_VERSION_PATTERN = re.compile(
    r"^Version:\s*(\d+\.\d+\.\d+)\s*$",
    re.MULTILINE,
)
FIXED_ZIP_TIMESTAMP = (2020, 1, 1, 0, 0, 0)


def fail(message: str) -> NoReturn:
    raise SystemExit(f"ERROR: {message}")


def load_metadata() -> dict[str, object]:
    if not INFO_PATH.is_file():
        fail(f"Missing {INFO_PATH.relative_to(ROOT)}")

    try:
        metadata = json.loads(INFO_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid info.json: {exc}")

    for field in ("name", "version", "title", "factorio_version"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            fail(f"info.json field '{field}' must be a non-empty string")

    name = str(metadata["name"])
    version = str(metadata["version"])

    if not NAME_PATTERN.fullmatch(name):
        fail("info.json name may contain only letters, digits, underscores and hyphens")
    if not VERSION_PATTERN.fullmatch(version):
        fail("info.json version must use MAJOR.MINOR.PATCH")
    if metadata["factorio_version"] != "2.1":
        fail("This release branch must target Factorio 2.1")

    return metadata


def validate_changelog(version: str) -> None:
    if not CHANGELOG_PATH.is_file():
        fail(f"Missing {CHANGELOG_PATH.relative_to(ROOT)}")

    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    match = CHANGELOG_VERSION_PATTERN.search(text)

    if not match:
        fail("changelog.txt does not contain a Version entry")
    if match.group(1) != version:
        fail(
            f"Top changelog version {match.group(1)} does not match info.json {version}"
        )


def validate_source() -> None:
    missing = sorted(
        relative
        for relative in REQUIRED_FILES
        if not (SOURCE_DIR / relative).is_file()
    )
    if missing:
        fail(f"Required mod files are missing: {', '.join(missing)}")

    lua_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(SOURCE_DIR.rglob("*.lua"))
    )

    for marker, description in FORBIDDEN_SOURCE_MARKERS.items():
        if marker in lua_text:
            fail(f"Found {description}: {marker}")

    category_declarations = len(
        re.findall(r'name\s*=\s*["\']lamp-burning["\']', lua_text)
    )
    if category_declarations != 1:
        fail(
            "Expected exactly one lamp-burning recipe-category declaration, "
            f"found {category_declarations}"
        )


def should_package(path: Path) -> bool:
    if not path.is_file():
        return False

    relative = path.relative_to(SOURCE_DIR)

    if any(part in EXCLUDED_NAMES for part in relative.parts):
        return False
    if relative.suffix.lower() in {".zip", ".pyc", ".pyo"}:
        return False

    return True


def collect_files() -> list[Path]:
    return sorted(
        (path for path in SOURCE_DIR.rglob("*") if should_package(path)),
        key=lambda path: path.relative_to(SOURCE_DIR).as_posix(),
    )


def add_file_to_zip(
    archive: zipfile.ZipFile,
    source: Path,
    archive_path: PurePosixPath,
) -> None:
    info = zipfile.ZipInfo(str(archive_path), date_time=FIXED_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, source.read_bytes())


def validate_archive(archive_path: Path, folder_name: str) -> None:
    expected_prefix = f"{folder_name}/"
    expected_info = f"{folder_name}/info.json"

    with zipfile.ZipFile(archive_path, mode="r") as archive:
        names = archive.namelist()
        bad_entries = [name for name in names if not name.startswith(expected_prefix)]

        if bad_entries:
            fail(
                "Archive contains entries outside the required top-level folder: "
                + ", ".join(bad_entries)
            )
        if expected_info not in names:
            fail(f"Archive does not contain {expected_info}")

        bad_file = archive.testzip()
        if bad_file is not None:
            fail(f"Archive integrity check failed at {bad_file}")


def build_archive(
    metadata: dict[str, object],
    source_files: list[Path],
) -> tuple[Path, Path]:
    name = str(metadata["name"])
    version = str(metadata["version"])
    folder_name = f"{name}_{version}"
    archive_path = DIST_DIR / f"{folder_name}.zip"
    checksum_path = DIST_DIR / f"{folder_name}.zip.sha256"

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    with zipfile.ZipFile(
        archive_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for source in source_files:
            relative = PurePosixPath(source.relative_to(SOURCE_DIR).as_posix())
            add_file_to_zip(
                archive,
                source,
                PurePosixPath(folder_name) / relative,
            )

    validate_archive(archive_path, folder_name)

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    checksum_path.write_text(
        f"{digest}  {archive_path.name}\n",
        encoding="utf-8",
    )

    return archive_path, checksum_path


def main() -> int:
    metadata = load_metadata()
    version = str(metadata["version"])

    validate_changelog(version)
    validate_source()

    source_files = collect_files()
    archive_path, checksum_path = build_archive(metadata, source_files)

    print(f"Mod name: {metadata['name']}")
    print(f"Version: {version}")
    print(f"Factorio version: {metadata['factorio_version']}")
    print(f"Packaged files: {len(source_files)}")
    print(f"Created: {archive_path.relative_to(ROOT)}")
    print(f"Created: {checksum_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
