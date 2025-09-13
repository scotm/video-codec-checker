"""FFmpeg command generation for video codec conversion."""


def get_audio_bitrate(channels):
    """Determine optimal Opus bitrate based on audio channels."""
    if channels == 1:
        return "48k"  # Mono
    elif channels == 2:
        return "128k"  # Stereo
    elif 3 <= channels <= 6:
        return "256k"  # 5.1 surround
    else:
        return "320k"  # 7.1 or higher


def generate_ffmpeg_command(input_file, channels):
    """Generate FFmpeg command to convert video to AV1 and audio to Opus."""
    output_file = input_file.with_stem(input_file.stem + "_av1").with_suffix(".mkv")
    audio_bitrate = get_audio_bitrate(channels)

    cmd_parts = [
        "ffmpeg",
        "-i",
        f"'{input_file}'",
        "-map_metadata",
        "-1",
        "-c:v",
        "libsvtav1",
        "-preset",
        "4",
        "-crf",
        "32",
        "-c:a",
        "libopus",
        "-b:a",
        audio_bitrate,
        f"'{output_file}'",
    ]

    return " ".join(cmd_parts)
