#!/usr/bin/env python3
"""Checks of a commit message against what the commit carries.

Usage: tools/commit_message_checks.py MESSAGE_FILE          (staged changes; the commit-msg hook's call)
       tools/commit_message_checks.py --replay N             (the last N commits, each against its own diff)
       tools/commit_message_checks.py --replay N --scripts   (the research scripts' labelled lines only)

Figures: a framework commit (one that changes tools/ or compute.sh and no notebook) may state a figure (a
count of tests, a time in seconds, N of M, a percentage, megabytes) only if each number of it appears in a
file the commit adds or changes under research/results or research/provenance. On 16 October 2026 a framework
commit message carried four figures seen on the terminal and saved nowhere, and its reviewer found them.

Qualifiers: for each claim the commit registers (new in research/claims/index.json), each condition of its
summary (a clause opened by if, when, provided, unless, at most, at least or for every) whose words the
message's sentences naming that claim do not carry is listed; the commit goes through with the listing, since
whether a dropped condition matters is for the author to judge. On 16 October 2026 a message dropped
"Gamma > 0" and turned "at most" into "about".

Scripts: a staged script under research/results must carry the labelled lines compute.sh asks of a script it
runs there (unlabelled_scripts), since a script run from a scratch directory and copied in was never asked.
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
        texts = list(filter(None, map(read, named or sources)))
        figures = [m.group(0) for m in FIGURE.finditer(paragraph)]
        missing += [figure for figure in figures if not figure_sourced(figure, texts)]
    return missing


def searched_files(message, paths):
    """For each paragraph of the message with a figure, the source files unsourced() checks it against: the files
    the paragraph names, or all the commit's sources when it names none. A refusal says what it examined, not only
    what it found missing (17 October 2026: the cause of a refusal was guessed as a line break, while the check had
    searched only the two files the paragraph named)."""
    sources = [p for p in paths if p.startswith(SOURCES)]
    body = '\n'.join(line for line in message.splitlines() if not line.startswith('#'))
    out = []
    for paragraph in re.split(r'\n\s*\n', body):
        if FIGURE.search(paragraph):
            named = [p for p in sources if Path(p).name in paragraph]
            out.append(sorted(Path(p).name for p in (named or sources)))
    return out


def figure_sourced(figure, texts):
    """Whether every number of the figure appears, as a whole number, in one of the texts."""
    return all(any(re.search(r'(?<![\d.])' + re.escape(n) + r'(?![\d])', t) for t in texts)
               for n in NUMBER.findall(figure))


def tokens(text):
    return {w for w in re.findall(r'[A-Za-z_]+|\d+(?:\.\d+)?|[<>=]+', text.lower()) if w not in STOP and len(w) > 1
            or w in '<>='}


def clauses(text):
    """The text split after each full stop, and after each semicolon outside parentheses: a semicolon inside a
    parenthesis that follows a claim belongs to that claim's clause (17 October 2026: "conj:X (... n = 3 to 6; its
    only-if direction at K = 1 ...)" was refused). Splitting at full stops only lost 10 of 59 catches over 300
    commits, in long sentences whose parts (a), (b) stand between semicolons
    (research/results/framework-builds-20261017/condition-split-replay-after.txt)."""
    out, start, depth = [], 0, 0
    for i, ch in enumerate(text):
        depth += (ch == '(') - (ch == ')')
        nxt = text[i + 1:i + 2]
        if (ch == '.' or (ch == ';' and depth <= 0)) and (nxt == '' or nxt.isspace()):
            out.append(text[start:i + 1].strip())
            start = i + 1
    rest = text[start:].strip()
    return out + ([rest] if rest else [])


def dropped_conditions(message, new_claims, windows_only=False):
    """(claim, condition) for each condition of a newly registered claim's summary that the message's sentences
    naming the claim carry fewer than half of the words of. With windows_only, only a condition that is an
    inequality on one variable ("If D >= l+1") is checked, by whether the sentences compare that variable: an
    entry's General statement, counted over the record's 2132, met the word rule in 1387 (17 October 2026)."""
    found = []
    sentences = clauses(' '.join(message.split()))
    for ident, summary in new_claims:
        about = ' '.join(s for s in sentences if ident in s)
        if not about:
            continue
        # TeX in an entry's sentence (\lceil, \ge) read as the summary's plain words (17 October 2026).
        about = re.sub(r'\\[lr](ceil|floor)', r' \1 ', about)
        about = re.sub(r'\\geq?\b', '>=', re.sub(r'\\leq?\b', '<=', about))
        held = tokens(about)
        for m in CONDITION.finditer(summary):
            words = tokens(m.group(0))
            bound = re.match(r'at (?:most|least)', m.group(0), re.I)   # "at most" turned "about" (16 October)
            # An inequality on one variable ("If D >= l+1"), whose single letters tokens() drops: the sentence
            # needs a comparison on that variable (17 October 2026: a General statement dropped both D windows).
            compared = re.match(r'\s*(?:if|when|provided)\s+([A-Za-z]\w*)\s*(?:>=|<=|>|<)', m.group(0), re.I)
            # In an entry, only the closure-degree window D: over the record's General statements a rule on any
            # variable met 133 of 2132, most of them conditions such as "when H>0" (17 October 2026).
            if windows_only and not (compared and compared.group(1) == 'D'):
                continue
            if (not windows_only and (len(words) >= 2 and len(words & held) < len(words) / 2
                                      or bound and bound.group(0).lower() not in about.lower())
                    or compared and not re.search(rf'\b{re.escape(compared.group(1))}\s*(?:>=|<=|>|<|\\ge|\\le|'
                                                  rf'\\geq|\\leq|≥|≤)', about)):
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
        # AGENTS.md is read by tools/tests/test_agents_scope.py (17 October 2026: a rule with a goal word was
        # committed without the suite, which that test fails on).
        if (path in ('compute.sh', 'AGENTS.md') or path.startswith('tools/hooks/')
                or path.startswith('tools/git-hooks')):
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


# A suite figure in a message, "1341 tests in 9.4 s" or "Ran 1341 tests in 9.4s".  On 17 October 2026 a message
# claimed a passing run of 1341 tests in 9.4 s before the run, which then failed; the figure check passed because
# the provenance file it cited held an older run's figure.
SUITE_FIGURE = re.compile(r'(\d[\d,]*) tests in (\d+(?:\.\d+)?) ?s\b')
# A failure reported, not denied: "Nothing failed: the suite ran ..." skipped a false figure in the bypass try.
FAILED_NEAR = re.compile(r'(?<!nothing )(?<!none )(?<!not )(?<!no test )(?:\bfail(?:ed|s|ure)?\b|\btoo slow\b)', re.I)


def suite_figures_unmatched(message, top):
    """The suite figures of MESSAGE that report a passing run (no failure word in the 60 characters before them)
    and differ from the last passing run of the whole suite, as tools/tests/run.py stamped it."""
    try:
        stamp = json.loads((top / 'tools/tests/.suite-pass.json').read_text())
    except (OSError, ValueError):
        stamp = {}
    found = []
    for m in SUITE_FIGURE.finditer(' '.join(message.split())):
        flat = ' '.join(message.split())
        if FAILED_NEAR.search(flat[max(0, m.start() - 60):m.start()]):
            continue
        tests, seconds = int(m.group(1).replace(',', '')), float(m.group(2))
        # one module's run ("test_goal_progress: 60 tests in 1.0 s") is a small part of the suite, not a claim
        # about it: over the last 300 messages, five such figures would otherwise have been refused
        if stamp.get('tests') and tests < stamp['tests'] / 2:
            continue
        if stamp.get('tests') != tests or stamp.get('seconds') is None or abs(stamp['seconds'] - seconds) > 0.05:
            found.append(m.group(0))
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


def compute_module(top):
    """compute.sh loaded as a module, for its script checks (its main runs only under __main__)."""
    from importlib.machinery import SourceFileLoader
    return SourceFileLoader('compute_checks', str(top / 'compute.sh')).load_module()


def unlabelled_scripts(paths, top, compute=None):
    """'path: what it lacks' for each staged script under research/results that compute.sh would refuse to run
    for its labelled lines (a refuting outcome or "No statement tested:", a Baseline, a Record checked, a
    positive control).  compute.sh checks a script under research/results when it runs it there; on 17 October
    2026 two scripts were run from scratch directories, where it checks nothing, and copied in with their
    outputs, so the labels were never asked for.  The commit is where every copy passes."""
    scripts = [p for p in paths if p.startswith('research/results/') and (top / p).is_file()
               and Path(p).suffix in ('.py', '.gp', '.m2', '.sing', '.g')]
    if not scripts or not (compute or (top / 'compute.sh').is_file()):
        return []
    compute = compute or compute_module(top)
    command = ['run'] + [str(top / p) for p in scripts]
    rel = lambda arg: str(Path(arg).relative_to(top))   # noqa: E731
    found = [f'{rel(arg)}: ' + '; '.join(missing) for arg, missing in compute.scripts_without_refuting_outcome(command)]
    found += [f'{rel(arg)}: a line "Baseline:"' for arg in compute.scripts_without_baseline(command)]
    found += [f'{rel(arg)}: a line "Record checked:"' for arg in compute.scripts_without_record_check(command)]
    found += [f'{rel(arg)}: a line "Positive control:" or "No positive control:"'
              for arg in compute.scripts_without_positive_control(command)]
    return found


def unconfirmed(message, dropped):
    """The (claim, condition) pairs of `dropped` whose claim no line "Conditions checked: ..." of the message names.
    17 October 2026: a flagged message was committed unchanged and the drop explained only in a reply; the
    confirmation now lives in the message, with why each condition does not matter there."""
    confirmed = ' '.join(re.findall(r'^Conditions checked:(.*)$', message, re.M))
    return [(ident, condition) for ident, condition in dropped
            if not re.search(r'(?<![\w:-])' + re.escape(ident) + r'(?![\w-])', confirmed)]


CALLERS = ('tools/finish-turn.py', 'tools/notebook-append.py', 'compute.sh', 'tools/check-claims.py',
           'tools/commit_message_checks.py', 'tools/git-hooks-branch/commit-msg', 'tools/git-hooks-branch/pre-commit')   # and tools/hooks/*.py: the gates a refusing check is wired into
BYPASS = re.compile(r'^Bypass tried:(?:\s+\S+){5,}', re.M)
RECENT = 20   # commits back in which an added tools module still counts as new when it is wired in


def unbypassed_checks(added, caller_lines, message):
    """The new tools/ modules a commit wires into the finisher, the append tool or a hook (an added line of one of
    them imports or calls the module) when the message has no line "Bypass tried: ..." of at least five words naming
    the cheapest way around the new check that was tried and what it did.  17 October 2026: a coverage check went
    into the finisher with two ways around it (a citation edge, a missing paragraph) that its reviewer, not the
    agent, found; AGENTS.md's rule to try the cheapest way around a refusing check before its commit let it through.
    `added`: paths the commit adds, and those added in the last RECENT commits, so that adding a module in one
    commit and wiring it in the next does not pass; `caller_lines`: the lines the commit adds to the callers.  Its
    limits, from its reviewer: five words of any kind pass the line's form, and a new check written as a function of
    an existing module is not seen (this check's own commit was of that kind and could not fire on itself), nor is
    a path built at run time (f'{TOOLS}/m.py', 'm' + '.py')."""
    modules = [Path(p).stem for p in added
               if p.startswith('tools/') and p.endswith('.py') and '/tests/' not in p and not p.startswith('tools/hooks/')]
    # Wiring, not mention: "import m", "from m import f", "m.f(" and a load by the path (spec_from_file_location,
    # SourceFileLoader), the ways around a narrower pattern tried before this check's commit; a module's own file
    # is not its caller, and a name in a message string is not a wiring (its replay of 17 October 2026 counted
    # both). `caller_lines` items are lines or (path, line) pairs.
    def wires(m, line):
        name = re.escape(m)
        return re.search(r'\bimport\s+' + name + r'\b|\bfrom\s+' + name + r'\s+import\b|\b' + name + r'\.(?!py\b)\w+\s*\('
                         r'|(?:spec_from_file_location|SourceFileLoader)\([^)]*\b' + name + r'\.py'
                         # a run by path: a string literal that is the path alone ('m.py', "tools/m.py"), where a
                         # message holds the path among other words (its reviewer: 5f3b7ed74 ran a check so)
                         r'''|['"](?:[\w.-]*/)*''' + name + r'''\.py['"]'''
                         # by bare name: import_module('m'), __import__('m'), run_module('m'), [..., '-m', 'm']
                         r'''|(?:import_module|__import__|run_module)\(\s*['"]''' + name + r'''['"]'''
                         r'''|['"]-m['"]\s*,\s*['"]''' + name + r'''['"]''', line)
    pairs = [item if isinstance(item, tuple) else ('', item) for item in caller_lines]
    wired = sorted({m for m in modules for path, line in pairs if Path(path).stem != m and wires(m, line)})
    return [] if not wired or BYPASS.search(message) else wired


REFUSAL_DEF = re.compile(r'^\s*def\s+(\w*(?:error|refus|without|unbypassed|unsourced|unlabelled|offenders'
                         r'|_with_)\w*)\s*\(')


def new_refusal_functions(caller_lines, removed_lines, message):
    """Refusal functions a commit defines inside a gate (compute.sh, the finisher, the append tool, a hook: the
    CALLERS and tools/hooks/*.py), by a name of the kinds the gates use (..._error, ...refus..., scripts_without_...,
    scripts_with_..., ..._offenders), when the message has no "Bypass tried:" line.  unbypassed_checks sees only a
    new module wired in; on 17 October 2026 a process-pool refusal written as two functions of compute.sh went to
    review untried against its ways around, and its reviewer found two (python -m and a self-declared worker count),
    then a third in the fix (Pool(processes=8)).  A function whose name the commit also removes (an edit, a move)
    is not new.  Not seen: a refusal written inline, or a function named otherwise."""
    removed = {m.group(1) for line in removed_lines for m in [REFUSAL_DEF.match(line)] if m}
    found = sorted({m.group(1) for line in caller_lines for m in [REFUSAL_DEF.match(line)] if m} - removed)
    return [] if not found or BYPASS.search(message) else found


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
    for figure in suite_figures_unmatched(message, top):
        print(f'commit-msg: the message reports a passing suite run, "{figure}", that is not the last passing run of '
              'the whole suite (tools/tests/.suite-pass.json): write the figure from the run\'s own output after it '
              'exists, or say in the 60 characters before it that the run failed.', file=sys.stderr)
        status = 1
    staged_changed = git('diff', '--cached', '--name-only', '--diff-filter=AM').split()
    callers = [p for p in paths if p in CALLERS or (p.startswith('tools/hooks/') and p.endswith('.py'))]
    caller_lines = [(p, line[1:]) for p in callers for line in git('diff', '--cached', '-U0', '--', p).splitlines()
                    if line.startswith('+') and not line.startswith('+++')]
    recent = git('log', f'-{RECENT}', '--diff-filter=A', '--name-only', '--format=', '--', 'tools', check=False).split()
    for module in unbypassed_checks(git('diff', '--cached', '--name-only', '--diff-filter=A').split() + recent,
                                    caller_lines, message):
        print(f'commit-msg: the commit wires the new check {module} into a finisher, append tool or hook; add a '
              'line "Bypass tried: ..." naming the cheapest way around it that was tried before the commit and what '
              'it did (AGENTS.md: a check that refuses an action is tried against the cheapest way around it).',
              file=sys.stderr)
        status = 1
    removed_lines = [line[1:] for p in callers for line in git('diff', '--cached', '-U0', '--', p).splitlines()
                     if line.startswith('-') and not line.startswith('---')]
    found = new_refusal_functions([line for _, line in caller_lines], removed_lines, message)
    if found:
        print('commit-msg: the commit defines the refusal ' + ', '.join(found) + ' in a gate; add a line "Bypass '
              'tried: ..." naming the cheapest ways around it that were tried before the commit and what each did '
              '(AGENTS.md: a check that refuses an action is tried against the cheapest way around it).',
              file=sys.stderr)
        status = 1
    for line in unlabelled_scripts(staged_changed, top):
        print(f'commit-msg: {line}, which compute.sh asks of a script it runs under research/results; a script '
              'run elsewhere and copied in gets the same lines before its commit (COMPUTATION_RULES.md).',
              file=sys.stderr)
        status = 1
    if is_framework(paths):
        missing = unsourced(message, paths, read)
        if missing:
            print('commit-msg: figures in a framework commit message found in no file it adds or changes under '
                  'research/results or research/provenance: ' + '; '.join(missing) + '. Save the output they '
                  'came from with the commit, or drop them (AGENTS.md: each figure beside its saved output). '
                  'Searched, by paragraph (a paragraph naming files is checked against those only): '
                  + ' | '.join(', '.join(names) or 'none' for names in searched_files(message, paths)) + '.',
                  file=sys.stderr)
            status = 1
    if 'research/claims/index.json' in paths:
        old = git('show', 'HEAD:research/claims/index.json', check=False)
        dropped = dropped_conditions(message, new_claims(old, read('research/claims/index.json')))
        for ident, condition in unconfirmed(message, dropped):
            print(f'commit-msg: the message\'s sentence on {ident} does not carry its condition "{condition}"; '
                  'state it, or add a line "Conditions checked: ' + ident + ' (why it does not matter there)".',
                  file=sys.stderr)
            status = 1
    return status


def replay_scripts(rev, root, compute):
    """For one commit: the research scripts it adds or changes, each written out as it was at `rev` under a
    research/results path of its own below `root`, and how many lack their labelled lines; prints each line."""
    changed = git('diff-tree', '--no-commit-id', '--name-only', '--diff-filter=AM', '-r', rev).split()
    seen = bad = 0
    for path in [p for p in changed if p.startswith('research/results/')
                 and Path(p).suffix in compute.REFUTATION_SUFFIXES]:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(git('show', f'{rev}:{path}', check=False))
        seen += 1
        lines = unlabelled_scripts([path], root, compute)
        bad += bool(lines)
        print('\n'.join(f'{rev[:9]}\tscript\t{line[:160]}' for line in lines), end='\n' if lines else '')
    return seen, bad


def replay(count, scripts_only=False):
    """Each of the last `count` commits checked against its own diff: the figures each framework commit's message
    states without a source, the conditions each claim-registering commit's message drops, and the research
    scripts each adds or changes without their labelled lines; `scripts_only` skips the first two, whose reads
    of the registry at each registering commit take most of the time (400 commits ran past 120 s)."""
    import tempfile
    refused = framework = listed = registering = scripts = unlabelled = condition_refused = 0
    compute = compute_module(ROOT) if (ROOT / 'compute.sh').is_file() else None
    scratch = tempfile.TemporaryDirectory(prefix='commit-replay-')
    for rev in git('log', f'-{count}', '--format=%H').split():
        if compute:
            seen, bad = replay_scripts(rev, Path(scratch.name) / rev, compute)
            scripts += seen
            unlabelled += bad
        if scripts_only:
            continue
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
            pairs = unconfirmed(message, dropped_conditions(message, new_claims(old, read('research/claims/index.json'))))
            condition_refused += bool(pairs)
            for ident, condition in pairs:
                listed += 1
                print(f'{rev[:9]}\tcondition\t{ident}\t{condition}')
    print(f'{count} commits read: {refused} of {framework} framework commits would be refused for figures; '
          f'{listed} unconfirmed conditions over {registering} commits that change the registry, {condition_refused} '
          f'of which would now be refused; {unlabelled} of '
          f'{scripts} research/results scripts added or changed would be refused for labelled lines (each written '
          'out now, so the record check\'s modification date applies to all).')
    scratch.cleanup()


def diff_lines(rev, paths):
    """(path, line) for each line of commit `rev`'s zero-context diff of each of `paths` (a helper, so that the
    replays below nest two loops, not three, which compute.sh refuses)."""
    out = []
    for p in paths:
        out += [(p, line) for line in git('show', '-U0', '--format=', rev, '--', p).splitlines()]
    return out


def replay_bypass(count):
    """The last `count` commits that would be refused by unbypassed_checks, against each commit's own diff."""
    revs = git('log', f'-{count}', '--format=%H').split()
    refused = 0
    for rev in revs:
        added = git('diff-tree', '--no-commit-id', '-r', '--name-only', '--diff-filter=A', rev).split()
        added += git('log', f'-{RECENT}', '--diff-filter=A', '--name-only', '--format=', f'{rev}^', '--', 'tools',
                     check=False).split()
        if not any(p.startswith('tools/') and p.endswith('.py') for p in added):
            continue
        changed = git('diff-tree', '--no-commit-id', '-r', '--name-only', rev).split()
        callers = [p for p in changed if p in CALLERS or (p.startswith('tools/hooks/') and p.endswith('.py'))]
        lines = [(p, line[1:]) for p, line in diff_lines(rev, callers)
                 if line.startswith('+') and not line.startswith('+++')]
        wired = unbypassed_checks(added, lines, git('log', '-1', '--format=%B', rev))
        if wired:
            refused += 1
            print(f'{rev[:9]}\t{git("log", "-1", "--format=%s", rev).strip()[:80]}\t' + ', '.join(wired))
    print(f'{len(revs)} commits read: {refused} would be refused for a new check wired in without "Bypass tried:".')


def replay_refusal_defs(count):
    """The last `count` commits that new_refusal_functions would refuse, against each commit's own diff."""
    revs = git('log', f'-{count}', '--format=%H').split()
    refused = 0
    for rev in revs:
        changed = git('diff-tree', '--no-commit-id', '-r', '--name-only', rev).split()
        callers = [p for p in changed if p in CALLERS or (p.startswith('tools/hooks/') and p.endswith('.py'))]
        if not callers:
            continue
        diff = [line for _, line in diff_lines(rev, callers)]
        added = [line[1:] for line in diff if line.startswith('+') and not line.startswith('+++')]
        removed = [line[1:] for line in diff if line.startswith('-') and not line.startswith('---')]
        found = new_refusal_functions(added, removed, git('log', '-1', '--format=%B', rev))
        if found:
            refused += 1
            print(f'{rev[:9]}\t{git("log", "-1", "--format=%s", rev).strip()[:80]}\t' + ', '.join(found))
    print(f'{len(revs)} commits read: {refused} would be refused for a new refusal function without "Bypass tried:".')


if __name__ == '__main__':
    if sys.argv[1:2] == ['--replay']:
        if '--bypass' in sys.argv[3:]:
            replay_bypass(int(sys.argv[2]))
        elif '--refusal-defs' in sys.argv[3:]:
            replay_refusal_defs(int(sys.argv[2]))
        else:
            replay(int(sys.argv[2]), scripts_only='--scripts' in sys.argv[3:])
        sys.exit(0)
    sys.exit(check_staged(sys.argv[1]))
