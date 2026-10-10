#!/usr/bin/env python3
"""Rewrap Markdown prose to a width, one paragraph or list item at a time.

GNU fmt joins lines by indentation alone, so a nested list item sitting at the
same indent as its parent's continuation lines is merged into the parent. This
keeps every list item a block of its own: its marker on the first line, its
text hung under the marker's text. A blockquote is wrapped as one, each line of
its paragraphs and items under its markers. YAML frontmatter, headings, blank lines,
tables, fenced code blocks and trailer lines (`Refs: <url>`) pass through
unchanged. The result
depends only on the words, so rewrapping twice changes nothing, and a later
edit changes only the lines its own words reflow.

Usage: tools/rewrap_md.py FILE [--section HEADING] [--width N] [--changed]

--section rewraps only from the heading whose text is HEADING to the next
heading of the same or a higher level; the file is rewritten in place.
--changed leaves every paragraph or list item that the file's committed
version (git HEAD) holds line for line as it is, so an edit rewraps only its
own text, also in a file wrapped unevenly.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import textwrap
from pathlib import Path

_MARKER = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")
# A blockquote line: its markers, nested ones included ("> > "), then its text.
_QUOTE = re.compile(r"^(\s*(?:>\s?)+)(.*)$")
# A trailer, "Refs: <url>": a key and one value, kept on its own line like a commit trailer.
_TRAILER = re.compile(r"^[A-Z][\w-]*: \S+$")


# A word that, starting a line, would open a list item, a heading or a quote.
_OPENS_BLOCK = re.compile(r"^(?:[-*+]|\d+[.)]|#{1,6}|>)$")
_GLUE = "\x00"


def _fill(words: list[str], first: str, rest: str, width: int) -> list[str]:
    # Such a word is glued to the one before it, so no line starts with it.
    glued: list[str] = []
    for word in words:
        if glued and _OPENS_BLOCK.match(word):
            glued[-1] += _GLUE + word
        else:
            glued.append(word)
    lines = textwrap.wrap(" ".join(glued), width=width, initial_indent=first, subsequent_indent=rest,
                          break_long_words=False, break_on_hyphens=False)
    return [line.replace(_GLUE, " ") for line in lines]


def rewrap(text: str, width: int = 100, base: str | None = None) -> str:
    """`text` rewrapped; with `base`, a block whose lines `base` holds consecutively stays as it is."""
    # YAML frontmatter (a skill's name and description) is data, not prose.
    front = ""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 3)
        if end != -1:
            front, text = text[: end + 5], text[end + 5 :]
    out: list[str] = []
    block: list[str] = []  # words of the paragraph or item being collected
    raw: list[str] = []  # its lines as written
    first = rest = ""
    in_fence = False
    quoting: str | None = None  # the marker of the blockquote paragraph being collected
    quoted_fence = False  # inside a fenced block of a blockquote

    def flush() -> None:
        nonlocal block, raw
        if block:
            kept = base is not None and "\n" + "\n".join(raw) + "\n" in "\n" + base + "\n"
            out.extend(raw if kept else _fill(block, first, rest, width))
            block, raw = [], []

    for line in text.split("\n"):
        if in_fence or _FENCE.match(line):
            flush()
            out.append(line)
            if _FENCE.match(line):
                in_fence = not in_fence
            continue
        stripped = line.strip()
        quote = _QUOTE.match(line)
        if quote:
            # A blockquote is wrapped as one: every line of a paragraph of it carries its marker.
            marker, body = quote.group(1).rstrip() + " ", quote.group(2)
            inner = _MARKER.match(body)
            if quoted_fence or _FENCE.match(body):
                flush()
                out.append(line)
                quoting = None
                if _FENCE.match(body):
                    quoted_fence = not quoted_fence
            elif not body.strip() or body.lstrip().startswith("|"):
                flush()
                out.append(line)
                quoting = None
            elif inner:
                flush()
                indent, sign, words = inner.groups()
                first, rest = f"{marker}{indent}{sign} ", marker + " " * (len(indent) + len(sign) + 1)
                block, raw, quoting = words.split(), [line], marker
            elif block and quoting == marker:
                block.extend(body.split())
                raw.append(line)
            else:
                flush()
                first = rest = marker
                block, raw, quoting = body.split(), [line], marker
            continue
        if quoting is not None:
            # A line without the marker ends the quote's paragraph: it is not drawn into it.
            flush()
            quoting = None
        if not stripped or _HEADING.match(line) or stripped.startswith("|") or _TRAILER.match(line):
            flush()
            out.append(line)
            continue
        item = _MARKER.match(line)
        if item:
            flush()
            indent, marker, body = item.groups()
            first, rest = f"{indent}{marker} ", " " * (len(indent) + len(marker) + 1)
            block, raw = body.split(), [line]
        elif block:
            block.extend(stripped.split())
            raw.append(line)
        else:
            first = rest = line[: len(line) - len(line.lstrip())]
            block, raw = stripped.split(), [line]
    flush()
    return front + "\n".join(out)


def rewrap_section(text: str, heading: str, width: int = 100, base: str | None = None) -> str:
    lines = text.split("\n")
    start = level = None
    for number, line in enumerate(lines):
        match = _HEADING.match(line)
        if not match:
            continue
        if start is None and match.group(2) == heading:
            start, level = number, len(match.group(1))
        elif start is not None and len(match.group(1)) <= level:
            end = number
            break
    else:
        end = len(lines)
    if start is None:
        raise ValueError(f"no heading {heading!r}")
    body = rewrap("\n".join(lines[start:end]), width, base).split("\n")
    return "\n".join(lines[:start] + body + lines[end:])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("file", type=Path)
    parser.add_argument("--section", help="rewrap only this heading's section")
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--changed", action="store_true",
                        help="leave the paragraphs and items the committed version holds as they are")
    args = parser.parse_args(argv)
    text = args.file.read_text()
    base = None
    if args.changed:
        # For a file git doesn't hold yet, `git show` prints nothing, so nothing is kept.
        base = subprocess.run(["git", "show", f"HEAD:./{args.file.name}"], cwd=args.file.resolve().parent,
                              capture_output=True, text=True).stdout
    try:
        new = (rewrap_section(text, args.section, args.width, base) if args.section
               else rewrap(text, args.width, base))
    except ValueError as exc:
        print(f"rewrap_md: {exc}", file=sys.stderr)
        return 1
    if new != text:
        args.file.write_text(new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
