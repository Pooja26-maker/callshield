# <CallShield>

## Problem
<Customers lose phones, find unknown SIMs registered in their name, or get fraud calls, and do not know the official steps. The answers are spread across Sanchar Saathi pages, DoT guidelines and press notes. Shop owners guess.>

## Who it is for
<Owner of a mobile recharge and repair shop in Kumbakonam whose customers ask about spam calls, number porting, wrong charges and threats of SIM disconnection>

## Signature feature
<Step guide: type a situation ('phone stolen in bus') and get the official steps with the exact Sanchar Saathi service to use.>

## Hardest problem (my interview story)
<Exact-term hybrid search + re-ranking. Users type exact things like an IMEI, '*#06#', 'Chakshu', 'CEIR' or a complaint number. The system uses BM25 for these exact terms together with vectors and a re-ranker, and is tested on a set of code-heavy questions.>

## Dataset
| Source | Link | Documents | Pages | Licence / terms |
|---|---|---|---|---|
| <name> | <url> | <n> | <n> | <licence> |

## 10 real questions
See [docs/QUESTIONS.md](docs/QUESTIONS.md).

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                 # Windows: copy .env.example .env
uvicorn app.main:app --reload
curl localhost:8000/health
```

## Live link
<Added in Week 2>
