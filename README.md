# Citizen Help Finder (CIT)

## Problem

Customers lose phones, discover unknown SIMs registered in their names, or receive suspected fraud calls, but may not know the official steps to take. Relevant information is spread across government service pages, telecom guidelines, and official notices. Mobile recharge and repair shop owners may struggle to find the correct procedure quickly.

## Who it is for

A mobile recharge and repair shop owner in Kumbakonam whose customers ask about spam calls, mobile number porting, incorrect charges, and threats of SIM disconnection.

## Signature feature

**Situation-to-steps guidance:** A user enters a situation such as "phone stolen on a bus" and receives a step-by-step guide pointing to the relevant official service, with supporting source references.

The guidance must be grounded in collected official documents. If the sources do not contain enough information, the application should clearly say so rather than inventing instructions.

## Hardest technical problem

**Exact-term hybrid search and re-ranking.**

Users may enter exact identifiers and terms such as an IMEI, `*#06#`, `Chakshu`, `CEIR`, or a complaint number. The planned retrieval approach combines BM25 keyword search with vector search and a re-ranking stage. Evaluation will include code-heavy and exact-term questions to check whether the correct source passages are retrieved.

*Implementation status:* This describes the planned technical approach; retrieval and re-ranking performance still need to be implemented and evaluated.

## Dataset

The initial collection contains 10 HTML documents and 5 PDFs from the official TRAI website. The five PDFs contain 241 pages according to the PDF page-count utility.

- Source URLs and download metadata: `data/manifest.csv`
- URL list: `urls.txt`
- Raw downloads: `data/raw/` (excluded from Git)
- Sample content: `data/sample/`
- Evaluation questions: `docs/QUESTIONS.md`

The current collection focuses on TRAI telecom consumer information, FAQs, consumer protection, and complaint-related regulations. Sanchar Saathi and DoT sources remain additional sources to investigate; do not assume they are already included in the dataset.

### Sample files

The files in `data/sample/` are illustrative samples created for this project. They are not copied from government websites and should not be treated as verified official guidance.

## Evaluation questions

See [`docs/QUESTIONS.md`](docs/QUESTIONS.md) for the questions used to evaluate retrieval quality and evidence-grounded responses.

## Run locally

Create and activate a virtual environment, then install the project dependencies.

```bash
python -m venv .venv
```s
Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1s
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Check the health endpoint:

```text
http://localhost:8000/health
```

## Live link
Planned for Week 2.