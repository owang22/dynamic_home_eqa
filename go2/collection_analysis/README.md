# Analysis of collect-mode sessions (first: 2026-10-23)

| file | does |
|---|---|
| `handholding.py` | groups a session's turns into tasks (hand-made table) and counts Oliver's hints, corrections and coaching per task -> `data/collection/analysis/handholding.md` |
| `questions.py` | memory questions with gold answers, ask times and evidence pictures, built from Oliver's notes and pictures checked by eye -> `questions_<day>.json` |
| `memory_qa.py` | the two baseline memories (A text tags, B SigLIP embeddings) answer the questions offline with Sonnet, then a Sonnet grader scores them -> `memory_qa_<day>.md` |

Run: `python3 handholding.py; python3 questions.py; python3 memory_qa.py retrieval; python3 memory_qa.py answer;
python3 memory_qa.py grade`. Model replies are cached in `data/collection/analysis/cache/` (gitignored with the rest of
`data/`).
