#!/usr/bin/env python3
"""Open one GitHub issue when Factorio moves to a new compatibility line."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INFO_PATH = ROOT / os.environ.get("FACTORIO_INFO_PATH", "LargerLamps-2.0/info.json")
RELEASES_URL = os.environ.get(
    "FACTORIO_RELEASES_URL", "https://factorio.com/api/latest-releases"
)
RELEASE_CHANNEL = os.environ.get("FACTORIO_RELEASE_CHANNEL", "stable")
FORCE_TARGET_VERSION = os.environ.get("FORCE_TARGET_VERSION", "").strip()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_API_URL = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")

LABELS: dict[str, tuple[str, str]] = {
    "factorio-update": ("D93F0B", "Automatically detected Factorio compatibility update"),
    "needs-ai-review": ("FBCA04", "Waiting for an optional AI compatibility review"),
    "ai-fix-approved": ("0E8A16", "Maintainer approved an AI-generated compatibility attempt"),
    "ai-pr-created": ("5319E7", "AI maintenance created or updated a draft pull request"),
    "needs-testing": ("B60205", "Requires manual Factorio and save-game testing"),
    "ai-reviewed": ("1D76DB", "AI review completed without a code proposal"),
}
VERSION_LINE_RE = re.compile(r"^(\d+)\.(\d+)")


class ApiError(RuntimeError):
    """Raised for an unexpected GitHub or Factorio API response."""


def http_json(
    url: str,
    *,
    method: str = "GET",
    token: str | None = None,
    payload: dict[str, Any] | None = None,
    accepted: tuple[int, ...] = (200,),
) -> tuple[int, Any]:
    data = None
    headers = {
        "Accept": "application/vnd.github+json, application/json",
        "User-Agent": "larger-lamps-factorio-version-watch/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = response.status
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read()
        if status not in accepted:
            body = raw.decode("utf-8", errors="replace")
            raise ApiError(f"{method} {url} returned HTTP {status}: {body}") from exc
    except urllib.error.URLError as exc:
        raise ApiError(f"Could not reach {url}: {exc}") from exc

    if status not in accepted:
        body = raw.decode("utf-8", errors="replace")
        raise ApiError(f"{method} {url} returned HTTP {status}: {body}")

    if not raw:
        return status, None
    try:
        return status, json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ApiError(f"{url} did not return valid JSON") from exc


def github_api(
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    accepted: tuple[int, ...] = (200,),
) -> tuple[int, Any]:
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY:
        raise ApiError("GITHUB_TOKEN and GITHUB_REPOSITORY are required")
    return http_json(
        f"{GITHUB_API_URL}{path}",
        method=method,
        token=GITHUB_TOKEN,
        payload=payload,
        accepted=accepted,
    )


def compatibility_line(version: str) -> str:
    match = VERSION_LINE_RE.match(version.strip())
    if not match:
        raise ApiError(f"Unsupported Factorio version format: {version!r}")
    return f"{match.group(1)}.{match.group(2)}"


def version_tuple(version_line: str) -> tuple[int, int]:
    major, minor = compatibility_line(version_line).split(".")
    return int(major), int(minor)


def load_current_metadata() -> dict[str, Any]:
    try:
        metadata = json.loads(INFO_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ApiError(f"Missing {INFO_PATH.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ApiError(f"Invalid JSON in {INFO_PATH.relative_to(ROOT)}: {exc}") from exc

    current = metadata.get("factorio_version")
    if not isinstance(current, str):
        raise ApiError("info.json does not contain a string factorio_version")
    return metadata


def select_release_version(releases: Any) -> str:
    if not isinstance(releases, dict):
        raise ApiError("Factorio release API returned an unexpected top-level value")
    channel = releases.get(RELEASE_CHANNEL)
    if not isinstance(channel, dict):
        raise ApiError(f"Factorio release API has no {RELEASE_CHANNEL!r} channel")

    for key in ("headless", "core-linux64", "alpha", "demo"):
        value = channel.get(key)
        if isinstance(value, str) and VERSION_LINE_RE.match(value):
            return value

    for value in channel.values():
        if isinstance(value, str) and VERSION_LINE_RE.match(value):
            return value
    raise ApiError(f"No usable version found in the {RELEASE_CHANNEL!r} channel")


def latest_release() -> tuple[str, str]:
    if FORCE_TARGET_VERSION:
        return compatibility_line(FORCE_TARGET_VERSION), FORCE_TARGET_VERSION
    _, releases = http_json(RELEASES_URL)
    full_version = select_release_version(releases)
    return compatibility_line(full_version), full_version


def ensure_labels() -> None:
    for name, (color, description) in LABELS.items():
        encoded = urllib.parse.quote(name, safe="")
        status, _ = github_api(
            f"/repos/{GITHUB_REPOSITORY}/labels",
            method="POST",
            payload={"name": name, "color": color, "description": description},
            accepted=(201, 422),
        )
        if status == 422:
            github_api(
                f"/repos/{GITHUB_REPOSITORY}/labels/{encoded}",
                method="PATCH",
                payload={"new_name": name, "color": color, "description": description},
                accepted=(200,),
            )


def find_existing_issue(marker: str) -> dict[str, Any] | None:
    page = 1
    while True:
        query = urllib.parse.urlencode(
            {
                "state": "all",
                "labels": "factorio-update",
                "per_page": "100",
                "page": str(page),
            }
        )
        _, issues = github_api(f"/repos/{GITHUB_REPOSITORY}/issues?{query}")
        if not isinstance(issues, list):
            raise ApiError("GitHub returned an unexpected issue list")
        for issue in issues:
            if "pull_request" in issue:
                continue
            if marker in str(issue.get("body") or ""):
                return issue
        if len(issues) < 100:
            return None
        page += 1


def set_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as output:
            output.write(f"{name}={value}\n")


def create_issue(
    *, current_line: str, target_line: str, full_version: str, mod_version: str
) -> dict[str, Any]:
    marker = f"<!-- factorio-version-watch:{target_line} -->"
    body = f"""{marker}
## A new Factorio compatibility line was detected

| Item | Version |
| --- | --- |
| Current mod compatibility | `{current_line}` |
| Latest {RELEASE_CHANNEL} Factorio release | `{full_version}` |
| New compatibility target | `{target_line}` |
| Current mod release | `{mod_version}` |

Source checked: `{RELEASES_URL}`

### Suggested workflow

- [ ] Read the official Factorio migration and modding notes.
- [ ] Review the mod for removed or changed prototypes, properties and runtime APIs.
- [ ] Add the `ai-fix-approved` label only when an AI-generated compatibility attempt is wanted.
- [ ] Review the resulting **draft** pull request.
- [ ] Test a clean startup and an existing save before merging.
- [ ] Publish to the Mod Portal manually through the existing release process.

### Safety boundaries

The AI workflow cannot merge a pull request or publish to the Factorio Mod Portal. It may only create or update a dedicated branch and draft pull request after a maintainer applies `ai-fix-approved`.
"""
    _, issue = github_api(
        f"/repos/{GITHUB_REPOSITORY}/issues",
        method="POST",
        payload={
            "title": f"Factorio {target_line} compatibility review",
            "body": body,
            "labels": ["factorio-update", "needs-ai-review"],
        },
        accepted=(201,),
    )
    if not isinstance(issue, dict):
        raise ApiError("GitHub returned an unexpected issue creation response")
    return issue


def main() -> int:
    metadata = load_current_metadata()
    current_line = compatibility_line(str(metadata["factorio_version"]))
    target_line, full_version = latest_release()

    print(f"Current compatibility line: {current_line}")
    print(f"Latest {RELEASE_CHANNEL} Factorio release: {full_version}")
    print(f"Detected compatibility line: {target_line}")

    if not FORCE_TARGET_VERSION and version_tuple(target_line) <= version_tuple(current_line):
        print("No newer Factorio compatibility line detected.")
        set_output("created", "false")
        return 0

    ensure_labels()
    marker = f"<!-- factorio-version-watch:{target_line} -->"
    existing = find_existing_issue(marker)
    if existing is not None:
        print(f"Issue already exists: {existing.get('html_url')}")
        set_output("created", "false")
        set_output("issue_number", str(existing.get("number", "")))
        set_output("issue_url", str(existing.get("html_url", "")))
        return 0

    issue = create_issue(
        current_line=current_line,
        target_line=target_line,
        full_version=full_version,
        mod_version=str(metadata.get("version", "unknown")),
    )
    print(f"Created issue: {issue.get('html_url')}")
    set_output("created", "true")
    set_output("issue_number", str(issue.get("number", "")))
    set_output("issue_url", str(issue.get("html_url", "")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ApiError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
