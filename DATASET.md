# Dataset

## Collection summary

| Metric | Current status |
|---|---:|
| Source | TRAI official website |
| HTML documents collected | 10 |
| PDF documents collected | 5 |
| Total PDF pages | 241 |
| 50+ page requirement | Met |
| Raw downloads | `data/raw/` (not committed) |
| Sample files | `data/sample/` |

The collection currently contains telecom consumer information, FAQs, consumer protection regulations, complaint/grievance information, and unsolicited commercial communication regulations.

## Sources and collection policy

Documents were collected from the official Telecom Regulatory Authority of India (TRAI) website. The downloader checks `robots.txt`, limits downloads to supported HTML and PDF documents, and applies a two-second delay between requests.

A URL being publicly accessible does not automatically establish permission to reproduce or redistribute its contents. Review the applicable website terms and document licences before redistributing the collected content.

## Manifest

See [`data/manifest.csv`](data/manifest.csv) for the downloaded files' source URLs, download dates, file sizes, and SHA-256 hashes.

## Storage

- `data/raw/`: full downloaded documents; excluded from Git.
- `data/sample/`: small sample files for the repository.
- `urls.txt`: source URLs used for collection.
- `tools/download.py`: downloader with collection safeguards.
- `tools/count_pages.py`: PDF page-count and dataset summary utility.
- `tools/find_pdf_links.py`: utility for finding PDF links in collected HTML pages.

## Limitations

The reported PDF page count is based on the PDF parser output. HTML files are counted as documents, not as their actual rendered page counts. Some PDF parser warnings were reported while reading one PDF; verify that file if exact page extraction or text parsing is needed.
