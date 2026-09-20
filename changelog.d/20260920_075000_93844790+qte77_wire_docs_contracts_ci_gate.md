### Fixed

- `docs/contracts.md` resynced with `src/doc_pipeline_engine/models/` (en-dash escaping + `ExtractionBundle` docstring paragraph split had drifted).

### Changed

- `tests.yaml` now runs `make docs_contracts` so contract-doc drift fails CI instead of accumulating silently.
