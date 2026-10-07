# Data dictionary

Every file has exact header order; unknown optional values are blank, never zero. Stable IDs are case-sensitive. All records are synthetic. Amounts use decimal arithmetic. Names do not resolve entities.

## synthetic_entities.csv

| Field | Meaning |
|---|---|
| `entity_id` | Stable identifier or exact typed reference as named; see validator. |
| `name` | Fictional display name; no match-based identity merging. |
| `entity_type` | person, company, trust or bank. |
| `jurisdiction` | Fictional jurisdiction; does not imply real legal applicability. |
| `registration_id` | Stable identifier or exact typed reference as named; see validator. |
| `start_date` | ISO YYYY-MM-DD; blank only when not known/applicable. |
| `end_date` | ISO YYYY-MM-DD; blank only when not known/applicable. |
| `status` | Table-specific lifecycle or one of six claim states; explicit Unknown/Unresolved retained. |
| `notes` | Human context and source-bounded cautions. |

## synthetic_relationships.csv

| Field | Meaning |
|---|---|
| `relationship_id` | Stable identifier or exact typed reference as named; see validator. |
| `source_entity_id` | Stable identifier or exact typed reference as named; see validator. |
| `target_entity_id` | Stable identifier or exact typed reference as named; see validator. |
| `relationship_type` | family, ownership, director, merger or bank_context. |
| `start_date` | ISO YYYY-MM-DD; blank only when not known/applicable. |
| `end_date` | ISO YYYY-MM-DD; blank only when not known/applicable. |
| `confidence` | High, Moderate, Low or Unknown; qualitative, never legal probability. |
| `source_ids` | Semicolon-delimited IDs from sources; required on all substantive rows. |
| `notes` | Human context and source-bounded cautions. |
| `temporal_status` | Current or Historical relative to explicit as-of date. |
| `ownership_percent` | Shareholding percentage; >0 and <=100 for ownership edges. |
| `support_basis` | Typed evidence category; human review must verify its truth. |

## synthetic_transactions.csv

| Field | Meaning |
|---|---|
| `transaction_id` | Stable identifier or exact typed reference as named; see validator. |
| `date` | ISO YYYY-MM-DD; blank only when not known/applicable. |
| `payer_entity_id` | Stable identifier or exact typed reference as named; see validator. |
| `payee_entity_id` | Stable identifier or exact typed reference as named; see validator. |
| `amount` | Positive finite decimal in row currency; no implicit conversion. |
| `currency` | Three-letter currency code; demo uses USD/EUR. |
| `payment_purpose_recorded` | Verbatim fictional recorded purpose; blank means unknown. |
| `account_bank_context` | Synthetic institutional context; no real account numbers. |
| `source_ids` | Semicolon-delimited IDs from sources; required on all substantive rows. |
| `confidence` | High, Moderate, Low or Unknown; qualitative, never legal probability. |
| `limitations` | Proposition-specific gaps and uncertainty; never convert blank into zero. |
| `earmarked_asset_id` | Blank absent asset-specific earmarking; reference to asset when supported. |

## synthetic_assets.csv

| Field | Meaning |
|---|---|
| `asset_id` | Stable identifier or exact typed reference as named; see validator. |
| `asset_type` | Synthetic property category. |
| `description` | Fictional asset display label. |
| `jurisdiction` | Fictional jurisdiction; does not imply real legal applicability. |
| `associated_entity_id` | Stable identifier or exact typed reference as named; see validator. |
| `ownership_status` | Historical purchaser; current title unresolved, or Address association only. |
| `valuation_status` | Purchase price only; market value unknown, or Unknown. |
| `source_ids` | Semicolon-delimited IDs from sources; required on all substantive rows. |
| `confidence` | High, Moderate, Low or Unknown; qualitative, never legal probability. |
| `limitations` | Proposition-specific gaps and uncertainty; never convert blank into zero. |
| `association_basis` | purchase_record or address; distinct from title. |
| `purchaser_entity_id` | Stable identifier or exact typed reference as named; see validator. |
| `purchase_date` | ISO YYYY-MM-DD; blank only when not known/applicable. |
| `purchase_price` | Recorded price, not market valuation; blank if unknown. |
| `currency` | Three-letter currency code; demo uses USD/EUR. |
| `value_basis` | purchase_record or unknown; funding_amount is deliberately invalid. |

## synthetic_claims.csv

| Field | Meaning |
|---|---|
| `claim_id` | Stable identifier or exact typed reference as named; see validator. |
| `proposition` | Exact assertion assessed; rejected assertions explicitly marked unsupported. |
| `subject_entity_id` | Stable identifier or exact typed reference as named; see validator. |
| `object_id` | Stable identifier or exact typed reference as named; see validator. |
| `claim_type` | ownership, control, funding, succession, title or beneficiary. |
| `status` | Table-specific lifecycle or one of six claim states; explicit Unknown/Unresolved retained. |
| `confidence` | High, Moderate, Low or Unknown; qualitative, never legal probability. |
| `source_ids` | Semicolon-delimited IDs from sources; required on all substantive rows. |
| `competing_explanation` | Plausible alternative rather than a probabilistic weight. |
| `required_next_evidence` | Actionable missing records; mandatory for open/analytic claims. |
| `maturity` | Established, Corroborated, Analytic, Experimental or Open dependency; independent of confidence. |
| `support_basis` | Typed evidence category; human review must verify its truth. |
| `limitations` | Proposition-specific gaps and uncertainty; never convert blank into zero. |
| `original_status` | Frozen claim state used to catch silent unresolved-state coercion. |
| `resolved_boolean` | Always blank. False/0/true outcomes are prohibited in this ledger. |
| `independent_source_count` | Integer number of distinct documented roots; not verified witness independence. |
| `evidence_record_id` | Explicit relationship or transaction basis when applicable; not a substitute for source_ids. |

## synthetic_sources.csv

| Field | Meaning |
|---|---|
| `source_id` | Stable identifier or exact typed reference as named; see validator. |
| `title` | Synthetic document title. |
| `publisher` | Fictional issuing institution. |
| `source_type` | Registry, disclosure, bank/purchase/merger record, news or bounded search log. |
| `publication_date` | ISO YYYY-MM-DD; blank only when not known/applicable. |
| `reference` | Synthetic demo:// locator; not an actual registry URL. |
| `source_quality` | High or Moderate synthetic quality judgment, not a weight. |
| `primary_or_secondary` | Primary or Secondary; derivatives must be Secondary. |
| `notes` | Human context and source-bounded cautions. |
| `derived_from` | Semicolon-delimited parent source IDs; blank only for a declared root. |
| `record_key` | Canonical source document identity; duplicate keys cannot claim separate ancestry. |

## synthetic_aggregations.csv

| Field | Meaning |
|---|---|
| `aggregation_id` | Stable identifier or exact typed reference as named; see validator. |
| `transaction_ids` | Semicolon-delimited transaction references included once in total. |
| `amount` | Positive finite decimal in row currency; no implicit conversion. |
| `currency` | Three-letter currency code; demo uses USD/EUR. |
| `fx_source_id` | Documented FX source ID for cross-currency totals; never guessed. |
| `fx_rates` | Optional JSON mapping source currency to multiplier in target currency; requires FX source. |
