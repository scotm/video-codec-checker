# Agent Guidelines for Video Codec Checker

## Assumptions
- GitHub CLI (`gh`) is installed and authenticated. You may directly use `gh` to create or edit GitHub Releases without additional setup in future sessions.

## Commands
- **Run Bash script**: `./check_video_codecs.sh`
- **Run Python script**: `python check_video_codecs.py`
- **Run Python script with uv** (recommended): `uv run check-video-codecs`
- **Make executable**: `chmod +x check_video_codecs.sh`
- **Output to file**: `./check_video_codecs.sh -o results.csv` or `python check_video_codecs.py -o results.csv` or `uv run check-video-codecs -o results.csv`
- **Auto-generated output**: `./check_video_codecs.sh` or `python check_video_codecs.py` or `uv run check-video-codecs` (creates timestamped filename)

## Development Commands
- **Linting**: `uv run ruff check .`
- **Formatting**: `uv run ruff format .`
- **Type checking**: `uv run mypy video_codec_checker/`
- **Run tests**: `uv run python -m pytest tests/`

## Makefile Targets
- `make check` — run lint (ruff), type-check (mypy), and tests (pytest)
- `make lint` — run `ruff check . --fix`
- `make format` — run `ruff format .`
- `make type` — run `mypy video_codec_checker/`
- `make test` — run `pytest`
- `make release VERSION=x.y.z TITLE="..." [NOTES="..."] [NOTES_FILE=path.md]` — create a GitHub Release, combining curated notes (string or file) with auto-generated notes by default.
- `make release_auto ...` — alias for `release` (kept for compatibility).

Notes:
- `UV` variable controls which runner is used (default: `uv`). Example: `make test UV="uv"`.
- The `release` target assumes the tag `v$(VERSION)` exists or will be created and pushed.

## Documentation Conventions
- README should list "What's New" only for the last two releases. Older release notes belong in `CHANGELOG.md`.
- CHANGELOG.md should list entries in descending version order (newest first).

## Future CI Enhancements
- When the project grows, consider adding test coverage reporting:
  - Measure coverage with `coverage.py` and fail if below a threshold (e.g., 90%).
  - Upload results to Codecov (or GitHub code coverage) for PR insights.
  - Gate merges on coverage checks in branch protection rules.
- Consider expanding CI matrix (OS variants, Python pypy) if portability becomes a concern.
- Consider caching wheels and pip dirs for faster cold starts.

## CI Expectations (Lessons Learned)
- CI runs a Python matrix on `3.10`, `3.11`, and `3.12` and requires:
  - `ruff check .` and `ruff format --check .` to pass.
  - `mypy video_codec_checker/` to pass (stubs required for third‑party libs).
  - `pytest` to pass.
- Before pushing:
  - Run `make check` (or run `ruff format .` then `ruff check .`, `mypy`, and `pytest`).
  - If mypy reports “Library stubs not installed”, add the appropriate `types-` package to `[project.optional-dependencies].dev` (e.g., `types-PyYAML`) and update the lockfile as needed.
  - Keep formatting consistent to satisfy `ruff format --check` in CI.

## Dependency & Lockfile Hygiene
- Add runtime deps to `[project].dependencies` and dev tools/stubs to `[project.optional-dependencies].dev`.
- Install locally with `uv pip install -e .[dev]` and confirm `uv.lock` stays in sync.
- Avoid unnecessary deps; prefer stdlib where practical.

## FFprobe/FFmpeg Conventions
- Prefer a single `ffprobe` JSON call without `-select_streams`; parse first video and audio streams from `streams`.
- Generate FFmpeg commands that:
  - Explicitly map primary streams: `-map 0:v:0` and `-map 0:a:0?`.
  - Use `-an` when no audio is present.
  - Quote paths robustly (POSIX single‑quote escaping) so commands survive special characters.
- Don’t execute conversion commands automatically; when adding automation, write a script (`--script`) for user‑initiated runs.

## Labels
Standard GitHub labels used in this repo and their intent:
- bug: Something isn’t working
- enhancement: New feature or request
- documentation: Docs changes
- chore: Maintenance tasks that don’t change behavior
- refactor: Code cleanup without behavior changes
- ci: Continuous integration changes
- test: Testing-related changes
- dependencies: Dependency updates (e.g., from Dependabot)
- good first issue: Issues suitable for newcomers
- help wanted: Extra attention is needed
- question: Further information requested

Notes:
- Prefer these labels on issues and PRs to aid triage and automation.
- If a label already exists with a different color/description, prefer not to overwrite without discussion.

## Code Quality Checks

Before committing changes, always run the following checks to ensure code quality:

1. **Linting**: `uv run ruff check .`
   - Identifies syntax errors, style issues, and potential bugs
   - Automatically fix simple issues: `uv run ruff check . --fix`

2. **Formatting**: `uv run ruff format .`
   - Ensures consistent code style across the project
   - Automatically formats code according to PEP 8 standards

3. **Type checking**: `uv run mypy video_codec_checker/`
   - Verifies type annotations and catches type-related errors
   - Helps prevent runtime errors by checking types at compile time

4. **Testing**: `uv run python -m pytest tests/`
   - Runs all unit tests to ensure functionality remains intact
   - Add `-v` flag for verbose output: `uv run python -m pytest tests/ -v`

## Writing Safe Changes

When making changes to the codebase, follow these guidelines to ensure safety:

1. **Type Annotations**:
   - Add type hints to all function parameters and return values
   - Use `typing` module for complex types when necessary
   - Avoid `typing.Any` wherever possible; prefer precise types, `Protocol`s, `TypeVar`/generics, and unions. If `Any` is truly unavoidable, constrain and document the rationale.
   - Run mypy after adding type annotations to verify correctness

2. **Unit Tests**:
   - Write tests for new functionality
   - Update existing tests when modifying behavior
   - Run tests locally before committing: `uv run python -m pytest tests/`

3. **Error Handling**:
   - Handle exceptions appropriately with try/except blocks
   - Provide meaningful error messages for debugging
   - Test error conditions in unit tests

4. **Code Validation**:
   - Run all checks (linting, formatting, type checking, tests) before committing
   - Fix any issues identified by the tools
   - Ensure new code follows existing style conventions

## Refactor & Design Guidance

- Prefer small, typed data models over tuples:
  - Use `dataclasses` (e.g., `AppConfig`, `ProbeSettings`, `CleanupPolicy`, `FileProbeResult`, `CsvRow`).
  - Define behavior interfaces with `Protocol` (e.g., a `Prober` callable) for easy injection/mocking.
- Preserve test patch points during refactors:
  - If tests monkeypatch `video_codec_checker.main.probe_video_metadata` (or similar), keep an import in `main` and inject that callable into helpers so patches still take effect.
  - Favor dependency injection over hard imports inside helpers for better testability.
- Normalize configuration at the edge:
  - Keep CLI parsing in `cli.py` and return a typed `AppConfig`; compute defaults there (e.g., timestamped output filename).
  - Merge environment and YAML config deterministically: CLI > env > YAML.
- Concurrency practices:
  - Use a bounded `ThreadPoolExecutor` (cap at CPU count or 32) and keep tasks stateless.
  - Aggregate probe stats centrally and print summaries to `stderr` only when relevant (e.g., fast-probe enabled).
- Probing strategy:
  - Prefer a single `ffprobe` JSON call for codec+channels; enable fast-probe by default with fallback to full.
  - Enforce timeouts and handle failures gracefully; return `(None, 0)` on errors.
- CSV and script generation:
  - Stream CSV writing with a fixed header; avoid buffering full results in memory.
  - Generate scripts safely: robust single-quote escaping, cleanup only after a successful conversion and destination exists, and support trash/delete via detected utilities.
- Logging:
  - Print progress and summaries to `stderr`; keep output concise to avoid overwhelming terminals/CI logs.
- CSV schema stability:
  - Keep column order stable; append new columns at the end.
  - Document each column briefly and update tests when schema changes.
  - Avoid renaming/removing columns without a migration note.
- Lazy/conditional outputs:
  - Defer side effects until needed (e.g., only create the script when a conversion-worthy file is found).
  - When zero conversions are found, do not create a script; print a concise note to `stderr`.
- Probe consolidation:
  - When adding new metrics (e.g., bits-per-pixel), prefer extending the primary ffprobe path to avoid extra subprocess calls.
  - If a temporary extra probe is added, leave a TODO to fold it into the primary probe.
- Feature flags & UX:
  - Distinguish “reporting-only” features (e.g., include `h264` analysis in CSV) from “conversion” features (script generation).
  - Consider explicit CLI toggles to include/exclude analysis features and thresholds.
- Release hygiene:
  - Bump `pyproject.toml` version and update CHANGELOG/README (last two releases only) on each release.
  - Use `make release_auto` to create releases with curated notes and append GitHub auto-generated notes; avoid committing temporary note files.
  - Push annotated tags before creating the GitHub Release; keep working tree clean.
- Performance guardrails:
  - Cap thread count; stream outputs; enforce timeouts.
  - Avoid multi-pass directory walks or redundant `ffprobe` invocations; favor single-pass, batched, and cached approaches.

## Testing Guidance

- Isolate external processes:
  - Never invoke real `ffprobe`/`ffmpeg` or rely on network in unit tests.
  - Patch `subprocess.run` to return deterministic `CompletedProcess` outputs (stdout/stderr/returncode).
  - For trash detection, patch `shutil.which` (e.g., return a fake path for `trash` or `gio`).
- Control file discovery:
  - Patch `get_video_files` to return a small, fixed list of `Path` instances; do not scan the real filesystem.
  - When testing CSV/script output, write into `tempfile.TemporaryDirectory()` and assert on file contents.
- Concurrency determinism:
  - Prefer `jobs=1` in tests to make ordering predictable.
  - If ordering matters, sort inputs or assert based on sets rather than sequence positions.
  - Where appropriate, inject a custom `probe_func` into executors to avoid threading concerns entirely.
- Patching strategy:
  - Tests often patch `video_codec_checker.main.*` symbols; keep that surface stable and funnel behavior via dependency injection (e.g., pass `probe_video_metadata` into helpers) so patches take effect.
  - Avoid patching deep internals of helpers; patch the seam used by `main`.
- Script generation assertions:
  - Verify presence of shebang, `set -euo pipefail`, and wrappers like `run_and_cleanup`.
  - For cleanup flags, assert that `USE_TRASH`, `TRASH_BIN/ARG`, and `run_and_cleanup` forms appear as expected.
  - Test quoting by including paths with spaces and single quotes in inputs and verifying the script or command string.
- Type safety in tests:
  - Keep the codebase `mypy`-clean; avoid `typing.Any`. If unavoidable, isolate and document why.
  - Prefer dataclasses (`FileProbeResult`, `CsvRow`) and typed helpers for fixtures.
- Artifacts & pre-commit:
  - Do not commit generated CSVs or temporary note files; `.pre-commit-config.yaml` blocks them.
  - Use temp dirs and clean up after tests.

## UV (Recommended Python Environment Manager)

This project uses uv for Python dependency management. uv is a fast Python package installer and resolver:

- **Setup virtual environment**: `uv venv`
- **Install dependencies**: `uv pip install -e .`
- **Run script**: `uv run check-video-codecs`
- **List installed packages**: `uv pip list`

Using uv ensures dependencies are properly contained and managed without affecting the system Python installation.

## Commit Guidelines

## Commit Guidelines

- Break down changes into small, focused commits
- Stage only relevant parts of files for each commit (partial staging is allowed)
- Ensure each commit is correct and complete
- Use clear, descriptive commit messages

## Command Line Options
- `-o, --output FILE`: Specify output CSV filename
- If no output file specified, generates `video_codec_check_YYYYMMDD_HHMMSS.csv`

## Code Style Guidelines

### Python Implementation
- Use Python 3.6+ with proper shebang `#!/usr/bin/env python3`
- Use lowercase variable names with underscores (e.g., `good_codecs`, `abs_file`)
- Quote all string variables appropriately
- Use sets for efficient membership testing: `GOOD_CODECS = {"av1", "hevc", "h264"}`
- Handle filenames with spaces/newlines using Path objects
- Use subprocess with timeouts for external command execution
- Use pathlib for path handling instead of `realpath`
- Add docstrings explaining class and function purpose

### FFmpeg/ffprobe Usage
- Use `ffprobe -of default=noprint_wrappers=1:nokey=1` for clean codec extraction
- Avoid CSV output format which can include trailing commas
- Detect audio channels with `-select_streams a:0 -show_entries stream=channels`

### Error Handling
- Check for empty variables before processing
- Use set membership tests for efficient codec filtering
- Handle subprocess errors and timeouts appropriately

### Output
- Use CSV format with proper escaping for special characters
- Include headers for clarity
- Generate complete, quoted FFmpeg commands ready to run
- Set Opus bitrate based on audio channels: 48k mono, 128k stereo, 256k 5.1, 320k 7.1+
## Release Publishing (using GitHub CLI)
- Verify authentication: `gh auth status`
- Preferred path: use `make release` (combines curated + auto-generated notes by default).
  - Example: `make release VERSION=0.7.5 TITLE=\"v0.7.5: feature\" NOTES_FILE=notes-0.7.5.md`
- Manual alternative (if needed):
  - Create release from an existing tag with `--notes-file`, then optionally append auto notes using `gh api ... releases/generate-notes` and `gh release edit ... --notes-file`.

## Pre-commit Hooks
- This repo includes a `.pre-commit-config.yaml` that blocks committing generated CSV outputs: `video_codec_check_*.csv`, `test_*.csv`, and `*_conversions.csv`.
- Install: `uv pip install -e .[dev] && uv run pre-commit install`

## Git Flow Branching Strategy

This project uses Git Flow for organizing branches and commits:

- **Main branch**: Contains production-ready code that can be released
- **Develop branch**: Integration branch for features and development work
- **Feature branches**: Used for developing new features, branched from develop and merged back to develop
- **Release branches**: Used for preparing new production releases, branched from develop
- **Hotfix branches**: Used for quickly addressing necessary changes in main, branched from main

When creating new features, use the following workflow:
1. Create a feature branch from develop: `git checkout develop && git checkout -b feature/your-feature-name`
2. Develop your feature and make commits
3. Push the feature branch to remote: `git push origin feature/your-feature-name`
4. Create a pull request to merge feature branch into develop
