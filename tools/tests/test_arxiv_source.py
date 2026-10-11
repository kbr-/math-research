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

    def test_a_directory_inside_the_repository_is_refused(self):
        self.assertEqual(arxiv_source.repository_of(ROOT / 'research' / 'no-such-dir'), ROOT)
        self.assertEqual(arxiv_source.main(['arxiv_source.py', '1204.3057', '--out', str(ROOT / 'research/x')]), 1)
        self.assertEqual(arxiv_source.main(['arxiv_source.py', 'bad id;', '--out', '/tmp/x']), 1)


if __name__ == '__main__':
    unittest.main()
