# qlvi — ELVIS for QDOS, built with GCC

A working Sinclair QL port of Steve Kirkendall's ELVIS 1.6, updated by Steve
Jennen from Dave Walker's original QDOS port. It supports editing files over
SNL and provides a resident SuperBASIC `VI` command. Terminal definitions are
built in: no TERM/TERMINFO setup or external terminfo file is required.
Working storage defaults to RAM1_; if it is unavailable, qlvi prompts for
a writable alternative such as WIN1_ or SNL1_.

## Ready-built download

Download the repository ZIP using GitHub's Code menu. The `bin/` directory
contains ready-built `elvis` and `vi_rext`; no compiler is needed.
See [bin/README.md](bin/README.md) for installation over SNL.

## Building from source

```sh
make -j4
make package
```

Requires the QDOS GCC toolchain, including its assembler, linker and curses
library, on PATH. Packages are written to `build/dist/`. Copy `elvis` and
`vi_rext` to the host directory served as SNL drive 4, then on the QL:

```basic
LRESPR snl4_vi_rext
VI_USE "snl4_elvis"
DATA_USE snl4_
VI error_txt
```

On Minerva without the Pointer Environment, press **Ctrl+C** after `VI error_txt`
to select the editor's console if input remains with SuperBASIC. See the
[Minerva notes](docs/minerva.md#selecting-the-editor-console).

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

## Version tracking

qlvi's version is in [VERSION](VERSION), independently of upstream ELVIS 1.6.
The build generates its C version header from that file; `:version` in the
editor and `build/dist/VERSION` report the same qlvi version.

Before each new local commit, bump the version and update [CHANGELOG.md](CHANGELOG.md):

```sh
make version
make bump-version NEW_VERSION=0.3.0
# Describe the changes in CHANGELOG.md, then:
make test
```

`68ed7d0` is the **0.1.0** baseline; VERSION identifies the current build.
New feature batches increment the minor version (0.1.0 -> 0.2.0), while bug
fixes and maintenance increment the patch version (0.2.0 -> 0.2.1). Reserve
`-rcN` for an explicitly planned release-candidate cycle. Versioning a commit
does not assert hardware verification or publish a GitHub release; those are
separate steps.

## License

Copyright (c) 2026 Steve Jennen, for original additions and copyrightable
modifications, under [BSD 2-Clause](LICENSE). Original ELVIS and third-party
terms remain in force. The tree is **not exclusively BSD-licensed**.
Read [THIRD_PARTY.md](THIRD_PARTY.md)
before redistributing, particularly for commercial use or binary releases.
