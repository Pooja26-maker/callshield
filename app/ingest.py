
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader

RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/processed/chunks.jsonl")

CHUNK_SIZE = 500
OVERLAP = 80


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.ignored_tags = {"script", "style", "noscript", "svg"}
        self.ignore_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.ignored_tags:
            self.ignore_depth += 1
        elif not self.ignore_depth and tag in {
            "p", "div", "br", "h1", "h2", "h3",
            "h4", "li", "tr", "section"
        }:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.ignored_tags and self.ignore_depth:
            self.ignore_depth -= 1
        elif not self.ignore_depth:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.ignore_depth:
            self.parts.append(data)


def clean_text(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def extract_pdf(path):
    reader = PdfReader(str(path))
    for page_number, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        if text:
            yield page_number, text


def extract_html(path):
    parser = TextExtractor()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    text = clean_text("".join(parser.parts))
    if text:
        yield 1, text


def make_chunks(text):
    words = text.split()
    step = CHUNK_SIZE - OVERLAP

    for start in range(0, len(words), step):
        chunk_words = words[start:start + CHUNK_SIZE]
        if len(chunk_words) < 30:
            continue
        yield " ".join(chunk_words)


def process_documents():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    total_chunks = 0
    total_documents = 0

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for path in sorted(RAW_DIR.iterdir()):
            if path.suffix.lower() not in {".pdf", ".html"}:
                continue

            try:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()

                pages = (
                    extract_pdf(path)
                    if path.suffix.lower() == ".pdf"
                    else extract_html(path)
                )

                document_chunks = 0

                for page_number, text in pages:
                    for chunk_number, chunk in enumerate(
                        make_chunks(text), start=1
                    ):
                        record = {
                            "chunk_id": (
                                f"{path.stem}-p{page_number}-c{chunk_number}"
                            ),
                            "source_file": path.name,
                            "source_hash": digest,
                            "file_type": path.suffix.lower().lstrip("."),
                            "page": page_number,
                            "text": chunk,
                        }

                        output.write(
                            json.dumps(record, ensure_ascii=False) + "\n"
                        )
                        document_chunks += 1

                total_documents += 1
                total_chunks += document_chunks
                print(f"Processed: {path.name} | Chunks: {document_chunks}")

            except Exception as error:
                print(f"Skipped: {path.name} | {type(error).__name__}: {error}")

    print("\nIngestion completed.")
    print(f"Documents processed: {total_documents}")
    print(f"Total chunks: {total_chunks}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    process_documents()
