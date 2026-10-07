"""Build a typed multigraph without promoting rejected/open claims into edges."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx

from .confidence import is_open
from .provenance import independent_roots, roots
from .validate_data import load_data, validate


def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def build_graph(tables, as_of='2026-02-01'):
    result = validate(tables, as_of)
    if result['errors']:
        raise ValueError('Refusing graph build: invalid inputs')
    graph = nx.MultiDiGraph(demo='SYNTHETIC ONLY', as_of=as_of, warning='Association, succession and timing do not prove ownership, title or funding.')
    for row in tables['entities']:
        graph.add_node(row['entity_id'], **row, label='DEMO ' + row['name'], node_kind='entity')
    for row in tables['assets']:
        graph.add_node(row['asset_id'], **row, label='DEMO ' + row['description'], node_kind='asset')
    for row in tables['relationships']:
        label = row['relationship_type'].replace('_', ' ')
        if row['relationship_type'] == 'ownership':
            label = row['ownership_percent'] + '% shares (' + row['temporal_status'].lower() + ')'
        if row['relationship_type'] == 'merger':
            label = 'legal merger; A001 title unresolved'
        graph.add_edge(row['source_entity_id'], row['target_entity_id'], key=row['relationship_id'], **row, label=label, edge_kind=row['relationship_type'])
    for row in tables['transactions']:
        purpose = row['payment_purpose_recorded'] or 'purpose unknown'
        graph.add_edge(row['payer_entity_id'], row['payee_entity_id'], key=row['transaction_id'], **row,
                       label=f"{row['transaction_id']} {row['currency']} {Decimal_label(row['amount'])}; {row['date']} / {purpose}; transfer only", edge_kind='transaction')
    for row in tables['assets']:
        graph.add_edge(row['associated_entity_id'], row['asset_id'], key='ASSET_' + row['asset_id'],
                       label='historical purchase; current title unresolved' if row['association_basis'] == 'purchase_record' else 'shared address ONLY',
                       source_ids=row['source_ids'], limitations=row['limitations'], confidence=row['confidence'],
                       edge_kind='purchase' if row['association_basis'] == 'purchase_record' else 'address', ownership_status=row['ownership_status'])
    return graph


def Decimal_label(value):
    from decimal import Decimal
    return format(Decimal(value), ',f')


def draw_graph(graph, path):
    # Fixed positions and curved parallel edges keep every relationship visible.
    positions = {
        'P001': (0, 4), 'P002': (2, 4), 'C001': (4, 4), 'C002': (4, 2.6),
        'P003': (2, 2.6), 'C003': (7, 2.6), 'C004': (10, 2.6), 'T001': (10, 4),
        'B001': (12.5, 4), 'B002': (4, 0.6), 'A001': (7, 0.6), 'A002': (1, 0.6),
    }
    colors = {'person': '#cfe5f4', 'company': '#d8ead5', 'trust': '#edddf5', 'bank': '#e8e8e8'}
    styles = {'family': ('#888888', 'dashed'), 'address': ('#888888', 'dotted'), 'transaction': ('#2674aa', 'solid'),
              'ownership': ('#35744b', 'solid'), 'purchase': ('#a66c12', 'dashed'), 'merger': ('#8755a8', 'dashdot'),
              'director': ('#777777', 'dashed'), 'bank_context': ('#aaaaaa', 'dotted')}
    fig, ax = plt.subplots(figsize=(20, 10))
    for node, attrs in graph.nodes(data=True):
        nx.draw_networkx_nodes(graph, positions, nodelist=[node], node_color=colors.get(attrs.get('entity_type'), '#fff0c2'),
                               node_shape='s' if attrs['node_kind'] == 'asset' else 'o', node_size=2700, ax=ax)
    names = {'P001': 'DEMO Alex Mercer\nPEP; no company attribution', 'P002': 'DEMO Dana Mercer', 'P003': 'DEMO Elias Voss',
             'C001': 'DEMO Northbridge\nHoldings', 'C002': 'DEMO Harbor Crest\nTrading', 'C003': 'DEMO Meridian\nProperty SPV',
             'C004': 'DEMO Summit Residential\nManagement', 'T001': 'DEMO Alder Family Trust\nbeneficiaries unknown',
             'B001': 'DEMO Continental\nPrivate Bank', 'B002': 'DEMO Eastport\nCommercial Bank',
             'A001': 'DEMO 14 Meridian Square\ncurrent title unknown', 'A002': 'DEMO Ridgeview Residence\naddress association only'}
    nx.draw_networkx_labels(graph, positions, labels=names, font_size=9, ax=ax)
    grouped = {}
    label_positions = {'R003': (4.95, 3.5), 'TX002': (3.12, 3.5), 'TX001': (5.5, 3.12), 'TX003': (5.5, 2.02), 'TX004': (11.25, 4.5)}
    for u, v, key, attrs in graph.edges(keys=True, data=True):
        grouped.setdefault((u, v), []).append((key, attrs))
    for (u, v), edges in grouped.items():
        for index, (key, attrs) in enumerate(edges):
            color, style = styles[attrs['edge_kind']]
            if attrs.get('temporal_status') == 'Historical' and attrs['edge_kind'] == 'ownership':
                style = 'dashed'
            radius = (index - (len(edges) - 1) / 2) * 0.44
            nx.draw_networkx_edges(graph, positions, edgelist=[(u, v, key)], edge_color=color, style=style, width=1.7,
                                   arrowsize=17, node_size=2700, connectionstyle=f'arc3,rad={radius}', ax=ax)
            x1, y1 = positions[u]; x2, y2 = positions[v]
            mx = (x1+x2)/2 + radius*(y2-y1)/2
            my = (y1+y2)/2 - radius*(x2-x1)/2
            mx, my = label_positions.get(key, (mx, my))
            label = attrs['label'].replace('; ', ';\n')
            ax.text(mx, my, label, fontsize=8, color=color, ha='center', va='center',
                    bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .92, 'pad': 2})
    ax.set_title('SYNTHETIC DEMO — PEP financial network\nRecords as of 2026-02-01; edge types carry different evidentiary meanings', fontsize=18, loc='left', pad=28)
    ax.legend(handles=[Line2D([0], [0], color=c, linestyle=s, label=k.replace('_', ' ')) for k, (c,s) in styles.items()]
              + [Line2D([0], [0], color='#35744b', linestyle='dashed', label='historical ownership')],
              loc='lower center', bbox_to_anchor=(.5, -.12), ncol=4, frameon=False)
    fig.text(.05, .015, 'Family ≠ ownership • transfer ≠ property funding • historical purchase ≠ current title • merger ≠ asset-specific title\n'
             'Rejected and unresolved claims are preserved in the evidence matrix and gaps table; they are not attribution edges. All labels depict fictional scenario roles.', fontsize=11)
    ax.set_xlim(-1,14); ax.set_ylim(-.4,5); ax.axis('off')
    fig.subplots_adjust(bottom=.2, top=.85, left=.03, right=.98)
    fig.savefig(path, dpi=150, metadata={'Software': 'Synthetic OSINT portfolio'})
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=Path('data'))
    parser.add_argument('--output', type=Path, default=Path('outputs'))
    parser.add_argument('--as-of', default='2026-02-01')
    args = parser.parse_args()
    tables = load_data(args.data)
    result = validate(tables, args.as_of)
    if result['errors']:
        print(json.dumps(result, indent=2))
        return 1
    args.output.mkdir(parents=True, exist_ok=True)
    graph = build_graph(tables, args.as_of)
    nx.write_graphml(graph, args.output / 'demo_network.graphml')
    draw_graph(graph, args.output / 'demo_network.png')
    sources = {s['source_id']: s for s in tables['sources']}
    evidence = [dict(row, lineage_roots=';'.join(sorted(independent_roots(row['source_ids'], sources)))) for row in tables['claims']]
    write_csv(args.output / 'evidence_matrix.csv', list(evidence[0]), evidence)
    gaps = [{'record_id': r['claim_id'], 'status': r['status'], 'gap': r['limitations'], 'next_evidence': r['required_next_evidence']} for r in tables['claims'] if is_open(r)]
    # Other material gaps must not disappear simply because their propositions are rejected/analytic.
    gaps += [{'record_id': r['claim_id'], 'status': r['status'], 'gap': r['limitations'], 'next_evidence': r['required_next_evidence']} for r in tables['claims'] if not is_open(r) and r['required_next_evidence']]
    gaps += [{'record_id': 'TX004', 'status': 'Unresolved', 'gap': 'Documented transfer; economic source of funds unresolved', 'next_evidence': 'Originating account records and trust funding instrument'}]
    write_csv(args.output / 'unresolved_gaps.csv', ['record_id', 'status', 'gap', 'next_evidence'], gaps)
    lineage = [{'source_id': s['source_id'], 'derived_from': s['derived_from'], 'lineage_roots': ';'.join(sorted(roots(s['source_id'], sources))), 'independent': 'No' if s['derived_from'] else 'Documented root; independence still requires review'} for s in tables['sources']]
    write_csv(args.output / 'source_dependencies.csv', ['source_id', 'derived_from', 'lineage_roots', 'independent'], lineage)
    (args.output / 'validation_clean.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    manifest = {'as_of': args.as_of, 'inputs': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.data.glob('*.csv'))},
                'nodes': graph.number_of_nodes(), 'edges': graph.number_of_edges(), 'layout': 'fixed', 'synthetic_only': True}
    (args.output / 'run_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f"Clean demo: {result['error_count']} errors; {graph.number_of_nodes()} nodes, {graph.number_of_edges()} typed edges")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
