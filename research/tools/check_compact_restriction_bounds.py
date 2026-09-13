#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Kamil Braun
"""Small exact rational ledger for the compiled restriction/code witness."""
import argparse
from fractions import Fraction
import json
from math import comb
from pathlib import Path


def encode(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator),
            "decimal_approximation": float(value)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Refusing existing output")
    parameters = summary = None
    with args.evidence.open() as stream:
        for line in stream:
            record = json.loads(line)
            if record["type"] == "parameters":
                parameters = record
            elif record["type"] == "summary":
                summary = record
    assert parameters and summary and summary["passed"]
    n, ell = parameters["holes"], parameters["ell"]
    kept, m = parameters["kept_holes"], parameters["pigeons"]
    h, r, inventory = parameters["accuracy"], parameters["rank"], parameters["literal_blocks"]
    assert n == 2**ell and m == n + 1 and r == 2*h + 1
    q = n - kept
    assert 1 <= r <= q
    live_probability = Fraction(kept + 1, m)
    alpha = Fraction(n, q - r + 1)
    first = live_probability + alpha/2
    last = live_probability + alpha/n
    # M beta^r < 1 iff both of these rational comparisons hold.
    literal_first = inventory * first**r
    literal_last_power = inventory**ell * last**r
    assert literal_first < 1 and literal_last_power < 1
    zeros = m - summary["minimum_code_weight"]
    rank_failure = (2**r - 1) * Fraction(comb(zeros, kept + 1), comb(m, kept + 1))
    assert 0 <= rank_failure < 1
    scale = Fraction(inventory, 1)/(1-rank_failure)
    joint_first = scale * first**r
    joint_last_power = scale**ell * last**r
    assert joint_first < 1 and joint_last_power < 1
    beta = max(float(first), float(last)**(1/ell))
    result = {
        "field": 2, "evidence": args.evidence.as_posix(),
        "parameters": parameters, "live_probability": encode(live_probability),
        "alpha": encode(alpha), "endpoint_one": encode(first),
        "endpoint_ell": encode(last),
        "literal_first_exact_test": encode(literal_first),
        "literal_last_power_exact_test": encode(literal_last_power),
        "beta_decimal_approximation": beta,
        "literal_union_bound_decimal_approximation": inventory * beta**r,
        "dense_rank_failure_upper_bound": encode(rank_failure),
        "dense_survival_lower_bound": encode(1-rank_failure),
        "joint_first_exact_test": encode(joint_first),
        "joint_last_power_exact_test": encode(joint_last_power),
        "all_decisions_use_exact_rationals": True,
        "literal_removal_positive_probability": True,
        "simultaneous_literal_removal_and_dense_survival_positive_probability": True,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print("Exact literal and simultaneous-witness probability tests passed.")
    print(f"Literal union bound approx {inventory * beta**r:.9g}; "
          f"dense rank-failure bound approx {float(rank_failure):.9g}.")


if __name__ == "__main__":
    main()
