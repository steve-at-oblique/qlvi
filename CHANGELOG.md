# Changelog

qlvi versions track this QDOS port independently of upstream ELVIS 1.6.

## 0.2.4 — 2026-11-17

- Add the Minerva Ctrl+C console-selection step to the main installation
  instructions and Minerva guide, alongside the existing binary instructions.
- Update testing notes to acknowledge reported Minerva startup without the
  Pointer Environment; broader Minerva verification remains pending.
- Record the development rule to commit only upon the user's explicit request.

## 0.2.3 — 2026-11-17

- Fit version messages to the measured console width, reserving room for
  message padding and [More...] rather than assuming an 80-column window.
- Exercise the actual message splitter with host tests at 30–132 columns.

## 0.2.2 — 2026-11-17

- Split version credits into shorter lines to leave room for the message
  continuation prompt in the standard 80-column console.
- Invalidate the editor display after :version so it redraws on return.
- Document Ctrl+C console selection when running VI on Minerva without the
  Pointer Environment. Automatic input selection remains unresolved.

## 0.2.1 — 2026-11-17

- Lead :version with Steve Jennen's name and retain ELVIS and QDOS port credits.
- Include ready-to-copy executables and installation instructions in bin/.
- User reports 0.2.0 editing passes on QIMSI Gold with SMSQ/E 3.43 in Normal
  and Large Mode 4, Aurora 8-bit colour, and Small, Medium, and Large 16-bit
  colour. Window placement varied across reboots; a cold start restored
  centering in Large Mode 4. Minerva remains untested.

## 0.2.0 — 2026-11-17

Second local commit; adds temporary-storage selection and explicit version tracking.

- Probe temporary storage at startup; prompt for a writable alternative if
  RAM1_ is missing, read-only, full, or otherwise unusable.
- Allow locations such as WIN1_ and SNL1_; retry bad choices and allow Escape
  to cancel before opening the original file.
- Keep the chosen location for the editor session and use flat QDOS temporary
  filenames without requiring a subdirectory.
- Add one VERSION source for the executable, :version, diagnostic logs, and
  packaged VERSION file.
- Document Minerva RAM-disk setup and add temporary-storage regression tests.

## 0.1.0 — 2026-11-17

Initial local/GitHub commit: `68ed7d0`. Designated the initial qlvi version;
the original commit did not yet contain an explicit VERSION file.

- SNL editing/saving and built-in terminal capabilities.
- Command-line cursor editing and a resident SuperBASIC VI command.
- Organized sources, build tools, tests, attribution, and licensing.

Hardware baseline: QIMSI Gold, SMSQ/E 3.43, Large 4 Color. The new temporary
storage prompt, other screen sizes, and Minerva remain untested on hardware.
