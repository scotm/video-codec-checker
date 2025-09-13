#!/bin/bash

# Script to find video files using codecs less than state-of-the-art (AV1, HEVC, H.264)
# Outputs CSV: File,Codec,FFmpeg_Command
# State-of-the-art: av1, hevc, h264

GOOD_CODECS=("av1" "hevc" "h264")

# CSV header
echo "File,Codec,FFmpeg_Command"

# Find video files recursively
find . -type f \( -iname "*.mp4" -o -iname "*.avi" -o -iname "*.mkv" -o -iname "*.mov" -o -iname "*.wmv" -o -iname "*.flv" -o -iname "*.webm" -o -iname "*.m4v" -o -iname "*.mpg" -o -iname "*.mpeg" -o -iname "*.3gp" -o -iname "*.ogv" \) | while read -r file; do
    # Get codec of first video stream
    codec=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 "$file" 2>/dev/null)
    # Check if codec is not in good list
    if [[ -n "$codec" && ! " ${GOOD_CODECS[@]} " =~ " ${codec} " ]]; then
        # Suggest FFmpeg command to convert to AV1 using SVT-AV1, audio to Opus, output MKV, strip metadata
        output_file="${file%.*}_av1.mkv"
        ffmpeg_cmd="ffmpeg -i '$file' -map_metadata -1 -c:v libsvtav1 -preset 8 -crf 28 -c:a libopus -b:a 128k '$output_file'"
        echo "\"$file\",\"$codec\",\"$ffmpeg_cmd\""
    fi
done