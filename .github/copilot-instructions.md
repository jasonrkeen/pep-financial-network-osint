# Copilot instructions: PEP Financial Network OSINT — synthetic portfolio

## Purpose
Reproducible financial-intelligence workflow for PEP, offshore-network, transaction, and asset analysis using synthetic data.

## Tech stack
- Python; dependencies in `requirements.txt`
- Key libraries: `networkx`, `matplotlib`, `pytest`

## Folder structure
- `.github/` (2 files)
- `data/` (7 files)
- `docs/` (8 files)
- `outputs/` (14 files)
- `src/` (5 files)
- `tests/` (16 files)
- `tools/` (1 files)
- `.gitattributes`
- `README.md`
- `pytest.ini`
- `requirements-lock.txt`
- `requirements.txt`

## Setup, run, test
Commands documented in README.md (referenced files exist):
```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pytest -q
python -m src.validate_data --data data --output outputs/validation_clean.json
python -m src.build_network --data data --output outputs
python -m src.validate_data --data tests/fixtures/broken --output outputs/validation_broken.json
```
- Tests: 1 Python test file(s) under `tests/`; framework appears to be pytest. Add/update tests with any logic change.
- CI workflows exist in `.github/workflows/`; keep them passing.

## Conventions observed
- Functions use type hints; keep annotating new code.
- Write paths relative to the repo root (no absolute local paths).

## Output artifacts
- Generated outputs go to `outputs/`.
- Charts are generated with matplotlib.

## Guardrails
- Never commit secrets, API keys, tokens, or `.env` files.
- Do not commit large raw datasets or binaries; keep data fetched or documented with its source.
- Keep analysis source-backed: cite data sources and assumptions; label scenario/forecast outputs as model estimates, not facts.
- Synthetic data must stay synthetic; never introduce real personal or sensitive records.
- Preserve reproducibility: no unseeded randomness, no hidden manual steps.
