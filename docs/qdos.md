# ELVIS with QDOS GCC

The QDOS port of ELVIS 1.6 now builds with QDOS GCC. The original build files and supplied binaries are preserved under `legacy/`. The user verified build 08 on a real
QL: SNL reading, editing, saving with ZZ, reopening, G/1G navigation, and
Left/Right editing of the command line. The user also verified the resident VI launcher, bare filename arguments,
and DATA_USE on the QL.

## Build and package

```sh
make -j4
make package
```

Requires `qdos-gcc`, `qdos-as`, and the toolchain's curses library. Ordinary
builds go in `build/qdos`. `package` produces:

- `build/dist/elvis`: executable with its QDOS metadata embedded in a
  30-byte Q-emulator wrapper. The dataspace comes from the GCC XTcc trailer.
- `build/dist/vi_rext`: a resident SuperBASIC extension defining VI.

Copy these two files through the host/shared directory into the directory
served as SNL drive 4, retaining the names `elvis` and `vi_rext`. The SNL
daemon exposes them as `snl4_elvis` and `snl4_vi_rext`. Its existing wrapper
support hides the 30 wrapper bytes and exposes executable type 1 and the
correct dataspace. No SEXEC, manual byte counts, or metadata sidecars are
needed for this packaged executable. Do not strip the wrapper when copying
through the host filesystem. An ordinary raw binary is still available as
`build/qdos/elvis` for other transfer methods.

This packaging relies on the SNL daemon's existing Q-emulator header support
(or another filesystem/emulator supporting that format); a generic QDOS disk
transfer that copies wrapper bytes verbatim without interpreting them is not
sufficient.

## QL setup and use

The QDOS screen and keyboard definitions are now compiled into ELVIS. Neither
`terminfo_qdos` nor `env_bin` nor the TERM/TERMINFO environment variables are
needed to start this build. Existing environment settings can stay in place;
the local QDOS console profile is selected directly.

After a fresh boot:

```basic
LRESPR snl4_vi_rext
VI snl4_error_txt
```

Load each resident extension only once per boot. `VI` stays available after
NEW. It accepts no argument, one bare filename, one quoted filename, or a
string variable/expression:

```basic
VI
VI snl4_error_txt
VI "snl4_error_txt"
f$="snl4_error_txt": VI f$
```

It starts an independent job at priority 32, using the executable's header
for code size and dataspace. It passes the filename on the standard QDOS EX
startup stack and closes the program channel before activation. Failed
loads remove the inactive job and release the per-call heap workspace.
The executable location is `snl4_elvis`, specified at the end of `src/qdos/vi_rext.s`;
change the length-prefixed string there and rebuild to use a different path.
Filename input is limited to 255 bytes. Existing ELVIS argument-list handling
still limits filenames containing spaces.

You can also run the packaged executable directly:

```basic
EX snl4_elvis
```

The resident extension is raw position-independent machine code, loaded with
LRESPR. It does not need an executable header or SEXEC conversion. To update
the extension after loading it, reboot before loading the replacement.
The editor can be updated independently after all running editor jobs exit.

## Port changes and limitations

- Use `-O -DQDOS` instead of the original C68-only compiler flags. Sources and headers use lowercase filenames in `src/` and `include/`.
- Fix old library declarations, QDOS startup callback types, and signed key
  bytes. Read file metadata with fstat on the channel already opened.
- Read keyboard bytes through QDOS, with native cursor visibility and
  timeouts. Query the real window size and position the cursor natively.
- Compile the original QDOS terminal capabilities into the existing tiny
  termcap reader; all 37 screen/key strings match the supplied terminfo file.
  The cursor-address capability uses the tiny reader's equivalent VT52 format.
- Explicitly link the curses console translator, including the ELVIS-specific
  line insertion/deletion and newline behavior. Terminate output buffers.
- Repaint command input natively and support Left/Right, insertion and
  backspace at the current command-line cursor.
- The default build does not install Unix-style signal handlers. It works
  without the optional SIGNAL_R extension and no longer prints its missing
  extension warning. Signal-based cleanup and suspension are not provided in
  this mode; define ELVIS_QDOS_SIGNALS when building for a system with working
  signal support. Ordinary editing, Escape, ZZ, and :q use no such extension.
- Temporary storage defaults to RAM1_. Before the first edit buffer is opened,
  qlvi probes that location. If it cannot be used, it prompts for another device
  or prefix such as win1_ or snl1_. Shell filtering via rpipe was already
  unsupported. Legacy void-main compiler warnings remain.

Diagnostic build (logs startup, key bytes, and file operations to SNL4):

```sh
make BUILD=build/qdos-debug \
  CFLAGS='-O -DQDOS -DELVIS_STARTUP_TRACE' build/qdos-debug/elvis
```

## Temporary storage

qlvi uses temporary working files even for an empty edit buffer. By default it
tries `ram1_`. It now checks temporary storage before opening the original
file or creating the first edit buffer. The check creates a separate probe
file exclusively, writes and reads four bytes with a seek, then closes and
removes the probe. It never overwrites an existing probe file.

If the location is missing, full, read-only or otherwise unusable, qlvi asks
for a writable device/prefix. Type `win1_`, `snl1_`, or another suitable prefix
and press Return. Leading/trailing spaces are trimmed, and a missing final
underscore is added. Empty or invalid input and unusable choices are retried;
Escape cancels startup before the original file is opened. The 30-byte
existing directory option allows at most 29 characters, including the final
underscore. No directories are created automatically.

The selected prefix is remembered for the current editor session. It is not
written to a configuration file automatically. Working filenames use a flat
QDOS prefix, for example `snl1_elv_<job>_<sequence>`, so choosing a device does
not require a pre-existing `elv_` subdirectory. Once a working location has
been accepted it stays fixed, including when changing files, so cut buffers
continue to refer to the correct working files. Losing that device or filling
it later is still a file-I/O error, not an automatic migration to another disk.

This startup selection and use of SNL for temporary files have automated
coverage but still require real QL testing. The previously verified 80 KB file
editing test used RAM1_ working storage. Minerva/other display modes remain
untested on hardware. See [Minerva RAM-disk setup](minerva.md).

## Checks

```sh
python3 tests/test_commandline.py
python3 tests/test_builtin_terminal.py
python3 tests/test_package_qdos.py
```

For packaging integration against a checkout of the actual SNL daemon:

```sh
SNL_SERVER=/path/to/snldriver/snl_serial python3 tests/test_package_qdos.py
```

`tests/test_vi_rext.py` requires the Unicorn emulator. It executes the
assembled 68000 instructions with QDOS trap stubs, checking procedure
registration, arguments, a relocated BASIC area, startup stack layout,
128-byte user-stack limit, and cleanup when allocation/open/header/job/load/
activation operations fail. Run after `make package`.
The trap stubs do not replace a real QDOS/ROM/hardware integration test.

References: QDOS/SMS Reference Manual, sections 9.7–9.10, 13, 16 and 18.5;
SNL `docs/EMULATOR_FILES.md` and its actual Session wrapper reader.
