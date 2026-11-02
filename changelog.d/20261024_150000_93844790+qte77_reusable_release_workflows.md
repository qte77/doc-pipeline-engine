### Changed

- Release workflows (`bump-my-version.yaml`, `tag-release.yaml`, `publish-release.yaml`) are now thin callers of the `qte77/.github` reusables (`bump-version.yml` with `use_uv` / `sync_lockfile` / `collect_scriv`, `tag-release.yml`, `publish-release.yml`), pinned by SHA. The bump commit is now GitHub-signed. Closes [#165](https://github.com/qte77/doc-pipeline-engine/issues/165).
