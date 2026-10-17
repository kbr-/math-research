#!/usr/bin/env python3
"""Resolve the conflicts a rebase or merge leaves in a notebook, where both sides changed whole elements.

Two branches that both work in one notebook conflict at the same places in commit after commit: each appends
entries to the record and items to the queue, and each rewrites its own paragraphs of a living section, which
sit on adjacent lines. Such a conflict is merged here element by element, an element being an article, a list
item or a labelled paragraph, known by its key (the article's id, the item's first data attribute, the
paragraph's label up to its first bracket or punctuation):

- an element one side changed or removed and the other left as the base has it takes the change;
- an element only one side has is kept: the current side's in their order, then the replayed side's;
- anything else is refused: an element both sides changed differently, one a side changed and the other
  removed, a key twice on one side, or a conflict whose sides are not whole elements.

A refusal changes nothing and names the place. Nothing here knows which side is right, so nothing is guessed.

Usage, in a worktree whose rebase or merge has stopped:
    tools/notebook_rebase.py [--file notebook.html]     resolve that file and stage it
    tools/notebook_rebase.py --continue                  the same, then continue the rebase, until it ends
                                                         or stops on something else
Exit status: 0 resolved, or the rebase finished; 3 a conflict needs a person; 4 git failed.
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ITEM = re.compile(r'\s*<li data-([\w-]+)="([^"]*)"')
ARTICLE = re.compile(r'\s*<article\b[^>]*\bid="([^"]+)"')
PARAGRAPH = re.compile(r"\s*<p><strong>([^<(:.]+)")


class Refused(Exception):
    """A conflict this tool does not merge, with why."""


def elements(lines):
    """[(key, the element's lines)] of `lines`, which must be whole elements one after another."""
    found, at = [], 0
    while at < len(lines):
        line = lines[at]
        if (item := ITEM.match(line)) and line.rstrip().endswith("</li>"):
            found.append((("item", *item.groups()), [line]))
            at += 1
        elif (paragraph := PARAGRAPH.match(line)) and line.rstrip().endswith("</p>"):
            found.append((("paragraph", paragraph.group(1).strip()), [line]))
            at += 1
        elif article := ARTICLE.match(line):
            end = next((index for index in range(at, len(lines)) if "</article>" in lines[index]), None)
            if end is None or any(ARTICLE.match(inner) for inner in lines[at+1:end+1]):
                raise Refused(f"an article that does not end inside the conflict: {line.strip()[:90]}")
            found.append((("article", article.group(1)), lines[at:end+1]))
            at = end+1
        else:
            raise Refused(f"no whole article, list item or labelled paragraph: {line.strip()[:90]}")
    keys = [key for key, _ in found]
    if len(set(keys)) != len(keys):
        raise Refused(f"an element twice on one side: {next(key for key in keys if keys.count(key) > 1)}")
    return found


def merged(ours, base, theirs):
    """The lines of one conflict merged element by element."""
    ours, base, theirs = elements(ours), dict(elements(base)), elements(theirs)
    has, gives = dict(ours), dict(theirs)
    result = []
    for key, mine in ours:
        if key not in gives:
            if key in base and base[key] != mine:
                raise Refused(f"changed on one side and removed on the other: {key}")
            # Removed by the other side where the base had it; kept where only this side has it.
            result += [] if key in base else mine
        elif gives[key] == mine or gives[key] == base.get(key):
            result += mine
        elif mine == base.get(key):
            result += gives[key]
        else:
            raise Refused(f"changed differently on both sides: {key}")
    for key, yours in theirs:
        if key in has:
            continue
        if key in base and base[key] != yours:
            raise Refused(f"changed on one side and removed on the other: {key}")
        result += [] if key in base else yours
    return result


def resolved(ours, base, theirs):
    """(the text of three versions of a notebook merged, how many conflicts were merged by element)."""
    with tempfile.TemporaryDirectory() as scratch:
        paths = []
        for name, text in (("ours", ours), ("base", base), ("theirs", theirs)):
            paths.append(Path(scratch)/name)
            paths[-1].write_text(text, encoding="utf-8")
        marked = subprocess.run(["git", "merge-file", "-p", "--diff3", "-L", "ours", "-L", "base", "-L", "theirs", *map(str, paths)],
                                capture_output=True, text=True)
    if marked.returncode < 0 or marked.returncode > 127:
        raise Refused(f"git merge-file failed: {marked.stderr.strip()}")
    result, sides, into, count = [], None, None, 0
    for line in marked.stdout.splitlines(keepends=True):
        mark = line.rstrip("\n")
        if mark == "<<<<<<< ours":
            sides = {"ours": [], "base": [], "theirs": []}
            into = "ours"
        elif sides is not None and mark == "||||||| base":
            into = "base"
        elif sides is not None and mark == "=======":
            into = "theirs"
        elif sides is not None and mark == ">>>>>>> theirs":
            result += merged(sides["ours"], sides["base"], sides["theirs"])
            sides, into, count = None, None, count+1
        elif sides is not None:
            sides[into].append(line)
        else:
            result.append(line)
    return "".join(result), count


def git(*arguments, check=True):
    done = subprocess.run(["git", *arguments], capture_output=True, text=True)
    if check and done.returncode:
        print(f"git {' '.join(arguments)}: {done.stderr.strip()}", file=sys.stderr)
        raise SystemExit(4)
    return done


def conflicted():
    return [name for name in git("diff", "--name-only", "--diff-filter=U").stdout.splitlines() if name]


def resolve(name):
    """Merge the conflicted notebook `name` from the three versions the index holds, and stage it."""
    versions = [git("show", f":{stage}:{name}").stdout for stage in (2, 1, 3)]
    text, count = resolved(*versions)
    Path(name).write_text(text, encoding="utf-8")
    git("add", "--", name)
    return count


def rebasing():
    return any(Path(git("rev-parse", "--git-path", name).stdout.strip()).is_dir() for name in ("rebase-merge", "rebase-apply"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--file", default="notebook.html", help="the notebook (default: notebook.html)")
    parser.add_argument("--continue", dest="carry_on", action="store_true", help="continue the rebase after each resolution, until it ends")
    options = parser.parse_args(argv)
    commits = merges = 0
    while True:
        names = conflicted()
        others = [name for name in names if name != options.file]
        if others:
            # The notebook is still merged by element, so that a tool for the other files (tools/claim_rebase.py
            # for the registry, which refuses while any other conflict remains) can run next: on 17 October 2026
            # a commit with a notebook and a registry conflict was refused by both tools in turn.
            where = git("log", "-1", "--format=%h %s", "REBASE_HEAD", check=False).stdout.strip()
            if options.file in names:
                try:
                    merges += resolve(options.file)
                except Refused as refused:
                    print(f"Stopped at {where}: {options.file} needs a person: {refused}")
                    break
                print(f"Resolved {merges} conflicts of {options.file} by element and staged it.")
            print(f"Stopped at {where}: conflicts for a person in {', '.join(others)}")
            break
        if names:
            try:
                merges += resolve(options.file)
            except Refused as refused:
                where = git("log", "-1", "--format=%h %s", "REBASE_HEAD", check=False).stdout.strip()
                print(f"Stopped at {where}: {options.file} needs a person: {refused}")
                break
            commits += 1
            if conflicted():
                print(f"{options.file} is still conflicted after its resolution was staged", file=sys.stderr)
                return 4
        if not options.carry_on:
            print(f"Resolved {merges} conflicts of {options.file} by element." if names else f"{options.file} has no conflict.")
            return 0
        if not rebasing():
            print(f"Rebase finished. Resolved {merges} conflicts of {options.file} by element in {commits} commits.")
            return 0
        carried = subprocess.run(["git", "-c", "core.editor=true", "rebase", "--continue"], capture_output=True, text=True)
        if carried.returncode and not conflicted() and rebasing():
            # Nothing left of the commit: the other side already has its change.
            if "nothing to commit" in carried.stdout+carried.stderr or "No changes" in carried.stdout+carried.stderr:
                print(f"Dropped, nothing left of it: {git('log', '-1', '--format=%h %s', 'REBASE_HEAD', check=False).stdout.strip()}")
                git("rebase", "--skip", check=False)
                continue
            print(f"git rebase --continue failed: {(carried.stderr or carried.stdout).strip()[-400:]}", file=sys.stderr)
            return 4
    print(f"Resolved {merges} conflicts of {options.file} by element in {commits} commits before that.")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
