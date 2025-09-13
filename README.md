# Video Codec Checker

This script recursively searches the current directory for video files using codecs that are considered less than state-of-the-art (anything other than AV1, HEVC/H.265, or H.264/AVC). It outputs a CSV-formatted list of such files, including the detected codec and a ready-to-run FFmpeg command to re-encode them to AV1 with Opus audio in an MKV container.

Available in both Bash (`check_video_codecs.sh`) and Python (`check_video_codecs.py`) implementations.

## Requirements

- **FFmpeg**: Must include `ffprobe`, `libsvtav1` (for AV1 encoding), and `libopus` (for audio encoding).
  - On macOS: Install via Homebrew with `brew install ffmpeg`.
  - Verify support: Run `ffmpeg -encoders | grep -E "(svtav1|opus)"` to confirm encoders are available.
- **Bash** (for Bash version): Standard on Unix-like systems.
- **Python** (for Python version): Python 3.6+ required.
- **realpath**: For absolute path handling (available on macOS; install coreutils if needed: `brew install coreutils`).
- **uv** (recommended): Python package manager for handling dependencies (install via `brew install uv`).

## Usage

For Bash version:
1. Make the script executable: `chmod +x check_video_codecs.sh`
2. Run it in the target directory: `./check_video_codecs.sh`
3. Specify output file: `./check_video_codecs.sh -o results.csv`

For Python version:
1. Run it in the target directory: `python check_video_codecs.py`
2. Specify output file: `python check_video_codecs.py -o results.csv`

For Python version with uv (recommended):
1. Run with uv: `uv run check-video-codecs`
2. Specify output file: `uv run check-video-codecs -o results.csv`

Both versions:
- If no output file is specified, a timestamped filename will be generated automatically
- Accept a directory argument to scan a specific directory: `./check_video_codecs.sh /path/to/videos` or `python check_video_codecs.py /path/to/videos`

### Environment Variables

The Python version also supports environment variables for configuration:
- `OUTPUT_FILE`: Default output CSV filename (equivalent to -o/--output argument)
- `SCAN_DIRECTORY`: Directory to scan for video files (equivalent to directory argument)

You can also use a `.env` file in the current directory to set these variables. See `.env.example` for reference.

### YAML Configuration File

The Python version supports YAML configuration files with the following options:
- `output_file`: Default output CSV filename (equivalent to -o/--output argument)
- `scan_directory`: Directory to scan for video files (equivalent to directory argument)

The default configuration file location is `~/.config/check-video-codecs.yml`. You can specify a different location using the `--config` argument.

The script outputs to a CSV file with a header row. Each row for legacy files includes:
- **File**: Relative path to the video file.
- **Codec**: Detected video codec (e.g., "mpeg4").
- **FFmpeg_Command**: A complete, quoted command to re-encode the file.

Example output:
```
File,Codec,FFmpeg_Command
"./old_video.avi","mpeg4","ffmpeg -i '/absolute/path/old_video.avi' -map_metadata -1 -c:v libsvtav1 -preset 4 -crf 32 -c:a libopus -b:a 128k '/absolute/path/old_video_av1.mkv'"
```

## What It Does

- **File Discovery**: Locates video files by extension (mp4, avi, mkv, mov, wmv, flv, webm, m4v, mpg, mpeg, 3gp, ogv).
- **Codec Detection**: Queries the first video stream with `ffprobe` to identify the codec.
- **Filtering**: Flags files not using AV1, HEVC, or H.264 as "legacy."
- **Re-encoding Suggestion**: Generates an FFmpeg command that:
   - Converts video to AV1 using SVT-AV1 (preset 4 for balanced speed/quality, CRF 32 for high quality).
   - Re-encodes audio to Opus (48k mono, 128k stereo, 256k 5.1, 320k 7.1+).
  - Outputs to MKV (flexible container for modern codecs).
  - Strips global metadata (e.g., titles, comments) with `-map_metadata -1`.
  - Uses absolute paths to ensure commands work from any directory.
- **Safety**: Handles filenames with spaces, newlines, or special characters properly.

## Notes

- Only checks the first video stream; files with multiple streams may need manual review.
- Re-encoding can be time-intensive; test on a small file first.
- Opus audio is efficient but ensure your playback software supports it in MKV (most modern players do).
- If SVT-AV1 is unavailable, modify the script to use `libaom-av1` (slower but more compatible).
- For large directories, consider running in parallel or adding exclusions (e.g., edit the `find` command to skip folders like `node_modules`).

## Customization

Edit the script to:
- Change good codecs: Modify the `GOOD_CODECS` array.
- Adjust FFmpeg settings: Tweak preset, CRF, bitrate, or output format.
- Add extensions: Update the `find` command's `-iname` list.
- Exclude directories: Add `-not -path '*/exclude/*'` to the `find` command.

## License

This script is provided as-is for personal use. Ensure compliance with FFmpeg and codec licensing.