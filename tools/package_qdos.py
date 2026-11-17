#!/usr/bin/env python3
# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
"""Wrap a QDOS GCC executable for SNL/sQLux using its XTcc dataspace."""
import argparse
import struct
from pathlib import Path

MAGIC = b']!QDOS File Header'


def wrap(payload):
    if len(payload) < 56 or payload[-8:-4] != b'XTcc':
        raise ValueError('expected a QDOS GCC executable with an XTcc trailer')
    if payload[6:8] != b'\x4a\xfb':
        raise ValueError('missing QDOS job signature')
    dataspace = struct.unpack('>I', payload[-4:])[0]
    if not dataspace:
        raise ValueError('XTcc dataspace must be nonzero')
    header = MAGIC.ljust(18, b'\0') + struct.pack('>HBBII', 15, 0, 1, dataspace, 0)
    assert len(header) == 30
    return header + payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('input and output must be different files')
    try:
        result = wrap(args.input.read_bytes())
    except ValueError as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(result)
    print(f'{args.output}: {len(result)-30} payload bytes, '
          f'{struct.unpack(">I", result[22:26])[0]} dataspace, executable type 1')


if __name__ == '__main__':
    main()
