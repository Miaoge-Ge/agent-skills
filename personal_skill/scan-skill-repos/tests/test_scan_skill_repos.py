"""Offline regression tests: catalog selection, skill validation and API failures."""
from __future__ import annotations

import base64
import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
import scan_skill_repos as scan


def content(text):
    return {'content': base64.b64encode(text.encode('utf-8')).decode('ascii')}


def make_catalog(root, rows=True):
    directory = root / 'third_party_skill'
    directory.mkdir(parents=True)
    text = '## Skills\n\n| Skill | Description | Version | Stars |\n| --- | --- | --- | ---: |\n'
    if rows:
        text += '| [toolbox](https://github.com/sample/toolbox) | A skill | 1.2.3 | 100 |\n'
    for name in ('README.md', 'README.en.md'):
        (directory / name).write_text(text, encoding='utf-8')
    return root


class TestSkillValidation(unittest.TestCase):
    repo = {'full_name': 'sample/toolbox', 'default_branch': 'main'}
    valid = '---\nname: toolbox\ndescription: |\n  Do one useful thing.\nmetadata:\n  version: "0.1.0"\n---\nRead the input and verify the result.\n'

    def verify(self, text, path='personal_skill/toolbox/SKILL.md'):
        with mock.patch.object(scan, 'try_gh_json', return_value=content(text)):
            return scan.verify_skill(self.repo, path)

    def test_short_valid_skill_and_multiline_yaml(self):
        self.assertTrue(self.verify(self.valid))
        self.assertTrue(self.verify(self.valid, 'SKILL.md'))

    def test_container_name_is_not_a_format_rule(self):
        for path in ('SKILL.md', 'personal_skill/toolbox/SKILL.md', 'skills/toolbox/SKILL.md',
                     'plugins/sample/skills/toolbox/SKILL.md', 'docs/toolbox/SKILL.md'):
            with self.subTest(path=path):
                self.assertTrue(scan.is_skill_path(path))
                self.assertTrue(self.verify(self.valid, path))

    def test_invalid_paths_are_not_skill_files(self):
        for path in ('notes.md', 'SKILL.md.bak', 'skills/toolbox/skill.md', '../SKILL.md',
                     'skills/../SKILL.md', '/SKILL.md', 'skills//SKILL.md'):
            with self.subTest(path=path):
                self.assertFalse(scan.is_skill_path(path))

    def test_invalid_yaml_types_lengths_and_names_are_rejected(self):
        cases = [
            'name: []\ndescription: Good',
            'name: toolbox\ndescription: ""',
            'name: toolbox\ndescription: "   "',
            'name: toolbox\ndescription: 42',
            'name: Toolbox\ndescription: Good',
            'name: tool--box\ndescription: Good',
            'name: another-name\ndescription: Good',
            'name: toolbox\ndescription: [bad',
            'name: toolbox\ndescription: Good\nmetadata: []',
            'name: toolbox\ndescription: Good\nmetadata:\n  version: 1.2',
            'name: toolbox\ndescription: ' + 'x' * 1025,
            'name: toolbox\ndescription: "' + ' ' * 1024 + 'x"',
            'name: ' + 'x' * 65 + '\ndescription: Good',
        ]
        for frontmatter in cases:
            with self.subTest(frontmatter=frontmatter[:90]):
                self.assertFalse(self.verify('---\n' + frontmatter + '\n---\nUseful instruction.\n'))

    def test_body_and_complete_yaml_delimiter_are_required(self):
        self.assertFalse(self.verify('---\nname: toolbox\ndescription: Good\n---\n  \n'))
        self.assertFalse(self.verify('---\nname: toolbox\ndescription: Good\n---broken\nInstruction'))

    def test_missing_yaml_dependency_is_actionable(self):
        with mock.patch.object(scan, 'yaml', None):
            with self.assertRaisesRegex(RuntimeError, 'PyYAML'):
                scan.verify_skill(self.repo, 'SKILL.md')

    def test_invalid_first_result_does_not_hide_valid_skill(self):
        bad = 'docs/broken/SKILL.md'
        good = 'personal_skill/toolbox/SKILL.md'
        tree = {'tree': [{'path': bad, 'type': 'blob'}, {'path': good, 'type': 'blob'}]}

        def api(path):
            if '/git/trees/' in path:
                return tree
            return content(self.valid if good in path else '---\nname: []\n---\nInvalid.')

        with mock.patch.object(scan, 'try_gh_json', side_effect=api):
            repo = dict(self.repo, _skill_path=bad)
            self.assertEqual((True, good), scan.find_skill(repo, verify=True))

    def test_truncated_tree_is_reported(self):
        with mock.patch.object(scan, 'try_gh_json', return_value={'tree': [], 'truncated': True}):
            with self.assertRaisesRegex(RuntimeError, 'truncated'):
                scan.find_skill(self.repo, verify=True)


class TestVersionsAndApi(unittest.TestCase):
    def test_semver_suffixes_are_preserved(self):
        cases = {'v1.2.3-rc.1': '1.2.3-rc.1', 'plugin-v1.2.3-beta.2': '1.2.3-beta.2',
                 'v1.2.3+build.47': '1.2.3+build.47', 'tool@1.2.3-rc.1+build.9': '1.2.3-rc.1+build.9',
                 'shadcn@4.23.0': '4.23.0', '2026-11-14': '2026-11-14',
                 'release-beta.2': 'release-beta.2'}
        for tag, expected in cases.items():
            with self.subTest(tag=tag):
                self.assertEqual(expected, scan.normalize_tag(tag))

    def test_only_http_404_is_optional_absence(self):
        with mock.patch.object(scan, 'gh_json', side_effect=RuntimeError('Not Found (HTTP 404)')):
            self.assertIsNone(scan.try_gh_json('example'))
        for message in ('rate limit (HTTP 403)', 'server failure (HTTP 503)', 'not authenticated'):
            with mock.patch.object(scan, 'gh_json', side_effect=RuntimeError(message)):
                with self.assertRaises(RuntimeError):
                    scan.try_gh_json('example')

    def test_timeout_is_not_optional_absence(self):
        with mock.patch.object(scan, 'gh_json', side_effect=subprocess.TimeoutExpired('gh', 30)):
            with self.assertRaises(subprocess.TimeoutExpired):
                scan.try_gh_json('example')

    def test_release_absence_falls_back_to_tag(self):
        with mock.patch.object(scan, 'try_gh_json', side_effect=[None, [{'name': 'v1.2.3-beta.2'}]]) as api:
            self.assertEqual('1.2.3-beta.2', scan.resolve_version('sample/toolbox', 'main'))
            self.assertEqual(2, api.call_count)

    def test_all_absent_returns_no_version_not_unknown(self):
        with mock.patch.object(scan, 'try_gh_json', return_value=None):
            self.assertIsNone(scan.resolve_version('sample/toolbox', 'main'))

    def test_refresh_preserves_old_version_and_reports_failures(self):
        records = [{'repo': 'sample/toolbox', 'version': '1.2.3', 'stars': 100}]
        info = {'sample/toolbox': {'stargazers_count': 200, 'default_branch': 'main'}}
        for failure in (RuntimeError('HTTP 403'), OSError('connection failed'),
                        subprocess.TimeoutExpired('gh', 30), None):
            with self.subTest(failure=type(failure).__name__), \
                 mock.patch.object(scan, 'graphql_repo_metadata', return_value=info), \
                 mock.patch.object(scan, 'resolve_version', side_effect=failure, return_value=None), \
                 contextlib.redirect_stderr(io.StringIO()) as errors:
                updates = scan.refresh_metadata(records)
                self.assertEqual('1.2.3', updates['sample/toolbox']['version'])
                self.assertEqual(200, updates['sample/toolbox']['stars'])
                self.assertIn('version_error', updates['sample/toolbox'])
                self.assertIn('keeping version', errors.getvalue())

    def test_stars_only_does_not_call_version_api(self):
        records = [{'repo': 'sample/toolbox', 'version': '1.2.3', 'stars': 100}]
        with mock.patch.object(scan, 'graphql_repo_metadata', return_value={
                'sample/toolbox': {'stargazers_count': 200}}), \
             mock.patch.object(scan, 'resolve_version') as resolver:
            updates = scan.refresh_metadata(records, stars_only=True)
            resolver.assert_not_called()
            self.assertEqual('1.2.3', updates['sample/toolbox']['version'])


class TestCatalogSelectionAndRefresh(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory(prefix='skill-scan-test-')
        self.addCleanup(self.context.cleanup)
        self.temp = Path(self.context.name)
        self.repo = make_catalog(self.temp / 'catalog')
        self.root_patch = mock.patch.object(scan, 'ROOT', None)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def test_finds_target_from_cwd_not_skill_installation(self):
        child = self.repo / 'deep/child'
        child.mkdir(parents=True)
        with mock.patch.object(Path, 'cwd', return_value=child):
            self.assertEqual(self.repo / 'third_party_skill/README.md', scan.catalog_paths()[0])
            self.assertEqual({'sample/toolbox'}, scan.existing_repos())

    def test_missing_bilingual_catalog_fails(self):
        unrelated = self.temp / 'unrelated'
        unrelated.mkdir()
        with self.assertRaisesRegex(FileNotFoundError, '--repo'):
            scan.find_repo_root(unrelated)
        (self.repo / 'third_party_skill/README.en.md').unlink()
        with self.assertRaises(FileNotFoundError):
            scan.find_repo_root(self.repo)

    def test_installed_copy_runs_with_explicit_repo(self):
        empty = make_catalog(self.temp / 'empty', rows=False)
        installed = self.temp / 'installed/scan-skill-repos/scripts'
        installed.mkdir(parents=True)
        script = installed / 'scan_skill_repos.py'
        shutil.copyfile(SKILL / 'scripts/scan_skill_repos.py', script)
        result = subprocess.run([sys.executable, str(script), '--repo', str(empty), '--refresh-stars-only'],
                                cwd=installed, capture_output=True, text=True, timeout=20)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn('refreshed metadata for 0 repositories', result.stderr)

    def test_partial_version_failure_preserves_both_catalogs_and_returns_nonzero(self):
        info = {'sample/toolbox': {'stargazers_count': 250, 'default_branch': 'main'}}
        with mock.patch.object(scan, 'graphql_repo_metadata', return_value=info), \
             mock.patch.object(scan, 'resolve_version', side_effect=RuntimeError('HTTP 403')), \
             contextlib.redirect_stderr(io.StringIO()):
            status = scan.main(['--repo', str(self.repo), '--refresh', '--apply'])
        self.assertEqual(1, status)
        for name in ('README.md', 'README.en.md'):
            records = scan.catalog_records(self.repo / 'third_party_skill' / name)
            self.assertEqual([{'repo': 'sample/toolbox', 'version': '1.2.3', 'stars': 250}], records)

    def test_dry_run_does_not_write_catalogs(self):
        files = list((self.repo / 'third_party_skill').iterdir())
        before = {p: p.read_bytes() for p in files}
        with mock.patch.object(scan, 'refresh_metadata', return_value={
                'sample/toolbox': {'version': '9.0.0', 'stars': 999}}), \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(0, scan.main(['--repo', str(self.repo), '--refresh']))
        self.assertEqual(before, {p: p.read_bytes() for p in files})


if __name__ == '__main__':
    unittest.main()
