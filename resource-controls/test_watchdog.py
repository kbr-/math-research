"""Verify aggregate killing with two small jobs, without filling system RAM."""

import os
from pathlib import Path
import subprocess
import sys
import time
import uuid


def run(*args, check=True):
    return subprocess.run(args, check=check, text=True, capture_output=True)


def prop(unit, key):
    return run('systemctl', '--user', 'show', unit, f'--property={key}', '--value').stdout.strip()


def wait_for(predicate, seconds=6):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.05)
    raise RuntimeError('Timed out waiting for resource-control test')


tag = uuid.uuid4().hex[:10]
slice_name = f'mathcompute-budgettest{tag}.slice'
anchor = f'mathcompute-test-anchor-{tag}.service'
watch = f'mathcompute-test-watch-{tag}.service'
worker1 = f'mathcompute-test-worker1-{tag}.service'
worker2 = f'mathcompute-test-worker2-{tag}.service'
units = [worker1, worker2, anchor, watch, slice_name]
binary = Path(__file__).resolve().parent.parent / '.resource-runtime/memory-watchdog'


def start(unit, slice_unit, *command, extra=()):
    return run('systemd-run', '--user', '--quiet', f'--unit={unit}',
               f'--slice={slice_unit}', '--property=CPUAffinity=0-13',
               '--property=MemoryMax=128M', '--property=MemorySwapMax=128M',
               '--property=RuntimeMaxSec=20s', '--property=KillMode=control-group',
               '--property=TimeoutStopSec=1s', *extra, '--', *command)


try:
    own = Path('/proc/self/cgroup').read_text()
    assert '/mathcompute.slice/' in own, 'Run this test through compute.sh'
    start(anchor, slice_name, '/usr/bin/sleep', '20')
    group = Path('/sys/fs/cgroup' + prop(slice_name, 'ControlGroup'))
    start(watch, 'mathcompute.slice', str(binary), str(group), str(64 * 1024**2),
          extra=('--property=Type=notify', '--property=WatchdogSec=2s', '--property=TimeoutStartSec=5s'))
    assert prop(watch, 'ActiveState') == 'active'
    worker = 'import time; data=b"x"*(40*1024**2); time.sleep(15)'
    start(worker1, slice_name, sys.executable, '-c', worker)
    wait_for(lambda: int((group / 'memory.current').read_text()) >= 40 * 1024**2)
    first_pid = int(prop(worker1, 'MainPID'))
    assert first_pid > 0
    assert prop(worker1, 'ActiveState') == 'active', 'First worker should fit alone'
    print('PASS: first 40 MiB worker fits within the 64 MiB test budget.', flush=True)
    start(worker2, slice_name, sys.executable, '-c', worker)
    wait_for(lambda: 'populated 0' in (group / 'cgroup.events').read_text())
    events = dict(line.split() for line in (group / 'memory.events').read_text().splitlines())
    assert int(events['oom_kill']) == 0, 'Expected watchdog kill, not kernel OOM'
    assert prop(watch, 'ActiveState') == 'active'
    assert prop(worker1, 'ExecMainStatus') == '9'
    assert prop(worker2, 'ExecMainStatus') == '9'
    print('PASS: adding a second worker triggers SIGKILL for the whole test group.', flush=True)
    print('PASS: no kernel OOM event; the combined-budget watchdog performed the kill.', flush=True)
finally:
    for unit in units:
        run('systemctl', '--user', 'stop', unit, check=False)
        run('systemctl', '--user', 'reset-failed', unit, check=False)
