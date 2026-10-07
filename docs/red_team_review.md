# Hostile review — 2026-10-06

Scope: frozen synthetic demo, code, both fixtures, generated GraphML/PNG, claims/evidence, source register, collection gaps and public-facing documentation. This is a documented hostile self-review, not an independent external audit. Repository access was restored through GitHub CLI and visibility verified private. No public release is authorized by this report.

## Questions and findings

| Attack question | Evidence and disposition |
|---|---|
| Can association be mistaken for ownership? | R002 is explicitly family-only; CL002 remains Rejected. A002 has a dotted address-only edge and an address-only node label; CL008 is Rejected. There is no P001→C001 ownership edge. Both attribution attacks fail validation. Sufficiently clear for the demo; a reader must retain the legend when reusing the visual. |
| Can timing be mistaken for proof of funding? | TX001 is labeled intercompany loan, dated and marked transfer only. CL004 states a qualified liquidity inference with an alternative use of funds and specific next records. CL005 rejects definitive funding. Promoting CL004 to Confirmed fails without earmark evidence. No property-funding edge is generated. |
| Can the graph imply stronger control than the table? | Initial graph had overlapping payment/shareholding labels. Fixed by separate label positions and preserving transaction purposes/dates. Historical shareholding uses a dashed edge and explicit historical label. Merger edge says A001 title unresolved. There is no C004→A001 title edge or P001→T001 beneficiary edge. GraphML round-trip retains typed multiedges and uncertainty metadata. |
| Do confidence labels imply legal certainty? | Labels are qualitative, proposition-specific and separate from evidence maturity. README/evidence rules explicitly reject legal probabilities. Confirmed describes the documented demo fact, not criminality or ultimate benefit. No numerical score or weighting is implemented. |
| Are negative findings source-bounded? | CL002/CL005/CL008 say unsupported on available evidence. S013 is explicitly a bounded demo-register search; CL007/CL009 stay Unresolved. No absence of a record is called proof of non-ownership or non-benefit. All open dependencies have next collection actions. |
| Could synthetic names create real-world confusion? | Frozen names are ordinary enough that coincidental matches cannot be ruled out. Every source title starts SYNTHETIC, references use demo://, jurisdictions/registrations are fictional, and every graph node says DEMO. README and ethics state these are fictional scenario roles and prohibit real-subject attribution. No external identity matching was attempted. Residual risk remains if labels/disclaimers are cropped; do not distribute cropped visuals. |

## Adversarial fixes and execution evidence

* Unrelated primary citations could previously appear to support ownership or price. Added matching shareholding/merger evidence-record checks, citation overlap checks and purchase-record type checks. Relabeling a family claim cannot supply a matching ownership record.
* Currency totals previously accepted any existing source as FX documentation. Now require an explicitly typed FX record, complete positive rate mapping, target-currency rate of one where applicable, and exact decimal recomputation.
* Added fictional-reference/jurisdiction controls and registration-collision detection. These are boundary aids; they cannot detect a real narrative disguised as fictional metadata.
* Source lineage detects missing parents, cycles, repeated canonical documents with separate roots, and inflated independence counts. S005 remains context, rooted in S004.
* Original unresolved states cannot silently become false/zero. CL007/CL009 remain visible, with TX004's economic source-of-funds gap also surfaced.

See [executed tests](../outputs/test_results.txt), [verification summary](../outputs/verification_summary.json), [clean validation](../outputs/validation_clean.json) and [broken validation](../outputs/validation_broken.json). The test suite includes the exact 14 frozen names plus regression checks. The clean demo has zero errors. The broken fixture must return exit code 1 and the graph builder must refuse it. Repeated local builds and GraphML round-trip are verified in the summary.

## Disposition

The six frozen review questions are addressed for this synthetic teaching artifact after the fixes above. Human evidence judgment remains necessary: typed metadata does not authenticate a source, validate hidden copying, verify foreign law, establish beneficial ownership or adjudicate legal responsibility. No operational or universal-methodology validity is claimed.

Private implementation/review may proceed. Public release remains gated by the owner's explicit visibility confirmation and license selection. Do not infer release permission from passing tests, a private PR or this review.
