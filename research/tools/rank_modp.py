"""Exact rank mod a small prime p of a sparse matrix, via the compiled OpenMP kernel rank_modp.cpp.

rank_mod_p(rows, ncols, p): rows is a list of dicts {col: value} (or lists of (col, value) pairs).
The kernel is compiled on first use into research/tmp/ (ignored) and rebuilt when the source changes.
Threads follow OMP_NUM_THREADS, which ./compute.sh --threads sets."""
import hashlib, os, struct, subprocess, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'rank_modp.cpp')
BUILD = os.path.join(HERE, '..', 'tmp', 'rank_modp_build')

def _binary():
    digest = hashlib.sha256(open(SRC, 'rb').read()).hexdigest()[:12]
    exe = os.path.join(BUILD, 'rank_modp_' + digest)
    if not os.path.exists(exe):
        os.makedirs(BUILD, exist_ok=True)
        subprocess.run(['g++', '-O3', '-march=native', '-fopenmp', '-o', exe, SRC], check=True)
    return exe

def rank_mod_p(rows, ncols, p):
    if not rows or ncols == 0:
        return 0
    os.makedirs(BUILD, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=BUILD, suffix='.bin', delete=False) as fh:
        path = fh.name
        fh.write(struct.pack('<3i', len(rows), ncols, p))
        for row in rows:
            items = list(row.items()) if isinstance(row, dict) else list(row)
            arr = np.array(items, dtype='<i4').reshape(-1) if items else np.zeros(0, dtype='<i4')
            fh.write(struct.pack('<i', len(items))); fh.write(arr.tobytes())
    try:
        out = subprocess.run([_binary(), path], check=True, capture_output=True, text=True)
    finally:
        os.remove(path)
    return int(out.stdout.strip())
