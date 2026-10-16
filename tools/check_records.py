#!/usr/bin/env python3
"""Lint the workspace's prose records before a commit.

Checks, in the notebook, the research notes and report, the skills, the rule files and the files the
branch's own module adds (tools/branch_extension.py); evidence under research/results/ is exempt,
since it quotes sources:

- commit-hash-like strings (7-40 hex characters with a digit and a letter), other than known
  session ids: a hash goes stale with the next rebase, so records name a commit by its subject;
- Markdown backticks inside the notebook's HTML, where they render literally;
- entry-meta status lines longer than a status plus one clause and the cycle label;
- literals from the git-ignored `.record-denylist` at the repository root, one regex per line
  (`#` starts a comment): the names of specific environments, clusters and instances, which
  committed prose must not carry;
- a statement that a number of tests pass on a line that gives no duration: a count alone hides a
  suite that got slow, so the run's time goes with it;
- notebook entries whose anchor carries a date later than today: an entry is dated when it is
  written, and a date ahead of the clock was once assumed rather than read;
- HTML character references that lost their ampersand (budget#39;s, (quot;): a sed replacement
  whose text held &#39; put the matched text in place of each & in two committed entries;
- adjacent HTML headings with the same level and visible text, including across comments.

Usage: ./tools/check_records.py [--diff [REV]] [PATH ...]
  Default: every record file, every line. With --diff, only lines added since REV (default HEAD),
  staged or not, and untracked record files: the mode for a check before committing, since older
  records carry findings from before this check existed. Exit 1 on any finding.
"""
import datetime
import html
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import branch_extension
from char_refs import broken_entities
from notebook_math import strip_tags_tight

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = Path.home() / ".claude" / "projects"
DEFAULT = ["notebook.html", "research/branches/*/notebook.html", "CLAUDE.md", "AGENTS.md", "PROMPTS.md",
           "COMPUTATION_RULES.md", "research/*.md", "research/notes/*.md", "skills/**/*.md",
           *branch_extension.ask("RECORD_PATHS", ())]
# The curve name ed25519 is all hex digits; it names a key type, never a commit.
HASH = re.compile(r"(?<![\w/#.-])(?!ed25519(?![\w-]))(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![\w-])")
META = re.compile(r'<p class="entry-meta">(.*?)</p>', re.S)
BACKTICK = re.compile(r"`[^`\n<>]{1,80}`")
MAX_META = 300    # as AGENTS.md has it
# The finisher appends this credit to the status line; it is not counted, so a line passes or
# fails the same way before and after finishing.
PRODUCER = re.compile(r'<span data-generated="finish-turn-producer-v1">.*?</span>', re.S)
ENTRY_DATE = re.compile(r'id="entry-(\d{4}-\d{2}-\d{2})-')
# A statement that tests pass, with their number; and a duration, which such a statement carries.
PASSED = re.compile(r"\b\d[\d,]*\s+(?:\w+\s+)?tests?\s+pass(?:es|ed|ing)?\b|\bpass(?:es|ed)?\s+\d[\d,]*\s+tests?\b"
                    r"|\b\d[\d,]*\s+passed\b(?=\s*(?:$|[`'\".,;:)<]|(?:in|at|on|and)\b))")
DURATION = re.compile(r"\b\d+(?:\.\d+)?\s?(?:s|ms|seconds?|min|minutes?)\b")
HEADING_TOKENS = re.compile(
    r'<(?:(?P<pre>pre\b[^>]*>.*?</pre>)|'
    r'h(?P<level>[1-6])\b[^>]*>(?P<body>.*?)</h(?P=level)>)', re.S | re.I)
COMMENTS = re.compile(r'<!--.*?-->', re.S)


def duplicate_headings(text):
    """(first line, last line, second heading's line, title) for adjacent duplicate headings.

    Comments are invisible separators; paragraphs and section boundaries are not. Preformatted
    examples are consumed as a single token so quoted heading markup is not treated as a record.
    Both headings' lines matter to --diff: inserting the first can leave the second unchanged.
    """
    previous = None
    line_no, counted = 1, 0
    for match in HEADING_TOKENS.finditer(text):
        line_no += text.count('\n', counted, match.start())
        counted = match.start()
        if match.group('pre'):
            previous = None
            continue
        title = ' '.join(html.unescape(strip_tags_tight(match.group('body'))).split())
        if previous is not None:
            level, old_title, end, first_line = previous
            gap = COMMENTS.sub('', text[end:match.start()])
            if level == match.group('level') and old_title == title and not gap.strip():
                last_line = line_no + match.group().count('\n')
                yield first_line, last_line, line_no, title
        previous = match.group('level'), title, match.end(), line_no


FIGURE = re.compile(r"\b\d+(?:\.\d+)? (?:of|in) \d+\b|\b\d+ tests\b|\b\d+(?:\.\d+)?%")
SOURCED = re.compile(r"research/(?:results|provenance)/")


def unsourced_figures(source):
    """[(line number, figure)] for each count or ratio (N of M, N tests, a percentage) in a Python file's
    docstrings and comments whose docstring or comment names no saved output under research/results or
    research/provenance. A docstring figure is a claim of a measurement; on 16 October 2026 a docstring
    quoted a reviewer's unsaved count as if measured. Over the tool files at that commit it flags the figures
    listed in research/results/framework-fixes-20261016g/figure-count.txt, one of them a line range rather than
    a measurement; only added lines are checked. Limits found in review: one results path anywhere in a
    docstring clears all its figures; line numbers drift in a docstring holding a backslash escape or line
    continuation; the pattern misses "1/241", spelled-out numbers, durations and other counted nouns; help
    texts, other strings and commit messages are not read."""
    import ast
    import io
    import tokenize
    found = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return found
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant) \
                    and isinstance(first.value.value, str):
                text = first.value.value
                if SOURCED.search(text):
                    continue
                for offset, line in enumerate(text.split("\n")):
                    for m in FIGURE.finditer(line):
                        found.append((first.lineno + offset, m.group(0)))
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.COMMENT and not SOURCED.search(tok.string):
                found.extend((tok.start[0], m.group(0)) for m in FIGURE.finditer(tok.string))
    except (tokenize.TokenError, IndentationError):
        pass
    return found


def untimed_counts(line):
    """The statements in `line` that a number of tests pass, where the line gives no duration."""
    return [] if DURATION.search(line) else [m.group(0) for m in PASSED.finditer(line)]


def status_text(meta_html):
    """The status line's text without the finisher's producer credit."""
    return html.unescape(strip_tags_tight(PRODUCER.sub("", meta_html))).strip()


def future_entry_dates(line, today):
    """The entry-anchor dates in `line` later than `today` (ISO strings compare as dates)."""
    return [m.group(1) for m in ENTRY_DATE.finditer(line) if m.group(1) > today.isoformat()]


def session_ids():
    ids = {p.stem[:8] for p in PROJECTS.glob("*/*.jsonl")}
    index = ROOT / "research" / "results" / "corpus" / "INDEX.md"
    if index.exists():
        ids |= set(re.findall(r"\| ([0-9a-f]{8}) \|", index.read_text()))
    return ids


def denylist():
    path = ROOT / ".record-denylist"
    if not path.exists():
        return []
    return [re.compile(l.strip()) for l in path.read_text().splitlines() if l.strip() and not l.startswith("#")]


def lines_of(path):
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        yield n, line


def added_lines(rev):
    """{path: set of line numbers added since rev}, untracked files included whole."""
    out = subprocess.run(["git", "-C", str(ROOT), "diff", "-U0", "--no-color", rev, "--"],
                         capture_output=True, text=True, check=True).stdout
    added, path = {}, None
    for line in out.splitlines():
        if line.startswith("+++ "):
            path = ROOT / line[6:] if line.startswith("+++ b/") else None
        elif path and line.startswith("@@"):
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            start, count = int(m.group(1)), int(m.group(2) or 1)
            added.setdefault(path, set()).update(range(start, start + count))
    untracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--others", "--exclude-standard"],
                               capture_output=True, text=True, check=True).stdout.split()
    for rel in untracked:
        added[ROOT / rel] = None
    return added


def main():
    args = sys.argv[1:]
    only = None
    if args and args[0] == "--diff":
        args.pop(0)
        rev = args.pop(0) if args and not args[0].startswith(("-", "/")) and not Path(args[0]).exists() else "HEAD"
        only = added_lines(rev)
    records = sorted({p for g in DEFAULT for p in ROOT.glob(g)})
    paths = [Path(p) for p in args] or ([p for p in records if p in only] if only is not None else records)
    known, deny = session_ids(), denylist()
    findings = 0

    def report(path, n, kind, text):
        nonlocal findings
        findings += 1
        print(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}:{n}: {kind}: {text[:100]}")

    if only is not None and not args:
        for path in sorted(p for p in only if p.suffix == ".py" and p.is_relative_to(ROOT / "tools")
                           and "tests" not in p.relative_to(ROOT).parts and p.exists()):
            wanted = only[path]
            for n, figure in unsourced_figures(path.read_text(encoding="utf-8")):
                if wanted is None or n in wanted:
                    report(path, n, "figure in a docstring or comment without its saved output "
                                    "(name the research/results path, or drop it)", figure)
    for path in paths:
        path = path if path.is_absolute() else (ROOT / path)
        is_html = path.suffix == ".html"
        in_pre = False
        wanted = None if only is None else only.get(path, set())
        for n, line in lines_of(path):
            if wanted is not None and n not in wanted:
                if is_html:
                    in_pre = (in_pre or "<pre" in line) and "</pre>" not in line
                continue
            if is_html:
                in_pre = (in_pre or "<pre" in line) and "</pre>" not in line
            for kind, found in line_findings(line, is_html, in_pre, known, deny):
                report(path, n, kind, found)
        if is_html:
            for n, kind, found in html_findings(path.read_text(encoding="utf-8"), wanted):
                report(path, n, kind, found)
    print(f"{len(paths)} files, {findings} findings")
    sys.exit(1 if findings else 0)


def line_findings(line, is_html, in_pre, known, deny):
    """(kind, text) for each finding of the record check on one line."""
    found = []
    for m in HASH.finditer(line):
        if m.group(0)[:8] not in known and not re.search(r"https?://\S*" + m.group(0), line):
            found.append(("commit hash", m.group(0)))
    if is_html and not in_pre:
        text = re.sub(r"<code>.*?</code>", "", line)
        found += [("Markdown backticks in HTML", m.group(0)) for m in BACKTICK.finditer(text)]
    for rx in deny:
        found += [("denylisted literal", m.group(0)) for m in rx.finditer(line)]
    found += [("test count without the run's time (say how long the run took)", c) for c in untimed_counts(line)]
    if is_html:
        found += [("entry dated after today", d) for d in future_entry_dates(line, datetime.date.today())]
        found += [("character reference without its &", r) for r in broken_entities(line)]
    return found


def html_findings(text, wanted=None):
    """(line, kind, text) for the whole-file findings of an HTML record: duplicate headings, long status lines."""
    found = []
    for first, last, n, title in duplicate_headings(text):
        if wanted is None or any(line in wanted for line in range(first, last + 1)):
            found.append((n, "adjacent duplicate heading", title))
    # Line numbers are counted on from the status line before: counting each from the top took 12.6 s
    # of a 15 s run on a notebook of 18 MB with 1341 status lines.
    line_no, counted = 1, 0
    for m in META.finditer(text):
        meta = status_text(m.group(1))
        line_no, counted = line_no + text.count("\n", counted, m.start()), m.start()
        if wanted is not None and line_no not in wanted:
            continue
        if len(meta) > MAX_META:
            found.append((line_no, "long status line", meta))
    return found


def draft_findings(text):
    """(line, kind, text) for every finding of the record check on an entry draft, as the checkpoint's
    --diff run would report its lines (16 October 2026: a commit hash in a draft was found only there)."""
    known, deny, found, in_pre = session_ids(), denylist(), [], False
    for n, line in enumerate(text.splitlines(), 1):
        in_pre = (in_pre or "<pre" in line) and "</pre>" not in line
        found += [(n, kind, item) for kind, item in line_findings(line, True, in_pre, known, deny)]
    return found + html_findings(text)


if __name__ == "__main__":
    main()
