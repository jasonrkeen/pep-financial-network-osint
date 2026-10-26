"""Exercise publication-sensitive brief behavior, not typography snapshots."""
from __future__ import annotations

from pathlib import Path
import shutil

import pytest
from pypdf import PdfReader

from src.build_employer_brief import build_brief

ROOT = Path(__file__).resolve().parents[1]


def test_brief_is_repeatable_and_carries_license_scope_and_unknowns(tmp_path: Path) -> None:
    pdf, markdown = build_brief(ROOT, tmp_path)
    first = pdf.read_bytes()
    build_brief(ROOT, tmp_path)
    assert pdf.read_bytes() == first
    reader = PdfReader(pdf)
    assert len(reader.pages) == 3
    text = '\n'.join(page.extract_text() for page in reader.pages)
    for required in ['MIT License', 'private', 'final approval', 'CL007', 'CL009', 'TX004', '24 errors', 'synthetic']:
        assert required.lower() in text.lower()
    assert 'license decision' not in text.lower()
    assert 'formal operational intelligence experience' in text
    assert not reader.attachments
    catalog = reader.trailer['/Root']
    assert '/OpenAction' not in catalog and '/AA' not in catalog
    assert 'JavaScript' not in str(catalog.get('/Names', {}))
    assert 'C:\\Users' not in text and 'file://' not in text
    assert reader.metadata.author == 'Jason Keen'
    assert 'MIT License' in markdown.read_text()


@pytest.mark.parametrize('defect', ['invalid_data', 'missing_license', 'failed_run'])
def test_brief_refuses_unreviewable_inputs(tmp_path: Path, defect: str) -> None:
    shutil.copytree(ROOT / 'data', tmp_path / 'data')
    (tmp_path / 'outputs').mkdir()
    shutil.copy2(ROOT / 'outputs/test_results.txt', tmp_path / 'outputs/test_results.txt')
    shutil.copy2(ROOT / 'LICENSE', tmp_path / 'LICENSE')
    if defect == 'invalid_data':
        target = tmp_path / 'data/synthetic_claims.csv'
        target.write_text(target.read_text().replace('P002', 'P999'))
    elif defect == 'missing_license':
        (tmp_path / 'LICENSE').write_text('License pending\n')
    else:
        (tmp_path / 'outputs/test_results.txt').write_text('1 failed, 26 passed\n')
    with pytest.raises(ValueError):
        build_brief(tmp_path, tmp_path / 'generated')
