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
file (wrapped by hand, or at another width) keeps every block as the side that wrote it left it, and only a
block merged from both sides is wrapped, at the width the file's own paragraphs keep. The command says how
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
    layouts = [layout(ours), layout(theirs)]
    if rewrap_md.rewrap(ours, width) == ours or None in layouts:
        return rewrap_md.rewrap(text, width), 0
    # A file this branch does not keep wrapped by the tool: a block one side wrote stays as that side wrote it,
    # and only a block merged from both is wrapped, at the width the file's own paragraphs keep.
    own = min(width, max([len(line) for block in layouts[0].values() if len(block) > 1 for line in block] or [width]))
    out = []
    for line in lines:
        out += layouts[0].get(line) or layouts[1].get(line) or rewrap_md.rewrap(line, own).split("\n")
    return "\n".join(out), 0


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
    import difflib
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
