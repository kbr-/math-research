"""Small, bounded checks for the computation launcher and OOM protection."""

import os
from pathlib import Path
import subprocess
import sys


def group_path():
    group = Path('/proc/self/cgroup').read_text().strip().split('0::')[-1]
    assert '/mathcompute.slice/' in group, group
    return Path('/sys/fs/cgroup' + group)


if len(sys.argv) > 1 and sys.argv[1] == '--oom-probe':
    group = group_path()
    # Never attempt the probe unless its own much smaller cap is in force.
    assert 0 < int((group / 'memory.max').read_text()) <= 96 * 1024**2
    assert (group / 'memory.swap.max').read_text().strip() == '0'
    assert (group / 'memory.oom.group').read_text().strip() == '1'
    print('Verified 96 MiB test cap and group kill. Starting two 64 MiB workers.', flush=True)
    worker = 'import time; data = b"x" * (64 * 1024**2); time.sleep(15)'
    children = [subprocess.Popen([sys.executable, '-c', worker]) for _ in range(2)]
    for child in children:
        print(f'Test child PID: {child.pid}', flush=True)
    for child in children:
        child.wait()
    raise RuntimeError('Expected the OOM killer to terminate the entire test service')

group = group_path()
assert os.sched_getaffinity(0) == set(range(14)), os.sched_getaffinity(0)
assert os.environ['OPENBLAS_NUM_THREADS'] == '1'
assert os.environ['OMP_NUM_THREADS'] == '1'
parent = group.parent
assert int((parent / 'memory.max').read_text()) <= 10_000_000_000
assert int((parent / 'memory.swap.max').read_text()) <= 10_000_000_000
assert (group / 'memory.oom.group').read_text().strip() == '1'
import numpy as np
import scipy
from scipy.linalg.blas import dgemm

matrix = np.array([[1., 2.], [3., 4.]])
assert np.array_equal(dgemm(1., matrix, matrix), np.array([[7., 10.], [15., 22.]]))
print('PASS: CPU affinity 0-13, shared cgroup backstops, job OOM flag, thread environment.')
print(f'PASS: compiled BLAS calculation (NumPy {np.__version__}, SciPy {scipy.__version__}).')
print(f'Job cgroup: {group}')
