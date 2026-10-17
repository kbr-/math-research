#!/usr/bin/env python3
"""Read one notebook section by exact anchor; missing boundaries fail closed."""
# Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT

import argparse
from datetime import date
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from pathlib import Path
import re
import sys
import subprocess
from recovery_evidence import observe
from notebooks import PUBLIC, selected, resolve_anchor, selection_file
from notebook_math import MATH, protect_math


def visible_text(source):
    """Visible HTML text with literal TeX retained, not mistaken for markup."""
    class Text(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
        def handle_data(self, data):
            self.parts.append(data)
        def handle_starttag(self, tag, attrs):
            if tag not in {'a', 'span', 'strong', 'em', 'b', 'i', 'code', 'sub', 'sup'}:
                self.parts.append(' ')
        def handle_endtag(self, tag):
            self.handle_starttag(tag, [])
    source = protect_math(source)
    parser = Text()
    parser.feed(source); parser.close()
    return ' '.join(''.join(parser.parts).split())


BLOCKS = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tr', 'div', 'article', 'section',
          'ol', 'ul', 'table', 'br'}
# The finisher writes data-generated before class (finish-turn.py), so the class may follow other attributes.
TIMING = re.compile(r'<div\b[^>]*\bclass="timing-report"[\s\S]*?</table>\s*<p class="timing-note">[\s\S]*?</p>\s*</div>')


def readable_text(source):
    """Plain text for reading: one line per block, TeX kept, entities decoded, timing tables dropped."""
    class Text(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
        def handle_data(self, data):
            self.parts.append(' '.join(data.split('\n')))
        def handle_starttag(self, tag, attrs):
            if tag in BLOCKS:
                self.parts.append('\n')
            elif tag in {'td', 'th'}:
                self.parts.append('\t')
        def handle_endtag(self, tag):
            if tag in BLOCKS:
                self.parts.append('\n')
    source = TIMING.sub('', source)
    source = protect_math(source)
    parser = Text()
    parser.feed(source); parser.close()
    lines = (' '.join(line.split('\t')[0].split()) + ''.join('\t' + ' '.join(c.split()) for c in line.split('\t')[1:])
             for line in ''.join(parser.parts).split('\n'))
    return '\n'.join(line for line in lines if line.strip()) + '\n'


def living_and_toc(source, tail=10):
    """The living sections (everything before the Research record), the record's contents table for its last
    `tail` entries, and the number of earlier entries, as Notebook(source).toc gives them, but parsing only the
    last `tail` articles: restoration needs no more, and parsing every entry made preparing the resume bundle
    take 2.6 s on 16 October 2026, 1.5 s of it in this parse.  The earlier articles are counted by a scan that
    skips TeX and comments, as the parser does."""
    opening = re.search(r'<section id="research-record"[^>]*>', source)
    if opening is None:
        raise ValueError("Expected one section/heading anchor 'research-record'; found 0")
    if tail < 1:
        raise ValueError('--tail must be positive')
    record = source[opening.start():]
    masked = re.sub(r'<!--.*?-->', lambda m: ' ' * len(m.group()), record, flags=re.S)
    masked = MATH.sub(lambda m: m.group().replace('<', ' ').replace('>', ' '), masked)
    opens = [m.start() for m in re.finditer(r'<article\b', masked)]
    if not opens:
        return source[:opening.start()], '', 0
    take = opens[-tail:]
    close = masked.find('</article>', take[-1])
    if close < 0:
        raise ValueError('Unclosed research-record article')
    mini = opening.group(0) + record[take[0]:close + len('</article>')] + '\n</section>\n'
    toc, _ = Notebook(mini).toc(tail=tail)
    return source[:opening.start()], toc, len(opens) - len(take)


class Notebook(HTMLParser):
    def __init__(self, source, *, end=None, capture_links=False, capture_anchors=False):
        super().__init__(convert_charrefs=False)
        if end is not None and not 0 < end <= len(source):
            raise ValueError("Invalid notebook prefix boundary")
        self.source, self.nodes, self.stack = source, [], []
        self.links = [] if capture_links else None
        self.anchor_owners = {} if capture_anchors else None
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        # Mask the complete source before slicing: a fake article can occur
        # inside a TeX expression whose closing delimiter is beyond the prefix.
        self.masked = MATH.sub(lambda m: m.group().replace('<', ' ').replace('>', ' '), source)
        self.parsed_end = 0
        self.extend(len(source) if end is None else end)

    def extend(self, end):
        if not self.parsed_end <= end <= len(self.source):
            raise ValueError("Invalid notebook prefix extension")
        if hasattr(self, "by_anchor"):
            del self.by_anchor
        self.feed(self.masked[self.parsed_end:end])
        self.close()
        self.parsed_end = end
        # Evidence may stop at a verified article end. Only its enclosing
        # sections may remain open; ordinary full-file reads stay strict.
        if self.stack and (end == len(self.source) or any(n["tag"] != "section" for n in self.stack)):
            raise ValueError("Unclosed notebook section or heading")

    def position(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        anchored = None
        if self.anchor_owners is not None:
            identifier = dict(attrs).get("id")
            if identifier is not None:
                anchored = {"owner": next((n for n in reversed(self.stack)
                                           if n["tag"] == "article"), None)}
                self.anchor_owners.setdefault(identifier, []).append(anchored)
        if tag == "a" and self.links is not None:
            owner = next((n for n in reversed(self.stack) if n["tag"] == "article"), None)
            href = dict(attrs).get("href")
            if owner is not None and href:
                self.links.append((href, owner))
        if tag not in {"section", "article", "h1", "h2", "h3", "h4", "h5", "h6"}:
            return
        scope = next((n for n in reversed(self.stack)
                      if n["tag"] in {"section", "article"}), None)
        node = dict(tag=tag, anchor=dict(attrs).get("id"),
                    start=self.position(), scope=scope)
        self.nodes.append(node)
        self.stack.append(node)
        if anchored is not None and tag == "article":
            anchored["owner"] = node

    def handle_endtag(self, tag):
        if tag not in {"section", "article", "h1", "h2", "h3", "h4", "h5", "h6"}:
            return
        if not self.stack or self.stack[-1]["tag"] != tag:
            raise ValueError(f"Unmatched closing tag: {tag}")
        node = self.stack.pop()
        node["close"] = self.position()
        node["end"] = self.source.index(">", node["close"]) + 1

    def anchor(self, name):
        if not hasattr(self, "by_anchor"):
            self.by_anchor = {}
            for n in self.nodes:
                self.by_anchor.setdefault(n["anchor"], []).append(n)
        matches = self.by_anchor.get(name.removeprefix("#"), [])
        if len(matches) != 1:
            raise ValueError(f"Expected one section/heading anchor {name!r}; found {len(matches)}")
        return matches[0]

    def excerpt(self, name, until=None):
        node = self.anchor(name)
        if until is not None:
            end = self.anchor(until)["start"]
        elif node["tag"].startswith("h"):
            end = node["scope"]["close"] if node["scope"] else len(self.source)
            level = int(node["tag"][1])
            end = next((n["start"] for n in self.nodes
                        if node["start"] < n["start"] < end
                        and n["tag"].startswith("h")
                        and int(n["tag"][1]) <= level), end)
        else:
            end = node["end"]
        if end <= node["start"]:
            raise ValueError("The end anchor must follow the start anchor")
        return self.source[node["start"]:end].rstrip() + "\n"

    def enclosing_excerpt(self, name):
        """Read the whole article for a unique element ID, including paragraph claims."""
        if self.anchor_owners is None:
            raise ValueError("Enclosing lookup requires capture_anchors=True")
        matches = self.anchor_owners.get(name.removeprefix("#"), [])
        if len(matches) != 1:
            raise ValueError(f"Expected one element anchor {name!r}; found {len(matches)}")
        owner = matches[0]["owner"]
        if owner is None:
            raise ValueError(f"Anchor {name!r} is not inside an article")
        return self.source[owner["start"]:owner["end"]].rstrip() + "\n"

    def entry_row(self, node, since=None):
        if not node['anchor']:
            raise ValueError('Research-record article lacks an anchor')
        match = re.search(r'\d{4}-\d{2}-\d{2}', node['anchor'])
        stamp = date.fromisoformat(match.group()) if match else None
        if since and stamp and stamp < since:
            return None
        heading = next((n for n in self.nodes if n['tag'] == 'h3'
                        and node['start'] < n['start'] < node['close']), None)
        title = visible_text(self.source[heading['start']:heading['end']]) if heading else '(untitled)'
        title = re.sub(r'^\d{1,2} [A-Za-z]+ \d{4}\s*[—–:-]\s*', '', title)
        words = title.split()
        short = ' '.join(words[:10]) + (' …' if len(words) > 10 else '')
        return f'{stamp or "undated"}\t{node["anchor"]}\t{short}'

    def toc(self, tail=10, since=None):
        if tail < 1:
            raise ValueError('--tail must be positive')
        record = self.anchor('research-record')
        entries = [n for n in self.nodes if n['tag'] == 'article'
                   and record['start'] < n['start'] < record['close']]
        rows = [row for n in entries if (row := self.entry_row(n, since)) is not None]
        return '\n'.join(rows[-tail:]) + ('\n' if rows else ''), max(0, len(rows)-tail)

    def backlinks(self, name, tail=10, since=None, *, source_path='notebook.html', route=''):
        """Exact-fragment citations in this notebook's record, including canonical self URLs."""
        if tail < 1:
            raise ValueError('--tail must be positive')
        if self.links is None:
            raise ValueError('Backlink lookup requires capture_links=True')
        target = self.anchor(name)
        owner = target
        while owner is not None and owner['tag'] != 'article':
            owner = owner['scope']
        target_start = (owner or target)['start']
        record = self.anchor('research-record')
        canonical = urlsplit(PUBLIC + route)
        public_path = canonical.path.rstrip('/')
        local_paths = {'', 'notebook.html', 'index.html', source_path, '/' + source_path}
        counts, entries = {}, {}
        for href, article in self.links:
            if unquote(href.partition('#')[2]) != target['anchor']:
                continue
            try:
                parsed = urlsplit(href)
            except ValueError:
                continue  # Not a resolvable self-link; link validation is separate.
            if parsed.scheme or parsed.netloc:
                same_book = (parsed.scheme in {'http', 'https'}
                             and parsed.netloc in {canonical.netloc, 'kbr-.github.io'}
                             and unquote(parsed.path).rstrip('/') == public_path)
            else:
                same_book = unquote(parsed.path).removeprefix('./') in local_paths
            if same_book and record['start'] < article['start'] < record['close']:
                key = article['start']
                counts[key] = counts.get(key, 0) + 1
                entries[key] = article
        rows = []
        for key in sorted(entries):
            row = self.entry_row(entries[key], since)
            if row is None:
                continue
            stamp, anchor, title = row.split('\t', 2)
            relation = 'later' if key > target_start else 'earlier' if key < target_start else 'self'
            rows.append(f'{stamp}\t{anchor}\t{relation}\t{counts[key]} link(s)\t{title}')
        return '\n'.join(rows[-tail:]) + ('\n' if rows else ''), max(0, len(rows)-tail)


def review_tests(source, width=600):
    """One line per review entry: its anchor and the start of its Decisive test, oldest first.  A review fixed
    a test that a review of the day before had fixed and that three entries had since attempted (10 October
    2026); this is the list to read before fixing another."""
    lines = []
    for found in re.finditer(r'<article\b([^>]*)>(.*?)</article>', source, re.S):
        if 'data-kind="review"' not in found.group(1):
            continue
        anchor = re.search(r'\bid="([^"]+)"', found.group(1))
        test = re.search(r'<strong>Decisive test\.</strong>(.*?)</p>', found.group(2), re.S)
        text = ' '.join(readable_text(test.group(1)).split()) if test else '(no Decisive test paragraph)'
        lines.append(f"{anchor.group(1) if anchor else '(no id)'}\t{text[:width]}")
    return '\n'.join(lines) + '\n' if lines else '(no review entries)\n'


RECORD_SHOWN = 1500     # characters of each record statement paragraph printed beside a registered summary
RECORD_MAX = 4          # statement paragraphs printed per claim
RECORD_MIN_SHARE = 0.2  # least share of a summary's words an unnamed, unanchored paragraph holds to be shown unmarked


def statement_rank(plain, ident, summary):
    """Sort key for a record statement paragraph: one naming the claim in its label first, then by the share of
    the summary's words of four or more letters it contains."""
    name = ident.split(':', 1)[-1].replace('-', ' ').lower() if ident else ''
    label = plain.split('.', 1)[0].replace('-', ' ').lower()
    words = {w for w in re.findall(r'[a-z]{4,}', (summary or '').lower())}
    held = {w for w in re.findall(r'[a-z]{4,}', plain.lower())}
    share = len(words & held) / len(words) if words else 0.0
    return (not (name and name in label), -share)


def record_statements(record, root, cache, ident=None, summary=''):
    """The Lemma, Theorem, Corollary, Proposition or Statement paragraphs of the entry a claim's record link
    points at, as plain text, or a line saying why none could be read.  `cache` maps notebook paths to text, so
    a brief naming several claims reads each notebook once.

    On 16 October 2026 an entry and then its reviewer took "not shown to be Hilbert-like" from a registered
    summary of prop:binary-word-rank-witness that omitted the word "placeholder-linear", which its record's
    proposition states; a brief carrying only summaries could not show the reviewer the difference.

    Only the first entry link of the record is followed. When the anchor names a paragraph inside an entry,
    the statement paragraph at that anchor comes first. Otherwise, when `ident` is given, a paragraph whose
    label names the claim (lem:cut-code-classes: "Lemma (cut-code classes)") comes first, then the others by
    the share of the summary's words they hold: on 16 October 2026 two claims of one entry both printed its
    first statements, neither its own. A paragraph neither at the anchor nor naming the claim, holding less
    than RECORD_MIN_SHARE of the summary's words, is printed marked as possibly another claim's and never
    dropped: a first version dropped them and lost a claim's real statement, and over the whole registry it
    would have left 490 of 4972 claims with no paragraph at all."""
    from claim_authoring import STATEMENT, _plain, source_notebook
    # A statement may open its paragraph (which may carry an id) or follow setup prose inside it, as in the
    # cut-code rank normalization entry: match the bold label wherever it stands, up to its paragraph's end.
    # The body may not cross into or out of a list item, table cell, heading or another paragraph, so a bold
    # reference in a list item matches nothing instead of swallowing the next paragraph's statement.
    within = r'(?:(?!</?(?:li|td|th|h\d|ul|ol|p)\b)[\s\S])*?'
    statement = re.compile(STATEMENT.pattern.replace('<p><strong>', '<strong>', 1)
                           .replace('</strong>.*?</p>', '</strong>' + within + '</p>', 1), STATEMENT.flags)
    assert within in statement.pattern, 'STATEMENT changed shape; update the element guard'
    link = re.search(r'\((https?://[^)\s]+#[^)\s]+)\)', record or '')
    if not link:
        return ['(the record link names no entry anchor; read the record)']
    path, anchor = source_notebook(link.group(1), root)
    if path is None or not path.exists():
        return [f'(record notebook for #{anchor} not found)']
    if path not in cache:
        cache[path] = path.read_text(encoding='utf-8')
    text = cache[path]
    at = text.find(f'<article id="{anchor}"')
    inner = None
    if at < 0:
        inner = text.find(f'id="{anchor}"')
        if inner < 0:
            return [f'(#{anchor} not found in {path.name})']
        at = text.rfind('<article', 0, inner)
        if at < 0 or text.rfind('</article>', 0, inner) > at:
            return [f'(#{anchor} is not inside an entry; read the record)']
    end = text.find('</article>', at)
    article = text[at:end if end >= 0 else None]
    matches = list(statement.finditer(article))
    offset = inner - at if inner is not None else -1
    ranked = sorted(((not (m.start() <= offset < m.end()), statement_rank(_plain(m.group(0)), ident, summary), i,
                      _plain(m.group(0))) for i, m in enumerate(matches)))
    if not ranked:
        return [f'(#{anchor} has no Lemma, Theorem, Corollary, Proposition or Statement paragraph)']
    # A paragraph neither at the record's anchor nor naming the claim, holding less than a fifth of the summary's
    # words, is marked as possibly another claim's: on 16 October 2026 a review entry's unrelated proposition was
    # printed as the statement of imp:depth-preserving-IPS-simulation (share 0.08), and a reviewer took it for the
    # claim's. Such a paragraph is not dropped: the one of cor:pang-observation-calibration (share 0.06) is the
    # linear-algebra statement that claim rests on.
    unjudged = not re.findall(r'[a-z]{4,}', (summary or '').lower())   # no summary words to compare
    statements = [plain if not elsewhere or not unnamed or -share >= RECORD_MIN_SHARE or unjudged else
                  f'(may be another claim\'s: it does not name this claim and holds {-share:.0%} of its summary\'s '
                  f'words) {plain}' for elsewhere, (unnamed, share), _, plain in ranked]
    shown = [s[:RECORD_SHOWN] + (' …' if len(s) > RECORD_SHOWN else '') for s in statements[:RECORD_MAX]]
    if len(statements) > RECORD_MAX:
        shown.append(f'({len(statements) - RECORD_MAX} more statement paragraphs in #{anchor})')
    return shown


def claim_excerpts(idents, registry, root=None):
    """The registered statement, assessment, status and record of each named claim, for a reviewer's brief;
    ValueError naming every identifier the registry does not hold.  On 11 October 2026 a dependency file given to
    a reviewer held the registry display's header lines in place of two claims, cut out by line numbers.  With
    `root`, each claim also gets the statement paragraphs of its record entry, read from the notebooks there."""
    claims = {claim['id']: claim for claim in registry['claims']}
    missing = [ident for ident in idents if ident not in claims]
    if missing:
        raise ValueError('not in the registry: ' + ', '.join(missing))
    blank = [ident for ident in idents if not str(claims[ident].get('summary', '')).strip()]
    if blank:      # an excerpt without its statement is the failure this mode exists against
        raise ValueError('registered without a statement: ' + ', '.join(blank))
    blocks, cache = [], {}
    for ident in idents:
        claim = claims[ident]
        block = (f"{ident}\n  Statement: {claim.get('summary', '')}\n  Assessment: {claim.get('assessment', '')}\n"
                 f"  Status: {claim.get('mathematical_status', '')}\n  Record: {claim.get('record', '')}\n")
        # 16 October 2026: a reviewer read a registered statement whose corrected clause was flagged only in its
        # assessment; the correcting claim's own statement now stands beside it.
        for edge in registry.get('relationships', []):
            source, kind, target = (str(edge.get('id', '')).split('::') + ['', '', ''])[:3]
            if kind == 'corrects' and target == ident:
                block += f"  Corrected by {source}: {claims.get(source, {}).get('summary', '')}\n"
        if root is not None:
            block += ''.join(f'  Record statement: {line}\n'
                             for line in record_statements(claim.get('record', ''), Path(root), cache, ident,
                                                           claim.get('summary', '')))
        blocks.append(block)
    if root is not None:
        size = sum(len(text) for text in cache.values())
        blocks.append(f'(record statements read from {len(cache)} notebook(s), {size / 1e6:.1f} MB)\n')
    return '\n'.join(blocks)


READ_LOG = 'research/logs/excerpt-reads.jsonl'


def log_read(root, notebook, anchors):
    """Append the anchors an excerpt printed or saved to the ignored read log, which tools/history_reads.py
    compares with a queue item's earlier entries when a cycle's mathematics begins.  A log that cannot be
    written is not an error."""
    import json
    import time
    try:
        path = Path(root) / READ_LOG
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as handle:
            handle.write(json.dumps({'unix_s': time.time(), 'notebook': notebook,
                                     'anchors': sorted(set(anchors))}) + '\n')
    except OSError:
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("anchor", nargs="?", help="Section, article, or heading ID")
    parser.add_argument("--current", action="store_true",
                        help="Read everything before Research record")
    parser.add_argument('--toc', action='store_true', help='Compact record contents, latest 10 by default')
    parser.add_argument('--review-tests', action='store_true',
                        help="Each review's anchor and the start of its Decisive test, oldest first")
    parser.add_argument('--backlinks', action='store_true', help='List record entries citing the exact anchor in this notebook')
    parser.add_argument('--tail', type=int, help='Maximum TOC/backlink entries, newest in record order')
    parser.add_argument('--since', type=date.fromisoformat, help='TOC/backlink date filter (YYYY-MM-DD); undated entries retained')
    parser.add_argument("--until", help="Stop before this exact anchor instead")
    parser.add_argument("--enclosing", action="store_true",
                        help="Read the complete article containing any element ID, including a paragraph claim")
    parser.add_argument("--out", type=Path, help="Write a new file instead of stdout")
    parser.add_argument("--notebook", help="Research thread name; defaults to worktree selection or main")
    parser.add_argument("--text", action="store_true",
                        help="Plain text for reading (one line per block, TeX kept, timing table dropped)")
    parser.add_argument('--claims', nargs='+', metavar='ID',
                        help='The registered statement and assessment of each named claim, for a reviewer\'s brief')
    args = parser.parse_args()
    if args.claims:
        if (args.anchor or args.current or args.toc or args.review_tests or args.backlinks or args.until
                or args.enclosing or args.text or args.notebook or args.tail is not None or args.since is not None):
            parser.error('--claims takes claim identifiers and, optionally, --out; no other option applies')
        import json
        try:
            root = Path(__file__).resolve().parents[1]
            registry = json.loads((root / 'research/claims/index.json').read_text())
            result = claim_excerpts(args.claims, registry, root=root)
            import claim_reads
            claim_reads.log(root, [c['id'] for c in registry.get('claims', []) if c.get('id') in set(args.claims)])
            if args.out:
                with args.out.open('x', encoding='utf-8') as stream:
                    stream.write(result)
            else:
                sys.stdout.write(result)
        except (OSError, ValueError) as error:
            parser.exit(1, f'notebook-excerpt.py: {error}\n')
        return
    if args.enclosing and (not args.anchor or args.current or args.toc or args.backlinks or args.until):
        parser.error('--enclosing requires an anchor and excludes --current, --toc, --backlinks and --until')
    if args.backlinks and (not args.anchor or args.current or args.toc or args.until or args.text):
        parser.error('--backlinks requires an anchor and excludes --current, --toc, --until and --text')
    if args.text and args.toc:
        parser.error('--text applies to an anchor or --current')
    if sum((bool(args.anchor), args.current, args.toc, args.review_tests)) != 1 or (args.until and not args.anchor):
        parser.error('Choose an anchor (optionally --until), --current, --toc or --review-tests')
    if not (args.toc or args.backlinks) and (args.tail is not None or args.since is not None):
        parser.error('--tail and --since require --toc or --backlinks')
    try:
        root = Path(__file__).resolve().parents[1]
        item = selected(args.notebook, root)
        # Bare lookups without a persisted selection must not pick an arbitrary
        # notebook when multiple threads reuse an anchor.
        if args.anchor and args.notebook is None:
            try:
                explicit_selection = selection_file(root).exists()
            except (OSError, subprocess.CalledProcessError):
                explicit_selection = False
            if not explicit_selection:
                item = resolve_anchor(args.anchor, root=root)
        source = (root / item["source"]).read_text()
        notebook = Notebook(source, capture_links=args.backlinks, capture_anchors=args.enclosing)
        if args.backlinks:
            result, omitted = notebook.backlinks(args.anchor, args.tail if args.tail is not None else 10,
                                                args.since, source_path=item['source'], route=item['route'])
            result = f"Research-record backlinks in {item['source']} only:\n" + (result or '(none)\n')
            if omitted:
                print(f'{omitted} matching earlier entries omitted; use --tail to expand.', file=sys.stderr)
        elif args.review_tests:
            result = review_tests(source)
        elif args.toc:
            result, omitted = notebook.toc(args.tail if args.tail is not None else 10, args.since)
            if omitted:
                print(f'{omitted} matching earlier entries omitted; use --tail to expand.', file=sys.stderr)
        elif args.current:
            result = source[:notebook.anchor("research-record")["start"]].rstrip() + "\n"
        elif args.enclosing:
            result = notebook.enclosing_excerpt(args.anchor)
        else:
            result = notebook.excerpt(args.anchor, args.until)
        if args.anchor and not args.backlinks:
            log_read(root, item['name'], [args.anchor] + re.findall(r'<article id="([^"]+)"', result))
        if args.text:
            result = readable_text(result)
        if args.out:
            with args.out.open("x", encoding="utf-8") as stream:
                stream.write(result)
        else:
            sys.stdout.write(result)
        selector = {
            'notebook':item['name'],'anchor':args.anchor,'until':args.until,'current':args.current,
            'toc':args.toc,'backlinks':args.backlinks,'tail':args.tail,'since':str(args.since)}
        if args.enclosing:
            selector['enclosing'] = True
        observe('read', tool='notebook-excerpt', selector=selector, text=result, shown=not bool(args.out))
    except (ValueError, OSError) as error:
        parser.exit(2, f"notebook-excerpt: {error}\n")


if __name__ == "__main__":
    main()
