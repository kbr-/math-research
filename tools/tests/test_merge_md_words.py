"""tools/merge_md_words.py: wrapped Markdown merged word by word."""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import merge_md_words as tool
import rewrap_md

WORDS = "Alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon phi chi psi omega."


def document(first, second="Second item stays as it is."):
    return rewrap_md.rewrap(f"# Rules\n\nIntro line.\n\n- {first}\n  - {second}\n\n| a  |  b |\n|----|----|\n\n```\nkept   as   is\n```\n\nEnd.\n", 40)


BASE = document(WORDS)


class MergeTest(unittest.TestCase):
    def test_two_changes_to_one_wrapped_item_both_land_and_the_item_is_rewrapped(self):
        # Each side's change reflows every later line of the item: by lines the two cannot be merged.
        ours = document(WORDS.replace("beta", "beta and a longer insertion of ours"))
        theirs = document(WORDS.replace("epsilon", "epsilon, changed by theirs,"))
        self.assertNotEqual(subprocess.run(["git", "merge-file", "-p", *self.files(ours, BASE, theirs)], capture_output=True).returncode, 0)
        text, conflicts = tool.merged(ours, BASE, theirs, 40)
        self.assertEqual(conflicts, 0)
        self.assertEqual(text, document(WORDS.replace("beta", "beta and a longer insertion of ours").replace("epsilon", "epsilon, changed by theirs,")))

    def files(self, *texts):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        paths = [Path(scratch.name)/str(number) for number in range(len(texts))]
        for path, text in zip(paths, texts):
            path.write_text(text)
        return map(str, paths)

    def test_a_new_item_and_a_changed_nested_item_keep_their_places_and_what_is_no_prose_stays_whole(self):
        ours = BASE.replace("- Alpha", "- A new item of ours.\n- Alpha")
        theirs = document(WORDS, "Second item, changed by theirs.")
        text, conflicts = tool.merged(ours, BASE, theirs, 40)
        self.assertEqual((text, conflicts), (document(WORDS, "Second item, changed by theirs.").replace("- Alpha", "- A new item of ours.\n- Alpha"), 0))
        self.assertIn("| a  |  b |\n|----|----|\n\n```\nkept   as   is\n```\n", text)

    def test_the_same_words_changed_on_both_sides_stay_a_conflict_around_those_words(self):
        text, conflicts = tool.merged(document(WORDS.replace("gamma", "OURS")), BASE, document(WORDS.replace("gamma", "THEIRS")), 40)
        self.assertEqual(conflicts, 1)
        self.assertIn("- Alpha beta\n<<<<<<< ours\nOURS\n=======\nTHEIRS\n>>>>>>> theirs\ndelta epsilon zeta", text)
        # Everything outside the conflict is whole, each paragraph a line.
        self.assertTrue(text.startswith("# Rules\n\nIntro line.\n\n") and text.endswith("  - Second item stays as it is.\n\n| a  |  b |\n|----|----|\n\n```\nkept   as   is\n```\n\nEnd.\n"))

    def test_a_text_is_taken_apart_and_put_back_unchanged(self):
        for text in (BASE, "", "one\n", "one", "- a\n\n\n- b\n", "```\n  code  here\n```"):
            unwrapped = rewrap_md.rewrap(text, tool.UNWRAPPED)
            self.assertEqual(tool.text_of(tool.tokens(unwrapped)), unwrapped)
        for text in ("a  b   c\n", "  two  spaces \n", "| a  |  b |\n"):
            self.assertEqual(tool.text_of(tool.tokens(text)), text)
        with self.assertRaisesRegex(ValueError, "reads as a conflict marker"):
            tool.merged("a\n\n=======\n\nb\n", "a\n", "a\n")


class CommandTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(scratch.name)
        self.git("init", "-q", "-b", "main")
        self.commit("base", BASE)
        self.git("checkout", "-q", "-b", "side")

    def git(self, *arguments):
        identity = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.org", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.org"}
        return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *arguments], capture_output=True, text=True, env={**os.environ, **identity})

    def commit(self, message, text):
        Path("RULES.md").write_text(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def conflict(self, ours, theirs):
        self.commit("theirs", theirs)
        self.git("checkout", "-q", "main")
        self.commit("ours", ours)
        self.assertNotEqual(self.git("merge", "side").returncode, 0)

    def run_tool(self, *arguments):
        said = io.StringIO()
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            status = tool.main(list(arguments))
        return status, said.getvalue()

    def test_a_conflicted_file_is_merged_and_staged(self):
        self.conflict(document(WORDS.replace("beta", "beta and more of ours")), document(WORDS.replace("omega.", "omega and more of theirs.")))
        self.assertEqual(self.run_tool("RULES.md"), (0, "RULES.md: merged word by word and rewrapped\n"))
        self.assertEqual(self.git("status", "--short").stdout, "M  RULES.md\n")
        self.assertIn("beta and more of ours", Path("RULES.md").read_text())
        self.assertIn("more of theirs.", Path("RULES.md").read_text())

    def driven(self):
        """Turn the driver on in this repository, as a clone does."""
        self.git("config", "merge.md-words.driver", f"{sys.executable} {Path(tool.__file__)} --driver %O %A %B 40")
        Path(".gitattributes").write_text("*.md merge=md-words\n")
        self.git("add", ".gitattributes")
        self.git("commit", "-q", "-m", "attributes")

    def test_as_git_s_merge_driver_a_merge_needs_no_second_step(self):
        self.git("checkout", "-q", "main")
        self.driven()
        self.git("checkout", "-q", "side")
        self.git("merge", "-q", "main")
        self.commit("theirs", document(WORDS.replace("omega.", "omega and more of theirs.")))
        self.git("checkout", "-q", "main")
        self.commit("ours", document(WORDS.replace("beta", "beta and more of ours")))
        self.assertEqual(self.git("merge", "side").returncode, 0)
        self.assertEqual(Path("RULES.md").read_text(), document(WORDS.replace("beta", "beta and more of ours").replace("omega.", "omega and more of theirs.")))

    def test_as_a_driver_a_conflict_left_fails_the_merge_and_a_file_not_kept_wrapped_is_merged_by_lines(self):
        scratch = Path(tempfile.mkdtemp(dir="."))
        files = [scratch/name for name in ("base", "ours", "theirs")]
        for path, text in zip(files, (BASE, document(WORDS.replace("gamma", "OURS")), document(WORDS.replace("gamma", "THEIRS")))):
            path.write_text(text)
        self.assertEqual(tool.main(["--driver", *map(str, files), "40"]), 1)
        self.assertIn("<<<<<<< ours\nOURS\n=======\nTHEIRS\n>>>>>>> theirs\n", files[1].read_text())
        # Ours in one long line a paragraph: rewrapping would change all of it, so git's line merge is used and kept.
        long = "One sentence that is far longer than the width a wrapped file has, " * 3
        for path, text in zip(files, (f"{long}\n\nEnd.\n", f"{long}\n\nEnd, ours.\n", f"Changed. {long}\n\nEnd.\n")):
            path.write_text(text)
        self.assertEqual(tool.main(["--driver", *map(str, files)]), 0)
        self.assertEqual(files[1].read_text(), f"Changed. {long}\n\nEnd, ours.\n")
        # And where that line merge leaves a conflict, the driver says so.
        for path, text in zip(files, (f"{long}\n\nEnd.\n", f"{long}\n\nEnd, ours.\n", f"{long}\n\nEnd, theirs.\n")):
            path.write_text(text)
        self.assertEqual(tool.main(["--driver", *map(str, files)]), 1)
        self.assertIn("<<<<<<< ours\nEnd, ours.\n", files[1].read_text())
        self.assertEqual(tool.main(["--driver", "one"]), 2)

    def test_a_file_with_a_conflict_left_is_written_and_not_staged_and_one_not_conflicted_is_refused(self):
        self.conflict(document(WORDS.replace("gamma", "OURS")), document(WORDS.replace("gamma", "THEIRS")))
        self.assertEqual(self.run_tool("RULES.md"), (
            3, "RULES.md: 1 conflicts left, each around the words both sides changed; its paragraphs are unwrapped\n"))
        self.assertEqual(self.git("status", "--short").stdout, "UU RULES.md\n")
        self.assertIn("<<<<<<< ours\nOURS\n=======\nTHEIRS\n>>>>>>> theirs\n", Path("RULES.md").read_text())
        status, said = self.run_tool("absent.md")
        self.assertEqual(status, 4)
        self.assertIn("absent.md: not a file both sides changed", said)


if __name__ == "__main__":
    unittest.main()
