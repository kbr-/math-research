import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'browser_get.cjs'
FIREFOX_MODULE = Path(__file__).resolve().parents[1] / 'browser_firefox.cjs'
NODE = shutil.which('node')
FIREFOX = shutil.which('firefox')
SEEN = []


class Site(http.server.BaseHTTPRequestHandler):
    """A page with a hidden and a visible download link (and an ad on another site with the same words) to
    a file behind a login cookie."""

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
            return self.answer(200, b'<html><title>Paper</title>'
                               b'<a href="https://ads.example.com/x">Download PDF now</a>'
                               b'<a style="display:none" href="/hidden.pdf">Download PDF</a>'
                               b'<a href="/paper.pdf">Download PDF</a></html>')
        if self.path == '/paper.pdf' and self.headers.get('Cookie') == 'session=yes':
            return self.answer(200, b'%PDF-1.4 test', 'application/octet-stream',
                               Content_Disposition='attachment; filename="paper.pdf"')
        return self.answer(403, b'<html><title>Verify you are human</title>captcha</html>')


PACING_MODULE = Path(__file__).resolve().parents[1] / 'browser_pacing.cjs'


def node(script, *args):
    """Run a few lines against the tool's exported functions, without a browser."""
    return subprocess.run([NODE, '-e', f'const t = require({json.dumps(str(TOOL))});\n'
                           f'const f = require({json.dumps(str(FIREFOX_MODULE))});\n'
                           f'const p = require({json.dumps(str(PACING_MODULE))});\n{script}', *args],
                          capture_output=True, text=True, timeout=10)


@unittest.skipUnless(NODE, 'node is not installed')
class BrowserGetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Site)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_usage_cookies_blockers_targets_and_challenge_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            cookies = Path(tmp) / 'c.json'
            # firefox_cookies.py saves Firefox's expiry, in milliseconds for recent profiles.
            cookies.write_text(json.dumps([{'name': 'a', 'value': 1, 'domain': '.x.org', 'path': '/',
                                            'expires': 1900000000000}]))
            store = Path(tmp) / '.cache' / 'browser-extensions'
            (store / 'uBOLite').mkdir(parents=True)
            (store / 'uBOLite' / 'manifest.json').write_text('{}')
            (store / 'uBlock0.firefox.signed.xpi').write_bytes(b'PK')
            done = node('''
const home = process.argv[2];
console.log(JSON.stringify([
  t.parse(['http://x.org/p']), t.parse(['http://x.org/p', '--out', 'f', '--bogus']),
  t.parse(['http://x.org/p', '--out', 'f', '--engine', 'lynx']),
  t.parse(['http://x.org/p', '--out', 'f', '--click', 'Get', '--headed']).engine,
  t.savedCookies({url: 'http://x.org/p', cookies: process.argv[1]}),
  t.savedCookies({url: 'http://x.org/p', noCookies: true}),
  t.blocker({engine: 'firefox'}, home).endsWith('uBlock0.firefox.signed.xpi'),
  t.blocker({engine: 'chromium'}, home).endsWith('uBOLite'),
  t.blocker({engine: 'firefox', noExtension: true}, home), t.blocker({engine: 'firefox'}, home + '/none'),
  t.pickTarget([{href: 'https://ads.example.com/x'}, {href: '/paper.pdf'}], 'www.researchgate.net'),
  t.pickTarget([{href: 'https://ads.example.com/x'}], 'x.org'), t.pickTarget([], 'x.org'),
  f.userJs('/d').includes('"pdfjs.disabled", true') && f.userJs('/d').includes('"browser.download.dir", "/d"'),
  t.isChallenge('ResearchGate - Temporarily Unavailable', ''), t.isChallenge('x', '<div>CAPTCHA</div>'),
  t.isChallenge('A paper on matchings', '<p>text</p>')]));''', str(cookies), tmp)
            self.assertEqual(done.returncode, 0, done.stderr)
            got = json.loads(done.stdout.strip().splitlines()[-1])
            self.assertEqual(got[:4], [None, None, None, 'firefox'])
            self.assertEqual(got[4], [{'name': 'a', 'value': '1', 'domain': '.x.org', 'path': '/',
                                       'expires': 1900000000}])
            self.assertEqual(got[5:], [[], True, True, None, None, 1, 0, -1, True, True, True, False])
        result = subprocess.run([NODE, str(TOOL), 'http://x.org'], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn('usage', result.stderr)

    def test_pacing_spaces_visits_to_a_site_and_caps_them_per_hour(self):
        with tempfile.TemporaryDirectory() as home:
            done = node('''
(async () => {
  const now = 100000;
  const out = [
    p.plan([], now), p.plan([now - 30], now), p.plan([now - 200], now),
    p.plan(Array.from({length: 10}, (_, i) => now - 3000 + i * 200), now).refuse !== undefined,
    p.plan([now - 3700], now), p.site('www.researchgate.net'), p.isLocal('127.0.0.1'), p.isLocal('arxiv.org')];
  // A local page is never paced; an outside one is recorded, and a second at once must wait.
  await p.beforeVisit('http://127.0.0.1:9/x', () => {}, process.argv[1]);
  await p.beforeVisit('https://www.example.org/a', () => {}, process.argv[1]);
  const fs = require('node:fs');
  const visits = JSON.parse(fs.readFileSync(process.argv[1] + '/.cache/browser-get/visits.json', 'utf8'));
  out.push(Object.keys(visits), p.plan(visits['example.org'], Date.now() / 1000).wait > 80);
  console.log(JSON.stringify(out));
})();''', home)
            self.assertEqual(done.returncode, 0, done.stderr)
            got = json.loads(done.stdout.strip().splitlines()[-1])
            self.assertEqual(got[0], {'wait': 0})
            self.assertEqual(got[1], {'wait': 60})
            self.assertEqual(got[2], {'wait': 0})
            self.assertEqual(got[3:], [True, {'wait': 0}, 'researchgate.net', True, False, ['example.org'], True])

    def download(self, engine):
        with tempfile.TemporaryDirectory() as tmp:
            cookies = Path(tmp) / 'cookies.json'
            cookies.write_text(json.dumps([{'name': 'session', 'value': 'yes', 'domain': '127.0.0.1',
                                            'path': '/', 'expires': 0}]))
            out = Path(tmp) / 'paper.pdf'
            result = subprocess.run(
                [NODE, str(TOOL), f'{self.base}/paper', '--out', str(out), '--click', 'Download PDF',
                 '--cookies', str(cookies), '--no-extension', '--engine', engine, '--timeout', '10'],
                capture_output=True, text=True, timeout=40)
            if 'cannot be loaded' in result.stderr:
                self.skipTest('Playwright is not available to node')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(out.read_bytes(), b'%PDF-1.4 test')
            self.assertIn('cookies: 1', result.stdout)
            self.assertIn('challenge page: no', result.stdout)
            self.assertIn('-> /paper.pdf', result.stdout)   # not the ad, not the hidden link
            self.assertIn(('/paper.pdf', 'session=yes'), SEEN)

    @unittest.skipUnless(FIREFOX, 'firefox is not installed')
    def test_firefox_clicks_the_visible_link_on_the_site_and_downloads_with_the_saved_cookies(self):
        self.download('firefox')

    # The fallback engine's end-to-end run costs a second browser launch, which pushed the whole suite past
    # its 10 s limit beside test_site's browser groups (16 October 2026); run it with BROWSER_GET_CHROMIUM=1
    # when the Chromium path changes.
    @unittest.skipUnless(os.environ.get('BROWSER_GET_CHROMIUM'), 'set BROWSER_GET_CHROMIUM=1 to run')
    def test_chromium_clicks_the_visible_link_on_the_site_and_downloads_with_the_saved_cookies(self):
        self.download('chromium')


if __name__ == '__main__':
    unittest.main()
