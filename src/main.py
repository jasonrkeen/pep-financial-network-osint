"""One offline command regenerates the demo outputs and employer brief."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from .build_employer_brief import build_brief
from .validate_data import load_data, validate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = (args.output or root / 'outputs').resolve()
    result = subprocess.run(
        [sys.executable, '-m', 'src.build_network', '--data', 'data', '--output', str(output)],
        cwd=root, check=False,
    )
    if result.returncode:
        return result.returncode
    broken = validate(load_data(root / 'tests/fixtures/broken'))
    if not broken['errors']:
        raise RuntimeError('Broken fixture unexpectedly passed validation')
    (output / 'validation_broken.json').write_text(
        json.dumps(broken, indent=2) + '\n', encoding='utf-8', newline='\n',
    )
    build_brief(root, output)
    print('Generated graph, evidence, source dependencies, gaps, validation and three-page brief.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
