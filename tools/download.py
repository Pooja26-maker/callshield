
import csv
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

# Project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent
URLS_FILE = PROJECT_ROOT / "urls.txt"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
MANIFEST_FILE = PROJECT_ROOT / "data" / "manifest.csv"

# Replace this with your contact email.
USER_AGENT = "CITDatasetCollector/1.0 (contact: poojabcc2006@gmail)"
DELAY_SECONDS = 2

MANIFEST_FIELDS = [
    "file",
    "source_url",
    "downloaded_on",
    "bytes",
    "sha256",
]


def load_urls():
    if not URLS_FILE.exists():
        raise FileNotFoundError(f"Missing URL list: {URLS_FILE}")

    with URLS_FILE.open("r", encoding="utf-8") as file:
        return [
            line.strip()
            for line in file
            if line.strip() and not line.strip().startswith("#")
        ]


def allowed_by_robots(url, session):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        response = session.get(robots_url, timeout=15)

        # If robots.txt cannot be checked, do not download.
        if response.status_code != 200:
            print(f"SKIP: Cannot verify robots.txt: {robots_url}")
            return False

        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(response.text.splitlines())

        return parser.can_fetch(USER_AGENT, url)

    except requests.RequestException as error:
        print(f"SKIP: Could not check robots.txt: {error}")
        return False


def make_filename(url, extension):
    parsed = urlparse(url)
    path_name = Path(parsed.path).name or "index"
    stem = Path(path_name).stem or "page"

    safe_stem = "".join(
        char if char.isalnum() or char in "-_" else "_"
        for char in stem
    )[:60]

    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    return f"{parsed.netloc}_{safe_stem}_{url_hash}.{extension}"


def write_manifest(filename, url, content):
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_exists = MANIFEST_FILE.exists() and MANIFEST_FILE.stat().st_size > 0

    with MANIFEST_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=MANIFEST_FIELDS)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "file": filename,
            "source_url": url,
            "downloaded_on": datetime.now(timezone.utc).isoformat(),
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        })


def download_file(url, session):
    if not url.startswith(("https://", "http://")):
        print(f"SKIP: Invalid URL: {url}")
        return

    if not allowed_by_robots(url, session):
        print(f"SKIP: Not permitted or permission could not be verified: {url}")
        return

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        if "application/pdf" in content_type:
            if not response.content.startswith(b"%PDF-"):
                print(f"SKIP: Response is not a valid PDF: {url}")
                return

            extension = "pdf"
            content = response.content

        elif (
            "text/html" in content_type
            or "application/xhtml+xml" in content_type
        ):
            extension = "html"
            content = response.text.encode("utf-8")

        else:
            print(f"SKIP: Unsupported content type {content_type}: {url}")
            return

        filename = make_filename(url, extension)
        destination = RAW_DIR / filename

        if destination.exists():
            print(f"SKIP: Already downloaded: {filename}")
            return

        destination.write_bytes(content)
        write_manifest(filename, url, content)

        print(f"OK: {filename} ({len(content)} bytes)")

    except requests.RequestException as error:
        print(f"ERROR downloading {url}: {error}")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    urls = load_urls()

    if not urls:
        print("urls.txt is empty. Add approved URLs first.")
        return

    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})

        for index, url in enumerate(urls):
            print(f"\n[{index + 1}/{len(urls)}] {url}")
            download_file(url, session)

            if index < len(urls) - 1:
                time.sleep(DELAY_SECONDS)

    print("\nFinished. Review data/raw/ and data/manifest.csv.")


if __name__ == "__main__":
    main()
