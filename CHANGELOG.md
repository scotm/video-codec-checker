Changelog
=========

All notable changes to this project will be documented in this file.

v0.7.2 - 2025-09-14
-------------------
- Docs: Expand AGENTS.md with a comprehensive Testing Guidance section:
  - Mock subprocess and trash detection, control file discovery, ensure concurrency determinism, patch seams in `main`, assert script behaviors, and maintain type safety.
  - No functional code changes in this release.

v0.7.1 - 2025-09-14
-------------------
- Build/Docs: Add `make release_auto` to publish releases with curated notes and appended GitHub auto-generated notes.
- Docs: Update AGENTS.md to recommend combining auto-generated release notes with curated notes; document commands.
- Maintenance: Merge modularization + typed dataclasses work into `main` (v0.7.0) and cut point release.

v0.7.0 - 2025-09-14
-------------------
- Refactor: modularize responsibilities out of `main.py` into dedicated modules:
  - `cli.py` for argument parsing and config normalization (env + YAML) returning a typed `AppConfig`.
  - `concurrency.py` with `ProbeExecutor` to parallelize probing and aggregate stats.
  - `stats.py` with `ProbeStats` for counters and timing summary.
  - `csv_writer.py` to stream CSV output with a fixed header.
- Strong typing: introduce dataclasses and protocols in `models.py` to clarify state and results:
  - `AppConfig`, `ProbeSettings`, `CleanupPolicy`/`CleanupMode`, `FileProbeResult`, `CsvRow`, and `Prober` protocol.
  - Add `process_config(AppConfig)` to `VideoCodecChecker` while keeping `process_files(...)` for compatibility.
- Code quality: add precise type hints to script generation helpers; remove or avoid `typing.Any` usage.
- Docs: Update AGENTS.md to instruct future changes to avoid `typing.Any` where possible and prefer precise types.

v0.6.0 - 2025-09-14
-------------------
- Add `-r/--delete-original` flag and `DELETE_ORIGINAL` environment variable to enable source file cleanup in generated scripts
- Generated scripts include a `run_and_cleanup` wrapper; removes the source only when conversion succeeds and the destination file exists
- Documentation updated to reflect new behavior

v0.5.1 - 2025-09-14
-------------------
- Add Makefile convenience targets for linting, formatting, type-checking, testing, and release publishing
- Add pre-commit hook to block generated CSV outputs from being committed
- Document Makefile and pre-commit usage in README and AGENTS

v0.5.0 - 2025-09-14
-------------------
- Add `scripts/convert_template.sh` to execute a file of FFmpeg commands with logging and optional dry-run
- Ignore generated conversion CSV outputs in `.gitignore` (e.g., `*_conversions.csv`)
- Remove previously tracked generated CSV from repository

v0.4.0 - 2025-09-14
-------------------
- Add `--script` (`-s`) option to write a runnable shell script containing the generated FFmpeg commands
- Script includes shebang and `set -euo pipefail`; commands are not executed automatically
- Commands stream to the script alongside CSV output as files are processed

v0.3.0 - 2025-09-14
-------------------
- Single ffprobe call (JSON) to obtain both video codec and audio channel count
- Optional concurrency via `--jobs` to parallelize metadata probing (default up to CPU count, capped at 32)
- Explicit FFmpeg stream mapping (`-map 0:v:0`, `-map 0:a:0?`) and `-an` when no audio
- Continue streaming CSV writing during processing

v0.2.1 - 2025-09-14
-------------------
- Faster file discovery using a single directory walk and suffix filtering
- Robust FFmpeg command quoting that safely handles single quotes in paths
- Avoid unnecessary ffprobe calls for files already using good codecs
- Stream CSV writing during processing to reduce memory usage on large sets
- Safer default Opus bitrate (128k) when audio channel count is unknown
- Update Python requirement to 3.10+

v0.2.0 - 2025-09-13
-------------------
- Python packaging, CLI entry point, and test suite
- Config via env and YAML
- Initial codec check and FFmpeg command generation
