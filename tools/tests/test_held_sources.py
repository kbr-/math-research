"""tools/held_sources.py: a source already held is listed before it is requested again."""
import contextlib
import io
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import held_sources  # noqa: E402


class HeldSources(unittest.TestCase):
    def run_tool(self, root, *words):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = held_sources.main([*words, "--root", str(root)])
        return status, out.getvalue()

    def checkout(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        root = pathlib.Path(scratch.name)
        (root / "private" / "deep").mkdir(parents=True)
        (root / "private" / "on-a-theorem-of-levinson.pdf").write_bytes(b"%PDF")
        (root / "private" / "deep" / "kiosk-ki2004.pdf").write_bytes(b"%PDF1")
        (root / "user_requests").write_text(
            "Request: H. Ki, On a theorem of Levinson.\n\nFulfilled: the sources were placed; Ki 2004 has a text"
            " layer.\n\nRequest: an unrelated book by Skinner; not fulfilled.\n")
        return root

    def test_held_file_and_request_are_listed(self):
        status, out = self.run_tool(self.checkout(), "levinson")
        self.assertEqual(status, 0)
        self.assertIn("1 of 2 held files and 1 request paragraphs match levinson", out)
        self.assertIn("on-a-theorem-of-levinson.pdf (4 bytes)", out)
        self.assertNotIn("kiosk", out)

    def test_file_in_a_subfolder_is_found(self):
        _, out = self.run_tool(self.checkout(), "kiosk")
        self.assertIn("kiosk-ki2004.pdf (5 bytes)", out)

    def test_short_word_matches_only_as_a_whole_word(self):
        _, out = self.run_tool(self.checkout(), "Ki")
        self.assertIn("0 of 2 held files and 2 request paragraphs match Ki", out)
        self.assertNotIn("Skinner", out)

    def test_fulfilment_note_is_marked_and_a_denial_is_not(self):
        _, out = self.run_tool(self.checkout(), "2004", "Skinner")
        self.assertIn("FULFILLED request: Fulfilled: the sources were placed", out)
        self.assertIn("\n  request: Request: an unrelated book by Skinner; not fulfilled.", out)

    def test_no_name_match_lists_every_held_file(self):
        _, out = self.run_tool(self.checkout(), "selberg")
        self.assertIn("0 of 2 held files and 0 request paragraphs match selberg", out)
        self.assertIn("no file name matches; every held file, to look through:", out)
        self.assertIn("on-a-theorem-of-levinson.pdf", out)
        self.assertIn("kiosk-ki2004.pdf", out)
        self.assertIn("not held: retrieve it with node tools/browser_get.cjs", out)


if __name__ == "__main__":
    unittest.main()
