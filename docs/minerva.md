# Minerva and RAM-disk setup

The user has tested editing on QIMSI Gold with SMSQ/E 3.43 in several display
modes and has reported Minerva startup without the Pointer Environment.
Broader Minerva testing and hardware testing of the temporary-storage prompt
remain pending.

## Selecting the editor console

On Minerva without the Pointer Environment, after starting the editor with:

```basic
VI error_txt
```

press **Ctrl+C** to select the editor's console if keyboard input remains
with SuperBASIC. This switches keyboard input between consoles; it does not
quit qlvi. This extra step was required in the user's Minerva test.

Minerva can use standalone QDOS device drivers; it does not need SMSQ/E's
built-in RAM disk. The following external downloads are available from the
[Sinclair QL toolkits archive](https://www.sinclairql.net/djw/tk/index.html).
Their binaries are not bundled with qlvi, and compatibility with this exact
QIMSI Gold/16 MB/Minerva configuration has not yet been verified here.

## RAM disk 2.11

The archive describes [ramdisk_211.zip](https://www.sinclairql.net/djw/tk/ramdisk_211.zip)
as a RAM disk with subdirectory support, installed by LRESPR'ing
`rd211_rext`. The ZIP contains `rd211.rext`.

Extract it on the host, copy/rename that file to `rd211_rext` in the directory
served by SNL drive 4, then boot Minerva and load the SNL driver. If no RAM
filesystem is already installed, use:

```basic
LRESPR snl4_rd211_rext
DIR ram1_
```

Load the driver only once per boot. A successful DIR confirms that RAM1_ is
recognized; a small disposable SAVE/LOAD/DELETE test is the next hardware
check before using it for editor working files. Do not load another RAM
driver over an existing RAM device. RAM-disk contents are temporary and are
lost on reset or power-off.

## Older dynamic/static RAM drivers

[ramdisks.zip](https://www.sinclairql.net/djw/tk/ramdisks.zip) is explicitly
provided for older QL systems/emulators without a RAM disk. It contains a
small dynamic driver plus a static driver and their installation notes.

The dynamic driver's `DynRAM.txt` says it grows and shrinks as needed, does
not need formatting, and may be installed with LRESPR when Toolkit II is
available. Copy `Dyn_RAMdisk.bin` as `Dyn_RAMdisk_bin` on SNL drive 4:

```basic
LRESPR snl4_Dyn_RAMdisk_bin
DIR ram1_
```

Its supplied boot example describes RAM1_ through RAM8_. Its author and
specific memory-limit compatibility are not identified, so prefer testing
the newer driver first. The static driver requires an explicit FORMAT with
a capacity; follow its own `StatRAM.txt` rather than assuming it behaves
like the dynamic driver.

## qlvi without a RAM disk

A RAM disk is optional for qlvi. In the new build, if RAM1_ cannot be used,
type a writable temporary location such as `win1_` or `snl1_` at its prompt.
Return accepts a working location; Escape cancels startup. See
[temporary storage behavior](qdos.md#temporary-storage) for details.
