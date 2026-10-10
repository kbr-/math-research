from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rewrap_md  # noqa: E402

NESTED = """\
- **Is it a question?** first line
  continues here
  - a sub-item
    with its continuation
  - another sub-item
- the next top item
"""


class RewrapMdTest(unittest.TestCase):
    def test_frontmatter_passes_through_and_the_prose_after_it_wraps(self):
        text = ("---\nname: skill\ndescription: Use when a description is long enough to pass the width.\n---\n\n"
                "A sentence\nlong enough to wrap here.\n")
        self.assertEqual(rewrap_md.rewrap(text, width=40),
                         "---\nname: skill\ndescription: Use when a description is long enough to pass the width.\n"
                         "---\n\nA sentence long enough to wrap here.\n")

    def test_trailer_lines_stay_on_their_own_lines(self):
        text = "Note: a sentence\nlong enough to wrap here.\n\nRefs: https://x.example/A-1\nRefs: https://x.example/A-2\n"
        self.assertEqual(rewrap_md.rewrap(text, width=40),
                         "Note: a sentence long enough to wrap\nhere.\n\nRefs: https://x.example/A-1\nRefs: https://x.example/A-2\n")

    def test_changed_keeps_what_the_committed_version_holds(self):
        base = ("An uneven\nparagraph kept as it is.\n\n- an uneven\n  item kept\n- an item to\nedit\n\nTo edit\n\n"
                "So cut\nshort.\n")
        # The last paragraph loses its first word: what remains is inside the old one, but not its lines.
        edited = (base.replace("to\nedit", "to\nedit, now longer").replace("To edit", "To edit, now longer")
                  .replace("So cut", "cut"))
        expected = ("An uneven\nparagraph kept as it is.\n\n- an uneven\n  item kept\n- an item to edit,\n  now longer\n\n"
                    "To edit, now\nlonger\n\ncut short.\n")
        self.assertEqual(rewrap_md.rewrap(edited, width=18, base=base), expected)
        self.assertEqual(rewrap_md.rewrap_section("# H\n" + edited, "H", width=18, base=base), "# H\n" + expected)
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        (root / "doc.md").write_text(base)
        for command in (["init", "-q"], ["add", "doc.md"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"]):
            subprocess.run(["git", *command], cwd=root, check=True)
        (root / "doc.md").write_text(edited)
        (root / "new.md").write_text(edited)
        for name in ("doc.md", "new.md"):
            self.assertEqual(rewrap_md.main([str(root / name), "--width", "18", "--changed"]), 0)
        self.assertEqual((root / "doc.md").read_text(), expected)
        self.assertEqual((root / "new.md").read_text(), rewrap_md.rewrap(edited, width=18))
        self.assertNotEqual(rewrap_md.rewrap(edited, width=18), expected)

    def test_nested_items_stay_items_with_hanging_indents(self):
        self.assertEqual(rewrap_md.rewrap(NESTED, width=40), """\
- **Is it a question?** first line
  continues here
  - a sub-item with its continuation
  - another sub-item
- the next top item
""")

    def test_long_items_wrap_under_their_text(self):
        text = "- " + "word " * 20 + "\n  1. " + "deep " * 12 + "\n"
        lines = rewrap_md.rewrap(text, width=30).splitlines()
        self.assertTrue(all(len(line) <= 30 for line in lines))
        self.assertEqual([line[:5] for line in lines[:2]], ["- wor", "  wor"])
        numbered = [i for i, line in enumerate(lines) if line.startswith("  1. ")]
        self.assertEqual(len(numbered), 1)
        self.assertTrue(all(line.startswith("     deep") for line in lines[numbered[0] + 1:]))

    def test_no_line_starts_with_a_word_that_opens_a_block(self):
        # Each marker sits where a 20-column wrap would otherwise start a line with it.
        for marker in ("-", "*", "+", "12.", "3)", "#", ">"):
            with self.subTest(marker=marker):
                # "  Engineering Group" is 19 columns, so a plain wrap starts the next line with it.
                text = f"- The group Engineering Group {marker} Org holds it, and more words follow.\n"
                lines = rewrap_md.rewrap(text, width=20).splitlines()
                self.assertEqual(lines[:2], ["- The group", "  Engineering"])
                self.assertTrue(lines[2].startswith(f"  Group {marker} "), lines)
                self.assertFalse([line for line in lines[1:] if line.lstrip().startswith(marker + " ")])
                self.assertEqual(rewrap_md.rewrap("\n".join(lines) + "\n", width=20), "\n".join(lines) + "\n")

    def test_rewrapping_twice_changes_nothing(self):
        text = "Para " + "word " * 40 + "\n\n" + NESTED
        once = rewrap_md.rewrap(text, width=50)
        self.assertEqual(rewrap_md.rewrap(once, width=50), once)

    def test_headings_tables_blank_lines_and_code_pass_through(self):
        text = "# Title\n\n| column one | column two |\n|---|---|\n\n```\n- not   an item\n  kept   as is\n```\npara\n"
        self.assertEqual(rewrap_md.rewrap(text, width=10), text)

    def test_a_long_word_is_never_broken(self):
        url = "https://example.com/" + "x" * 80
        self.assertEqual(rewrap_md.rewrap(f"see {url} here", width=30), f"see\n{url}\nhere")

    def test_only_the_named_section_is_rewrapped(self):
        text = "# Doc\n\n## Theory\n\nshort\nlines\n\n### Sub\n\njoined\ntoo\n\n## Path\n\nkept\nas is\n"
        self.assertEqual(rewrap_md.rewrap_section(text, "Theory"),
                         "# Doc\n\n## Theory\n\nshort lines\n\n### Sub\n\njoined too\n\n## Path\n\nkept\nas is\n")

    def test_an_unknown_section_fails_and_leaves_the_file(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        path = root / "plan.md"
        path.write_text("## Path\n\na\nb\n")
        self.assertEqual(rewrap_md.main([str(path), "--section", "Theory"]), 1)
        self.assertEqual(path.read_text(), "## Path\n\na\nb\n")
        self.assertEqual(rewrap_md.main([str(path), "--section", "Path"]), 0)
        self.assertEqual(path.read_text(), "## Path\n\na b\n")


if __name__ == "__main__":
    unittest.main()
