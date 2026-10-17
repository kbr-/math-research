"""tools/notebook_rebase.py: a notebook's conflicts merged element by element, and what it refuses."""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import notebook_rebase as tool


def notebook(paragraphs, items, articles):
    return "".join([
        '<section id="where-we-stand">\n', *(f"  <p><strong>{label} ({state}).</strong> {text}</p>\n" for label, state, text in paragraphs), "</section>\n",
        '<section id="lead-queue">\n<ol>\n', *(f'<li data-build="{name}" data-source="s">{text}</li>\n' for name, text in items), "</ol>\n</section>\n",
        '<section id="record">\n', *(f'<article id="{name}" data-kind="task">\n<h3>{name}</h3>\n<p>{text}</p>\n</article>\n' for name, text in articles),
        "</section>\n"])


BASE = notebook([("alpha", "started", "a"), ("beta", "started", "b"), ("gamma", "done", "c")], [("one", "1")], [("entry-one", "first")])


class MergeTest(unittest.TestCase):
    def test_each_side_s_paragraphs_items_and_entries_are_all_kept_ours_first(self):
        # Ours rewrote two adjacent paragraphs and dropped a finished one; theirs rewrote the third between them; both
        # appended an item and an entry at the same place.
        ours = notebook([("alpha", "merged", "a2"), ("beta", "started", "b")], [("one", "1"), ("two", "2")], [("entry-one", "first"), ("entry-ours", "o")])
        theirs = notebook([("alpha", "started", "a"), ("beta", "building", "b2"), ("gamma", "done", "c")],
                          [("one", "1"), ("three", "3")], [("entry-one", "first"), ("entry-theirs", "t")])
        text, count = tool.resolved(ours, BASE, theirs)
        self.assertEqual(text, notebook([("alpha", "merged", "a2"), ("beta", "building", "b2")], [("one", "1"), ("two", "2"), ("three", "3")],
                                        [("entry-one", "first"), ("entry-ours", "o"), ("entry-theirs", "t")]))
        self.assertEqual(count, 3)

    def test_a_paragraph_the_replayed_side_removed_beside_one_ours_rewrote_is_gone(self):
        ours = notebook([("alpha", "merged", "a2"), ("beta", "started", "b"), ("gamma", "done", "c")], [("one", "1")], [("entry-one", "first")])
        theirs = notebook([("alpha", "started", "a"), ("gamma", "done", "c")], [("one", "1")], [("entry-one", "first")])
        self.assertEqual(tool.resolved(ours, BASE, theirs), (
            notebook([("alpha", "merged", "a2"), ("gamma", "done", "c")], [("one", "1")], [("entry-one", "first")]), 1))

    def test_a_notebook_with_no_conflict_comes_back_as_git_merges_it(self):
        theirs = BASE.replace("first", "second")
        self.assertEqual(tool.resolved(BASE, BASE, theirs), (theirs, 0))

    def test_what_nothing_says_how_to_merge_is_refused(self):
        def side(*paragraphs):
            return notebook(list(paragraphs), [("one", "1")], [("entry-one", "first")])
        both = (side(("alpha", "merged", "x"), ("beta", "started", "b"), ("gamma", "done", "c")),
                side(("alpha", "paused", "y"), ("beta", "started", "b"), ("gamma", "done", "c")))
        removed = (side(("beta", "started", "b"), ("gamma", "done", "c")), side(("alpha", "paused", "y"), ("beta", "started", "b"), ("gamma", "done", "c")))
        for (ours, theirs), reason in ((both, "changed differently on both sides: ('paragraph', 'alpha')"),
                                       (removed, "changed on one side and removed on the other: ('paragraph', 'alpha')"),
                                       (removed[::-1], "changed on one side and removed on the other: ('paragraph', 'alpha')")):
            with self.assertRaises(tool.Refused) as refused:
                tool.resolved(ours, BASE, theirs)
            self.assertEqual(str(refused.exception), reason)
        # Lines that are no whole element, as where both sides rewrote a paragraph of an entry.
        with self.assertRaises(tool.Refused) as refused:
            tool.resolved(BASE.replace("<p>first</p>", "<p>ours</p>"), BASE, BASE.replace("<p>first</p>", "<p>theirs</p>"))
        self.assertIn("no whole article, list item or labelled paragraph: <p>ours</p>", str(refused.exception))

    def test_an_element_is_whole_or_refused(self):
        entry = ['  <article class="research-entry" id="e" data-kind="task">\n', "<p>x</p>\n", "  </article>\n"]
        self.assertEqual(tool.elements([*entry, '<li data-check="c" data-source="s">q</li>\n', "  <p><strong>ALPHA-1 (a thing): open.</strong> t</p>\n"]),
                         [(("article", "e"), entry), (("item", "check", "c"), ['<li data-check="c" data-source="s">q</li>\n']),
                          (("paragraph", "ALPHA-1"), ["  <p><strong>ALPHA-1 (a thing): open.</strong> t</p>\n"])])
        for lines, reason in ((entry[:2], "an article that does not end inside the conflict"), ([*entry[:2], *entry], "an article that does not end inside the conflict"),
                              ([*entry, *entry], "an element twice on one side: ('article', 'e')"), (['<li data-check="c">q\n'], "no whole article"),
                              (["<p><strong>Label.</strong> two\n"], "no whole article")):
            with self.assertRaises(tool.Refused) as refused:
                tool.elements(lines)
            self.assertIn(reason, str(refused.exception))

    def test_an_identical_addition_on_both_sides_is_kept_once(self):
        both = notebook([("alpha", "started", "a"), ("beta", "started", "b"), ("gamma", "done", "c")], [("one", "1"), ("two", "2")], [("entry-one", "first")])
        ours = both.replace('<li data-build="two" data-source="s">2</li>\n', '<li data-build="two" data-source="s">2</li>\n<li data-build="mine" data-source="s">m</li>\n')
        theirs = both.replace('<li data-build="two" data-source="s">2</li>\n', '<li data-build="two" data-source="s">2</li>\n<li data-build="yours" data-source="s">y</li>\n')
        text, _ = tool.resolved(ours, BASE, theirs)
        self.assertEqual([line[16:line.index('"', 16)] for line in text.splitlines() if line.startswith("<li ")], ["one", "two", "mine", "yours"])


class RebaseTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.repository = Path(self.scratch.name)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.repository)
        self.git("init", "-q", "-b", "main")
        self.commit("base", BASE)

    def git(self, *arguments):
        environment = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.org", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.org"}
        return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *arguments], capture_output=True, text=True, env=environment)

    def commit(self, message, text, other=None):
        Path("notebook.html").write_text(text)
        if other is not None:
            Path("other.txt").write_text(other)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def run_tool(self, *arguments):
        said = io.StringIO()
        with contextlib.redirect_stdout(said):
            status = tool.main(list(arguments))
        return status, said.getvalue()

    def branches(self, theirs_other=None, ours_other=None):
        """`main` with an entry of its own, and `work` with two commits that each add an entry and rewrite a paragraph."""
        paragraphs = [("alpha", "started", "a"), ("beta", "started", "b"), ("gamma", "done", "c")]
        self.git("checkout", "-q", "-b", "work")
        first = notebook([paragraphs[0], ("beta", "building", "b2"), paragraphs[2]], [("one", "1")], [("entry-one", "first"), ("entry-work-1", "w1")])
        self.commit("work: first", first, ours_other)
        self.commit("work: second", notebook([paragraphs[0], ("beta", "built", "b3"), paragraphs[2]], [("one", "1")],
                                             [("entry-one", "first"), ("entry-work-1", "w1"), ("entry-work-2", "w2")]))
        self.git("checkout", "-q", "main")
        self.commit("main: more", notebook([("alpha", "merged", "a2"), paragraphs[1]], [("one", "1")], [("entry-one", "first"), ("entry-main", "m")]), theirs_other)
        self.git("checkout", "-q", "work")
        return self.git("rebase", "main")

    def test_a_rebase_is_carried_to_its_end_through_every_commit_s_notebook_conflict(self):
        self.assertNotEqual(self.branches().returncode, 0)
        status, said = self.run_tool("--continue")
        self.assertEqual((status, said), (0, "Rebase finished. Resolved 3 conflicts of notebook.html by element in 2 commits.\n"))
        self.assertEqual(Path("notebook.html").read_text(), notebook(
            [("alpha", "merged", "a2"), ("beta", "built", "b3")], [("one", "1")],
            [("entry-one", "first"), ("entry-main", "m"), ("entry-work-1", "w1"), ("entry-work-2", "w2")]))
        self.assertEqual(self.git("log", "--format=%s").stdout.split("\n")[:3], ["work: second", "work: first", "main: more"])
        self.assertEqual(self.git("status", "--short").stdout, "")

    def test_a_conflict_in_another_file_stops_it_with_the_notebook_merged_and_staged(self):
        # The other file's own tool (tools/claim_rebase.py) refuses while the notebook is conflicted, so the
        # notebook is merged first: on 17 October 2026 a notebook and a registry conflict were refused by each.
        self.branches(theirs_other="main\n", ours_other="work\n")
        status, said = self.run_tool("--continue")
        self.assertEqual(status, 3)
        self.assertRegex(said, r"^Resolved \d+ conflicts of notebook.html by element and staged it.\nStopped at \w+ work: first: conflicts for a person in other.txt\n")
        self.assertEqual(self.git("diff", "--name-only", "--diff-filter=U").stdout, "other.txt\n")
        Path("other.txt").write_text("work\n")
        self.git("add", "other.txt")
        status, said = self.run_tool("--continue")
        self.assertEqual(status, 0)
        self.assertEqual(self.git("status", "--short").stdout, "")

    def test_without_the_option_one_stop_is_resolved_and_staged_and_the_rebase_is_left_to_its_caller(self):
        self.branches()
        self.assertEqual(self.run_tool(), (0, "Resolved 2 conflicts of notebook.html by element.\n"))
        self.assertEqual(self.git("status", "--short").stdout, "M  notebook.html\n")
        self.assertTrue(tool.rebasing())
        self.assertEqual(self.run_tool(), (0, "notebook.html has no conflict.\n"))

    def test_a_refused_conflict_leaves_the_file_as_git_left_it(self):
        self.git("checkout", "-q", "-b", "work")
        self.commit("work: alpha", BASE.replace("alpha (started)", "alpha (paused)"))
        self.git("checkout", "-q", "main")
        self.commit("main: alpha", BASE.replace("alpha (started)", "alpha (merged)"))
        self.git("checkout", "-q", "work")
        self.git("rebase", "main")
        before = Path("notebook.html").read_text()
        status, said = self.run_tool("--continue")
        self.assertEqual(status, 3)
        self.assertIn("notebook.html needs a person: changed differently on both sides: ('paragraph', 'alpha')", said)
        self.assertEqual(Path("notebook.html").read_text(), before)
        self.assertIn("<<<<<<<", before)


if __name__ == "__main__":
    unittest.main()
