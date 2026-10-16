"""tools/user_request.py appends a wrapped paragraph to the main checkout's user_requests."""
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('user_request', ROOT / 'tools/user_request.py')
ur = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ur)


class UserRequestTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        subprocess.run(['git', 'init', '-q', str(self.dir / 'main')], check=True)

    def test_path_is_beside_the_common_git_dir(self):
        self.assertEqual(ur.requests_path(self.dir / 'main'), (self.dir / 'main/user_requests').resolve())

    def test_add_appends_a_wrapped_paragraph_after_a_blank_line(self):
        path = self.dir / 'user_requests'
        path.write_text('First request.\n')
        ur.add(path, 'word ' * 60)
        text = path.read_text()
        self.assertTrue(text.startswith('First request.\n\nword word'))
        self.assertTrue(all(len(line) <= 100 for line in text.splitlines()))
        self.assertTrue(text.endswith('word\n'))

    def test_empty_text_is_refused(self):
        with self.assertRaises(SystemExit):
            ur.paragraph('   ')


if __name__ == '__main__':
    unittest.main()
