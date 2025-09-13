# Video Codec Checker

This Bash script recursively searches the current directory for video files using codecs that are considered less than state-of-the-art (anything other than AV1, HEVC/H.265, or H.264/AVC). It outputs a CSV-formatted list of such files, including the detected codec and a ready-to-run FFmpeg command to re-encode them to AV1 with Opus audio in an MKV container.

## Requirements

- **FFmpeg**: Must include `ffprobe`, `libsvtav1` (for AV1 encoding), and `libopus` (for audio encoding).
  - On macOS: Install via Homebrew with `brew install ffmpeg`.
  - Verify support: Run `ffmpeg -encoders | grep -E "(svtav1|opus)"` to confirm encoders are available.
- **Bash**: Standard on Unix-like systems.
- **realpath**: For absolute path handling (available on macOS; install coreutils if needed: `brew install coreutils`).

## Usage

1. Make the script executable: `chmod +x check_video_codecs.sh`
2. Run it in the target directory: `./check_video_codecs.sh`
3. Specify output file: `./check_video_codecs.sh -o results.csv`
   - If no output file is specified, a timestamped filename will be generated automatically

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

- **File Discovery**: Uses `find` to locate video files by extension (mp4, avi, mkv, mov, wmv, flv, webm, m4v, mpg, mpeg, 3gp, ogv).
- **Codec Detection**: Queries the first video stream with `ffprobe` to identify the codec.
- **Filtering**: Flags files not using AV1, HEVC, or H.264 as "legacy."
- **Re-encoding Suggestion**: Generates an FFmpeg command that:
   - Converts video to AV1 using SVT-AV1 (preset 4 for balanced speed/quality, CRF 32 for high quality).
   - Re-encodes audio to Opus (48k mono, 128k stereo, 256k 5.1, 320k 7.1+).
  - Outputs to MKV (flexible container for modern codecs).
  - Strips global metadata (e.g., titles, comments) with `-map_metadata -1`.
  - Uses absolute paths to ensure commands work from any directory.
- **Safety**: Handles filenames with spaces, newlines, or special characters using null-delimited processing.

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