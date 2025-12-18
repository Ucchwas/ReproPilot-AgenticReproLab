# ReproPilot-AgenticReproLab

ReproPilot is a Python AI agent that reads a research paper PDF and generates a **reproducible repository scaffold** (a “repro repo” starter kit). Instead of only summarizing a paper, it creates an executable project layout with clear run instructions and sanity checks, so you can start reproducing results faster.

## What it generates
- `README.md` (what the paper does + how to reproduce, step-by-step)
- `requirements.txt` (environment dependencies)
- `.gitignore` (safe defaults; excludes secrets + local artifacts)
- `CITATION.cff` (citation metadata placeholder)
- `src/` (runnable placeholder code structure for `data/`, `train/`, `eval/`)
- `tests/` (simple sanity checks so the scaffold is not broken)
- `reports/reproducibility_report.md` (what was extracted + what was generated + what still needs manual work)

## How it works (overview)
1) Give ReproPilot a PDF path.  
2) It extracts: problem, dataset, model, metrics, training/evaluation details.  
3) It writes a reproducible repo scaffold into your output folder (`--out`).  
4) It runs basic checks (compile/tests) and logs everything into a local SQLite DB (`workspace/repropilot.sqlite3`).

## Quickstart (Windows)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .

# add API key in .env
# OPENAI_API_KEY=...
# OPENAI_MODEL=gpt-4.1-mini

repropilot reproduce --paper ".\papers\my_paper.pdf" --out ".\demo_repro_repo"
