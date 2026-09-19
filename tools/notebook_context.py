#!/usr/bin/env python3
"""Measure and enforce configured pre-record notebook budgets; never truncate."""
import argparse
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('context_excerpt', ROOT/'tools/notebook-excerpt.py')
excerpt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(excerpt)


def budgets(source, config):
    required = {'version', 'hard_multiplier', 'characters_per_word', 'total_soft_words', 'regions'}
    if set(config) != required or config['version'] != 1:
        raise ValueError('Unknown context-budget configuration')
    regions = config['regions']
    if not isinstance(regions, dict) or '@intro' not in regions or 'research-record' in regions:
        raise ValueError('Budget @intro and living sections only; Research record is unlimited')
    for number in [config['characters_per_word'], config['total_soft_words'], *regions.values()]:
        if type(number) is not int or number <= 0:
            raise ValueError('Context budgets must be positive integers')
    multiplier = Fraction(str(config['hard_multiplier']))
    if multiplier < 1:
        raise ValueError('Hard multiplier must be at least one')
    book = excerpt.Notebook(source)
    record = book.anchor('research-record')
    if record['tag'] != 'section' or record['scope'] is not None:
        raise ValueError('Research record must be a top-level section')
    sections = [n for n in book.nodes if n['tag'] == 'section' and n['start'] < record['start']]
    ids = [n['anchor'] for n in sections]
    if None in ids or len(set(ids)) != len(ids):
        raise ValueError('Every pre-record section needs a unique ID')
    unknown = set(ids) - (set(regions)-{'@intro'})
    missing = (set(regions)-{'@intro'}) - set(ids)
    if unknown or missing:
        raise ValueError(f'Unbudgeted sections: {sorted(unknown)}; missing sections: {sorted(missing)}')
    if any(n['end'] > record['start'] for n in sections):
        raise ValueError('Living section crosses the Research-record boundary')
    # Attribute every span to its deepest section. Nested sections are budgeted
    # separately, and aggregate accounting includes their text exactly once.
    pieces = {key: [] for key in regions}
    cuts = sorted({0, record['start'], *(n['start'] for n in sections), *(n['end'] for n in sections)})
    for start, end in zip(cuts, cuts[1:]):
        owners = [n for n in sections if n['start'] <= start and end <= n['end']]
        owner = max(owners, key=lambda n: n['start'])['anchor'] if owners else '@intro'
        pieces[owner].append(source[start:end])
    rows = []
    def row(label, words, chars, soft):
        hard = int(soft * multiplier)
        soft_chars, hard_chars = soft*config['characters_per_word'], hard*config['characters_per_word']
        status = ('hard' if words > hard or chars > hard_chars else
                  'soft' if words > soft or chars > soft_chars else 'ok')
        return dict(id=label, words=words, characters=chars, soft_words=soft, hard_words=hard,
                    soft_characters=soft_chars, hard_characters=hard_chars, status=status,
                    excess_words=max(0,words-hard), excess_characters=max(0,chars-hard_chars))
    for label, parts in pieces.items():
        text = excerpt.visible_text(' '.join(parts))
        rows.append(row(label, len(text.split()), len(text), regions[label]))
    total = row('@total', sum(r['words'] for r in rows), sum(r['characters'] for r in rows), config['total_soft_words'])
    return {'passed': all(r['status'] != 'hard' for r in [*rows,total]), 'regions': rows, 'total': total,
            'metric': 'Whitespace-delimited visible words plus normalized visible-character guard, including literal TeX; not token counts.'}


def describe(report):
    return '\n'.join(f"{r['id']}: {r['words']} words (soft {r['soft_words']}, hard {r['hard_words']}); "
                     f"{r['characters']} chars (soft {r['soft_characters']}, hard {r['hard_characters']}); "
                     f"{r['status']}; excess {r['excess_words']} words/{r['excess_characters']} chars"
                     for r in [*report['regions'], report['total']])


def check(root=ROOT):
    report = budgets((root/'notebook.html').read_text(), json.loads((root/'research/context-budgets.json').read_text()))
    if not report['passed']:
        raise ValueError('Notebook context hard limit exceeded:\n'+describe(report))
    for row in [*report['regions'], report['total']]:
        if row['status'] == 'soft':
            print(f"Context warning: {row['id']} exceeds its soft target; consolidate before the hard limit.", file=sys.stderr)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notebook', type=Path, default=ROOT/'notebook.html')
    parser.add_argument('--config', type=Path, default=ROOT/'research/context-budgets.json')
    parser.add_argument('--out', type=Path, help='Save complete counts; exit status still enforces limits')
    args = parser.parse_args()
    try:
        report = budgets(args.notebook.read_text(), json.loads(args.config.read_text()))
        if args.out:
            with args.out.open('x') as stream:
                json.dump(report, stream, indent=2); stream.write('\n')
        print(describe(report))
        return 0 if report['passed'] else 1
    except (ValueError, OSError) as error:
        parser.exit(2, f'notebook-context: {error}\n')


if __name__ == '__main__':
    sys.exit(main())
