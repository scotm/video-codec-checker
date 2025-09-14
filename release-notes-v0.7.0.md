## v0.7.0 — Modularization + typed dataclasses

This release focuses on maintainability and clarity. We modularized the main script, introduced strong typing across configuration and results, and tightened developer guidance.

Highlights
- Refactor: move responsibilities out of `main.py` into dedicated modules
  - `cli.py`: argument parsing + config normalization (env + YAML) → typed `AppConfig`
  - `concurrency.py`: `ProbeExecutor` for parallel probing + stats aggregation
  - `stats.py`: `ProbeStats` counters and timing summary
  - `csv_writer.py`: streaming CSV writer with a fixed header
- Strong typing via dataclasses and protocol
  - `models.py`: `AppConfig`, `ProbeSettings`, `CleanupPolicy`/`CleanupMode`, `FileProbeResult`, `CsvRow`, `Prober`
  - `VideoCodecChecker.process_config(AppConfig)` added; legacy `process_files(...)` retained
- Code quality
  - Added precise type hints to script helpers; avoided `typing.Any`
  - Formatted and sorted imports (ruff); `mypy` clean across the package
- Docs
  - AGENTS.md: explicitly advise avoiding `typing.Any` and prefer precise types and protocols

No user-facing behavior changes — CLI options and CSV/script outputs remain the same. All tests pass.

Thanks to this modular structure, future enhancements (e.g., richer output formats, new probes, or alternative runners) will be easier and safer to implement.
