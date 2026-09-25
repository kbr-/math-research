#!/usr/bin/env python3
"""Read one notebook section by exact anchor; missing boundaries fail closed."""
# Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT

import argparse
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import subprocess
from recovery_evidence import observe
from notebooks import selected, resolve_anchor, selection_file


MATH = re.compile(r'\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]')


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
    source = MATH.sub(lambda m: m.group().replace('<', '&lt;').replace('>', '&gt;'), source)
    parser = Text()
    parser.feed(source); parser.close()
    return ' '.join(''.join(parser.parts).split())


BLOCKS = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tr', 'div', 'article', 'section',
          'ol', 'ul', 'table', 'br'}
TIMING = re.compile(r'<div class="timing-report"[\s\S]*?</table>\s*<p class="timing-note">[\s\S]*?</p>\s*</div>')


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
    source = MATH.sub(lambda m: m.group().replace('<', '&lt;').replace('>', '&gt;'), source)
    parser = Text()
    parser.feed(source); parser.close()
    lines = (' '.join(line.split('\t')[0].split()) + ''.join('\t' + ' '.join(c.split()) for c in line.split('\t')[1:])
             for line in ''.join(parser.parts).split('\n'))
    return '\n'.join(line for line in lines if line.strip()) + '\n'


class Notebook(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.nodes, self.stack = source, [], []
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        # Preserve offsets while protecting TeX comparisons from HTML parsing.
        self.feed(MATH.sub(lambda m: m.group().replace('<', ' ').replace('>', ' '), source))
        self.close()
        if self.stack:
            raise ValueError("Unclosed notebook section or heading")

    def position(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag not in {"section", "article", "h1", "h2", "h3", "h4", "h5", "h6"}:
            return
        scope = next((n for n in reversed(self.stack)
                      if n["tag"] in {"section", "article"}), None)
        node = dict(tag=tag, anchor=dict(attrs).get("id"),
                    start=self.position(), scope=scope)
        self.nodes.append(node)
        self.stack.append(node)

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

    def toc(self, tail=10, since=None):
        if tail < 1:
            raise ValueError('--tail must be positive')
        record = self.anchor('research-record')
        entries = [n for n in self.nodes if n['tag'] == 'article'
                   and record['start'] < n['start'] < record['close']]
        rows = []
        for node in entries:
            if not node['anchor']:
                raise ValueError('Research-record article lacks an anchor')
            match = re.search(r'\d{4}-\d{2}-\d{2}', node['anchor'])
            stamp = date.fromisoformat(match.group()) if match else None
            if since and stamp and stamp < since:
                continue
            heading = next((n for n in self.nodes if n['tag'] == 'h3'
                            and node['start'] < n['start'] < node['close']), None)
            title = visible_text(self.source[heading['start']:heading['end']]) if heading else '(untitled)'
            # Date is already in the first column; retain only the descriptive title.
            title = re.sub(r'^\d{1,2} [A-Za-z]+ \d{4}\s*[—–:-]\s*', '', title)
            words = title.split()
            short = ' '.join(words[:10]) + (' …' if len(words) > 10 else '')
            rows.append(f'{stamp or "undated"}\t{node["anchor"]}\t{short}')
        return '\n'.join(rows[-tail:]) + ('\n' if rows else ''), max(0, len(rows)-tail)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("anchor", nargs="?", help="Section, article, or heading ID")
    parser.add_argument("--current", action="store_true",
                        help="Read everything before Research record")
    parser.add_argument('--toc', action='store_true', help='Compact record contents, latest 10 by default')
    parser.add_argument('--tail', type=int, help='Maximum TOC entries, newest in record order')
    parser.add_argument('--since', type=date.fromisoformat, help='TOC date filter (YYYY-MM-DD); undated entries retained')
    parser.add_argument("--until", help="Stop before this exact anchor instead")
    parser.add_argument("--out", type=Path, help="Write a new file instead of stdout")
    parser.add_argument("--notebook", help="Research thread name; defaults to worktree selection or main")
    parser.add_argument("--text", action="store_true",
                        help="Plain text for reading (one line per block, TeX kept, timing table dropped)")
    args = parser.parse_args()
    if args.text and args.toc:
        parser.error('--text applies to an anchor or --current')
    if sum((bool(args.anchor), args.current, args.toc)) != 1 or (args.until and not args.anchor):
        parser.error('Choose an anchor (optionally --until), --current, or --toc')
    if not args.toc and (args.tail is not None or args.since is not None):
        parser.error('--tail and --since require --toc')
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
        notebook = Notebook(source)
        if args.toc:
            result, omitted = notebook.toc(args.tail if args.tail is not None else 10, args.since)
            if omitted:
                print(f'{omitted} matching earlier entries omitted; use --tail to expand.', file=sys.stderr)
        elif args.current:
            result = source[:notebook.anchor("research-record")["start"]].rstrip() + "\n"
        else:
            result = notebook.excerpt(args.anchor, args.until)
        if args.text:
            result = readable_text(result)
        if args.out:
            with args.out.open("x", encoding="utf-8") as stream:
                stream.write(result)
        else:
            sys.stdout.write(result)
        observe('read', tool='notebook-excerpt', selector={
            'notebook':item['name'],'anchor':args.anchor,'until':args.until,'current':args.current,
            'toc':args.toc,'tail':args.tail,'since':str(args.since)},
            text=result, shown=not bool(args.out))
    except (ValueError, OSError) as error:
        parser.exit(2, f"notebook-excerpt: {error}\n")


if __name__ == "__main__":
    main()
