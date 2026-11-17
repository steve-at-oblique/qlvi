# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
"""Check executable packaging, including SNL's real wrapper reader when supplied."""
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import runpy
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
wrap = runpy.run_path(str(ROOT / 'tools/package_qdos.py'))['wrap']


class PackageTests(unittest.TestCase):
    def test_build_preserves_code_and_exposes_executable_metadata(self):
        raw = (ROOT / 'build/qdos/elvis').read_bytes()
        packaged = (ROOT / 'build/dist/elvis').read_bytes()
        self.assertEqual(packaged[30:], raw)
        self.assertEqual(packaged, wrap(raw))
        self.assertEqual(packaged[21], 1)
        self.assertEqual(packaged[22:26], raw[-4:])
        self.assertNotIn(b'SIGNAL extension not loaded', raw)

    def test_rejects_data_files_and_double_wrapping(self):
        with self.assertRaises(ValueError):
            wrap(b'ordinary file' * 20)
        with self.assertRaises(ValueError):
            wrap((ROOT / 'build/dist/elvis').read_bytes())

    @unittest.skipUnless(os.environ.get('SNL_SERVER'), 'set SNL_SERVER for SNL integration')
    def test_actual_snl_reader(self):
        loader = importlib.machinery.SourceFileLoader('qlc_snl_test', os.environ['SNL_SERVER'])
        spec = importlib.util.spec_from_loader(loader.name, loader)
        snl = importlib.util.module_from_spec(spec)
        loader.exec_module(snl)
        raw = (ROOT / 'build/qdos/elvis').read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'elvis').write_bytes(wrap(raw))
            session = snl.Session({'4': directory})
            try:
                self.assertEqual(session.open('4', 1, b'elvis'), len(raw))
                header = session.read_header()
                self.assertEqual(header[5], 1)
                self.assertEqual(header[6:10], raw[-4:])
                self.assertEqual(struct.unpack('>I', header[:4])[0], len(raw))
                self.assertEqual(session.read(0, 64), raw[:64])
            finally:
                session.close()


if __name__ == '__main__':
    unittest.main()
