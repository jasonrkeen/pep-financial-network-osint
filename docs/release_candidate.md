# Public-release preparation — 2026-10-14

The owner approved MIT licensing and subsequently authorized public release of this synthetic portfolio. Approval is recorded; it is not evidence that repository visibility has changed.

## Release scope

The release covers this repository's synthetic demonstration, Python implementation, documentation, fixtures and outputs. It does not include named investigative case files, unpublished editorial submissions or operational deployment claims. The separate private research baseline is unchanged.

## Verification gates

The existing Validate synthetic portfolio workflow reruns the automated tests, clean validator, graph build and expected broken-fixture failure. The additional Release boundary audit scans all reachable fetched Git history for a listed set of credential patterns and sensitive/case-specific filenames, verifies production source metadata is synthetic, checks the sole historical binary against the previously reviewed graph hash, confirms the approved MIT license and checks relative documentation links. This is a bounded automated check, not an independent security certification.

Inspect the results attached to the exact release commit. Before changing visibility, also consider the commit author name/email and prior Actions logs, issues, comments and artifacts, which may become publicly accessible and are not comprehensively covered by the history script. No automated step changes visibility.

## Publication status

As of preparation, the repository remains private and no v1.0.0 tag or GitHub Release has been created. The public visibility change must be performed through an authenticated repository-administration channel. Afterward, verify the README and license without authentication before enabling the LinkedIn launch announcement.

Do not call the self-review an independent audit, software tests empirical validation of the method, or an unsupported ownership claim disproven in reality. Tests exercise authored synthetic records and encoded controls only.
