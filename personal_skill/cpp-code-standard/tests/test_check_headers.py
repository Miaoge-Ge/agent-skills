"""Header checker regressions and compiled tests of the documented C++ example."""
from __future__ import annotations

import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
import check_headers as checker

HEADER = '/** @file sample.hpp\n * @brief Sample header. */\n'


class TestHeaderChecks(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory(prefix='cpp-header-test-')
        self.addCleanup(self.context.cleanup)
        self.root = Path(self.context.name)
        self.path = self.root / 'sample.hpp'

    def check(self, body, strict=False):
        self.path.write_text(HEADER + body, encoding='utf-8')
        return checker.check_file(self.path, strict)

    def test_pragma_once_and_matching_guard(self):
        for body in ('#pragma once\n', '#ifndef SAMPLE_HPP\n#define SAMPLE_HPP\n#endif\n',
                     '#ifndef SAMPLE_HPP\n#define SAMPLE_HPP\n#if FEATURE\n#endif\n#endif\n'):
            with self.subTest(body=body):
                self.assertEqual([], self.check(body))

    def test_mismatched_incomplete_and_non_enclosing_guards(self):
        for body in ('#ifndef SAMPLE_HPP\n#define WRONG_HPP\n#endif\n',
                     '#ifndef SAMPLE_HPP\n#define SAMPLE_HPP\n',
                     '#ifndef SAMPLE_HPP\n#define SAMPLE_HPP\n#endif\nint outside;\n'):
            with self.subTest(body=body):
                self.assertIn('HDR001', [p[1] for p in self.check(body)])

    def test_fake_pragma_in_comments_and_raw_strings_is_ignored(self):
        body = '// #pragma once\nconst char* text = R"x(\n#pragma once\n)x";\n'
        self.assertIn('HDR001', [p[1] for p in self.check(body)])

    def test_namespace_directive_inside_comments_or_strings_is_ignored(self):
        body = '#pragma once\n// using namespace std;\nconst char* text = "using namespace std;";\n'
        self.assertEqual([], self.check(body))
        self.assertIn('NS001', [p[1] for p in self.check(body + 'using namespace std;\n')])

    def test_file_brief_does_not_document_function(self):
        problems = self.check('#pragma once\nint undocumented();\n', strict=True)
        self.assertEqual(['DOC003'], [p[1] for p in problems])
        self.assertIn('undocumented', problems[0][2])

    def test_one_documented_function_does_not_hide_other_missing_comment(self):
        body = '#pragma once\n/** @brief Documented. */\nint documented();\nint missing();\n'
        problems = self.check(body, strict=True)
        self.assertEqual(1, len(problems))
        self.assertIn('missing', problems[0][2])
        self.assertEqual(6, problems[0][0])

    def test_documented_multiline_members_and_definitions(self):
        body = '''#pragma once
class Service
{
public:
    /** @brief Construct. */
    explicit Service(int count) : m_count(count) {}
    /** @brief Read the value. */
    int value(
        int fallback = 0) const noexcept
    {
        if (m_count) { return m_count; }
        return fallback;
    }
    /** @brief Implement in subclass. */
    virtual void execute() = 0;
private:
    int m_count;
};
'''
        self.assertEqual([], self.check(body, strict=True))

    def test_missing_member_is_reported(self):
        problems = self.check('#pragma once\nclass Service { public: void execute(); };\n', strict=True)
        self.assertEqual(['DOC003'], [p[1] for p in problems])

    def test_file_header_must_be_a_real_leading_comment(self):
        self.path.write_text('#pragma once\nconst char* fake = "/** @file x @brief y */";\n', encoding='utf-8')
        codes = [p[1] for p in checker.check_file(self.path, False)]
        self.assertEqual(['DOC001', 'DOC002'], codes)

    def test_mixed_valid_and_missing_input_is_failure(self):
        self.check('#pragma once\n')
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(2, checker.main([str(self.path), str(self.root / 'missing.hpp')]))

    def test_invalid_utf8_and_empty_directory_are_failures(self):
        self.path.write_bytes(b'\xff\xfeinvalid')
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(2, checker.main([str(self.path)]))
        self.path.unlink()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(1, checker.main([str(self.root)]))


class TestDocumentedFileProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++') or shutil.which('clang++')
        if not compiler:
            raise unittest.SkipTest('g++/clang++ is required to compile the C++17 documentation example')
        cls.context = tempfile.TemporaryDirectory(prefix='cpp-example-test-')
        cls.addClassCleanup(cls.context.cleanup)
        cls.root = Path(cls.context.name)
        reference = (SKILL / 'references/modern-cpp.md').read_text(encoding='utf-8')
        blocks = re.findall(r'```cpp\n(.*?)```', reference, re.S)
        if len(blocks) != 1:
            raise AssertionError('Expected the complete FileProcessor example')
        cls.header = cls.root / 'file_processor.hpp'
        cls.header.write_text(blocks[0], encoding='utf-8')
        harness = cls.root / 'main.cpp'
        harness.write_text(r'''
#include "file_processor.hpp"
#include <iostream>

int main(int argc, char** argv)
{
    if (argc != 2) return 10;
    std::string mode = argv[1];
    try
    {
        if (mode == "prefix")
        {
            std::string storage = "path.bin-other";
            FileProcessor reader(std::string_view(storage.data(), 8));
            return reader.readAll() == "requested" ? 0 : 1;
        }
        if (mode == "nonterminated")
        {
            const char storage[8] = {'p', 'a', 't', 'h', '.', 'b', 'i', 'n'};
            FileProcessor reader(std::string_view(storage, sizeof(storage)));
            return reader.readAll() == "requested" ? 0 : 2;
        }
        if (mode == "nul")
        {
            std::string storage("path.bin\0other", 14);
            try { FileProcessor reader(storage); }
            catch (const std::invalid_argument&) { return 0; }
            return 3;
        }
        if (mode == "missing")
        {
            try { FileProcessor reader("does-not-exist.bin"); }
            catch (const std::runtime_error&) { return 0; }
            return 4;
        }
        if (mode == "binary")
        {
            FileProcessor reader("binary.bin");
            std::string expected(9000, 'x');
            expected[2] = '\0';
            expected[4096] = '\0';
            return reader.readAll() == expected ? 0 : 5;
        }
        if (mode == "empty")
        {
            FileProcessor reader("empty.bin");
            return reader.readAll().empty() ? 0 : 6;
        }
    }
    catch (const std::exception& error)
    {
        std::cerr << error.what();
        return 11;
    }
    return 12;
}
''', encoding='utf-8')
        cls.exe = cls.root / ('example.exe' if os.name == 'nt' else 'example')
        cls.env = dict(os.environ, PATH=str(Path(compiler).parent) + os.pathsep + os.environ.get('PATH', ''))
        built = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror', str(harness), '-o', str(cls.exe)],
                               capture_output=True, text=True, env=cls.env, timeout=60)
        if built.returncode:
            raise AssertionError(built.stdout + built.stderr)
        (cls.root / 'path.bin').write_bytes(b'requested')
        (cls.root / 'path.bin-other').write_bytes(b'wrong file')
        binary = bytearray(b'x' * 9000)
        binary[2] = binary[4096] = 0
        (cls.root / 'binary.bin').write_bytes(binary)
        (cls.root / 'empty.bin').write_bytes(b'')

    def run_example(self, mode):
        result = subprocess.run([str(self.exe), mode], cwd=self.root, env=self.env,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(0, result.returncode, f'{mode}: {result.stdout}{result.stderr}')

    def test_example_passes_its_own_strict_checker(self):
        self.assertEqual([], checker.check_file(self.header, strict=True))

    def test_string_view_length_selects_requested_file(self):
        self.run_example('prefix')

    def test_nonterminated_view_is_safe(self):
        self.run_example('nonterminated')

    def test_embedded_nul_is_rejected(self):
        self.run_example('nul')

    def test_open_failure_is_reported(self):
        self.run_example('missing')

    def test_binary_data_across_multiple_chunks_is_preserved(self):
        self.run_example('binary')

    def test_empty_file_is_read(self):
        self.run_example('empty')


if __name__ == '__main__':
    unittest.main()
