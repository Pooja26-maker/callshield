
import csv
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

RAW_DIR = Path("data/raw")
MANIFEST = Path("data/manifest.csv")


class PDFLinkParser(HTMLParser):
    def __init__(self, page_url):
        super().__init__()
        self.page_url = page_url
        self.pdf_links = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                url = urljoin(self.page_url, value)
                if ".pdf" in url.lower().split("?")[0]:
                    self.pdf_links.add(url)


def main():
    if not MANIFEST.exists():
        print("Manifest not found:", MANIFEST)
        return

    found = set()

    with MANIFEST.open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            path = RAW_DIR / row["file"]
            if not path.exists():
                continue

            parser = PDFLinkParser(row["source_url"])
            parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
            found.update(parser.pdf_links)

    print(f"Unique PDF links found: {len(found)}")
    for url in sorted(found):
        print(url)


if __name__ == "__main__":
    main()
