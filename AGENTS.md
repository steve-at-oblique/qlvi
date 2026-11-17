# qlvi development

- Keep upstream ELVIS 1.6 attribution and licensing intact. Jennen changes are
  BSD-2-Clause as scoped in LICENSE and THIRD_PARTY.md.
- Before committing a new batch of qlvi changes, bump the root VERSION and
  update CHANGELOG.md, unless the user explicitly asks to retain the version.
  Use `make bump-version NEW_VERSION=...`; never maintain a second handwritten
  qlvi version in source files. Upstream ELVIS remains version 1.6.
- Use minor bumps for new features (0.1.0 -> 0.2.0) and patch bumps for fixes
  or maintenance (0.2.0 -> 0.2.1). Do not add rc suffixes unless the user
  explicitly wants a release-candidate cycle. Untested hardware configurations
  belong in the testing notes, not automatically in the version suffix.
  Commit messages should include the qlvi version.
- Run `make test` for relevant changes. Launcher changes also require
  `make test-launcher` with Unicorn. Distinguish host/emulator tests from real
  QL results; do not claim new Minerva or display-mode hardware verification.
- Do not push, tag a release, or publish artifacts without user authorization.
