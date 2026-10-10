#!/usr/bin/env python3
"""Replace one passage of a text file with another, line-aligned and keeping its indentation.

Usage: tools/replace_text.py FILE OLD_FILE NEW_FILE

OLD_FILE holds the passage to replace, NEW_FILE its replacement. The passage matches whatever its
words' line breaks are in FILE, since a rewrap moves them, but it starts at a line's start, after
its indentation, and ends at a line's end. It must match exactly once; otherwise FILE is left as it
is. The replacement's first line takes the indentation of the passage's first line, and each other
line keeps its offset from the replacement's first line, so a list item stays at its level, and a
replacement starting on a continuation line can end with a new item one level out.
"""
import re
import sys
from pathlib import Path


def replace(text, old, new):
    """`text` with its one line-aligned occurrence of `old` replaced by `new`, re-indented; ValueError
    when `old` matches no line-aligned passage or more than one."""
    words = old.split()
    if not words:
        raise ValueError('the passage to replace is empty')
    pattern = re.compile(r'^([ \t]*)' + r'\s+'.join(map(re.escape, words)) + r'[ \t]*$', re.M)
    found = list(pattern.finditer(text))
    if len(found) != 1:
        raise ValueError(f'the passage matches {len(found)} line-aligned places, not one')
    match = found[0]
    indent = match.group(1)
    lines = new.strip('\n').split('\n')
    first = len(lines[0]) - len(lines[0].lstrip())

    def placed(line):
        # Each line keeps its offset from the replacement's first line, so a line indented less than
        # the first, such as a new list item after a continuation line, comes out less indented too.
        offset = len(line) - len(line.lstrip()) - first
        return ' ' * max(len(indent) + offset, 0) + line.lstrip()

    body = '\n'.join(placed(line) if line.strip() else '' for line in lines)
    return text[:match.start()] + body + text[match.end():], text.count('\n', 0, match.start()) + 1


def main(argv):
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        updated, line = replace(path.read_text(), Path(argv[2]).read_text(), Path(argv[3]).read_text())
    except (ValueError, OSError) as error:
        print(f'replace_text: {path}: {error}', file=sys.stderr)
        return 1
    path.write_text(updated)
    print(f'{path}: replaced the passage at line {line}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
