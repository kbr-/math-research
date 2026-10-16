#!/usr/bin/env python3
"""Checks of a commit message against what the commit carries.

Usage: tools/commit_message_checks.py MESSAGE_FILE          (staged changes; the commit-msg hook's call)
       tools/commit_message_checks.py --replay N             (the last N commits, each against its own diff)

Figures: a framework commit (one that changes tools/ or compute.sh and no notebook) may state a figure (a
count of tests, a time in seconds, N of M, a percentage, megabytes) only if each number of it appears in a
file the commit adds or changes under research/results or research/provenance. On 16 October 2026 a framework
commit message carried four figures seen on the terminal and saved nowhere, and its reviewer found them.

Qualifiers: for each claim the commit registers (new in research/claims/index.json), each condition of its
summary (a clause opened by if, when, provided, unless, at most, at least or for every) whose words the
message's sentences naming that claim do not carry is listed; the commit goes through with the listing, since
whether a dropped condition matters is for the author to judge. On 16 October 2026 a message dropped
"Gamma > 0" and turned "at most" into "about".
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURE = re.compile(r'\b\d+(?:\.\d+)?\s?(?:of|in)\s\d+(?:\.\d+)?\b|\b\d+(?:\.\d+)?\s?(?:tests?|s|ms|MB|GB|%)(?![\w/])'
                    r'|\b\d+(?:\.\d+)?\s(?:matches|entries|briefs|commands|calls|flags|findings|refusals|texts|'
                   r'paragraphs|conditions|commits|cases|sentences|listings|instances|failures|defects)\b')
NUMBER = re.compile(r'\d+(?:\.\d+)?')
SOURCES = ('research/results/', 'research/provenance/')
CONDITION = re.compile(r'\b(?:if|when|provided|unless|at most|at least|for every|for all)\b[^,;.]*', re.I)
STOP = set('if when provided unless at most least for every all the a an of and or with in on to is are be by '
           'its it this that as any each'.split())


def git(*args, check=True):
    done = subprocess.run(['git', *args], capture_output=True, text=True)    # the repository being committed to
    if check and done.returncode != 0:
        raise RuntimeError(done.stderr.strip())
    return done.stdout


def figures(message):
    """The figures of a message, outside git's comment lines."""
    body = '\n'.join(line for line in message.splitlines() if not line.startswith('#'))
    return [m.group(0) for m in FIGURE.finditer(body)]


def is_framework(paths):
    return any(p.startswith('tools/') or p == 'compute.sh' for p in paths) and \
        not any(p.endswith('notebook.html') for p in paths)


def unsourced(message, paths, read):
    """The message's figures some number of which appears in none of their source files; `read(path)` gives a
    file's text in the commit. A paragraph that names files of the commit (by their names) is checked against
    those files only: a figure anywhere in a long committed profile passed before (the builds' reviewer, 17
    October 2026)."""
    sources = [p for p in paths if p.startswith(SOURCES)]
    body = '\n'.join(line for line in message.splitlines() if not line.startswith('#'))
    missing = []
    for paragraph in re.split(r'\n\s*\n', body):
        named = [p for p in sources if Path(p).name in paragraph]
        texts = [t for t in (read(p) for p in (named or sources)) if t]
        for figure in (m.group(0) for m in FIGURE.finditer(paragraph)):
            if not all(any(re.search(r'(?<![\d.])' + re.escape(n) + r'(?![\d])', t) for t in texts)
                       for n in NUMBER.findall(figure)):
                missing.append(figure)
    return missing


def tokens(text):
    return {w for w in re.findall(r'[A-Za-z_]+|\d+(?:\.\d+)?|[<>=]+', text.lower()) if w not in STOP and len(w) > 1
            or w in '<>='}


def dropped_conditions(message, new_claims):
    """(claim, condition) for each condition of a newly registered claim's summary that the message's sentences
    naming the claim carry fewer than half of the words of."""
    found = []
    sentences = re.split(r'(?<=[.;])\s+', ' '.join(message.split()))
    for ident, summary in new_claims:
        about = ' '.join(s for s in sentences if ident in s)
        if not about:
            continue
        held = tokens(about)
        for m in CONDITION.finditer(summary):
            words = tokens(m.group(0))
            bound = re.match(r'at (?:most|least)', m.group(0), re.I)   # "at most" turned "about" (16 October)
            if (len(words) >= 2 and len(words & held) < len(words) / 2
                    or bound and bound.group(0).lower() not in about.lower()):
                found.append((ident, m.group(0).strip()[:100]))
    return found


def new_claims(old_index, new_index):
    old = {c['id'] for c in json.loads(old_index)['claims']} if old_index else set()
    return [(c['id'], c.get('summary', '')) for c in json.loads(new_index)['claims'] if c['id'] not in old]


def shared_code(paths, top):
    """The staged paths a change to which needs the whole suite (AGENTS.md: shared code, fixtures, hooks): hooks,
    compute.sh, the tests' own runner and fixtures, and a tools module another tool imports by name."""
    tools = (list((top / 'tools').glob('*.py')) + list((top / 'tools/hooks').glob('*.py'))
             + [p for p in (top / 'tools').glob('git-hooks*/*') if p.is_file()])
    found = []
    for path in paths:
        if path == 'compute.sh' or path.startswith('tools/hooks/') or path.startswith('tools/git-hooks'):
            found.append(path)
        elif path.startswith('tools/') and path.endswith('.py') and not path.startswith('tools/tests/test_'):
            stem = Path(path).stem
            # By name, or by path as a quoted string (spec_from_file_location of 'tools/finish-turn.py'): the
            # builds' reviewer found finish-turn.py, loaded by path, not counted as shared (17 October 2026).
            uses = re.compile(rf'^\s*(?:import [\w, ]*\b{re.escape(stem)}\b|from {re.escape(stem)} import)'
                              rf'|[\'"/]{re.escape(Path(path).name)}[\'"]', re.M)
            if path.startswith('tools/tests/') or any(
                    other.name != Path(path).name and uses.search(other.read_text(errors='replace'))
                    for other in tools):
                found.append(path)
    return found


def suite_after(paths, top):
    """None when the whole suite passed after the last edit of each staged shared path, else the refusal."""
    shared = [p for p in shared_code(paths, top) if (top / p).exists()]
    if not shared:
        return None
    stamp = top / 'tools/tests/.suite-pass.json'
    try:
        passed = json.loads(stamp.read_text())['unix_s']
    except (OSError, ValueError, KeyError):
        passed = 0.0
    later = [p for p in shared if (top / p).stat().st_mtime > passed]
    if not later:
        return None
    return ('commit-msg: the commit changes shared code (' + ', '.join(later[:5]) + (' ...' if len(later) > 5 else '')
            + ') edited after the last passing run of the whole suite: run ./compute.sh --threads 1 --timeout 60 '
            'python3 tools/tests/run.py, then commit (AGENTS.md: a change to shared code, fixtures or hooks needs '
            'the whole suite).')


def check_staged(message_path):
    message = Path(message_path).read_text(encoding='utf-8', errors='replace')
    paths = git('diff', '--cached', '--name-only').split()
    top = Path(git('rev-parse', '--show-toplevel').strip())
    read = lambda p: (top / p).read_text(errors='replace') if (top / p).is_file() else ''   # noqa: E731
    status = 0
    refusal = suite_after(paths, top)
    if refusal:
        print(refusal, file=sys.stderr)
        status = 1
    if is_framework(paths):
        missing = unsourced(message, paths, read)
        if missing:
            print('commit-msg: figures in a framework commit message found in no file it adds or changes under '
                  'research/results or research/provenance: ' + '; '.join(missing) + '. Save the output they '
                  'came from with the commit, or drop them (AGENTS.md: each figure beside its saved output).',
                  file=sys.stderr)
            status = 1
    if 'research/claims/index.json' in paths:
        old = git('show', 'HEAD:research/claims/index.json', check=False)
        dropped = dropped_conditions(message, new_claims(old, read('research/claims/index.json')))
        for ident, condition in dropped:
            print(f'commit-msg: the message\'s sentence on {ident} does not carry its condition "{condition}"; '
                  'state it, or confirm it does not matter there.', file=sys.stderr)
    return status


def replay(count):
    """Each of the last `count` commits checked against its own diff: the figures each framework commit's message
    states without a source, and the conditions each claim-registering commit's message drops."""
    refused = framework = listed = registering = 0
    for rev in git('log', f'-{count}', '--format=%H').split():
        message = git('log', '-1', '--format=%B', rev)
        paths = git('diff-tree', '--no-commit-id', '--name-only', '-r', rev).split()
        read = lambda p, rev=rev: git('show', f'{rev}:{p}', check=False)   # noqa: E731
        subject = message.splitlines()[0][:80] if message else ''
        if is_framework(paths):
            framework += 1
            missing = unsourced(message, paths, read)
            if missing:
                refused += 1
                print(f'{rev[:9]}\tfigures\t{subject}\t' + '; '.join(missing))
        if 'research/claims/index.json' in paths:
            registering += 1
            old = git('show', f'{rev}^:research/claims/index.json', check=False)
            for ident, condition in dropped_conditions(message, new_claims(old, read('research/claims/index.json'))):
                listed += 1
                print(f'{rev[:9]}\tcondition\t{ident}\t{condition}')
    print(f'{count} commits read: {refused} of {framework} framework commits would be refused for figures; '
          f'{listed} conditions listed over {registering} commits that change the registry.')


if __name__ == '__main__':
    if sys.argv[1:2] == ['--replay']:
        replay(int(sys.argv[2]))
        sys.exit(0)
    sys.exit(check_staged(sys.argv[1]))
