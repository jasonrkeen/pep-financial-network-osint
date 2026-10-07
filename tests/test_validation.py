"""Frozen 14 acceptance tests: clean behavior plus isolated adversarial mutations."""
import copy
from pathlib import Path

import pytest
from src.build_network import build_graph
from src.provenance import independent_roots, roots
from src.validate_data import load_data, validate

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def clean():
    result = load_data(ROOT / 'tests/fixtures/clean')
    assert validate(result)['error_count'] == 0
    return result


def codes(data):
    return {error['code'] for error in validate(data)['errors']}


def test_all_entity_references_resolve(clean):
    clean['claims'][0]['subject_entity_id'] = 'P999'
    assert 'ENTITY_REFERENCE' in codes(clean)


def test_all_source_references_resolve(clean):
    clean['claims'][0]['source_ids'] = 'S999'
    assert 'SOURCE_REFERENCE' in codes(clean)


def test_relationship_endpoints_resolve(clean):
    clean['relationships'][0]['target_entity_id'] = ''
    assert 'ENTITY_REFERENCE' in codes(clean)


def test_transactions_have_valid_counterparties(clean):
    for field in ['payer_entity_id', 'payee_entity_id']:
        bad = copy.deepcopy(clean)
        bad['transactions'][0][field] = 'C999'
        assert 'ENTITY_REFERENCE' in codes(bad)


def test_claims_require_sources(clean):
    assert clean['claims'][0]['status'] == 'Confirmed'
    assert clean['claims'][0]['source_ids'] == 'S001'
    clean['claims'][0]['source_ids'] = ''
    assert 'SOURCE_REQUIRED' in codes(clean)


def test_unresolved_claims_preserved(clean):
    assert clean['claims'][6]['status'] == clean['claims'][8]['status'] == 'Unresolved'
    for value in ['false', '0']:
        bad = copy.deepcopy(clean)
        bad['claims'][6].update(status='Rejected', resolved_boolean=value)
        assert 'UNKNOWN_COERCION' in codes(bad)


def test_temporal_ownership_separation(clean):
    historical = clean['relationships'][7]
    assert historical['temporal_status'] == 'Historical' and historical['end_date']
    historical['temporal_status'] = 'Current'
    assert 'TEMPORAL_OWNERSHIP' in codes(clean)
    historical.update(start_date='', end_date='')
    assert 'TEMPORAL_OWNERSHIP' in codes(clean)


def test_no_unsupported_currency_aggregation(clean):
    clean['aggregations'][0].update(transaction_ids='TX001;TX002', amount='5200000')
    assert 'CURRENCY_AGGREGATION' in codes(clean)


def test_funding_not_equal_valuation(clean):
    assert clean['assets'][0]['purchase_price'] == '5500000'
    clean['assets'][0].update(purchase_price='4000000', value_basis='funding_amount')
    assert 'FUNDING_NOT_VALUATION' in codes(clean)


def test_derivative_sources_not_independent(clean):
    sources = {s['source_id']: s for s in clean['sources']}
    assert independent_roots('S004;S005', sources) == {'S004'}
    assert any(w['record_id'] == 'S005' for w in validate(clean)['warnings'])
    clean['claims'][7]['independent_source_count'] = '2'
    assert 'DERIVATIVE_INDEPENDENCE' in codes(clean)


def test_family_relation_not_ownership(clean):
    assert clean['claims'][1]['status'] == 'Rejected'
    clean['claims'][1]['status'] = 'Strongly supported'
    assert 'FAMILY_NOT_OWNERSHIP' in codes(clean)


def test_address_association_not_title(clean):
    assert clean['assets'][1]['ownership_status'] == 'Address association only'
    clean['claims'][7]['status'] = 'Confirmed'
    assert 'ADDRESS_NOT_TITLE' in codes(clean)
    clean['assets'][1]['ownership_status'] = 'Owned'
    assert 'ADDRESS_NOT_TITLE' in codes(clean)


def test_asset_funding_requires_earmark_or_explicit_inference_label(clean):
    inference = clean['claims'][3]
    assert inference['status'] == 'Probable / analytic judgment' and inference['limitations'] and inference['required_next_evidence']
    inference['status'] = 'Confirmed'
    assert 'FUNDING_EARMARK' in codes(clean)


def test_open_dependencies_remain_visible(clean):
    assert clean['claims'][6]['required_next_evidence'] and clean['claims'][8]['required_next_evidence']
    clean['claims'][6]['required_next_evidence'] = ''
    assert 'OPEN_DEPENDENCY' in codes(clean)


def test_full_clean_fixture_matches_demo(clean):
    assert clean == load_data(ROOT / 'data')


def test_full_broken_fixture_detects_all_frozen_failure_classes():
    result = codes(load_data(ROOT / 'tests/fixtures/broken'))
    assert {
        'ENTITY_REFERENCE', 'SOURCE_REFERENCE', 'SOURCE_REQUIRED', 'UNKNOWN_COERCION',
        'TEMPORAL_OWNERSHIP', 'CURRENCY_AGGREGATION', 'FUNDING_NOT_VALUATION',
        'DERIVATIVE_INDEPENDENCE', 'FAMILY_NOT_OWNERSHIP', 'ADDRESS_NOT_TITLE',
        'FUNDING_EARMARK', 'OPEN_DEPENDENCY',
    } <= result


def test_lineage_missing_parent_cycle_and_undeclared_duplicate(clean):
    bad = copy.deepcopy(clean)
    bad['sources'][4]['derived_from'] = 'S999'
    assert 'SOURCE_LINEAGE' in codes(bad)
    bad = copy.deepcopy(clean)
    bad['sources'][3]['derived_from'] = 'S005'
    assert 'SOURCE_LINEAGE' in codes(bad)
    bad = copy.deepcopy(clean)
    bad['sources'][4].update(derived_from='', record_key=bad['sources'][3]['record_key'])
    assert 'DUPLICATE_LINEAGE' in codes(bad)


def test_multi_parent_lineage(clean):
    sources = {s['source_id']: s for s in clean['sources']}
    sources['S005']['derived_from'] = 'S004;S003'
    assert roots('S005', sources) == {'S004', 'S003'}


def test_supported_fx_requires_valid_rates_and_matching_total(clean):
    source = dict(clean['sources'][6], source_id='S014', source_type='fx_record', record_key='demo-fx', title='SYNTHETIC: documented USD/EUR rate')
    clean['sources'].append(source)
    row = clean['aggregations'][0]
    row.update(transaction_ids='TX001;TX002', amount='5320000', currency='USD', fx_source_id='S014', fx_rates='{"USD":1,"EUR":1.1}')
    assert 'CURRENCY_AGGREGATION' not in codes(clean)
    row['fx_rates'] = '{"USD":1,"EUR":0}'
    assert 'CURRENCY_AGGREGATION' in codes(clean)
    row['fx_rates'] = '{"USD":2,"EUR":1.1}'
    assert 'CURRENCY_AGGREGATION' in codes(clean)


def test_relabeling_family_cannot_launder_ownership_evidence(clean):
    clean['claims'][1].update(status='Confirmed', support_basis='registry')
    assert 'OWNERSHIP_EVIDENCE' in codes(clean)


def test_unrelated_primary_record_cannot_establish_purchase_or_fx(clean):
    clean['assets'][0]['source_ids'] = 'S006'
    assert 'PURCHASE_EVIDENCE' in codes(clean)
    clean['aggregations'][0].update(transaction_ids='TX001;TX002', amount='5320000', fx_source_id='S007', fx_rates='{"USD":1,"EUR":1.1}')
    assert 'CURRENCY_AGGREGATION' in codes(clean)


def test_chronology_and_counterparty_falsification(clean):
    clean['transactions'][0]['date'] = '2025-03-01'
    assert 'FUNDING_CHRONOLOGY' in codes(clean)
    clean['transactions'][0].update(date='2025-02-03', payee_entity_id='C001')
    assert 'FUNDING_CHRONOLOGY' in codes(clean)


def test_structural_errors_are_explanatory(clean):
    clean['transactions'][0]['amount'] = 'NaN'
    assert 'TRANSACTION_AMOUNT' in codes(clean)
    clean['entities'].append(copy.deepcopy(clean['entities'][0]))
    assert 'DUPLICATE_ID' in codes(clean)
    clean['claims'][0]['confidence'] = '99%'
    assert 'INVALID_CONFIDENCE' in codes(clean)


def test_graph_retains_parallel_edges_without_open_attributions(clean):
    graph = build_graph(clean)
    assert graph.number_of_nodes() == 12
    assert graph.number_of_edges() == 14
    assert graph.number_of_edges('C002', 'C003') == 2
    assert not graph.has_edge('P001', 'C001')
    assert not graph.has_edge('P001', 'T001')
    assert not graph.has_edge('C004', 'A001')
    assert graph['C002']['A002']['ASSET_A002']['edge_kind'] == 'address'
    assert graph['C003']['C004']['R008']['temporal_status'] == 'Historical'


def test_graph_refuses_broken_inputs():
    with pytest.raises(ValueError, match='Refusing graph build'):
        build_graph(load_data(ROOT / 'tests/fixtures/broken'))


def test_synthetic_boundary_and_registration_collision(clean):
    clean['sources'][0]['reference'] = 'https://real-source.invalid/record'
    assert 'SYNTHETIC_BOUNDARY' in codes(clean)
    duplicate = dict(clean['entities'][3], entity_id='C099')
    clean['entities'].append(duplicate)
    assert 'REGISTRATION_COLLISION' in codes(clean)
