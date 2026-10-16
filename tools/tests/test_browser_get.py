import http.server
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'browser_get.cjs'
NODE = shutil.which('node')
SEEN = []


class Site(http.server.BaseHTTPRequestHandler):
    """A page with a download link to a file behind a login cookie."""

    def log_message(self, *args):
        pass

    def answer(self, status, body, kind='text/html', **headers):
        self.send_response(status)
        self.send_header('Content-Type', kind)
        for name, value in headers.items():
            self.send_header(name.replace('_', '-'), value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        SEEN.append((self.path, self.headers.get('Cookie')))
        if self.path == '/paper':
            return self.answer(200, b'<html><title>Paper</title><a href="/paper.pdf">Download PDF</a></html>')
        if self.path == '/paper.pdf' and self.headers.get('Cookie') == 'session=yes':
            return self.answer(200, b'%PDF-1.4 test', 'application/pdf',
                               Content_Disposition='attachment; filename="paper.pdf"')
        return self.answer(403, b'<html><title>Verify you are human</title>captcha</html>')


def node(script, *args):
    """Run a few lines against the tool's exported functions, without a browser."""
    return subprocess.run([NODE, '-e', f'const t = require({json.dumps(str(TOOL))});\n{script}', *args],
                          capture_output=True, text=True, timeout=10)


@unittest.skipUnless(NODE, 'node is not installed')
class BrowserGetTest(unittest.TestCase):
    def test_usage_cookies_and_challenge_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            cookies = Path(tmp) / 'c.json'
            # firefox_cookies.py saves Firefox's expiry, in milliseconds for recent profiles.
            cookies.write_text(json.dumps([{'name': 'a', 'value': 1, 'domain': '.x.org', 'path': '/',
                                            'expires': 1900000000000}]))
            done = node('''
console.log(JSON.stringify([
  t.parse(['http://x.org/p']), t.parse(['http://x.org/p', '--out', 'f', '--bogus']),
  t.parse(['http://x.org/p', '--out', 'f', '--click', 'Get', '--headed']).click,
  t.savedCookies({url: 'http://x.org/p', cookies: process.argv[1]}),
  t.savedCookies({url: 'http://x.org/p', noCookies: true}),
  t.isChallenge('ResearchGate - Temporarily Unavailable', ''), t.isChallenge('x', '<div>CAPTCHA</div>'),
  t.isChallenge('A paper on matchings', '<p>text</p>')]));''', str(cookies))
            self.assertEqual(done.returncode, 0, done.stderr)
            got = json.loads(done.stdout.strip().splitlines()[-1])
            self.assertEqual(got[:3], [None, None, 'Get'])
            self.assertEqual(got[3], [{'name': 'a', 'value': '1', 'domain': '.x.org', 'path': '/',
                                       'expires': 1900000000}])
            self.assertEqual(got[4:], [[], True, True, False])
        result = subprocess.run([NODE, str(TOOL), 'http://x.org'], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn('usage', result.stderr)

    def test_a_click_downloads_the_file_with_the_saved_cookies(self):
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Site)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                cookies = Path(tmp) / 'cookies.json'
                cookies.write_text(json.dumps([{'name': 'session', 'value': 'yes', 'domain': '127.0.0.1',
                                                'path': '/', 'expires': 0}]))
                out = Path(tmp) / 'paper.pdf'
                result = subprocess.run(
                    [NODE, str(TOOL), f'http://127.0.0.1:{server.server_port}/paper', '--out', str(out),
                     '--click', 'Download PDF', '--cookies', str(cookies), '--timeout', '10'],
                    capture_output=True, text=True, timeout=30)
                if 'cannot be loaded' in result.stderr:
                    self.skipTest('Playwright is not available to node')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(out.read_bytes(), b'%PDF-1.4 test')
                self.assertIn('cookies: 1', result.stdout)
                self.assertIn('challenge page: no', result.stdout)
                self.assertIn(('/paper.pdf', 'session=yes'), SEEN)
        finally:
            server.shutdown()


if __name__ == '__main__':
    unittest.main()
