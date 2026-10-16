#!/usr/bin/env python3
"""Replace one passage of a text file with another, line-aligned and keeping its indentation.

Usage: tools/replace_text.py FILE OLD_FILE NEW_FILE

OLD_FILE holds the passage to replace, NEW_FILE its replacement. The passage matches whatever its
words' line breaks are in FILE, since a rewrap moves them, but it starts at a line's start, after
its indentation, and ends at a line's end. It must match exactly once; otherwise FILE is left as it
is. The replacement's first line takes the indentation of the passage's first line, and each other
line keeps its offset from the replacement's first line, so a list item stays at its level, and a
replacement starting on a continuation line can end with a new item one level out. When a one-line
passage matches no line-aligned place, it may lie inside a longer line: it then matches there,
literally, once, never starting or ending inside a word, and a one-line replacement takes its place;
failing that, single line breaks (never a blank line) may fall between its words, and the
replacement takes the whole span on one line, to be rewrapped. A replacement of several lines is still placed line-aligned only.
"""
import re
import sys
from pathlib import Path


def replace(text, old, new, prose=False):
    """`text` with its one line-aligned occurrence of `old` replaced by `new`, re-indented; ValueError
    when `old` matches no line-aligned passage or more than one."""
    words = old.split()
    if not words:
        raise ValueError('the passage to replace is empty')
    pattern = re.compile(r'^([ \t]*)' + r'\s+'.join(map(re.escape, words)) + r'[ \t]*$', re.M)
    found = list(pattern.finditer(text))
    if not found and (prose or '\n' not in old.strip() and '\n' not in new.strip()):
        # A one-line passage inside a longer line, as in a notebook paragraph kept on one line (16 October 2026:
        # the passage sat mid-line and the tool refused it): it matches within that line only, and the one-line
        # replacement takes its place with no re-indentation.
        # A passage starting or ending with a word character does not start or end inside a word, and places
        # that overlap are counted apart (a lookahead finds each start).
        body = r'[ \t]+'.join(map(re.escape, words))
        body = (r'(?<!\w)' if re.match(r'\w', words[0]) else '') + body + (r'(?!\w)' if re.search(r'\w$', words[-1]) else '')
        starts = [m.start() for m in re.finditer(f'(?=(?:{body}))', text)]
        if not starts:
            # A passage whose words cross line breaks and start or end mid-line, as in wrapped Markdown or a
            # commit message (16 October 2026): its words match across any whitespace, and the one-line
            # replacement takes its place, to be rewrapped by the file's own tool.
            # One line break between two words, never a blank line, so two paragraphs are not merged.
            body = body.replace(r'[ \t]+', r'(?:[ \t]*\n[ \t]*|[ \t]+)')
            starts = [m.start() for m in re.finditer(f'(?=(?:{body}))', text)]
        if len(starts) == 1:
            match = re.compile(body).match(text, starts[0])
            # In prose (Markdown, plain text, HTML) a replacement of several lines is joined into the flow, to be
            # rewrapped (17 October 2026: a passage of several lines that a rewrap had moved mid-line was refused).
            placed = ' '.join(new.split()) if prose else new.strip()
            return text[:match.start()] + placed + text[match.end():], text.count('\n', 0, match.start()) + 1
        raise ValueError(f'the passage matches no line-aligned place and {len(starts)} places within or across lines, '
                         'not one')
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
    # 16 October 2026: a write of the new text failed, and the next call replaced a passage with the stale file
    # left by an earlier edit.  New text written before the old text it replaces is that case.
    try:
        if Path(argv[3]).stat().st_mtime + 1 < Path(argv[2]).stat().st_mtime:
            print(f'replace_text: {argv[3]} was written before {argv[2]}: the new text is probably left from an '
                  'earlier edit (a failed write?); write it again', file=sys.stderr)
            return 1
    except OSError:
        pass
    # 16 October 2026: a byte cut from a file written without a trailing newline left "</p" at the end of the new
    # text, and the notebook took an unclosed tag.
    try:
        new_text = Path(argv[3]).read_text()
        cut = re.search(r'</?(?:p|li|ul|ol|strong|em|h[1-6]|div|span|code|section|article|table|tr|td)\b[^<>]*$',
                        new_text)
        if cut:
            print(f'replace_text: {argv[3]} ends inside a tag ("{cut.group(0)[:20]}"): '
                  'the text was probably cut; write it again', file=sys.stderr)
            return 1
    except OSError:
        pass
    try:
        updated, line = replace(path.read_text(), Path(argv[2]).read_text(), Path(argv[3]).read_text(),
                                prose=path.suffix in ('.md', '.txt', '.html', ''))
    except (ValueError, OSError) as error:
        print(f'replace_text: {path}: {error}', file=sys.stderr)
        return 1
    path.write_text(updated)
    print(f'{path}: replaced the passage at line {line}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
