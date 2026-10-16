import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import firefox_cookies as fc  # noqa: E402

HOST = 'app.example.ts.net'


class FirefoxCookiesTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.db = self.root / 'cookies.sqlite'
        connection = sqlite3.connect(self.db)
        connection.execute('CREATE TABLE moz_cookies (name, value, host, path, expiry)')
        connection.executemany('INSERT INTO moz_cookies VALUES (?, ?, ?, ?, ?)', [
            ('session.0', 'first-half', HOST, '/', 1),
            ('session.1', 'second', HOST, '/', 1),
            ('theme', 'dark', HOST, '/', 1),
            ('session', 'shared', '.' + HOST, '/', 1),
            ('session', 'other-site', 'example.com', '/', 1),
            ('session_like', 'x', 'evil' + HOST, '/', 1),
            ('clearance', 'parent', '.example.ts.net', '/', 1),
        ])
        connection.commit()
        connection.close()

    def run_tool(self, *args):
        out = self.root / 'out.json'
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
            code = fc.main([HOST, '--db', str(self.db), '--out', str(out), *args])
        return code, out, stdout.getvalue()

    def test_keeps_every_chunk_of_one_host_and_prefix_only(self):
        code, out, printed = self.run_tool('--prefix', 'session')
        self.assertEqual(code, 0)
        names = [c['name'] for c in json.loads(out.read_text())]
        self.assertEqual(names, ['session', 'session.0', 'session.1'])
        self.assertEqual(out.stat().st_mode & 0o777, 0o600)

    def test_never_prints_a_value(self):
        _, _, printed = self.run_tool('--prefix', 'session')
        for value in ('first-half', 'second', 'shared'):
            self.assertNotIn(value, printed)
        self.assertIn('session.0: 10 characters', printed)

    def test_without_prefix_takes_the_host_cookies_only(self):
        _, out, _ = self.run_tool()
        values = sorted(c['value'] for c in json.loads(out.read_text()))
        self.assertEqual(values, ['dark', 'first-half', 'second', 'shared'])

    def test_site_adds_the_parent_domains_cookies_and_no_others(self):
        _, out, _ = self.run_tool('--site')
        values = sorted(c['value'] for c in json.loads(out.read_text()))
        self.assertEqual(values, ['dark', 'first-half', 'parent', 'second', 'shared'])
        self.assertEqual(fc.site_hosts('www.researchgate.net'), ['www.researchgate.net', 'researchgate.net'])

    def test_fails_when_nothing_matches(self):
        code, out, _ = self.run_tool('--prefix', 'missing')
        self.assertEqual(code, 1)
        self.assertFalse(out.exists())

    def test_prefix_wildcards_are_literal(self):
        _, out, _ = self.run_tool('--prefix', 'session_')
        self.assertFalse(out.exists())

    def test_writes_every_field_into_a_new_directory(self):
        out = self.root / 'new' / 'dir' / 'out.json'
        with contextlib.redirect_stdout(io.StringIO()):
            code = fc.main([HOST, '--db', str(self.db), '--out', str(out), '--prefix', 'session.0'])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.read_text()), [
            {'name': 'session.0', 'value': 'first-half', 'domain': HOST, 'path': '/', 'expires': 1}])

    def test_reads_a_cookie_still_in_the_write_ahead_log(self):
        # A running Firefox keeps recent writes in cookies.sqlite-wal until a checkpoint, so a
        # just-made login exists only there.
        writer = sqlite3.connect(self.db)
        self.addCleanup(writer.close)
        writer.execute('PRAGMA journal_mode=WAL')
        writer.execute('PRAGMA wal_autocheckpoint=0')
        writer.execute("INSERT INTO moz_cookies VALUES ('fresh', 'new-login', ?, '/', 1)", (HOST,))
        writer.commit()
        self.assertTrue(Path(str(self.db) + '-wal').stat().st_size > 0)
        _, out, _ = self.run_tool('--prefix', 'fresh')
        self.assertEqual([c['value'] for c in json.loads(out.read_text())], ['new-login'])

    def test_defaults_to_the_newest_profile_and_a_private_cache_file(self):
        home = self.root / 'home'
        older = home / '.mozilla/firefox/old.default/cookies.sqlite'
        newer = home / '.config/mozilla/firefox/new.default-release/cookies.sqlite'
        for db in (older, newer):
            db.parent.mkdir(parents=True)
            shutil.copy(self.db, db)
        connection = sqlite3.connect(older)
        connection.execute("UPDATE moz_cookies SET value = 'stale' WHERE name = 'session.0'")
        connection.commit()
        connection.close()
        os.utime(older, (1, 1))
        with mock.patch.object(fc.Path, 'home', return_value=home), \
                contextlib.redirect_stdout(io.StringIO()):
            code = fc.main([HOST, '--prefix', 'session.0'])
        out = home / '.cache' / f'cookies-{HOST}.json'
        self.assertEqual(code, 0)
        self.assertEqual([c['value'] for c in json.loads(out.read_text())], ['first-half'])
        self.assertEqual(out.stat().st_mode & 0o777, 0o600)

    def test_no_profile_found_stops_with_a_message(self):
        with self.assertRaises(SystemExit) as stopped:
            fc.find_db(self.root / 'empty-home')
        self.assertIn('no Firefox cookies.sqlite found', str(stopped.exception))


if __name__ == '__main__':
    unittest.main()
