import io
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import register_codex as registry


class CodexRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root/'skills/example/SKILL.md'
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text('A single authoritative skill')

    def test_relative_links_are_idempotent_and_use_present_sources(self):
        source = self.root/'skills/Capital-Skill'
        source.mkdir();(source/'SKILL.md').write_text('another source')
        result = registry.register(self.root)
        self.assertEqual(result, {'skills': 2, 'changed': 2})
        link = self.root/'.agents/skills/example'
        self.assertEqual(os.readlink(link), '../../skills/example')
        self.assertEqual((link/'SKILL.md').read_text(), self.skill.read_text())
        self.assertTrue((self.root/'.agents/skills/Capital-Skill').is_symlink())
        self.assertEqual(registry.register(self.root)['changed'], 0)
        (self.root/'skills/zebra').mkdir()
        (self.root/'skills/zebra/SKILL.md').write_text('added after unchanged links')
        self.assertEqual(registry.register(self.root), {'skills': 3, 'changed': 1})
        self.assertTrue((self.root/'.agents/skills/zebra/SKILL.md').is_file())
        self.skill.write_text('Updated authoritative source')
        self.assertEqual((link/'SKILL.md').read_text(), 'Updated authoritative source')

    def test_removed_sources_and_unmanaged_edits(self):
        registry.register(self.root)
        self.skill.unlink()
        self.assertEqual(registry.register(self.root), {'skills': 0, 'changed': 1})
        self.assertFalse((self.root/'.agents/skills/example').is_symlink())
        self.skill.write_text('Restored source')
        registry.register(self.root)
        link = self.root/'.agents/skills/example';link.unlink();link.write_text('user-owned edit')
        another = self.root/'skills/another';another.mkdir();(another/'SKILL.md').write_text('new source')
        with self.assertRaisesRegex(ValueError, 'preserved'):
            registry.register(self.root)
        self.assertEqual(link.read_text(), 'user-owned edit')
        self.assertFalse((self.root/'.agents/skills/another').exists())

    def test_rejects_invalid_names_paths_and_directories(self):
        bad = self.root/'skills/invalid name';bad.mkdir();(bad/'SKILL.md').write_text('bad')
        with self.assertRaisesRegex(ValueError, 'Invalid skill'):
            registry.register(self.root)
        shutil.rmtree(bad)
        base = self.root/'.codex/framework'
        (base/'registrations.json').write_text(json.dumps({'../../outside': {'link': 'x'}}))
        with self.assertRaisesRegex(ValueError, 'Invalid managed'):
            registry.register(self.root)
        with self.assertRaises(ValueError):
            registry.target_path(self.root, '.agents/skills/../../other')
        with self.assertRaisesRegex(ValueError, 'not a file/link'):
            registry.contents(self.skill.parent)

    def test_parallel_registration_and_cli_reports(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(registry.register, [self.root, self.root]))
        self.assertEqual(sorted(r['changed'] for r in results), [0, 1])
        with patch.object(registry, 'ROOT', self.root), redirect_stdout(io.StringIO()) as stream:
            self.assertEqual(registry.main(), 0)
        self.assertEqual(json.loads(stream.getvalue()), {'skills': 1, 'changed': 0})
        link = self.root/'.agents/skills/example';link.unlink();link.write_text('edited')
        with patch.object(registry, 'ROOT', self.root), redirect_stderr(io.StringIO()) as stream:
            self.assertEqual(registry.main(), 1)
        self.assertIn('preserved', stream.getvalue())

    def test_recovery_before_manifest_write(self):
        registry.register(self.root)
        (self.root/'.codex/framework/registrations.json').unlink()
        self.assertEqual(registry.register(self.root), {'skills': 1, 'changed': 0})
        (self.root/'.agents/skills/example').unlink()
        self.assertEqual(registry.register(self.root)['changed'], 1)

    def test_symlinked_ancestors_cannot_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside)
            (self.root/'.agents').symlink_to(external, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'escapes'):
                registry.register(self.root)
            self.assertEqual(list(external.iterdir()), [])
            (self.root/'.agents').unlink();shutil.rmtree(self.root/'.codex')
            (self.root/'.codex').symlink_to(external, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'escapes'):
                registry.register(self.root)
            self.assertEqual(list(external.iterdir()), [])
            (self.root/'.codex').unlink()
            directory = self.root/'.codex/framework';directory.mkdir(parents=True)
            (directory/'registrations.json').symlink_to(external/'manifest')
            with self.assertRaisesRegex(ValueError, 'manifest'):
                registry.register(self.root)
            self.assertFalse((external/'manifest').exists())

    def test_portability_accepts_only_canonical_skill_descriptors(self):
        spec = importlib.util.spec_from_file_location('verify_checkout_skills', ROOT/'tools/verify-checkout.py')
        checker = importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
        registry.register(self.root)
        name = '.agents/skills/example'
        self.assertTrue(checker.skill_descriptor(self.root, name))
        link = self.root/name;link.unlink();link.symlink_to(self.skill.parent)
        self.assertFalse(checker.skill_descriptor(self.root, name))
        link.unlink();link.write_text('not a descriptor')
        self.assertFalse(checker.skill_descriptor(self.root, name))
        self.assertFalse(checker.skill_descriptor(self.root, '.agents/runtime.json'))
        link.unlink();link.symlink_to('../../skills/missing')
        self.assertFalse(checker.skill_descriptor(self.root, name))
        link.unlink();link.symlink_to('../../skills/example');self.skill.unlink()
        self.assertFalse(checker.skill_descriptor(self.root, name))

    def test_atomic_link_location_and_failed_write_are_verified(self):
        original = registry.tempfile.mkstemp
        def local_temporary(*args, **kwargs):
            self.assertIsNotNone(kwargs.get('dir'))
            self.assertTrue(Path(kwargs['dir']).resolve().is_relative_to(self.root))
            return original(*args, **kwargs)
        replace = Path.replace
        def lose_link(path, target):
            if target.name == 'example':
                path.unlink()
                return target
            return replace(path, target)
        with patch.object(registry.tempfile, 'mkstemp', side_effect=local_temporary), \
             patch.object(Path, 'replace', lose_link):
            with self.assertRaisesRegex(ValueError, 'did not persist'):
                registry.register(self.root)
        self.assertEqual(registry.register(self.root)['changed'], 1)
        self.assertEqual(registry.register(self.root)['changed'], 0)


if __name__ == '__main__':
    unittest.main()
