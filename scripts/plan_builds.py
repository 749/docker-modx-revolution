#!/usr/bin/env python3
"""Select the newest stable MODX release in every major line."""

import json
import os
import re
import sys
import time
from urllib.request import Request, urlopen


TAGS_URL = "https://api.github.com/repos/modxcms/revolution/tags"
STABLE_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)-pl$")
PAGE_SIZE = 100


def fetch_tags(open_url=urlopen):
    tags = []
    for page in range(1, 101):
        headers = {"Accept": "application/vnd.github+json"}
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
        request = Request(f"{TAGS_URL}?per_page={PAGE_SIZE}&page={page}", headers=headers)
        for attempt in range(3):
            try:
                with open_url(request, timeout=30) as response:
                    batch = json.load(response)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
        if not isinstance(batch, list):
            raise ValueError("Upstream tags API did not return a list")
        tags.extend(item["name"] for item in batch)
        if len(batch) < PAGE_SIZE:
            return tags
    raise ValueError("Upstream tags API exceeded 100 pages")


def latest_per_major(tags):
    latest = {}
    for tag in tags:
        match = STABLE_TAG.fullmatch(tag)
        if not match:
            continue
        version = tuple(map(int, match.groups()))
        if version[0] >= 2 and version > latest.get(version[0], (0, 0, 0)):
            latest[version[0]] = version
    if not latest or set(latest) != set(range(2, max(latest) + 1)):
        raise ValueError("Missing a stable MODX major release starting with 2")
    return latest


def build_matrix(tags, event_name, ref, image_repo):
    latest = latest_per_major(tags)
    newest_major = max(latest)
    entries = []
    for major in sorted(latest):
        version = latest[major]
        full = ".".join(map(str, version))
        minor = ".".join(map(str, version[:2]))
        tags_for_build = [
            f"{image_repo}:{full}",
            f"{image_repo}:{minor}",
            f"{image_repo}:{major}",
        ]
        if major == newest_major:
            tags_for_build.append(f"{image_repo}:latest")
            if event_name == "push" and ref == "refs/heads/main":
                tags_for_build.append(f"{image_repo}:edge")
        entries.append({"major": str(major), "version": full, "tags": "\n".join(tags_for_build)})
    return {"include": entries}


if __name__ == "__main__":
    matrix = build_matrix(
        fetch_tags(),
        os.environ["GITHUB_EVENT_NAME"],
        os.environ["GITHUB_REF"],
        os.environ["IMAGE_REPO"],
    )
    print("matrix=" + json.dumps(matrix, separators=(",", ":")))
    for entry in matrix["include"]:
        print(f"MODX {entry['version']}: {entry['tags'].replace(chr(10), ', ')}", file=sys.stderr)
