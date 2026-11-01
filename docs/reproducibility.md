# Reproducibility

Reference interpreter: Python 3.14.4; direct dependencies pinned in `requirements.txt`. `requirements-lock.txt` captures all packages used for the verified Windows run. On another platform use a fresh environment; compiled dependencies and image rendering may vary. Network access is needed to install dependencies, but the demo itself is offline.

Follow README commands from the repository root. Windows activation: `.venv\Scripts\Activate.ps1`; POSIX activation: `source .venv/bin/activate`. The validator is also usable without third-party packages. Install the lock file when recreating the full recorded dependency set.

Data is in seven UTF-8 CSV files; ID lists use semicolons inside cells. The additive aggregation table makes currency controls executable without adding totals to transaction rows. Assets A001/A002 are asset nodes, not duplicate entity rows. Dates are ISO 8601; cutoff is fixed at 2026-02-01 and passed explicitly for historical checks.

The clean fixture is a full copy of demo inputs; tests assert consistency. The broken fixture is a full alternative dataset with deliberately documented reference and inference defects. See `tests/fixtures/README.md`. It MUST fail with exit code 1; the normal build refuses invalid data and produces no fresh outputs. Existing outputs do not certify a failed run; inspect the validation file and input hashes.

Generated outputs: GraphML, PNG, one row per claim evidence matrix, collection-gap table, source-dependency table, clean validation JSON and SHA-256 input manifest. Broken validation JSON and the test report are captured separately. CSV/GraphML semantics, layout positions and input hashes are deterministic. PNG bytes may differ by platform/font/library version; compare labels and relationships, not cross-platform pixel hashes.

Run `python -m pytest -q` for all frozen tests and regression checks. See `outputs/test_results.txt` and `docs/red_team_review.md` for the actual execution record. Each guardrail test mutates an otherwise clean dataset to prove the relevant control detects its intended failure. Full broken-fixture tests verify the combined defect classes.

No credentials are committed. GitHub authentication is external to these scripts. CI performs validation/tests/build only, with read-only repository permissions. It does not deploy, publish or make the repository public.

## Employer brief and single command

After installing the pinned requirements, run `python -m src.main` from the repository root. It uses the frozen synthetic CSV inputs to regenerate GraphML/PNG, evidence/source/gap tables, clean/broken validation, the three-page PDF and `docs/employer_brief.md`. It performs no network collection and never changes repository visibility. To regenerate only the brief, run `python -m src.build_employer_brief`.

The brief uses ReportLab 4.4.9 and pypdf 6.10.0, both pinned. PDF metadata uses deterministic timestamps and contains the intended author name, not a local filesystem path. `BriefConfig` separates the document update date (2026-11-01) from the unchanged evidence cutoff (2026-02-01). The test count displayed in the brief comes from the successful recorded `outputs/test_results.txt`; rebuilding a PDF alone does not rerun pytest or refresh that record. The final review records a fresh full-suite run. Layout is fixed to the frozen 12-node/14-edge demo; changed data requires a new visual review.

Verify semantic content and three-page layout after any edit. Byte repeatability is checked within one dependency environment; different platforms may render graph fonts or compression differently. The release audit checks committed binary hashes against explicit reviewed versions; a changed PDF or graph must be visually reviewed and added deliberately, never accepted automatically by extension.
