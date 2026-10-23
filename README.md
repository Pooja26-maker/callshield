CallShield

## Problem
Customers lose phones, find unknown SIMs registered in their name, or get fraud calls, and do not know the official steps. The answers are spread across Sanchar Saathi pages, DoT guidelines and press notes. Shop owners guess.

## Who it is for
Owner of a mobile recharge and repair shop in Kumbakonam whose customers ask about spam calls, number porting, wrong charges and threats of SIM disconnection

## Signature feature
Step guide: type a situation ('phone stolen in bus') and get the official steps with the exact Sanchar Saathi service to use.

## Hardest problem (my interview story)
Exact-term hybrid search + re-ranking. Users type exact things like an IMEI, '*#06#', 'Chakshu', 'CEIR' or a complaint number. The system uses BM25 for these exact terms together with vectors and a re-ranker, and is tested on a set of code-heavy questions.

## Dataset

# Sample 01: Telecom FAQ

Type: Illustrative sample
Source: Original sample content, not copied from a government website
Language: English

Q: Where can a citizen find information about telecom services?

A: A citizen can consult official telecom department and regulator websites for service information, consumer guidance, and complaint procedures.

Q: Should a citizen share an OTP with someone claiming to be a telecom official?

A: Do not disclose an OTP to an unverified caller. Verify the request through an official service channel.



# Sample 02: Suspicious Call Guidance

Type: Illustrative sample
Source: Original sample content, not copied from a government website
Language: English

Q: What should someone do after receiving a suspicious call?

A: Avoid sharing personal information, passwords, OTPs, or financial details. Verify claims independently through an official channel.

Q: What information should be recorded when reporting a suspicious call?

A: Record relevant details such as the date, time, and caller information where appropriate. Avoid publishing another person's private information.




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
