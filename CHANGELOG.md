# Changelog

qlvi versions track this QDOS port independently of upstream ELVIS 1.6.

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
