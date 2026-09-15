#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Kamil Braun
set -euo pipefail

draft_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "$draft_dir" rev-parse --show-toplevel)"
compute_args=(--threads 1 --category local_processing --timeout 180)

if [[ $# -gt 0 ]]; then
    if [[ $# -ne 2 || $1 != --session ]]; then
        echo "Usage: $0 [--session TURN]" >&2
        exit 2
    fi
    compute_args+=(--session "$2")
fi

cd "$repo_root"
exec ./compute.sh "${compute_args[@]}" bash -c '
    set -euo pipefail
    cd "$1"
    for pass in 1 2 3; do
        if ! pdflatex -interaction=nonstopmode -halt-on-error \
            -file-line-error -no-shell-escape whitepaper.tex \
            >"pdflatex-pass-${pass}.log" 2>&1; then
            cat "pdflatex-pass-${pass}.log"
            exit 1
        fi
    done
    pdfinfo whitepaper.pdf
' whitepaper-build "$draft_dir"
