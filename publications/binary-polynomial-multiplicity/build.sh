#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Kamil Braun
set -euo pipefail
note_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "$note_dir" rev-parse --show-toplevel)"
compute_args=(--threads 1 --category local_processing --timeout 180)
if [[ $# -gt 0 ]]; then
    if [[ $# -ne 2 || $1 != --session ]]; then
        echo "Usage: $0 [--session TURN]" >&2
        exit 2
    fi
    compute_args+=(--session "$2")
fi
cd "$repo_root"
# Python handles pass-specific filenames without systemd shell-variable expansion.
exec ./compute.sh "${compute_args[@]}" python3 -c '
from pathlib import Path
import subprocess
import sys
note = Path(sys.argv[1])
for number in range(1, 4):
    log = note / ("pdflatex-pass-" + str(number) + ".log")
    with log.open("wb") as output:
        result = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
            "-file-line-error", "-no-shell-escape", "whitepaper.tex"], cwd=note,
            stdout=output, stderr=subprocess.STDOUT)
    if result.returncode:
        print(log.read_text(errors="replace"))
        raise SystemExit(result.returncode)
subprocess.run(["pdfinfo", str(note / "whitepaper.pdf")], check=True)
' "$note_dir"
