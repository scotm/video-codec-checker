# Agent Guidelines for Video Codec Checker

## Commands
- **Run Bash script**: `./check_video_codecs.sh`
- **Run Python script**: `python check_video_codecs.py`
- **Make executable**: `chmod +x check_video_codecs.sh`
- **Output to file**: `./check_video_codecs.sh -o results.csv` or `python check_video_codecs.py -o results.csv`
- **Auto-generated output**: `./check_video_codecs.sh` or `python check_video_codecs.py` (creates timestamped filename)

No build, lint, or test commands exist - this is a standalone script available in both Bash and Python implementations.

## Commit Guidelines

- Break down changes into small, focused commits
- Stage only relevant files for each commit
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