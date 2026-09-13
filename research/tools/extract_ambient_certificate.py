#!/usr/bin/env python3
"""Extract a small ambient certificate from existing exact C++ output."""
# Copyright (c) 2026 Kamil Braun. MIT License; see ../../LICENSE.
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--relative', required=True, type=Path)
    parser.add_argument('--squares', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('Output already exists')
    board = family = base = block = None
    base_affine_pivots, block_pivots, block_affine_pivots = [], [], []
    with args.relative.open() as stream:
        for line in stream:
            row = json.loads(line)
            kind = row['type']
            if kind == 'board' and row['name'] == 'functional':
                board = row
            elif kind == 'family' and row['name'] == 'random':
                family = row
            elif kind == 'base_summary' and row['board'] == 'functional':
                base = row
            elif kind == 'base_step' and row['board'] == 'functional':
                if 0 <= row['pivot'] <= board['variables']:
                    base_affine_pivots.append(row['pivot'])
            elif kind == 'input_step' and row['family'] == 'random' and row['group'] == 0:
                if row['pivot'] >= 0:
                    block_pivots.append(row['pivot'])
                    if row['pivot'] <= board['variables']:
                        block_affine_pivots.append(row['pivot'])
            elif kind == 'block_summary' and row['family'] == 'random' and row['group'] == 0:
                block = row
    if any(value is None for value in (board, family, base, block)):
        raise ValueError('Missing required source records')
    square = square_inputs = None
    with args.squares.open() as stream:
        for line in stream:
            row = json.loads(line)
            if row['type'] == 'family' and row['name'] == 'random':
                square_inputs = row['inputs'][0]
            elif row['type'] == 'square_space_summary' and row['family'] == 'random' and row['group'] == 0:
                square = row
    if square is None or square_inputs != family['inputs'][0]:
        raise ValueError('Ambient inputs do not agree across the two source records')
    n, v, r = board['N'], board['variables'], family['arity']
    m, free = n + 1, v - (n + 1)
    if family['joint_rank_with_rows'] != m + family['groups'] * r:
        raise ValueError('Source does not certify joint input independence modulo rows')
    if len(block_pivots) != block['additional_rank'] or len(set(block_pivots)) != len(block_pivots):
        raise ValueError('Additional-space pivot count does not match its recorded rank')
    ideal_dimension = r * (free + 1) - r * (r + 1) // 2
    module_dimension = ideal_dimension + (free + 1) - r
    measured_module = block['additional_rank'] + (v + 1 - len(base_affine_pivots)) - len(block_affine_pivots)
    faithful = (len(base_affine_pivots) == m and block['additional_rank'] == ideal_dimension
                and len(block_affine_pivots) == r and measured_module == module_dimension)
    if not faithful or block['contains_unit_class'] or square['contains_unit']:
        raise ValueError('The required ambient module hypotheses are not certified')
    if square['rank'] != r * (r + 1) // 2:
        raise ValueError('The ambient input-product space is not faithful')
    result = {
        'source_relative': args.relative.as_posix(), 'source_squares': args.squares.as_posix(),
        'N': n, 'variables': v, 'row_rank': m, 'row_quotient_variables': free,
        'ambient_rank': r, 'ambient_inputs': family['inputs'][0],
        'affine_encoding': 'index 0 is one; index 1+i*N+j is x_(i,j)',
        'old_NS_rank_in_matching_form': base['rank'], 'old_quadratic_quotient_dimension': base['quotient_dimension'],
        'old_affine_pivots': base_affine_pivots,
        'relative_ideal_rank': block['additional_rank'], 'relative_affine_pivots': block_affine_pivots,
        'relative_affine_dimension': len(block_affine_pivots),
        'Boolean_row_ideal_dimension': ideal_dimension,
        'Boolean_row_linear_plus_ideal_dimension': module_dimension,
        'measured_linear_plus_ideal_dimension': measured_module,
        'square_space_dimension': square['rank'], 'unital_quadratic_algebra_dimension': 1 + square['rank'],
        'relative_ideal_contains_unit': False, 'linear_plus_ideal_map_injective': faithful,
        'scope': 'Metadata and scalar dimension accounting from complete prior C++ certificates; no new Gaussian elimination.'
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(f'Ambient rank {r}; relative ideal {ideal_dimension}; affine part {len(block_affine_pivots)}; '
          f'injective linear-plus-ideal dimension {module_dimension}; quadratic algebra {1+square["rank"]}.')


if __name__ == '__main__':
    main()
