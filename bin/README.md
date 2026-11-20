# QLVI ready-built files

Copy `elvis` and `vi_rext` to the host directory served as SNL drive 4.
Use `VI_USE` to set the full executable filename after loading the extension.
The default is `win1_elvis`; no personal SNL drive is built into the launcher.
For example: `LRESPR vi_rext : VI_USE "win1_vi"` (with the editor saved as
`win1_vi`). The setting lasts until reset; put it in your boot program.

On the QL, load the command once per boot:

```basic
LRESPR snl4_vi_rext
VI_USE "snl4_elvis"
DATA_USE snl4_
VI error_txt
```

On Minerva without the Pointer Environment, press Ctrl+C to select the
editor's console if keyboard input remains with SuperBASIC after VI starts.

The executable includes the QDOS header wrapper understood by SNL. No SEXEC
conversion or terminal environment setup is required. Temporary storage uses
RAM1_; if unavailable, QLVI prompts for another writable location.

`VERSION` identifies this build. Diagnostic logging is disabled.

Hardware testing of 0.2.0: QIMSI Gold, SMSQ/E 3.43, Normal and Large Mode 4,
Aurora 8-bit colour, and Small, Medium and Large 16-bit colour. Window placement
has varied between boots. Minerva startup has also been reported, requiring
Ctrl+C for console selection without the Pointer Environment. The latest
version-display fixes have host tests; hardware verification remains pending.

ELVIS 1.6 is by Steve Kirkendall; the original QDOS port is by Dave Walker.
Steve Jennen's additions are BSD-2-Clause. Retain the repository's LICENSE,
THIRD_PARTY.md and licenses/ when redistributing. These downloads are intended
to be distributed with the repository, including those notices.

Maintainers: run `make bin` to refresh the binaries from the current source.
