import gzip
import importlib.util
import io
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('arxiv_source', ROOT / 'tools/arxiv_source.py')
arxiv_source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arxiv_source)


def tar_of(files, links=()):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w') as archive:
        for name, text in files:
            info = tarfile.TarInfo(name)
            info.size = len(text)
            archive.addfile(info, io.BytesIO(text))
        for name, target in links:
            info = tarfile.TarInfo(name)
            info.type = tarfile.SYMTYPE
            info.linkname = target
            archive.addfile(info)
    return buffer.getvalue()


class UnpackTest(unittest.TestCase):
    def test_a_gzipped_tex_file_a_tar_archive_and_a_pdf(self):
        with tempfile.TemporaryDirectory() as scratch:
            out = Path(scratch)
            self.assertEqual(arxiv_source.unpack(gzip.compress(b'\\documentclass{article}'), out / 'a'), ['paper.tex'])
            self.assertEqual((out / 'a/paper.tex').read_bytes(), b'\\documentclass{article}')
            packed = gzip.compress(tar_of([('main.tex', b'x'), ('fig/a.txt', b'yy')]))
            self.assertEqual(sorted(arxiv_source.unpack(packed, out / 'b')), ['fig/a.txt', 'main.tex'])
            self.assertEqual((out / 'b/fig/a.txt').read_bytes(), b'yy')
            self.assertEqual(arxiv_source.unpack(b'%PDF-1.5 ...', out / 'c'), ['paper.pdf'])

    def test_members_leaving_the_directory_and_links_are_skipped(self):
        with tempfile.TemporaryDirectory() as scratch:
            out = Path(scratch) / 'd'
            packed = tar_of([('../escape.tex', b'x'), ('ok.tex', b'y')], links=[('link.tex', '/etc/passwd')])
            self.assertEqual(arxiv_source.unpack(packed, out), ['ok.tex'])
            self.assertFalse((Path(scratch) / 'escape.tex').exists())

    def test_the_fetched_title_and_authors_are_found_and_matched_against_expected_words(self):
        with tempfile.TemporaryDirectory() as scratch:
            out = Path(scratch)
            (out / 'main.tex').write_text('% \\title{Commented out}\n\\title[Short]{A quadratic large sieve\n'
                                          ' over \\textbf{number} fields}\n\\author{L. G.}\n\\author{B. L.}\n')
            (out / 'plain.tex').write_text('\n%only a comment\nFirst line.\nSecond.\nThird.\nFourth.\n')
            (out / 'fig.txt').write_text('\\title{not TeX}')
            found = arxiv_source.titles(out, ['main.tex', 'plain.tex', 'fig.txt'])
            self.assertEqual(found, [('main.tex', 'title', 'A quadratic large sieve over \\textbf{number} fields'),
                                     ('main.tex', 'author', 'L. G.'), ('main.tex', 'author', 'B. L.'),
                                     ('plain.tex', 'first lines', 'First line. | Second. | Third.')])
            self.assertTrue(arxiv_source.expected(found, ['Sieve']))
            self.assertFalse(arxiv_source.expected(found, ['graph', 'fidelity']))
            self.assertFalse(arxiv_source.expected(found, ['Second']))       # a title is asked, not a first line
            self.assertEqual(arxiv_source.titles(out, ['fig.txt']), [])
            # the AMS-TeX form, met on 12 October 2026 in a paper of 1998 whose title the tool did not find
            (out / 'ams.tex').write_text('\\topmatter\n\\title\nzeta and\n L-functions\n\\endtitle\n'
                                         '\\author\nJ. C. and X. L.\n\\endauthor\n')
            self.assertEqual(arxiv_source.titles(out, ['ams.tex']),
                             [('ams.tex', 'title', 'zeta and L-functions'), ('ams.tex', 'author', 'J. C. and X. L.')])

    def test_a_fetch_names_the_title_meant_and_a_wrong_paper_is_marked(self):
        import contextlib
        from unittest import mock
        payload = gzip.compress(b'\\title{Perfect state transfer}\n\\author{A. B.}\n')

        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        def run(*options):
            err = io.StringIO()
            with tempfile.TemporaryDirectory() as scratch, contextlib.redirect_stderr(err), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    mock.patch.object(arxiv_source.urllib.request, 'urlopen', lambda *a, **k: Response(payload)):
                out = Path(scratch) / 'p'
                status = arxiv_source.main(['arxiv_source.py', '1108.0339', '--out', str(out), *options])
                return status, err.getvalue(), (out / 'NOT-THE-PAPER-EXPECTED.txt').exists()
        self.assertEqual(run('--expect', 'sieve', 'quadratic')[::2], (3, True))
        self.assertIn('NOT THE PAPER EXPECTED', run('--expect', 'sieve')[1])
        self.assertEqual(run('--expect', 'transfer')[::2], (0, False))
        self.assertEqual(run('--unchecked', 'a payload without a title')[::2], (0, False))
        self.assertEqual(run()[0], 1)                                  # neither option: nothing is fetched
        self.assertEqual(run('--unchecked', 'because')[0], 1)
        self.assertEqual(run('--expect', 'a')[0], 1)                   # a word that matches nearly any title
        self.assertIn('Give --expect WORDS', run()[1])
        # a marker left by an earlier failed fetch into the directory is removed by a later fetch
        with tempfile.TemporaryDirectory() as scratch, contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()), \
                mock.patch.object(arxiv_source.urllib.request, 'urlopen', lambda *a, **k: Response(payload)):
            out = Path(scratch) / 'p'
            arxiv_source.main(['arxiv_source.py', '1108.0339', '--out', str(out), '--expect', 'sieve'])
            self.assertTrue((out / 'NOT-THE-PAPER-EXPECTED.txt').exists())
            arxiv_source.main(['arxiv_source.py', '1108.0339', '--out', str(out), '--expect', 'transfer'])
            self.assertFalse((out / 'NOT-THE-PAPER-EXPECTED.txt').exists())

    def test_a_directory_inside_the_repository_is_refused(self):
        self.assertEqual(arxiv_source.repository_of(ROOT / 'research' / 'no-such-dir'), ROOT)
        import contextlib
        for argv, said in ((['1204.3057', '--out', str(ROOT / 'research/x'), '--expect', 'sieve'],
                            'lies inside the repository'),
                           (['bad id;', '--out', '/tmp/x', '--expect', 'sieve'], 'Not an arXiv identifier')):
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(arxiv_source.main(['arxiv_source.py', *argv]), 1)
            self.assertIn(said, err.getvalue())                      # refused for this reason, not another


if __name__ == '__main__':
    unittest.main()
