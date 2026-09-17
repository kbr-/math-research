#!/usr/bin/env python3
"""Export timing, archive evidence, and fill one notebook timing placeholder."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def session_name(value):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', value) or value in ('.', '..'):
        raise argparse.ArgumentTypeError('Use a simple session name, not a path')
    return value


def validate_marker(body, marker):
    if body.count(marker) != 1:
        raise ValueError(f'Notebook must contain exactly one {marker}')
    position = body.index(marker)
    record = body.find('<section id="research-record">')
    end = body.find('</section>', record) if record >= 0 else -1
    article = body.rfind('<article', record, position) if record >= 0 else -1
    close = body.find('</article>', article) if article >= 0 else -1
    if not (0 <= record < article < position < close < end):
        raise ValueError('Timing marker must be inside a Research-record article')


def finish(root, turn, next_turn=None):
    notebook = root / 'notebook.html'
    marker = f'<!-- TIMING {turn} -->'
    validate_marker(notebook.read_text(), marker)
    if next_turn and (root / 'research/logs' / f'{next_turn}.jsonl').exists():
        raise ValueError('Next session already exists; omit --next when retrying finalization')

    compute = str(root / 'compute.sh')
    fragment = root / 'research/results' / turn / 'timing.html'
    subprocess.run([compute, 'report', turn, '--stop', '--html-out', str(fragment)],
                   cwd=root, check=True, stdout=subprocess.PIPE, text=True)
    if next_turn:
        # Continuous research keeps the finished cycle's recorded agent and model.
        journal = root / 'research/logs' / f'{turn}.jsonl'
        first = json.loads(journal.read_text().splitlines()[0]) if journal.exists() else {}
        inherit = [f'--{key}={first[key]}' for key in ('agent', 'model') if first.get(key)]
        subprocess.run([compute, 'start', next_turn, *inherit], cwd=root, check=True,
                       stdout=subprocess.PIPE, text=True)
        subprocess.run([compute, 'phase', next_turn, 'preparation', '--note',
                        f'Finalize checkpoint {turn}, then begin the next research cycle'],
                       cwd=root, check=True)

    # Archival may copy large outputs, so keep it inside the shared resource limits.
    archive = [compute]
    if next_turn:
        archive += ['--session', next_turn]
    archive += ['--threads', '1', '--category', 'local_processing',
                '--tail-bytes', '1000', sys.executable,
                str(root / 'tools/archive-session.py'), turn]
    subprocess.run(archive, cwd=root, check=True)

    # Re-read after commands so unrelated edits made meanwhile are retained.
    current = notebook.read_text()
    try:
        validate_marker(current, marker)
    except ValueError as error:
        raise ValueError(f'Timing and archive are saved, but {error}') from error
    updated = current.replace(marker, fragment.read_text().strip())
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=root, prefix='.notebook-timing-',
                                         encoding='utf-8', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(updated)
        temporary.chmod(notebook.stat().st_mode & 0o777)
        os.replace(temporary, notebook)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f'Finished {turn}: timing embedded and evidence archived; review and commit.')
    if next_turn:
        print(f'{next_turn} is running in preparation phase.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('turn', type=session_name)
    parser.add_argument('--next', dest='next_turn', type=session_name,
                        help='Start the next cycle immediately after the timing snapshot')
    args = parser.parse_args()
    finish(ROOT, args.turn, args.next_turn)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'finish-turn.py: {error}', file=sys.stderr)
        sys.exit(1)
