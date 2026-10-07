"""Deterministic structural and typed evidence controls, not truth adjudication."""
import argparse
import csv
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .confidence import CONFIDENCE, MATURITY, STATES, is_open
from .provenance import independent_roots, roots, split_ids

SCHEMAS = {
    'entities': 'entity_id name entity_type jurisdiction registration_id start_date end_date status notes',
    'relationships': 'relationship_id source_entity_id target_entity_id relationship_type start_date end_date confidence source_ids notes temporal_status ownership_percent support_basis',
    'transactions': 'transaction_id date payer_entity_id payee_entity_id amount currency payment_purpose_recorded account_bank_context source_ids confidence limitations earmarked_asset_id',
    'assets': 'asset_id asset_type description jurisdiction associated_entity_id ownership_status valuation_status source_ids confidence limitations association_basis purchaser_entity_id purchase_date purchase_price currency value_basis',
    'claims': 'claim_id proposition subject_entity_id object_id claim_type status confidence source_ids competing_explanation required_next_evidence maturity support_basis limitations original_status resolved_boolean independent_source_count evidence_record_id',
    'sources': 'source_id title publisher source_type publication_date reference source_quality primary_or_secondary notes derived_from record_key',
    'aggregations': 'aggregation_id transaction_ids amount currency fx_source_id fx_rates',
}
TABLE_IDS = {name: schema.split()[0] for name, schema in SCHEMAS.items()}
REL_TYPES = {'family', 'ownership', 'director', 'merger', 'bank_context'}
CLAIM_TYPES = {'ownership', 'control', 'funding', 'succession', 'title', 'beneficiary'}
BASES = {'registry', 'family', 'corporate_ownership', 'chronology', 'merger_record', 'general_succession', 'address', 'missing_record', 'earmark'}


def load_data(directory):
    tables = {}
    for table, schema in SCHEMAS.items():
        with (Path(directory) / ('synthetic_' + table + '.csv')).open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != schema.split():
                raise ValueError(f'{table}: expected exact columns {schema}')
            rows = list(reader)
            if any(None in row or None in row.values() for row in rows):
                raise ValueError(f'{table}: malformed CSV row')
            tables[table] = rows
    return tables


def validate(tables, as_of='2026-02-01'):
    errors, warnings = [], []

    def error(code, table, row, detail):
        errors.append({'code': code, 'table': table, 'record_id': row.get(TABLE_IDS[table], ''), 'detail': detail})

    def number(value):
        try:
            result = Decimal(value)
            return result if result.is_finite() else None
        except (InvalidOperation, TypeError):
            return None

    cutoff = date.fromisoformat(as_of)
    indexes = {}
    for table, rows in tables.items():
        indexes[table] = {}
        for row in rows:
            record_id = row[TABLE_IDS[table]]
            if not record_id or record_id in indexes[table]:
                error('DUPLICATE_ID', table, row, 'ID must be nonempty and unique in its table')
            indexes[table][record_id] = row
            for field in ['start_date', 'end_date', 'date', 'publication_date', 'purchase_date']:
                if field in row and row[field]:
                    try:
                        date.fromisoformat(row[field])
                    except ValueError:
                        error('INVALID_DATE', table, row, field)
            if row.get('start_date') and row.get('end_date') and row['start_date'] > row['end_date']:
                error('INVALID_DATE', table, row, 'end precedes start')
            if 'confidence' in row and row['confidence'] not in CONFIDENCE:
                error('INVALID_CONFIDENCE', table, row, 'use qualitative vocabulary')
    entities, sources = indexes['entities'], indexes['sources']
    registrations = set()
    for row in tables['entities']:
        if row['entity_type'] not in {'person', 'company', 'trust', 'bank'}:
            error('ENTITY_TYPE', 'entities', row, 'unsupported entity type')
        if not row['jurisdiction'].startswith('Demo ') or (row['registration_id'] and not row['registration_id'].startswith('DEMO-')):
            error('SYNTHETIC_BOUNDARY', 'entities', row, 'use fictional jurisdictions and registration keys')
        if row['registration_id']:
            identity = (row['jurisdiction'], row['registration_id'])
            if identity in registrations:
                error('REGISTRATION_COLLISION', 'entities', row, 'same registration/jurisdiction needs explicit identity review')
            registrations.add(identity)
    all_objects = set(entities) | set(indexes['assets']) | set(indexes['transactions'])
    if len(all_objects) != sum(len(indexes[x]) for x in ['entities', 'assets', 'transactions']):
        errors.append({'code': 'AMBIGUOUS_ID', 'table': 'entities', 'record_id': '', 'detail': 'entity/asset/transaction IDs must be globally disjoint'})
    refs = {
        'relationships': ['source_entity_id', 'target_entity_id'],
        'transactions': ['payer_entity_id', 'payee_entity_id'],
        'assets': ['associated_entity_id', 'purchaser_entity_id'],
        'claims': ['subject_entity_id'],
    }
    for table, fields in refs.items():
        for row in tables[table]:
            for field in fields:
                optional = field == 'purchaser_entity_id'
                if (row[field] or not optional) and row[field] not in entities:
                    error('ENTITY_REFERENCE', table, row, field)
            if table == 'claims' and row['object_id'] not in all_objects:
                error('OBJECT_REFERENCE', table, row, 'object_id')
    for table in ['relationships', 'transactions', 'assets', 'claims']:
        for row in tables[table]:
            ids = split_ids(row['source_ids'])
            if not ids:
                error('SOURCE_REQUIRED', table, row, 'even rejected/open propositions need source-bounded context')
            for source_id in ids:
                if source_id not in sources:
                    error('SOURCE_REFERENCE', table, row, source_id)
            if len(ids) != len(set(ids)):
                error('DUPLICATE_SOURCE', table, row, 'repeated citation')
    for row in tables['sources']:
        if not row['reference'].startswith('demo://') or not row['title'].startswith('SYNTHETIC:'):
            error('SYNTHETIC_BOUNDARY', 'sources', row, 'source register is synthetic-only')
        if row['primary_or_secondary'] not in {'Primary', 'Secondary'}:
            error('SOURCE_KIND', 'sources', row, 'invalid primary_or_secondary')
        if row['derived_from'] and row['primary_or_secondary'] == 'Primary':
            error('SOURCE_KIND', 'sources', row, 'derivative must be labeled Secondary')
        try:
            roots(row['source_id'], sources)
        except ValueError as exc:
            error('SOURCE_LINEAGE', 'sources', row, str(exc))
        if row['derived_from']:
            warnings.append({'code': 'DERIVATIVE_CONTEXT', 'record_id': row['source_id'], 'detail': 'retained for context; not independent corroboration'})
    record_keys = {}
    for row in tables['sources']:
        if not row['record_key']:
            error('RECORD_KEY_REQUIRED', 'sources', row, 'canonical document identifier required')
        record_keys.setdefault(row['record_key'], []).append(row)
    for group in record_keys.values():
        if len(group) > 1:
            try:
                ancestry = set.union(*(roots(x['source_id'], sources) for x in group))
                if len(ancestry) > 1:
                    error('DUPLICATE_LINEAGE', 'sources', group[-1], 'same record_key claims separate roots')
            except ValueError:
                pass
    for row in tables['relationships']:
        if row['relationship_type'] not in REL_TYPES:
            error('RELATIONSHIP_TYPE', 'relationships', row, 'unsupported relation')
        if row['support_basis'] not in BASES:
            error('SUPPORT_BASIS', 'relationships', row, 'invalid basis')
        if row['temporal_status'] not in {'Current', 'Historical'}:
            error('TEMPORAL_OWNERSHIP', 'relationships', row, 'explicit temporal state required')
        if row['relationship_type'] == 'ownership':
            if not row['start_date'] or (row['temporal_status'] == 'Historical' and not row['end_date']):
                error('TEMPORAL_OWNERSHIP', 'relationships', row, 'ownership requires dated interval')
            if row['temporal_status'] == 'Current' and (row['start_date'] > as_of or (row['end_date'] and row['end_date'] <= as_of)):
                error('TEMPORAL_OWNERSHIP', 'relationships', row, f'not current at {cutoff}')
            if row['temporal_status'] == 'Historical' and (not row['end_date'] or row['end_date'] > as_of):
                error('TEMPORAL_OWNERSHIP', 'relationships', row, 'historical interval must end by cutoff')
            pct = number(row['ownership_percent'])
            if pct is None or not 0 < pct <= 100:
                error('OWNERSHIP_PERCENT', 'relationships', row, 'percentage must be >0 and <=100')
            if row['support_basis'] == 'family':
                error('FAMILY_NOT_OWNERSHIP', 'relationships', row, 'kinship supplies no ownership evidence')
    for row in tables['transactions']:
        amount = number(row['amount'])
        if amount is None or amount <= 0 or not re.fullmatch('[A-Z]{3}', row['currency']):
            error('TRANSACTION_AMOUNT', 'transactions', row, 'positive finite amount and ISO-style currency required')
        if not row['date']:
            error('INVALID_DATE', 'transactions', row, 'transaction date required')
        if row['earmarked_asset_id'] and row['earmarked_asset_id'] not in indexes['assets']:
            error('OBJECT_REFERENCE', 'transactions', row, 'earmarked asset missing')
    for row in tables['assets']:
        if row['association_basis'] not in {'address', 'purchase_record'}:
            error('SUPPORT_BASIS', 'assets', row, 'invalid asset association basis')
        if row['value_basis'] not in {'purchase_record', 'unknown', 'funding_amount'}:
            error('VALUE_BASIS', 'assets', row, 'invalid value basis')
        if row['value_basis'] == 'funding_amount':
            error('FUNDING_NOT_VALUATION', 'assets', row, 'funding cannot substitute for purchase price or valuation')
        if row['valuation_status'] not in {'Purchase price only; market value unknown', 'Unknown'}:
            error('VALUATION_STATUS', 'assets', row, 'purchase price is not current market value')
        if row['purchase_price']:
            amount = number(row['purchase_price'])
            if amount is None or amount <= 0 or not row['currency'] or row['value_basis'] != 'purchase_record':
                error('FUNDING_NOT_VALUATION', 'assets', row, 'price requires separate purchase record and currency')
            if not any(sources.get(s, {}).get('source_type') == 'purchase_record' for s in split_ids(row['source_ids'])):
                error('PURCHASE_EVIDENCE', 'assets', row, 'recorded price requires a cited purchase record')
            if not row['purchaser_entity_id'] or not row['purchase_date']:
                error('PURCHASE_EVIDENCE', 'assets', row, 'purchase needs purchaser and date')
        if row['ownership_status'] not in {'Historical purchaser; current title unresolved', 'Address association only'}:
            error('OWNERSHIP_STATUS', 'assets', row, 'unsupported title state')
        if row['association_basis'] == 'address' and (row['ownership_status'] != 'Address association only' or row['purchaser_entity_id'] or row['purchase_price']):
            error('ADDRESS_NOT_TITLE', 'assets', row, 'shared address does not establish title')
    for row in tables['claims']:
        record = indexes['relationships'].get(row['evidence_record_id']) or indexes['transactions'].get(row['evidence_record_id'])
        if row['evidence_record_id'] and record is None:
            error('EVIDENCE_REFERENCE', 'claims', row, 'evidence record missing')
        if record and not set(split_ids(record['source_ids'])) & set(split_ids(row['source_ids'])):
            error('EVIDENCE_CITATION', 'claims', row, 'claim does not cite its underlying evidence record')
        accepted = row['status'] in {'Confirmed', 'Strongly supported', 'Probable / analytic judgment'}
        if accepted and row['claim_type'] in {'ownership', 'control'}:
            if not record or record.get('relationship_type') != 'ownership' or record.get('source_entity_id') != row['subject_entity_id'] or record.get('target_entity_id') != row['object_id'] or record.get('support_basis') not in {'registry', 'corporate_ownership'}:
                error('OWNERSHIP_EVIDENCE', 'claims', row, 'attribution requires matching documented shareholding record in this demo')
        if accepted and row['claim_type'] == 'succession':
            if not record or record.get('relationship_type') != 'merger' or record.get('source_entity_id') != row['subject_entity_id'] or record.get('target_entity_id') != row['object_id']:
                error('SUCCESSION_EVIDENCE', 'claims', row, 'succession requires matching merger record')
        if row['status'] not in STATES or row['original_status'] not in STATES or row['maturity'] not in MATURITY:
            error('CLAIM_VOCABULARY', 'claims', row, 'invalid status/maturity')
        if row['claim_type'] not in CLAIM_TYPES or row['support_basis'] not in BASES:
            error('CLAIM_VOCABULARY', 'claims', row, 'invalid claim type/basis')
        if row['resolved_boolean']:
            error('UNKNOWN_COERCION', 'claims', row, 'claims retain explicit states, never boolean/zero outcomes')
        if row['original_status'] == 'Unresolved' and row['status'] != 'Unresolved':
            error('UNKNOWN_COERCION', 'claims', row, 'reassessment requires a new version and evidence review')
        if is_open(row) and (not row['required_next_evidence'] or not row['limitations']):
            error('OPEN_DEPENDENCY', 'claims', row, 'open evidence needs gap and next collection action')
        if row['status'] == 'Probable / analytic judgment' and (row['maturity'] != 'Analytic' or not row['limitations'] or not row['competing_explanation'] or not row['required_next_evidence']):
            error('INFERENCE_LABEL', 'claims', row, 'inference requires assumptions, alternative and collection gap')
        if row['status'] == 'Confirmed' and not any(sources.get(s, {}).get('primary_or_secondary') == 'Primary' for s in split_ids(row['source_ids'])):
            error('PRIMARY_REQUIRED', 'claims', row, 'demo confirmed claims require a primary record')
        if row['claim_type'] in {'ownership', 'control'} and row['support_basis'] == 'family' and row['status'] != 'Rejected':
            error('FAMILY_NOT_OWNERSHIP', 'claims', row, 'family association cannot support attribution')
        if row['claim_type'] == 'title' and row['support_basis'] == 'address' and row['status'] != 'Rejected':
            error('ADDRESS_NOT_TITLE', 'claims', row, 'address-only claim must remain rejected')
        if row['claim_type'] == 'title' and row['support_basis'] == 'general_succession' and row['status'] != 'Unresolved':
            error('SUCCESSION_NOT_TITLE', 'claims', row, 'asset-specific transfer/title evidence missing')
        if row['claim_type'] == 'funding' and row['status'] != 'Rejected':
            tx = indexes['transactions'].get(row['evidence_record_id'])
            asset = indexes['assets'].get(row['object_id'])
            if not tx or not asset:
                error('FUNDING_EVIDENCE', 'claims', row, 'funding requires linked transaction and asset records')
            elif row['support_basis'] == 'chronology':
                if row['status'] != 'Probable / analytic judgment':
                    error('FUNDING_EARMARK', 'claims', row, 'chronology supports only explicit inference')
                if tx['date'] > asset['purchase_date'] or tx['payee_entity_id'] != asset['purchaser_entity_id']:
                    error('FUNDING_CHRONOLOGY', 'claims', row, 'date or counterparty incompatible with acquisition')
            elif row['support_basis'] != 'earmark' or tx['earmarked_asset_id'] != row['object_id']:
                error('FUNDING_EARMARK', 'claims', row, 'definitive funding requires earmark evidence')
        try:
            count = len(independent_roots(row['source_ids'], sources))
            if int(row['independent_source_count']) != count:
                error('DERIVATIVE_INDEPENDENCE', 'claims', row, 'claimed source count differs from distinct lineage roots')
            if row['maturity'] == 'Corroborated' and count < 2:
                error('DERIVATIVE_INDEPENDENCE', 'claims', row, 'corroboration needs at least two documented roots')
        except ValueError:
            error('DERIVATIVE_INDEPENDENCE', 'claims', row, 'invalid count or source ancestry')
    for row in tables['aggregations']:
        txs = [indexes['transactions'].get(tx) for tx in split_ids(row['transaction_ids'])]
        if not txs or any(tx is None for tx in txs):
            error('TRANSACTION_REFERENCE', 'aggregations', row, 'unknown or empty transaction list')
            continue
        if len(split_ids(row['transaction_ids'])) != len(set(split_ids(row['transaction_ids']))):
            error('TRANSACTION_REFERENCE', 'aggregations', row, 'duplicate transactions in total')
        currencies = {tx['currency'] for tx in txs}
        try:
            if currencies != {row['currency']}:
                if row['fx_source_id'] not in sources or not row['fx_rates']:
                    raise ValueError('cross-currency total requires documented FX source and rates')
                if sources[row['fx_source_id']]['source_type'] != 'fx_record':
                    raise ValueError('FX evidence must be explicitly typed as fx_record')
                rates = json.loads(row['fx_rates'])
                if set(rates) != currencies or any(number(str(v)) is None or number(str(v)) <= 0 for v in rates.values()):
                    raise ValueError('FX mapping must cover every source currency with finite positive rates')
                if row['currency'] in rates and Decimal(str(rates[row['currency']])) != 1:
                    raise ValueError('target currency rate must be 1')
            else:
                rates = {row['currency']: 1}
            total = sum(Decimal(tx['amount']) * Decimal(str(rates[tx['currency']])) for tx in txs)
            if number(row['amount']) != total:
                raise ValueError('total does not match documented conversion')
        except (ValueError, InvalidOperation, TypeError, KeyError) as exc:
            error('CURRENCY_AGGREGATION', 'aggregations', row, str(exc))
    return {'as_of': as_of, 'errors': errors, 'warnings': warnings, 'error_count': len(errors), 'warning_count': len(warnings)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=Path('data'))
    parser.add_argument('--as-of', default='2026-02-01')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = validate(load_data(args.data), args.as_of)
    except (OSError, ValueError) as exc:
        result = {'errors': [{'code': 'LOAD_ERROR', 'detail': str(exc)}], 'error_count': 1, 'warnings': []}
    payload = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding='utf-8')
    print(payload)
    return 1 if result['error_count'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
