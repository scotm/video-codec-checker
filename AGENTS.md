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
- `make release VERSION=x.y.z TITLE="..." NOTES="..."` — create a GitHub Release for an existing tag (requires clean working tree and authenticated `gh`).

Notes:
- `UV` variable controls which runner is used (default: `uv`). Example: `make test UV="uv"`.
- The `release` target assumes the tag `v$(VERSION)` exists or will be created and pushed.

## Documentation Conventions
- README should list "What's New" only for the last two releases. Older release notes belong in `CHANGELOG.md`.

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
- Create a release from an existing tag: `gh release create vX.Y.Z --title "<title>" --notes "<summary>"`
- Optionally generate notes: `gh release create vX.Y.Z --generate-notes`
- Edit an existing release: `gh release edit vX.Y.Z --title "<title>" --notes-file CHANGELOG.md`

## Pre-commit Hooks
- This repo includes a `.pre-commit-config.yaml` that blocks committing generated CSV outputs: `video_codec_check_*.csv`, `test_*.csv`, and `*_conversions.csv`.
- Install: `uv pip install -e .[dev] && uv run pre-commit install`
