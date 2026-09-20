### Changed

- `dependabot.yaml` now groups updates per ecosystem (`pip`, `github-actions`) into a `*-version-updates` and a separate `*-security-updates` group, so routine bumps land as one grouped PR instead of one PR per dependency.

### Fixed

- `codeql.yaml`'s pinned actions (`actions/checkout`, `github/codeql-action/{init,autobuild,analyze}`, `advanced-security/dismiss-alerts`) brought current, applying the version bumps their own now-superseded dependabot PRs had already computed.

(#199)
