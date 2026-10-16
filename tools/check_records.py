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
            for m in HASH.finditer(line):
                if m.group(0)[:8] not in known and not re.search(r"https?://\S*" + m.group(0), line):
                    report(path, n, "commit hash", m.group(0))
            if is_html and not in_pre:
                text = re.sub(r"<code>.*?</code>", "", line)
                for m in BACKTICK.finditer(text):
                    report(path, n, "Markdown backticks in HTML", m.group(0))
            for rx in deny:
                for m in rx.finditer(line):
                    report(path, n, "denylisted literal", m.group(0))
            for count in untimed_counts(line):
                report(path, n, "test count without the run's time (say how long the run took)", count)
            if is_html:
                for date in future_entry_dates(line, datetime.date.today()):
                    report(path, n, "entry dated after today", date)
                for ref in broken_entities(line):
                    report(path, n, "character reference without its &", ref)
        if is_html:
            text = path.read_text(encoding="utf-8")
            for first, last, n, title in duplicate_headings(text):
                if wanted is None or any(line in wanted for line in range(first, last + 1)):
                    report(path, n, "adjacent duplicate heading", title)
            # Line numbers are counted on from the status line before: counting each from the top took 12.6 s
            # of a 15 s run on a notebook of 18 MB with 1341 status lines.
            line_no, counted = 1, 0
            for m in META.finditer(text):
                meta = status_text(m.group(1))
                line_no, counted = line_no + text.count("\n", counted, m.start()), m.start()
                if wanted is not None and line_no not in wanted:
                    continue
                if len(meta) > MAX_META:
                    report(path, line_no, "long status line", meta)
    print(f"{len(paths)} files, {findings} findings")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
