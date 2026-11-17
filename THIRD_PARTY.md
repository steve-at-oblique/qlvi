# Copyright, redistribution, and publication

This is Steve Jennen's QDOS GCC port of **ELVIS 1.6**, originally written by
**Steve Kirkendall**, based on the earlier QDOS port by **Dave Walker**.
It is not a new editor written entirely by Steve Jennen.

## Original ELVIS 1.6

The supplied manual permits redistribution in source or executable form and
says there are no restrictions on use. Its FAQ explicitly says ELVIS is
copyrighted by Steve Kirkendall, not public domain. For modifications it asks
that his name remain in the source, changes be noted near the top of modified
files, and his name be mentioned in the documentation. The exact supplied
statements are preserved in [licenses/ELVIS-1.6.txt](licenses/ELVIS-1.6.txt);
the source document is [docs/original/Elvis.doc](docs/original/Elvis.doc).

Those statements support publishing this modified ELVIS distribution in a
public GitHub repository with its original terms and credits retained.
They do not turn all upstream code into BSD-licensed code. Do not substitute
the Artistic License used by later ELVIS versions: this tree is version 1.6.

The FAQ distinguishes redistribution of ELVIS from reuse of individual pieces:
some files were contributed by other people, and Kirkendall says he cannot
grant permission on their behalf. Keep their notices. Do not extract those
pieces and advertise them as independently BSD-licensed.

## Earlier QDOS port

The supplied [issue notes](docs/original/readme.doc) identify Dave Walker and
the original QDOS port, dated 20 September 1992. Those notes contain no
separate blanket relicensing grant. Existing QDOS work remains attributed to
that port; the new BSD notice covers the subsequent Jennen changes only.

## Explicit exceptions and other contributors

The unused OS-9 implementation (`osk.c`) and its companion header have been
removed from this fork. Their non-commercial-only terms no longer apply to
any bundled source file on that basis. Historical manuals and build scripts
may still mention the original OS-9 port.

- `legacy/platforms/vmswild.c`: its header declares the code public domain
  and asks for credit to Gregg Townsend and John Campbell.
- `legacy/platforms/vmsio.c`: John Campbell's header says it may be used
  as desired while leaving credit.
- `legacy/platforms/alias.c`: Peter Reinig. Amiga sources credit Mike Rieser
  and Dale Rahn. Atari/DOS helpers credit Guntram Blohm. Preserve their
  existing credits; no independent BSD grant is asserted for those files.
- Other original files sometimes lack a file-level author/license statement.
  Their presence in the supplied distribution is recorded; it is not evidence
  that Steve Jennen owns them. The ELVIS distribution statement above remains
  the basis for redistributing this fork, not an invented per-file license.

## Jennen additions

`LICENSE` grants BSD 2-Clause terms for Steve Jennen's original additions and
copyrightable modifications. New launcher/build/tool/test/example files carry
BSD SPDX notices. Modified upstream sources carry a changes-only notice
without replacing their original authors' comments.

The QDOS launcher implementation was checked against QDOS ROM/utility source
and documentation for calling conventions; their implementations were not
copied into the launcher. The QDOS terminal profile reproduces the control/key
capabilities of the supplied terminfo entry; the underlying tiny terminal
reader is still original ELVIS code with marked modifications.

## Toolchain, libraries, and binaries

The cross-compiler and its libraries are **external dependencies**, not covered
by the project's BSD license. The build links QDOS libc/libcurses and compiler
support code; it extracts the curses console translator from the installed
library. This audit has not established the complete redistribution terms of
every linked library version. Keep the applicable toolchain/library notices
with a binary release and verify those terms before publishing binaries.

Supplied historical executables and `env.bin` remain in `legacy/bin/` for
reference and are ignored by Git by default. Generated objects, extracted
library objects, current executables, and packages under `build/` are also
ignored. Neither collection is automatically included in a source push.

## GitHub publication

A source fork may retain its original ELVIS permissions while adding BSD terms
for the new work. Preserve this file, LICENSE, licenses/, original source
credits. Do not use GitHub's license chooser to replace
the entire project's terms with a blanket BSD license.

No repository has been created or pushed as part of the layout/license work.
The conclusions here are a reading of the supplied notices, not a legal
opinion about authorship or every possible commercial redistribution.
