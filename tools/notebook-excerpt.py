#!/usr/bin/env python3
"""Read one notebook section by exact anchor; missing boundaries fail closed."""
# Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT

import argparse
from html.parser import HTMLParser
from pathlib import Path
import sys


class Notebook(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.nodes, self.stack = source, [], []
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.feed(source)
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
        matches = [n for n in self.nodes if n["anchor"] == name.removeprefix("#")]
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("anchor", nargs="?", help="Section, article, or heading ID")
    parser.add_argument("--current", action="store_true",
                        help="Read everything before Research record")
    parser.add_argument("--until", help="Stop before this exact anchor instead")
    parser.add_argument("--out", type=Path, help="Write a new file instead of stdout")
    args = parser.parse_args()
    if bool(args.anchor) == args.current or (args.current and args.until):
        parser.error("Choose an anchor (optionally --until), or --current")
    try:
        source = (Path(__file__).resolve().parents[1] / "notebook.html").read_text()
        notebook = Notebook(source)
        if args.current:
            result = source[:notebook.anchor("research-record")["start"]].rstrip() + "\n"
        else:
            result = notebook.excerpt(args.anchor, args.until)
        if args.out:
            with args.out.open("x", encoding="utf-8") as stream:
                stream.write(result)
        else:
            sys.stdout.write(result)
    except (ValueError, OSError) as error:
        parser.exit(2, f"notebook-excerpt: {error}\n")


if __name__ == "__main__":
    main()
