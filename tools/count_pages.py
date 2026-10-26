from pathlib import Path

from pypdf import PdfReader

RAW_DIR = Path("data/raw")


def main():
    if not RAW_DIR.exists():
        print("data/raw/ does not exist.")
        return

    html_files = list(RAW_DIR.rglob("*.html"))
    pdf_files = list(RAW_DIR.rglob("*.pdf"))

    pdf_pages = 0

    print(f"HTML documents found: {len(html_files)}")

    for pdf in pdf_files:
        try:
            reader = PdfReader(str(pdf))
            pages = len(reader.pages)
            pdf_pages += pages
            print(f"{pdf.name}: {pages} pages")
        except Exception as error:
            print(f"Could not count {pdf.name}: {error}")

    total_pages = len(html_files) + pdf_pages

    print("\n--- Dataset Summary ---")
    print(f"HTML documents: {len(html_files)}")
    print(f"PDF documents: {len(pdf_files)}")
    print(f"PDF pages: {pdf_pages}")
    print(f"Estimated total pages: {total_pages}")
    print(f"50+ page target reached: {'YES' if total_pages >= 50 else 'NO'}")


if __name__ == "__main__":
    main()
