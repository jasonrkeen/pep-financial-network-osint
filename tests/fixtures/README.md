# Fixtures

`clean/` mirrors all seven demo input CSVs exactly. `broken/` changes:

* CL001 subject → P999 (unknown entity).
* CL003 source → S999 (unknown source).
* R004 target and TX003 payer → C999 (unknown endpoints/counterparties).
* A001 price copied from TX001; value basis → funding_amount.
* AG001 mixes TX001 USD with TX002 EUR and no FX evidence.
* CL009 original Unresolved → Rejected/0, with its next-evidence action removed.
* R008 historical ownership → Current with dates removed.
* CL002 family-only attribution → Strongly supported.
* CL008 address-only title → Confirmed, counting S004/S005 as two roots.
* CL006 Confirmed with citations removed.
* CL004 chronology-only funding → Confirmed.
* CL007 open title dependency loses next-evidence action.

Multiple errors per row are expected. The frozen 14 tests isolate these controls using fresh clean copies; full-fixture testing verifies all combined failure categories. Broken data is labeled and never used as the portfolio graph.
