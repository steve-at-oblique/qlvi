# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
"""Check release-candidate ordering and the generated build header."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
version = runpy.run_path(str(ROOT / 'tools/version.py'))


class VersionTests(unittest.TestCase):
    def test_candidate_then_release_order(self):
        values = ['0.1.0-rc1', '0.1.0-rc2', '0.1.0-rc10', '0.1.0',
                  '0.1.1-rc1', '0.1.1', '0.2.0-rc1', '1.0.0']
        keys = [version['version_key'](value) for value in values]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(len(keys), len(set(keys)))

    def test_invalid_versions(self):
        for value in ['', '1.6', '0.01.0', '0.1.0-rc0', '0.1.0-rc02',
                      '0.1.0-dev', '0.1.0\nunsafe']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                version['validate'](value)

    def test_header_matches_source(self):
        current = (ROOT / 'VERSION').read_text().strip()
        with tempfile.TemporaryDirectory() as directory:
            header = Path(directory) / 'qlvi_version.h'
            subprocess.run(['python3', str(ROOT / 'tools/version.py'), 'header',
                            str(header)], check=True)
            self.assertIn(f'#define QLVI_VERSION "{current}"', header.read_text())


if __name__ == '__main__':
    unittest.main()
