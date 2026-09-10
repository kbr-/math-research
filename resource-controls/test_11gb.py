"""Control a real 11 GB allocation test; the allocator runs through compute.sh.

The small controller stays outside the workload group to record its termination.
Do not run concurrently with other computation jobs: the expected kill is shared.
"""

import importlib.util
import importlib.machinery
import json
from pathlib import Path
import subprocess
import sys
import time

project = Path(__file__).resolve().parent.parent
loader = importlib.machinery.SourceFileLoader('compute', str(project / 'compute.sh'))
spec = importlib.util.spec_from_loader(loader.name, loader)
compute = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compute)
group, _ = compute.check_limits()
assert 'populated 0' in (group / 'cgroup.events').read_text(), 'Other computation jobs are running'
watch_group = Path('/sys/fs/cgroup' + subprocess.check_output(
    ['systemctl', '--user', 'show', compute.WATCHDOG, '--property=ControlGroup', '--value'],
    text=True).strip())
meminfo = {line.split(':')[0]: int(line.split()[1]) * 1024
           for line in Path('/proc/meminfo').read_text().splitlines() if line.split()[1].isdigit()}
assert meminfo['MemAvailable'] + meminfo['SwapFree'] > 12_000_000_000, 'Insufficient available RAM plus swap for this test'
before_events = dict(line.split() for line in (group / 'memory.events').read_text().splitlines())
start = time.time()
log = project / '.resource-runtime/11gb-allocation.log'
peak = ram_at_peak = swap_at_peak = 0
timed_out = False
with log.open('w') as output:
    child = subprocess.Popen([str(project / 'compute.sh'), '--threads', '1',
                              str(project / '.resource-runtime/stress'), 'memory'],
                             cwd=project, stdout=output, stderr=subprocess.STDOUT)
    while child.poll() is None:
        ram = sum(int((path / 'memory.current').read_text()) for path in (group, watch_group))
        swap = sum(int((path / 'memory.swap.current').read_text()) for path in (group, watch_group))
        if ram + swap > peak:
            peak, ram_at_peak, swap_at_peak = ram + swap, ram, swap
        if time.time() - start > 90:
            (group / 'cgroup.kill').write_text('1\n')
            timed_out = True
            child.wait(timeout=5)
            break
        time.sleep(0.02)
elapsed = time.time() - start
after_events = dict(line.split() for line in (group / 'memory.events').read_text().splitlines())
journal = subprocess.run(['journalctl', '--user', '--unit=' + compute.WATCHDOG,
                          '--since=@' + str(int(start)), '--no-pager', '--output=cat'],
                         check=True, capture_output=True, text=True).stdout
result = {
    'requested_bytes': 11_000_000_000,
    'exit_code': child.returncode,
    'elapsed_seconds': round(elapsed, 3),
    'sampled_peak_combined_bytes': peak,
    'ram_at_sampled_peak_bytes': ram_at_peak,
    'swap_at_sampled_peak_bytes': swap_at_peak,
    'kernel_oom_kills': int(after_events['oom_kill']) - int(before_events['oom_kill']),
    'timed_out': timed_out,
    'watchdog_log': journal.strip(),
}
(project / '.resource-runtime/11gb-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(log.read_text(), end='')
print(json.dumps(result, indent=2))
assert not timed_out, 'The test timed out; no pass claimed'
assert child.returncode != 0, 'The over-budget allocation must not complete successfully'
assert 'Combined memory budget exceeded:' in journal or result['kernel_oom_kills'] > 0
assert 'populated 0' in (group / 'cgroup.events').read_text()
print('PASS: the 11 GB allocation was killed and the workload group is empty.')
