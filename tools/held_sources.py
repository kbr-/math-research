#!/usr/bin/env python3
"""List the sources already held on this machine that match the given words.

Run before a retrieval is called failed or a request for a source is filed
(AGENTS.md, publication rules): it prints the files of the main checkout's
private folder whose names hold one of the words, and the paragraphs of the
user's request file that hold one of them, each marked when it says Fulfilled.
A word of fewer than four letters matches only as a whole word. Matching is by
file name, not by a file's content, so when no name matches every held file is
listed to be looked through.
"""
import argparse
import pathlib
import re
import subprocess
import sys
import time


def main_checkout():
    """The main checkout's root, from any worktree."""
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True, check=True).stdout.strip()
    return pathlib.Path(common).parent


def matcher(words):
    """A test of a text for any of WORDS: short words as whole words, longer ones anywhere."""
    patterns = [re.compile(rf"(?<![a-z0-9]){re.escape(word.lower())}(?![a-z0-9])" if len(word) < 4
                           else re.escape(word.lower())) for word in words]
    return lambda text: any(pattern.search(text.lower()) for pattern in patterns)


def held(root, words):
    """All files of ROOT/private, those whose names match, and matching paragraphs of ROOT/user_requests."""
    matches = matcher(words)
    private = root / "private"
    every = sorted(path for path in private.rglob("*") if path.is_file()) if private.is_dir() else []
    files = [path for path in every if matches(path.name)]
    paragraphs = []
    requests = root / "user_requests"
    if requests.is_file():
        for paragraph in re.split(r"\n\s*\n", requests.read_text(errors="replace")):
            if matches(paragraph):
                paragraphs.append(paragraph.strip())
    return every, files, paragraphs


def fulfilled(paragraph):
    """Whether PARAGRAPH reports a fulfilment, and not that something is not fulfilled."""
    low = paragraph.lower()
    return "fulfilled" in re.sub(r"\b(?:not|un)\W*fulfilled", "", low)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("words", nargs="+", help="author, title word or file-name word")
    parser.add_argument("--root", type=pathlib.Path, help="main checkout (default: found through git)")
    args = parser.parse_args(argv)
    started = time.monotonic()
    root = args.root or main_checkout()
    every, files, paragraphs = held(root, args.words)
    print(f"{len(files)} of {len(every)} held files and {len(paragraphs)} request paragraphs match "
          f"{' '.join(args.words)} under {root}, in {time.monotonic() - started:.2f} s")
    if not files and every:
        print("  no file name matches; every held file, to look through:")
    for path in files or every:
        print(f"  held: {path} ({path.stat().st_size} bytes)")
    for paragraph in paragraphs:
        mark = "FULFILLED " if fulfilled(paragraph) else ""
        print(f"  {mark}request: {' '.join(paragraph.split())[:300]}")
    if not files:
        # Where retrieval starts, the tool for it: a source refusing curl may serve a browser.
        print("  not held: retrieve it with node tools/browser_get.cjs URL --out FILE [--click TEXT] "
              "(Firefox with the user's session and an ad blocker, paced like a person) before filing a request")
    return 0


if __name__ == "__main__":
    sys.exit(main())
