"""Group scuffers scrape output by color inferred from product URL.

Usage:
  python scripts/group_by_color.py 
  (reads scuffers_output.json in repo root and writes scuffers_grouped_by_color.json)

The script finds the product slug (last path segment) and searches for color tokens
and simple modifiers (e.g. "light blue", "dark", "grey", "burgundy"). If no color
is found the item is grouped under "unknown".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'scuffers_output.json'
OUTPUT = ROOT / 'scuffers_grouped_by_color.json'

# Known color words and modifiers (extend as needed)
COLORS = {
    'black', 'white', 'grey', 'gray', 'blue', 'navy', 'green', 'red', 'pink', 'beige',
    'burgundy', 'ecru', 'brown', 'camel', 'cream', 'tan', 'yellow', 'orange', 'purple', 'khaki',
    'ivory', 'stone', 'leopard'
}
MODIFIERS = {'light', 'dark'}

# Mapping for material/color tokens to normalized label
NORMALIZE = {
    'au': 'gold',
    'ag': 'silver',
    'gold': 'gold',
    'silver': 'silver',
    'rose-gold': 'rose gold',
    'rosegold': 'rose gold',
}


if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from index_tools.color_utils import infer_color_from_url


def group_items(items: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {}
    for it in items:
        url = it.get('url', '')
        color = infer_color_from_url(url)
        groups.setdefault(color, []).append(it)
    return groups


def main(infile: Path = INPUT, outfile: Path = OUTPUT) -> int:
    if not infile.exists():
        print(f"Input file {infile} not found.")
        return 2

    data = json.loads(infile.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        print('Expected a JSON array of items in input file.')
        return 3

    grouped = group_items(data)

    outfile.write_text(json.dumps(grouped, ensure_ascii=False, indent=2), encoding='utf-8')

    # print brief summary
    counts = {k: len(v) for k, v in grouped.items()}
    print('Grouped items written to', outfile)
    print('Counts by color:')
    for k, c in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f'  {k}: {c}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
