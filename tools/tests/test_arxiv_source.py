import gzip
import io
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import arxiv_source


class ManagedDestinationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root / '.gitignore').write_text('/research/tmp/\n')
        self.env = patch.dict(os.environ, {'CODEX_THREAD_ID': 'test-owner'}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.owned = arxiv_source.scratch_directory(self.root, 'test-owner')

    def test_owned_ignored_destination_and_protected_job_identity(self):
        out = self.owned / 'paper'
        self.assertEqual(arxiv_source.validate_destination(out), out)
        out.mkdir(parents=True)
        (out / 'regular.tex').write_text('ordinary source')
        (out / 'subdir').mkdir()
        # Unrelated tracked operands must not enter the scoped Git query.
        for name in ('XX-zXX', 'XX--XX'):
            unrelated = self.root / name
            unrelated.write_text('unrelated tracked file')
            subprocess.run(['git', '-C', str(self.root), 'add', '--', str(unrelated)], check=True)
        self.assertEqual(arxiv_source.validate_destination(out), out)
        with patch.dict(os.environ, {'MATH_CODEX_SCRATCH': str(self.owned)}, clear=True):
            self.assertEqual(arxiv_source.validate_destination(out), out)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'current Codex actor'):
                arxiv_source.validate_destination(out)
        other = arxiv_source.scratch_directory(self.root, 'other-owner') / 'paper'
        with self.assertRaisesRegex(ValueError, 'current Codex actor'):
            arxiv_source.validate_destination(other)
        with patch.dict(os.environ, {'MATH_CODEX_SCRATCH': str(self.root)}, clear=True):
            with self.assertRaisesRegex(ValueError, 'Invalid inherited'):
                arxiv_source.validate_destination(out)
        for invalid in (self.owned.parent / 'not-an-owner', self.root / self.owned.name):
            with patch.dict(os.environ, {'MATH_CODEX_SCRATCH': str(invalid)}, clear=True):
                with self.assertRaisesRegex(ValueError, 'Invalid inherited'):
                    arxiv_source.validate_destination(invalid / 'paper')
        # A native actor identity wins over an inherited parent path.
        with patch.dict(os.environ, {'MATH_CODEX_SCRATCH': str(other.parent)}):
            self.assertEqual(arxiv_source.validate_destination(out), out)

    def test_unignored_and_force_tracked_destinations_are_refused(self):
        out = self.owned / 'paper'
        (self.root / '.gitignore').write_text('')
        with self.assertRaisesRegex(ValueError, 'Git-ignored'):
            arxiv_source.validate_destination(out)
        # An unrelated ignored name must not satisfy the destination's ignore check.
        out.mkdir(parents=True)
        (self.root / '.gitignore').write_text('*\n!research/\n!research/**\n')
        with self.assertRaisesRegex(ValueError, 'Git-ignored'):
            arxiv_source.validate_destination(out)
        (self.root / '.gitignore').write_text('/research/tmp/\n')
        for name in ('paper', 'paper[1]'):
            out = self.owned / name
            out.mkdir(parents=True, exist_ok=True)
            tracked = out / 'already.tex'
            tracked.write_text('keep this file')
            subprocess.run(['git', '-C', str(self.root), 'add', '-f', '--', str(tracked)], check=True)
            with self.assertRaisesRegex(ValueError, 'tracked files'):
                arxiv_source.validate_destination(out)
            self.assertEqual(tracked.read_text(), 'keep this file')

    def test_links_and_traversal_are_refused_before_fetch(self):
        out = self.owned / 'paper'
        out.mkdir(parents=True)
        external = Path(self.tmp.name) / 'external'
        external.mkdir()
        victim = external / 'kept.tex'
        victim.write_text('keep this file')
        with self.assertRaisesRegex(ValueError, 'must be a directory'):
            arxiv_source.validate_destination(victim)
        link = out / 'link'
        for target in (victim, external):
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                arxiv_source.validate_destination(out)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                arxiv_source.validate_destination(link / 'child')
            link.unlink()
        os.link(victim, link)
        with self.assertRaisesRegex(ValueError, 'hard link'):
            arxiv_source.validate_destination(out)
        link.unlink()
        with self.assertRaisesRegex(ValueError, 'parent traversal'):
            arxiv_source.validate_destination(out / '..' / 'escape')
        out.rmdir()
        out.symlink_to(external)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            arxiv_source.validate_destination(out)
        self.assertEqual(victim.read_text(), 'keep this file')

    def test_nested_repository_is_not_a_source_destination(self):
        out = self.owned / 'paper'
        nested = out / 'nested'
        nested.mkdir(parents=True)
        subprocess.run(['git', 'init', '-q', str(nested)], check=True)
        tracked = nested / 'kept.tex'
        tracked.write_text('tracked by the nested repository')
        subprocess.run(['git', '-C', str(nested), 'add', 'kept.tex'], check=True)
        with self.assertRaisesRegex(ValueError, 'repository'):
            arxiv_source.validate_destination(out)
        self.assertEqual(tracked.read_text(), 'tracked by the nested repository')

    def test_git_metadata_destination_is_refused_before_fetch(self):
        import contextlib
        for out in (self.root / '.git', self.root / '.git' / 'source'):
            with self.subTest(out=out), self.assertRaisesRegex(ValueError, 'Git metadata'):
                arxiv_source.validate_destination(out)
            with patch.object(arxiv_source.urllib.request, 'urlopen',
                              side_effect=AssertionError('Git metadata reached network')) as fetch, \
                    contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(arxiv_source.main(['arxiv_source.py', '1210.0819v3',
                                                   '--out', str(out), '--expect', 'Persistence']), 1)
            fetch.assert_not_called()

    def test_cli_allows_owned_fetch_but_refuses_foreign_before_network(self):
        import contextlib
        payload = io.BytesIO(gzip.compress(b'\\title{Persistence modules}\n'))
        out = self.owned / 'paper'
        with patch.object(arxiv_source.urllib.request, 'urlopen', return_value=payload) as fetch, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(arxiv_source.main(['arxiv_source.py', '1210.0819v3', '--out', str(out),
                                               '--expect', 'Persistence']), 0)
        fetch.assert_called_once()
        self.assertIn('Persistence', (out / 'paper.tex').read_text())
        foreign = arxiv_source.scratch_directory(self.root, 'foreign') / 'paper'
        with patch.object(arxiv_source.urllib.request, 'urlopen',
                          side_effect=AssertionError('foreign destination reached network')) as fetch, \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(arxiv_source.main(['arxiv_source.py', '1210.0819v3', '--out', str(foreign),
                                               '--expect', 'Persistence']), 1)
        fetch.assert_not_called()


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
            packed = tar_of([('../escape.tex', b'x'), ('.git/config', b'git metadata'), ('ok.tex', b'y')],
                            links=[('link.tex', '/etc/passwd')])
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

    def test_a_title_set_by_hand_in_large_type_is_read_when_no_title_command_gives_one(self):
        with tempfile.TemporaryDirectory() as scratch:
            out = Path(scratch)
            (out / 'hand.tex').write_text('\\documentclass{article}\n'
                                          '\\renewcommand{\\section}{-.2ex 2.3ex plus .2ex \\large\\bf}\n'
                                          '\\begin{document}\n\\begin{center}\n'
                                          '{\\Large {\\bf  Li  Coefficients for Automorphic $L$-Functions}}\\\\\n'
                                          '{\\em J. C. L.} \\\\\n\\end{center}\n{\\Large A later heading}\n')
            found = arxiv_source.titles(out, ['hand.tex'])
            self.assertEqual(found, [('hand.tex', 'title', 'Li Coefficients for Automorphic L -Functions')])
            self.assertTrue(arxiv_source.expected(found, ['coefficients']))
            # a title that runs over lines to its line break, with an accent; a large line in a file that
            # begins no document (an included file, a macro file) is not a title
            (out / 'run.tex').write_text('\\begin{document}\n{\\Large\n On a theorem of Erd\\H{o}s\n'
                                         'and G\\"odel \\\\\n A. B.}\n')
            self.assertEqual(arxiv_source.titles(out, ['run.tex']),
                             [('run.tex', 'title', 'On a theorem of Erdos and Godel')])
            (out / 'inc.tex').write_text('{\\Large Macros and more}\nSecond line.\n')
            self.assertEqual(arxiv_source.titles(out, ['inc.tex']),
                             [('inc.tex', 'first lines', '{\\Large Macros and more} | Second line.')])
            # a title command wins, and large type far into the body or of one word is no title
            (out / 'cmd.tex').write_text('\\title{The real one}\n\\begin{document}\n{\\Large Not this one}\n')
            self.assertEqual(arxiv_source.titles(out, ['cmd.tex']), [('cmd.tex', 'title', 'The real one')])
            (out / 'far.tex').write_text('\\begin{document}\n\\begin{center}\n\\vspace{2ex}\n{\\Large Abstract}\n'
                                         + 'text\n' * 50 + '{\\Large Far down the body}\n')
            self.assertEqual(arxiv_source.titles(out, ['far.tex']),          # of the body, layout lines skipped
                             [('far.tex', 'first lines', 'Abstract | text | text')])

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
