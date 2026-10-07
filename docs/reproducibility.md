# Reproducibility

Reference interpreter: Python 3.14.4; direct dependencies pinned in `requirements.txt`. `requirements-lock.txt` captures all packages used for the verified Windows run. On another platform use a fresh environment; compiled dependencies and image rendering may vary. Network access is needed to install dependencies, but the demo itself is offline.

Follow README commands from the repository root. Windows activation: `.venv\Scripts\Activate.ps1`; POSIX activation: `source .venv/bin/activate`. The validator is also usable without third-party packages. Install the lock file when recreating the full recorded dependency set.

Data is in seven UTF-8 CSV files; ID lists use semicolons inside cells. The additive aggregation table makes currency controls executable without adding totals to transaction rows. Assets A001/A002 are asset nodes, not duplicate entity rows. Dates are ISO 8601; cutoff is fixed at 2026-02-01 and passed explicitly for historical checks.

The clean fixture is a full copy of demo inputs; tests assert consistency. The broken fixture is a full alternative dataset with deliberately documented reference and inference defects. See `tests/fixtures/README.md`. It MUST fail with exit code 1; the normal build refuses invalid data and produces no fresh outputs. Existing outputs do not certify a failed run; inspect the validation file and input hashes.

Generated outputs: GraphML, PNG, one row per claim evidence matrix, collection-gap table, source-dependency table, clean validation JSON and SHA-256 input manifest. Broken validation JSON and the test report are captured separately. CSV/GraphML semantics, layout positions and input hashes are deterministic. PNG bytes may differ by platform/font/library version; compare labels and relationships, not cross-platform pixel hashes.

Run `python -m pytest -q` for all frozen tests and regression checks. See `outputs/test_results.txt` and `docs/red_team_review.md` for the actual execution record. Each guardrail test mutates an otherwise clean dataset to prove the relevant control detects its intended failure. Full broken-fixture tests verify the combined defect classes.

No credentials are committed. GitHub authentication is external to these scripts. CI performs validation/tests/build only, with read-only repository permissions. It does not deploy, publish or make the repository public.
