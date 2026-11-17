#!/usr/bin/env python3
# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
"""Validate qlvi's VERSION, generate its C header, or set the next version."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-rc([1-9][0-9]*))?')


def validate(value):
    if not PATTERN.fullmatch(value):
        raise ValueError('use MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-rcN')
    return value


def read_version():
    return validate((ROOT / 'VERSION').read_text().strip())


def version_key(value):
    match = PATTERN.fullmatch(validate(value))
    major, minor, patch, candidate = match.groups()
    return (int(major), int(minor), int(patch), candidate is None,
            int(candidate or 0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('show')
    header = commands.add_parser('header')
    header.add_argument('output', type=Path)
    change = commands.add_parser('set')
    change.add_argument('version')
    args = parser.parse_args()
    try:
        current = read_version()
        if args.command == 'show':
            print(current)
        elif args.command == 'header':
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text('/* Generated from VERSION; do not edit. */\n'
                                   '#ifndef QLVI_VERSION_H\n#define QLVI_VERSION_H\n'
                                   f'#define QLVI_VERSION "{current}"\n#endif\n')
        else:
            next_version = validate(args.version)
            if version_key(next_version) <= version_key(current):
                parser.error('the next version must be newer than the current version')
            (ROOT / 'VERSION').write_text(next_version + '\n')
            print(f'{current} -> {next_version}; update CHANGELOG.md before committing')
    except ValueError as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
