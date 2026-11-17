# qlvi — ELVIS for QDOS, built with GCC

A working Sinclair QL port of Steve Kirkendall's ELVIS 1.6, updated by Steve
Jennen from Dave Walker's original QDOS port. It supports editing files over
SNL and provides a resident SuperBASIC `VI` command. Terminal definitions are
built in: no TERM/TERMINFO setup or external terminfo file is required.

```sh
make -j4
make package
```

Requires the QDOS GCC toolchain, including its assembler, linker and curses
library, on PATH. Packages are written to `build/dist/`. Copy `elvis` and
`vi_rext` to the host directory served as SNL drive 4, then on the QL:

```basic
LRESPR snl4_vi_rext
DATA_USE snl4_
VI error_txt
```

Load the resident extension once per boot. The packaged executable includes
its QDOS metadata in a wrapper supported by SNL; no SEXEC conversion is needed.

## Layout

| Directory | Contents |
| --- | --- |
| `src/` | Active ELVIS and helper-program C sources |
| `src/qdos/` | Resident SuperBASIC VI launcher |
| `include/` | Project headers |
| `tools/` | Executable packaging tool |
| `tests/` | Command editing, terminal profile, packaging and 68000 launcher checks |
| `examples/` | Hello-world and read-only SNL file-access programs |
| `docs/` | Build, setup and port details |
| `docs/original/` | Supplied manuals, old boot example and terminal data |
| `legacy/` | Unused platform sources, original build files and supplied binaries |
| `licenses/` | Preserved upstream licensing statements |
| `build/` | Generated files; excluded from Git |

See [QDOS build and usage](docs/qdos.md) and [licensing and credits](THIRD_PARTY.md).
The original build scripts in `legacy/build/` are historical references, not
maintained entry points for the new directory layout. `make -f Makefile.qdos`
remains available as a compatibility alias for `make`.

## Verification

```sh
make test
```

The optional assembled-launcher test requires Python's `unicorn` package:

```sh
make test-launcher
```

Real QL testing has confirmed read/edit/save/reopen over SNL, command-line
cursor editing, fast G/1G navigation, and the resident VI command with
DATA_USE. New builds should still be checked on the target QL.

## License

Copyright (c) 2026 Steve Jennen, for original additions and copyrightable
modifications, under [BSD 2-Clause](LICENSE). Original ELVIS and third-party
terms remain in force. The tree is **not exclusively BSD-licensed**.
Read [THIRD_PARTY.md](THIRD_PARTY.md)
before redistributing, particularly for commercial use or binary releases.
