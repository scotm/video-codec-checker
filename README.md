# Video Codec Checker

This tool recursively searches a directory for video files using codecs that are considered less than state-of-the-art (anything other than AV1, HEVC/H.265, or H.264/AVC). It outputs a CSV with the detected codec, audio channels, bits‑per‑pixel, and a ready‑to‑run FFmpeg command to re‑encode legacy files to AV1 with Opus audio in an MKV container.

Use the Python CLI entry point `check-video-codecs` (via `uv run` is recommended).

## What's New in 0.7.4
- CSV: `FFmpeg_Command` now populated for all reported files, including `h264`, to simplify quick evaluation.
- Script generation remains limited to non-good codecs and is created lazily only if conversions are needed.

## What's New in 0.7.3
- Report: Added `Bits_Per_Pixel` column to CSV; includes `h264` files to assess efficiency
- Report: Include `h264` videos in the CSV with empty `FFmpeg_Command` column (changed in v0.7.4)
- Script generation remains limited to non-good codecs and is created lazily only if conversions are needed

<!-- Older release notes are available in CHANGELOG.md. Keep only the last two here. -->

## Requirements

- **FFmpeg**: Must include `ffprobe`, `libsvtav1` (for AV1 encoding), and `libopus` (for audio encoding).
  - On macOS: Install via Homebrew with `brew install ffmpeg`.
  - Verify support: Run `ffmpeg -encoders | grep -E "(svtav1|opus)"` to confirm encoders are available.
- **Python**: Python 3.10+ required.
- **uv** (recommended): Python package manager for handling dependencies (e.g., `brew install uv`).

## Usage

### Usage (with uv)

1. Run: `uv run check-video-codecs`
2. Specify output file: `uv run check-video-codecs -o results.csv`
3. Write a shell script with commands: `uv run check-video-codecs -s convert.sh`
   - Make it executable: `chmod +x convert.sh`
   - Run it manually when ready: `./convert.sh`
4. Parallelize metadata probing: `uv run check-video-codecs -j 8`
5. Include cleanup in generated script (delete or trash source on success):
   - Delete: `uv run check-video-codecs -s convert.sh -r`
   - Trash: `uv run check-video-codecs -s convert.sh -t`
6. Scan a specific directory: `uv run check-video-codecs /path/to/videos`

### Conversion Script Template

You can also run commands from a generated script using the provided template:

- Generate commands: `uv run check-video-codecs -o results.csv -s convert.sh`
- Make executable: `chmod +x convert.sh`
- Execute manually when ready: `./convert.sh`

Alternatively, use the template runner to execute a file of commands line-by-line with logging and optional dry-run:

- `scripts/convert_template.sh -f convert.sh -l convert.log` (runs commands)
- Dry-run: `scripts/convert_template.sh -f convert.sh -n`
 - Optional cleanup: generate the script with `-r/--delete-original` or set `DELETE_ORIGINAL=1` so the script removes the source file after successful conversion and when the destination file exists.

The template ignores blank lines and comments (lines starting with `#`), logs each command, and continues on failures.

Notes:
- If no output file is specified, a timestamped filename is generated automatically.

### Environment Variables

The CLI also supports environment variables (via `.env`):
- `OUTPUT_FILE`: Default output CSV filename (equivalent to `-o/--output`).
- `SCAN_DIRECTORY`: Directory to scan (equivalent to the `directory` argument).
- `DELETE_ORIGINAL`: Truthy to delete source in generated scripts (equivalent to `-r/--delete-original`).
- `TRASH_ORIGINAL`: Truthy to move source to Trash on success (equivalent to `-t/--trash-original`).
- `FAST_PROBE`: Truthy/falsey to toggle fast ffprobe (default: enabled).
- `FFPROBE_PROBESIZE`: Value for `-probesize` when fast-probe is enabled (default: `5M`).
- `FFPROBE_ANALYZEDURATION`: Value for `-analyzeduration` when fast-probe is enabled (default: `10M`).

You can also use a `.env` file in the current directory to set these variables. See `.env.example` for reference.

### YAML Configuration File

YAML configuration supports the following options:
- `output_file`: Default output CSV filename (equivalent to -o/--output argument)
- `scan_directory`: Directory to scan for video files (equivalent to directory argument)

The default configuration file location is `~/.config/check-video-codecs.yml`. You can specify a different location using the `--config` argument.

The script outputs to a CSV file with a header row. Each row includes:
- **File**: Relative path to the video file.
- **Codec**: Detected video codec (e.g., "mpeg4").
- **Audio_Channels**: Detected number of audio channels (0 if unknown).
- **Bits_Per_Pixel**: Computed bits per pixel value for assessing codec efficiency.
- **FFmpeg_Command**: A complete, quoted command to re-encode the file.

Example output:
```
File,Codec,Audio_Channels,Bits_Per_Pixel,FFmpeg_Command
"./old_video.avi","mpeg4",2,0.25,"ffmpeg -y -i '/absolute/path/old_video.avi' -map_metadata -1 -map 0:v:0 -c:v libsvtav1 -preset 3 -crf 32 -map 0:a:0? -c:a libopus -b:a 128k '/absolute/path/old_video_av1.mkv'"
```

## What It Does

- **File Discovery**: Locates video files by extension (mp4, avi, mkv, mov, wmv, flv, webm, m4v, mpg, mpeg, 3gp, ogv).
- **Codec & Audio Probe**: Uses a single `ffprobe` call (JSON) to obtain the primary video codec and primary audio channel count efficiently.
- **Filtering**: Reports on all video files, flagging files not using AV1, HEVC, or H.264 as "legacy."
- **Re-encoding Suggestion**: Generates an FFmpeg command that:
   - Converts video to AV1 using SVT-AV1 (preset 3 by default, CRF 32).
   - Re-encodes audio to Opus (48k mono, 128k stereo, 256k 5.1, 320k 7.1+). If audio is absent, uses `-an` to omit audio.
   - Explicitly maps primary streams only: `-map 0:v:0` and `-map 0:a:0?` for predictable outputs.
  - Outputs to MKV (flexible container for modern codecs).
  - Strips global metadata (e.g., titles, comments) with `-map_metadata -1`.
  - Uses absolute paths to ensure commands work from any directory.
- **Safety**: Handles filenames with spaces, newlines, or special characters properly.
 - **Performance**: Parallel metadata probing via `--jobs` and a single directory walk for file discovery.

## Notes

- Only checks the first video stream; files with multiple streams may need manual review.
- Re-encoding can be time-intensive; test on a small file first.
- Opus audio is efficient but ensure your playback software supports it in MKV (most modern players do).
- If SVT-AV1 is unavailable, modify the script to use `libaom-av1` (slower but more compatible).
- For large directories, consider running in parallel or adding exclusions (e.g., edit the `find` command to skip folders like `node_modules`).

## Customization

- Adjust FFmpeg settings: tweak preset/CRF/bitrate in `video_codec_checker/ffmpeg_generator.py`.
- Extend recognized extensions: update `get_video_files` in `video_codec_checker/video_processor.py`.
- Good codecs set: `{"av1","hevc","h264"}` in `video_codec_checker/main.py`; scripts are generated only for legacy codecs (not `h264`).

## Development Tools

This project now includes development tools for code quality assurance:

- **Linting and formatting**: Uses Ruff for both linting and formatting
- **Type checking**: Uses MyPy for static type checking
- **Testing**: Uses pytest for running tests

To run these tools:
1. Install development dependencies: `uv pip install -e .[dev]`
2. Run linting: `uv run ruff check .`
3. Run formatting: `uv run ruff format .`
4. Run type checking: `uv run mypy video_codec_checker/`
5. Run tests: `uv run python -m pytest tests/`

These tools help maintain code quality and catch potential issues early in the development process.

### CI Checklist (before pushing)

- Format: `uv run ruff format .`
- Lint: `uv run ruff check .`
- Types: `uv run mypy video_codec_checker/`
- Tests: `uv run python -m pytest -q`
- If mypy reports missing stubs (e.g., PyYAML), add the appropriate `types-` package to dev deps in `pyproject.toml` (e.g., `types-PyYAML`) and reinstall.

### Makefile Shortcuts

Common tasks are available via `make`:

- `make check` — run lint, type check, and tests
- `make lint` — run ruff with `--fix`
- `make format` — run ruff formatter
- `make type` — run mypy
- `make test` — run pytest
- `make release VERSION=x.y.z TITLE="..." [NOTES="..."] [NOTES_FILE=path.md]` — create a GitHub Release. Ensures the tag `vX.Y.Z` exists (creates and pushes if missing) and combines curated notes with auto‑generated notes by default.

### Pre-commit Hooks

This repo includes a `.pre-commit-config.yaml` to block accidental commits of generated CSV outputs.

Setup:
- Install dev deps: `uv pip install -e .[dev]`
- Install hooks: `uv run pre-commit install`

On commit, files matching `video_codec_check_*.csv`, `test_*.csv`, and `*_conversions.csv` will be rejected.

## GitHub CLI & Releases

To publish GitHub Releases from the command line, use GitHub CLI (`gh`).

- Install GitHub CLI:
  - macOS (Homebrew): `brew install gh`
  - Linux (Debian/Ubuntu): `sudo apt-get install gh` (or see https://github.com/cli/cli#installation)
  - Windows: `winget install --id GitHub.cli` (or see link above)

- Authenticate once:
  - `gh auth login`
  - Choose GitHub.com, HTTPS, and sign in via browser or token
  - Verify with: `gh auth status`

- Create a release from an existing tag (example: v0.3.0):
  - Title + notes: `gh release create v0.3.0 --title "v0.3.0: single ffprobe, concurrency, explicit mapping, no-audio handling" --notes "See README and CHANGELOG for details."`
  - Or use generated notes: `gh release create v0.3.0 --generate-notes`
  - To edit later: `gh release edit v0.3.0 --title "..." --notes-file CHANGELOG.md`

Notes:
- Ensure the tag exists locally and is pushed: `git tag -a vX.Y.Z -m "..." && git push --tags`.
- In this repo we tag as part of releases; the command above just publishes a GitHub Release entry for that tag.

## License

This script is provided as-is for personal use. Ensure compliance with FFmpeg and codec licensing.
