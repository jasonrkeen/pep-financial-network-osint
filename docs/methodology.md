# Implementation workflow and maturity

This module implements a small frozen synthetic scenario. It is not a universal doctrine, proprietary risk score or automated accusation system.

| Stage | Question and control | Artifact |
|---|---|---|
| Requirements | What records support distinct ownership, control, funding and title propositions as of 2026-02-01? Scope is the demo only. | README, nine claims |
| Entity resolution | Join exact stable IDs; fictional registration identifiers are retained; no automatic name-based merging. Uncertain matches need separate IDs and collection. | entities, reference validator |
| Ownership/control | Shareholding, directors, family and account context remain different relations. Ownership intervals are explicit; formal shareholding does not alone prove practical control or ultimate benefit. | relationships, CL001–CL003 |
| Transactions | Preserve amount, currency, date, stated purpose and bank context. Blank purpose means unknown. Totals are currency-separated. | transactions, aggregations |
| Asset linkage | Compare payee/purchaser and chronology; require earmarking for definitive funding. Independently record purchase price and unknown market value. | A001, CL004–CL005 |
| Corporate succession/title | Merger certificate supports legal succession. An omitted asset-specific schedule leaves title open. | CL006–CL007 |
| Confidence/unknowns | Retain explicit states, qualitative judgments and competing explanations. Rejected means unsupported on the current record. | claims, evidence matrix |
| Collection gaps | Name missing records and next collection action; preserve title, beneficiaries and source-of-funds gaps. | unresolved gaps |

All implementation controls are **demo-tested**, not independently validated production methodology. Established/Corroborated/Analytic/Open dependency describe evidence maturity, not software maturity. Experimental is a reserved vocabulary value, with no scoring implementation. A human must reassess typed evidence and prose before new cases or real records are introduced.

The graph is a MultiDiGraph so parallel transactions and historical shareholding are retained. Claims do not generate edges: rejected ownership and unresolved beneficiary/title assertions cannot appear as facts. Historical purchase is labeled separately from current title; the directed family edge is just a stored relation and has no ownership meaning. Account context does not attribute control to a bank. No proximity or centrality measure is used as a risk judgment.
