# Private release candidate review — 2026-10-25

MIT licensing is approved and implemented. The owner's current instruction on 2026-10-25 is to update/add the brief and complete the release review while keeping the repository private until a new final approval. This instruction supersedes earlier publication-preparation wording. Neither passing checks nor merging a private PR authorizes a visibility change.

## Release scope

The release covers this repository's synthetic demonstration, Python implementation, documentation, fixtures and outputs. It does not include named investigative case files, unpublished editorial submissions or operational deployment claims. The separate private research baseline is unchanged.

## Verification gates

The Validate synthetic portfolio workflow reruns the automated tests, clean validator, full graph/table/PDF pipeline and expected broken-fixture failure. The Release boundary audit scans all reachable fetched Git history for listed credential patterns and sensitive/case-specific filenames, verifies production source metadata is synthetic, checks graph/PDF binaries against exact reviewed hashes, confirms MIT licensing and checks relative documentation links. Changed binaries are rejected unless explicitly reviewed and recorded in `reviewed_binary_hashes.json`. This is a bounded check, not an independent security certification.

Inspect the results attached to the exact release commit. Before changing visibility, also consider the commit author name/email and prior Actions logs, issues, comments and artifacts, which may become publicly accessible and are not comprehensively covered by the history script. No automated step changes visibility.

The final review separately inventories and inspects these GitHub surfaces. Its scope, counts, metadata disclosure and any unavailable items are recorded in [the final review](final_release_review.md). The prior hostile review remains a self-review of the synthetic teaching artifact, not an independent methodology audit.

## Publication status

As of preparation, the repository remains private and no v1.0.0 tag or GitHub Release has been created. The public visibility change must be performed through an authenticated repository-administration channel. Afterward, verify the README and license without authentication before enabling the LinkedIn launch announcement.

Do not call the self-review an independent audit, software tests empirical validation of the method, or an unsupported ownership claim disproven in reality. Tests exercise authored synthetic records and encoded controls only.
