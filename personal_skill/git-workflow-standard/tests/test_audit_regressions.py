"""Behavioral regressions for the skill audit, using disposable local repos."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_test_utils import SCRIPTS, SKILL_ROOT, commit, git, head, init_repo, run_script, stage, temp_workspace, write

sys.path.insert(0, str(SCRIPTS))
import git_guard


class TestCredentialParsing(unittest.TestCase):
    def test_quoted_json_and_yaml_keys(self):
        for assignment in ('"password": "made-up-value-987"', "'api_key': 'made-up-value-987'",
                           'client_secret = "made-up-value-987"'):
            with self.subTest(assignment=assignment):
                findings = git_guard.scan_text('.', 'config.txt', assignment.encode(), [])
                self.assertIn('generic-credential', [f.code for f in findings])

    def test_environment_placeholder_still_allowed(self):
        text = '{"password": "${DATABASE_PASSWORD}"}'
        self.assertEqual([], git_guard.scan_text('.', 'config.json', text.encode(), []))

    def test_breaking_change_examples_pass_strict_linter(self):
        for path in (SKILL_ROOT / 'SKILL.md', SKILL_ROOT / 'references/commit-message.md'):
            blocks = re.findall(r'```[^\n]*\n(.*?)```', path.read_text(encoding='utf-8'), re.S)
            examples = [b for b in blocks if b.startswith('feat(') and 'BREAKING CHANGE:' in b]
            self.assertTrue(examples, path)
            for example in examples:
                result = run_script('commit_msg_lint.py', '--strict', '--stdin', stdin=example)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)


class TestRepositoryRegressions(unittest.TestCase):
    def setUp(self):
        self.context = temp_workspace()
        self.temp = self.context.__enter__()
        self.repo = init_repo(self.temp / 'repo')
        self.bundle = self.repo / '.git/hooks/git-standard'

    def tearDown(self):
        self.context.__exit__(None, None, None)

    def hooks(self, *args):
        return run_script('install_hooks.py', '--repo', str(self.repo), *args)

    def test_uninstall_without_manifest_preserves_unowned_directory(self):
        foreign = write(self.bundle / 'custom/note.txt', 'keep this\n')
        result = self.hooks('--uninstall')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('keep this\n', foreign.read_text())

    def test_uninstall_preserves_untracked_file_next_to_managed_scripts(self):
        self.assertEqual(0, self.hooks().returncode)
        foreign = write(self.bundle / 'other.txt', 'keep\n')
        self.assertEqual(0, self.hooks('--uninstall').returncode)
        self.assertTrue(foreign.exists())
        self.assertFalse((self.bundle / 'git_guard.py').exists())
        self.assertFalse((self.bundle / '.managed-files.json').exists())

    def test_uninstall_preserves_modified_managed_file(self):
        self.assertEqual(0, self.hooks().returncode)
        modified = write(self.bundle / 'git_guard.py', '# local customization\n')
        self.assertEqual(0, self.hooks('--uninstall').returncode)
        self.assertEqual('# local customization\n', modified.read_text())
        self.assertFalse((self.bundle / 'commit_msg_lint.py').exists())
        manifest = json.loads((self.bundle / '.managed-files.json').read_text())
        self.assertEqual(['git_guard.py'], list(manifest['files']))

    def test_reinstall_refuses_collision_then_force_preserves_backup(self):
        target = write(self.bundle / 'git_guard.py', '# not installed by this skill\n')
        self.assertEqual(2, self.hooks().returncode)
        self.assertEqual('# not installed by this skill\n', target.read_text())
        self.assertFalse((self.bundle / 'commit_msg_lint.py').exists())
        self.assertEqual(0, self.hooks('--force').returncode)
        backup = self.bundle / 'git_guard.py.bak'
        self.assertEqual('# not installed by this skill\n', backup.read_text())
        self.assertEqual(0, self.hooks('--uninstall').returncode)
        self.assertTrue(backup.exists())

    def test_invalid_manifest_leaves_hooks_and_other_files_intact(self):
        self.assertEqual(0, self.hooks().returncode)
        victim = write(self.repo / 'keep.txt', 'keep\n')
        write(self.bundle / '.managed-files.json', json.dumps({
            'owner': 'git-workflow-standard', 'files': {'../../../keep.txt': 'a' * 64}}))
        result = self.hooks('--uninstall')
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertTrue(victim.exists())
        self.assertTrue((self.repo / '.git/hooks/pre-commit').exists())

    def test_staged_json_credential_is_blocked_in_strict_mode(self):
        git(self.repo, 'switch', '-c', 'feat/test-credentials')
        write(self.repo / 'config.json', '{"password": "made-up-value-987"}\n')
        stage(self.repo, 'config.json')
        result = run_script('git_guard.py', '--repo', str(self.repo), '--staged', '--strict', '--json')
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn('generic-credential', [f['code'] for f in json.loads(result.stdout)['findings']])

    def test_staged_token_beyond_two_mib_is_detected(self):
        git(self.repo, 'switch', '-c', 'feat/test-large-text')
        padding = 'safe padding\n' * (2 * 1024 * 1024 // 13 + 1)
        token = 'ghp_' + 'aB1' * 12  # Deliberately synthetic, constructed only in the fixture.
        write(self.repo / 'large.txt', padding + token + '\n')
        stage(self.repo, 'large.txt')
        result = run_script('git_guard.py', '--repo', str(self.repo), '--staged', '--json')
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        findings = json.loads(result.stdout)['findings']
        self.assertIn('github-token', [f['code'] for f in findings])
        self.assertNotIn('large-file', [f['code'] for f in findings])

    def test_explicit_lease_rejects_peer_commit_even_after_fetch(self):
        remote = self.temp / 'remote.git'
        git(self.temp, 'init', '--bare', '-q', '--initial-branch=main', str(remote))
        write(self.repo / 'file.txt', 'initial\n')
        commit(self.repo, 'feat: initial', 'file.txt')
        git(self.repo, 'remote', 'add', 'origin', str(remote))
        git(self.repo, 'push', '-u', 'origin', 'main')
        git(self.repo, 'fetch', 'origin')
        expected = git(self.repo, 'rev-parse', 'refs/remotes/origin/main').stdout.strip()
        peer = self.temp / 'peer'
        git(self.temp, 'clone', '-q', str(remote), str(peer))
        git(peer, 'config', 'user.name', 'Peer')
        git(peer, 'config', 'user.email', 'peer@example.com')
        git(peer, 'config', 'commit.gpgsign', 'false')
        write(peer / 'peer.txt', 'peer change\n')
        commit(peer, 'feat: peer change', 'peer.txt')
        git(peer, 'push', 'origin', 'main')
        write(self.repo / 'file.txt', 'rewritten\n')
        stage(self.repo, 'file.txt')
        git(self.repo, 'commit', '--amend', '-q', '-m', 'feat: revised initial')
        git(self.repo, 'fetch', 'origin')  # Simulate a background fetch after review.
        divergence = git(self.repo, 'log', '--left-right', '--oneline', 'HEAD...origin/main').stdout
        self.assertIn('<', divergence)
        self.assertIn('>', divergence)
        pushed = git(self.repo, 'push', f'--force-with-lease=refs/heads/main:{expected}',
                     'origin', 'HEAD:refs/heads/main', check=False)
        self.assertNotEqual(0, pushed.returncode)
        self.assertEqual(head(peer), git(remote, 'rev-parse', 'refs/heads/main').stdout.strip())

    def test_stash_and_backup_branch_restore_index_worktree_and_untracked(self):
        write(self.repo / 'file.txt', 'initial\n')
        commit(self.repo, 'feat: initial', 'file.txt')
        write(self.repo / 'file.txt', 'committed\n')
        commit(self.repo, 'feat: second', 'file.txt')
        saved_head = head(self.repo)
        git(self.repo, 'branch', 'backup/before-reset')
        write(self.repo / 'file.txt', 'staged\n')
        stage(self.repo, 'file.txt')
        write(self.repo / 'file.txt', 'unstaged\n')
        write(self.repo / 'new.txt', 'untracked\n')
        git(self.repo, 'stash', 'push', '-u', '-m', 'before reset')
        stash = git(self.repo, 'rev-parse', 'stash@{0}').stdout.strip()
        git(self.repo, 'reset', '--hard', 'HEAD~1')
        git(self.repo, 'switch', 'backup/before-reset')
        git(self.repo, 'stash', 'apply', '--index', stash)
        self.assertEqual(saved_head, head(self.repo))
        self.assertEqual('staged\n', git(self.repo, 'show', ':file.txt').stdout)
        self.assertEqual('unstaged\n', (self.repo / 'file.txt').read_text())
        self.assertEqual('untracked\n', (self.repo / 'new.txt').read_text())


if __name__ == '__main__':
    unittest.main()
