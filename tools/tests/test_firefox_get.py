import contextlib
import http.server
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import firefox_get  # noqa: E402

SEEN = []


class Site(http.server.BaseHTTPRequestHandler):
    """A site behind a login: it answers by the cookie it is sent and records each request."""

    def log_message(self, *args):
        pass

    def answer(self, status, body, kind='application/json', **headers):
        self.send_response(status)
        self.send_header('Content-Type', kind)
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        SEEN.append((self.command, self.path, self.headers.get('Cookie')))
        if self.path == '/moved':
            return self.answer(302, '', Location='/api/clients?page=2')
        if self.path == '/away':
            return self.answer(302, '', Location=f'http://localhost:{self.server.server_port}/api/clients')
        if self.headers.get('Cookie') != 'session.0=first; session.1=second':
            return self.answer(401, '{"error": "sign in"}')
        if self.path == '/admin':
            return self.answer(403, '{"error": "needs the admin role"}')
        if self.path == '/page':
            return self.answer(200, '<h1>żółw</h1>', kind='text/html; charset=utf-8')
        self.answer(200, json.dumps({'path': self.path, 'names': ['ż']}))


class FirefoxGetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Site)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.host = f'127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.home = Path(scratch.name)
        (self.home / '.cache').mkdir()
        self.saved = self.home / '.cache' / f'cookies-{self.host}.json'
        self.saved.write_text(json.dumps([{'name': 'session.0', 'value': 'first'}, {'name': 'session.1', 'value': 'second'}]))
        SEEN.clear()

    def run_tool(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = firefox_get.main([self.host, *argv, '--http'], home=self.home)
        return status, out.getvalue(), err.getvalue()

    def test_a_path_is_fetched_with_the_saved_cookies_and_its_json_printed(self):
        status, out, err = self.run_tool('api/clients?limit=2')
        self.assertEqual((status, json.loads(out)), (0, {'path': '/api/clients?limit=2', 'names': ['ż']}))
        self.assertIn('  "names": [\n    "ż"', out)                      # indented, its letters as they are
        self.assertEqual(err, f'GET http://{self.host}/api/clients?limit=2: 200 (application/json)\n')
        self.assertEqual(SEEN, [('GET', '/api/clients?limit=2', 'session.0=first; session.1=second')])
        self.assertNotIn('first', out + err)                               # no cookie value is printed
        # A leading slash is the same path; a page that is no JSON is printed as it came.
        self.assertEqual(self.run_tool('/api/clients?limit=2')[2], err)
        status, out, err = self.run_tool('page')
        self.assertEqual((status, out), (0, '<h1>żółw</h1>\n'))
        self.assertIn('200 (text/html; charset=utf-8)', err)

    def test_an_answer_that_is_no_success_exits_one_and_says_what_it_means(self):
        status, out, err = self.run_tool('admin')
        self.assertEqual((status, json.loads(out)), (1, {'error': 'needs the admin role'}))
        self.assertTrue(err.rstrip().endswith('403 (application/json): the signed-in account lacks the permission the answer names'))
        self.saved.write_text(json.dumps([{'name': 'session.0', 'value': 'stale'}]))
        status, out, err = self.run_tool('api/clients')
        self.assertEqual((status, json.loads(out)), (1, {'error': 'sign in'}))
        self.assertIn('401 (application/json): the session expired or the cookie names are wrong', err)
        # No saved cookies: nothing is sent. No server: the reason, and status 1.
        self.saved.unlink()
        SEEN.clear()
        status, out, err = self.run_tool('api/clients')
        self.assertEqual((status, out, SEEN), (1, '', []))
        self.assertIn(f'no cookies saved at {self.saved}', err)
        self.assertIn(f'tools/firefox_cookies.py {self.host}', err)
        other = self.home / 'other.json'
        other.write_text('[]')
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = firefox_get.main(['127.0.0.1:9', 'x', '--http', '--cookies', str(other), '--timeout', '2'], home=self.home)
        self.assertEqual((status, out.getvalue()), (1, ''))
        self.assertIn('GET http://127.0.0.1:9/x: no answer:', err.getvalue())

    def test_a_redirect_is_followed_within_the_host_and_never_to_another(self):
        status, out, _ = self.run_tool('moved')
        self.assertEqual((status, json.loads(out)['path']), (0, '/api/clients?page=2'))
        self.assertEqual([path for _, path, _ in SEEN], ['/moved', '/api/clients?page=2'])
        SEEN.clear()
        status, out, err = self.run_tool('away')
        self.assertEqual(status, 1)
        self.assertEqual([path for _, path, _ in SEEN], ['/away'])           # the cookies went nowhere else
        self.assertIn('302', err)
        self.assertIn('redirect to another host not followed: http://localhost:', out)

    def test_a_cookies_file_given_by_name_is_the_one_sent(self):
        other = self.home / 'other.json'
        other.write_text(json.dumps([{'name': 'session.0', 'value': 'first'}, {'name': 'session.1', 'value': 'second'}]))
        self.saved.write_text('[]')
        self.assertEqual(self.run_tool('api/x', '--cookies', str(other))[0], 0)
        self.assertEqual(self.run_tool('api/x')[0], 1)


if __name__ == '__main__':
    unittest.main()
