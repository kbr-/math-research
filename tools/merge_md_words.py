#!/usr/bin/env python3
"""Merge a conflicted Markdown file word by word, then rewrap it.

Prose wrapped to a width conflicts by the paragraph: one side changes a sentence, the lines after it
reflow, and every reflowed line differs from the other side's, which changed another sentence of the same
paragraph. Line by line the two changes cannot be told apart; word by word they can. This takes the three
versions the index holds of a conflicted file, unwraps each paragraph and list item to one line
(tools/rewrap_md.py's blocks; headings, tables, fenced code and blank lines stay as they are), merges the
three by those lines, merges the paragraphs that conflict there with every word a line of its own, and
rewraps the result.

A file this branch keeps wrapped by tools/rewrap_md.py at its default width comes out wrapped so. Any other
file (wrapped by hand, or at another width) keeps every block this branch has as this branch wrote it. A
block the merge changed keeps this branch's line breaks, with the changed words put into their lines, unless
a line would then be longer than any the block or the file keeps; that block, and a block the merge brought
in, is wrapped at the width the file's own paragraphs keep. The other side's line breaks are never taken: its
copy may be wrapped at another width. The command says how
many lines differ from this branch's version, so a merge that reflowed more than it merged is seen at once.

Where the two sides changed the same words, the conflict stays, marked, around those words alone, in a
paragraph left unwrapped: resolve it, then run tools/rewrap_md.py on the file.

Git's own merge has no such mode: its whitespace options and diff algorithms leave the same conflicts
(tried on a rule file's three versions, 10 October 2026). Its extension point is a merge driver, which this
is with --driver: .gitattributes names the driver `md-words` for *.md, and a clone turns it on with

    git config merge.md-words.name "wrapped Markdown, word by word"
    git config merge.md-words.driver 'f=tools/merge_md_words.py; if [ -f "$f" ]; then python3 "$f" --driver %O %A %B; else git merge-file -q %A %O %B; fi'

after which a merge or a rebase merges such files this way by itself. A clone without the setting merges
them by lines, as before.

Usage, during a merge or a rebase: tools/merge_md_words.py FILE...
       as git's merge driver:        tools/merge_md_words.py --driver BASE OURS THEIRS [WIDTH]
Exit status: 0 every file merged and staged; 3 a file has conflicts left (written, not staged); 4 git failed
or a file has a line that reads as a conflict marker. As a driver: 0 merged into OURS, 1 conflicts left in it.
"""

import difflib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rewrap_md

UNWRAPPED = 10**9
END = "\x1e"    # ends a line of the unwrapped text
MARKERS = ("<<<<<<< ours", "=======", ">>>>>>> theirs")
BASE_MARKER = "||||||| base"


def tokens(text):
    """The unwrapped `text` as words, each line ended by END. A line's indentation stays with its first word,
    and every space between two words is kept, so the words put back together are the text."""
    found = []
    for line in text.split("\n"):
        indent = line[:len(line)-len(line.lstrip(" "))]
        words = line[len(indent):].split(" ")
        found += [indent+words[0], *words[1:], END]
    return found[:-1]


def text_of(found):
    """The text the tokens of `tokens` stand for; a conflict marker is a line of its own."""
    lines, line, marked = [], [], False
    for token in found:
        if token == END:
            lines.append(" ".join(line))
            line, marked = [], False
        elif token in MARKERS:
            # The words before it are a line, and so are the words after it.
            if line:
                lines.append(" ".join(line))
            lines.append(token)
            line, marked = [], True
        else:
            line.append(token)
            marked = False
    return "\n".join(lines if marked else [*lines, " ".join(line)])


def merge_file(versions, *options):
    """(the lines git merge-file prints for three texts, ours, base, theirs; how many conflicts it left)."""
    with tempfile.TemporaryDirectory() as scratch:
        paths = [Path(scratch)/name for name in ("ours", "base", "theirs")]
        for path, text in zip(paths, versions):
            path.write_text(text+"\n", encoding="utf-8")
        done = subprocess.run(["git", "merge-file", "-p", *options, "-L", "ours", "-L", "base", "-L", "theirs", *map(str, paths)], capture_output=True, text=True)
    if done.returncode < 0 or done.returncode > 127:
        raise ValueError(f"git merge-file failed: {done.stderr.strip()}")
    return done.stdout.split("\n")[:-1], done.returncode


def merged(ours, base, theirs, width=100):
    """(the three versions of a Markdown text merged, how many conflicts are left). The unwrapped paragraphs
    are merged as lines first, and only the paragraphs that conflict there are merged word by word: the words
    of a whole file line up wrongly where one side adds a long item beside a change of the other. With no
    conflict left the text is rewrapped to `width`; otherwise its paragraphs are unwrapped and the conflicts
    marked."""
    versions = [rewrap_md.rewrap(text, UNWRAPPED) for text in (ours, base, theirs)]
    if any({*MARKERS, BASE_MARKER} & {*tokens(text), *text.split("\n")} for text in versions):
        raise ValueError("the text has a line that reads as a conflict marker")
    lines, conflicts, sides, side = [], 0, None, None
    for line in merge_file(versions, "--diff3")[0]:
        if line == MARKERS[0]:
            sides, side = {"ours": [], "base": [], "theirs": []}, "ours"
        elif sides is None:
            lines.append(line)
        elif line == BASE_MARKER:
            side = "base"
        elif line == MARKERS[1]:
            side = "theirs"
        elif line == MARKERS[2]:
            words, left = merge_file(["\n".join(tokens("\n".join(sides[name]))) for name in ("ours", "base", "theirs")])
            lines += text_of(words).split("\n")
            conflicts += left
            sides = None
        else:
            sides[side].append(line)
    text = "\n".join(lines)
    if conflicts:
        return text, conflicts
    written = layout(ours)
    if rewrap_md.rewrap(ours, width) == ours or written is None:
        return rewrap_md.rewrap(text, width), 0
    # A file this branch does not keep wrapped by the tool: a block this branch has stays as it wrote it, a
    # block the merge changed keeps this branch's line breaks around the words that changed, and a block the
    # merge brought in is wrapped at the width the file's own paragraphs keep. The other side's line breaks are
    # not taken: its copy of the file may be wrapped at another width.
    # Wrapped as a whole text, so that a line of code or a table's row is known for what it is and left alone.
    own = own_width(written, width)
    wrapped = layout(rewrap_md.rewrap(text, own)) or {}
    # The blocks of this branch the merge changed: those of several lines that are gone from the result. A block
    # of one line (a table's row, a line of code) is no prose to move words within.
    gone = [block for block in written if block not in set(lines) and len(written[block]) > 1]
    out = []
    for line in lines:
        if line in written:
            out += written[line]
            continue
        old = max(gone, key=lambda block: alike(block, line), default=None)
        placed = changed_in_place(written[old], line) if old is not None and alike(old, line) > 0.5 else []
        # Words put in can make a line longer than any the block or the file keeps: then the block is wrapped.
        fits = placed and max(map(len, placed)) <= max(own, *map(len, written[old]))
        out += placed if fits else wrapped.get(line, [line])
    return "\n".join(out), 0


def alike(one, other):
    """How much of two unwrapped blocks' words are the same words in the same order, from 0 to 1."""
    return difflib.SequenceMatcher(None, one.split(), other.split(), autojunk=False).ratio()


PREFIX = re.compile(r"[ >]*")


def changed_in_place(block, line):
    """The lines of `block`, a block as this branch wrote it, with its words changed to those of `line`, the
    same block unwrapped after the merge: each line keeps the words it had, a word put in joins the line of
    the word before it, and a line left with no word is dropped."""
    prefixes = [PREFIX.match(row).group(0) for row in block]
    rows = [row[len(prefix):].split() for row, prefix in zip(block, prefixes)]
    old = [word for row in rows for word in row]
    home = [number for number, row in enumerate(rows) for _ in row]       # the line each old word stands on
    new = line[len(PREFIX.match(line).group(0)):].split()
    result = [[] for _ in rows]
    for kind, low, high, start, end in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if kind == "equal":
            for offset in range(high - low):
                result[home[low + offset]].append(new[start + offset])
        else:
            result[home[low - 1] if low else 0] += new[start:end]
    return [prefix + " ".join(words) for prefix, words in zip(prefixes, result) if words]


def own_width(written, width):
    """The width a file's wrapped blocks keep, at most `width`: the length 95 lines of 100 stay within, so that
    a link or another word that cannot be broken, longer than any wrapped line, does not pass for the width."""
    lengths = sorted(len(line) for block in written.values() if len(block) > 1 for line in block)
    return min(width, lengths[-(-95 * (len(lengths) - 1) // 100)]) if lengths else width


def layout(text):
    """{a block of `text` unwrapped to one line: its lines as written}, or None where the two cannot be lined
    up. A quote's marker, which every written line of it repeats, is no word of the block."""
    def words(lines):
        return [word for word in " ".join(lines).split() if set(word) != {">"}]
    written, found, at = text.split("\n"), {}, 0
    for line in rewrap_md.rewrap(text, UNWRAPPED).split("\n"):
        end = at + 1
        if at >= len(written):
            return None
        if written[at] != line:
            while end <= len(written) and words(written[at:end]) != words([line]):
                end += 1
            if end > len(written):
                return None
        found.setdefault(line, written[at:end])
        at = end
    return found if at == len(written) else None


def differing(before, after):
    """How many lines of `after` are not lines of `before` in its order: what a merge changed in a file."""
    return sum(1 for line in difflib.unified_diff(before.split("\n"), after.split("\n"), lineterm="", n=0)
               if line.startswith("+") and not line.startswith("+++"))


def driver(base, ours, theirs, width=100):
    """As git's merge driver: merge the files `base` and `theirs` into `ours`; 0 when no conflict is left.
    A file this branch does not keep wrapped is merged by lines, as git would: rewrapping it would change
    every paragraph of it."""
    texts = [Path(path).read_text(encoding="utf-8") for path in (ours, base, theirs)]
    try:
        if rewrap_md.rewrap(texts[0], int(width)) != texts[0]:
            raise ValueError("not kept wrapped")
        text, conflicts = merged(*texts, int(width))
    except ValueError:
        by_lines = subprocess.run(["git", "merge-file", "-q", "-L", "ours", "-L", "base", "-L", "theirs", ours, base, theirs])
        return 1 if by_lines.returncode else 0
    Path(ours).write_text(text, encoding="utf-8")
    return 1 if conflicts else 0


def main(argv=None):
    names = sys.argv[1:] if argv is None else argv
    if not names or names[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if names else 2
    if names[0] == "--driver":
        if len(names) not in (4, 5):
            print("--driver takes the files git names %O %A %B, and the width where it is not 100", file=sys.stderr)
            return 2
        return driver(*names[1:])
    left = 0
    for name in names:
        stages = [subprocess.run(["git", "show", f":{stage}:{name}"], capture_output=True, text=True) for stage in (2, 1, 3)]
        if any(stage.returncode for stage in stages):
            print(f"{name}: not a file both sides changed: {next(stage.stderr.strip() for stage in stages if stage.returncode)}", file=sys.stderr)
            return 4
        try:
            text, conflicts = merged(*(stage.stdout for stage in stages))
        except ValueError as error:
            print(f"{name}: {error}", file=sys.stderr)
            return 4
        Path(name).write_text(text, encoding="utf-8")
        if conflicts:
            left += 1
            print(f"{name}: {conflicts} conflicts left, each around the words both sides changed; its paragraphs are unwrapped")
        elif subprocess.run(["git", "add", "--", name]).returncode:
            return 4
        else:
            print(f"{name}: merged word by word; {differing(stages[0].stdout, text)} of its {text.count(chr(10)) + 1} "
                  "lines differ from this branch's version")
    return 3 if left else 0


if __name__ == "__main__":
    raise SystemExit(main())
