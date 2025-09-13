# Agent Guidelines for Video Codec Checker

## Commands
- **Run script**: `./check_video_codecs.sh`
- **Make executable**: `chmod +x check_video_codecs.sh`
- **Output to file**: `./check_video_codecs.sh -o results.csv`
- **Auto-generated output**: `./check_video_codecs.sh` (creates timestamped filename)

No build, lint, or test commands exist - this is a standalone Bash script.

## Command Line Options
- `-o, --output FILE`: Specify output CSV filename
- If no output file specified, generates `video_codec_check_YYYYMMDD_HHMMSS.csv`

## Code Style Guidelines

### Bash Scripting
- Use `#!/bin/bash` shebang
- Use lowercase variable names with underscores (e.g., `good_codecs`, `abs_file`)
- Quote all variable expansions: `"$variable"`
- Use arrays for lists: `GOOD_CODECS=("av1" "hevc" "h264")`
- Handle filenames with spaces/newlines using null-delimited processing (`-print0`, `read -r -d ''`)
- Redirect stderr to /dev/null for quiet operations: `2>/dev/null`
- Use `realpath` for absolute path handling
- Add comments explaining script purpose and key sections

### FFmpeg/ffprobe Usage
- Use single `ffprobe` call to get both video codec and audio channels for efficiency
- Use `ffprobe -of default=noprint_wrappers=1:nokey=1` for clean extraction
- Avoid CSV output format which can include trailing commas
- Parse multi-line output: first line = codec, second line = channels

### Error Handling
- Check for empty variables before processing: `[[ -n "$codec" ]]`
- Use array membership tests: `[[ ! " ${array[@]} " =~ " ${value} " ]]`

### Output
- Use CSV format with proper escaping for special characters
- Include headers for clarity
- Generate complete, quoted FFmpeg commands ready to run
- Set Opus bitrate based on audio channels: 48k mono, 128k stereo, 256k 5.1, 320k 7.1+