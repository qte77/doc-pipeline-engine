### Added

- Release automation: `bump-my-version.yaml` (manual version bump → release PR),
  `tag-release.yaml` (annotated tag on main's merge commit), and `publish-release.yaml`
  (GitHub Release from the `CHANGELOG.md` block). Adds `[tool.bumpversion]` config and a
  "Releasing" CONTRIBUTING section; bump-my-version runs via `uv run` (SHA-pinned actions
  only, no composite action). (#134)
