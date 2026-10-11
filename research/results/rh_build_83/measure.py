"""Measurements for the entry on the session-reads listing, on one Claude Code transcript.

Usage: measure.py TRANSCRIPT.jsonl.  Prints: what the draft tool's wiring would have printed at the first run
of the draft tool in the turn rh-bridge-78 (the transcript cut there); what the finisher prints for four turns
(each cut at its own first finisher command);
how many shell commands that print line ranges the range pattern reads; the time of one finisher listing."""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
import session_reads as reads      # noqa: E402


def main():
    started = time.time()
    lines = Path(sys.argv[1]).read_text(errors='replace').splitlines()
    loaded = time.time() - started
    found = list(reads.calls(lines))
    commands = [str(given.get('command', '')) for name, given in found if name == 'Bash']
    at = [i for i, (name, given) in enumerate(found)
          if name == 'Bash' and 'phase rh-bridge-78 network_tool' in str(given.get('command', ''))][0]
    cut = at + [i for i, (name, given) in enumerate(found[at:])
                if name == 'Bash' and 'draft_claim_sentences.py' in str(given.get('command', ''))][0]
    before = reads.short_lines(reads.after(found[:cut], reads.FINISHER, last=True))
    print(f'Before the brief of rh-bridge-78 (the calls since the last finisher command, cut at the draft '
          f"tool's first run): {len(before)} lines")
    for line in before:
        print(line[:150])
    for turn in ('rh-bridge-78', 'rh-build-79', 'rh-lead-81', 'rh-lead-82'):
        started = time.time()
        end = [i for i, (name, given) in enumerate(found) if name == 'Bash'
               and re.search(r'finish-turn\.py\s+' + re.escape(turn) + r'(?![\w-])', str(given.get('command', '')))][0]
        out = reads.short_lines(reads.after(found[:end], reads.FINISHER + re.escape(turn) + r'(?![\w-])'))
        print(f'At the finisher of {turn}: {len(out)} lines, {time.time() - started:.2f} s after loading')
        for line in out:
            print(line[:150])
    sed = [command for command in commands if 'sed -n' in command]
    print(f'{len(sed)} shell commands hold "sed -n"; the range pattern reads {sum(bool(reads.SED.search(c)) for c in sed)} '
          f'of them; {sum(bool(re.search(r"(?:head|tail)", c)) for c in commands)} commands use head or tail.')
    print(f'Loading the transcript ({Path(sys.argv[1]).stat().st_size / 1e6:.0f} MB, {len(found)} tool calls): '
          f'{loaded:.2f} s.')


if __name__ == '__main__':
    main()
