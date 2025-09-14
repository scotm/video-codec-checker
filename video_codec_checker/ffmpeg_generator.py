"""FFmpeg command generation for video codec conversion."""

from pathlib import Path


def _single_quote(path: str) -> str:
    """Return path wrapped in single quotes with internal quotes escaped.

    Uses the POSIX-safe pattern: ' -> '\'' inside single-quoted strings.
    Always returns a single-quoted string to keep output consistent.
    """
    return "'" + path.replace("'", "'\"'\"'") + "'"


def get_audio_bitrate(channels: int) -> str:
    """Determine optimal Opus bitrate based on audio channels.

    Uses a safe default of 128k when channels are unknown or <= 0.
    """
    if channels <= 0:
        return "128k"  # Unknown; default to stereo bitrate
    if channels == 1:
        return "48k"  # Mono
    if channels == 2:
        return "128k"  # Stereo
    if 3 <= channels <= 6:
        return "256k"  # 5.1 surround
    return "320k"  # 7.1 or higher


def get_output_path(input_file: Path) -> Path:
    """Return the destination path for a converted file.

    Example: /dir/video.mp4 -> /dir/video_av1.mkv
    """
    return input_file.with_stem(input_file.stem + "_av1").with_suffix(".mkv")


def generate_ffmpeg_command(input_file: Path, channels: int) -> str:
    """Generate FFmpeg command to convert video to AV1 and audio to Opus.

    - Explicitly maps primary video stream and optional primary audio stream
    - Uses -an when no audio is present
    """
    output_file = get_output_path(input_file)
    q_input = _single_quote(str(input_file))
    q_output = _single_quote(str(output_file))

    cmd_parts = [
        "ffmpeg",
        "-i",
        q_input,
        "-map_metadata",
        "-1",
        "-map",
        "0:v:0",
        "-c:v",
        "libsvtav1",
        "-preset",
        "4",
        "-crf",
        "32",
    ]

    if channels and channels > 0:
        audio_bitrate = get_audio_bitrate(channels)
        cmd_parts += [
            "-map",
            "0:a:0?",
            "-c:a",
            "libopus",
            "-b:a",
            audio_bitrate,
        ]
    else:
        cmd_parts += ["-an"]

    cmd_parts.append(q_output)
    return " ".join(cmd_parts)
