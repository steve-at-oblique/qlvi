# QLVI ready-built files

Copy `elvis` and `vi_rext` to the host directory served as SNL drive 4.
Keep these filenames: the resident VI command opens `snl4_elvis`.

On the QL, load the command once per boot:

```basic
LRESPR snl4_vi_rext
DATA_USE snl4_
VI error_txt
```

The executable includes the QDOS header wrapper understood by SNL. No SEXEC
conversion or terminal environment setup is required. Temporary storage uses
RAM1_; if unavailable, QLVI prompts for another writable location.

`VERSION` identifies this build. Diagnostic logging is disabled.

Hardware testing of 0.2.0: QIMSI Gold, SMSQ/E 3.43, Normal and Large Mode 4,
Aurora 8-bit colour, and Small, Medium and Large 16-bit colour. Window placement
has varied between boots. Version 0.2.1 has host tests; its hardware testing
and Minerva testing remain pending.

ELVIS 1.6 is by Steve Kirkendall; the original QDOS port is by Dave Walker.
Steve Jennen's additions are BSD-2-Clause. Retain the repository's LICENSE,
THIRD_PARTY.md and licenses/ when redistributing. These downloads are intended
to be distributed with the repository, including those notices.

Maintainers: run `make bin` to refresh the binaries from the current source.
