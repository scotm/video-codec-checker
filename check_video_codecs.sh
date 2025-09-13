#!/bin/bash

# Script to find video files using codecs less than state-of-the-art (AV1, HEVC, H.264)
# Outputs CSV: File,Codec,FFmpeg_Command
# State-of-the-art: av1, hevc, h264

GOOD_CODECS=("av1" "hevc" "h264")

# Parse command line arguments
OUTPUT_FILE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 [-o output_file]"
            exit 1
            ;;
    esac
done

# Generate default output filename if not provided
if [[ -z "$OUTPUT_FILE" ]]; then
    OUTPUT_FILE="video_codec_check_$(date +%Y%m%d_%H%M%S).csv"
fi

# CSV header
echo "File,Codec,FFmpeg_Command" > "$OUTPUT_FILE"

# Find video files recursively
find . -type f \( -iname "*.mp4" -o -iname "*.avi" -o -iname "*.mkv" -o -iname "*.mov" -o -iname "*.wmv" -o -iname "*.flv" -o -iname "*.webm" -o -iname "*.m4v" -o -iname "*.mpg" -o -iname "*.mpeg" -o -iname "*.3gp" -o -iname "*.ogv" \) -print0 | while IFS= read -r -d '' file; do
    # Get absolute path
    abs_file=$(realpath "$file")
    # Get codec and audio channels in single ffprobe call for efficiency
    # Use optimized flags: reduced probesize/analyzeduration for faster scanning
    probe_output=$(ffprobe -v quiet -probesize 100000 -analyzeduration 1000000 -fflags +fastseek+discardcorrupt -select_streams v:0 -show_entries stream=codec_name -select_streams a:0 -show_entries stream=channels -of default=noprint_wrappers=1:nokey=1 "$file" 2>/dev/null)
    # Parse the output: first line is codec, second line is channels (if audio exists)
    codec=$(echo "$probe_output" | head -n1)
    channels=$(echo "$probe_output" | sed -n '2p')
    # Check if codec is not in good list
    if [[ -n "$codec" && ! " ${GOOD_CODECS[@]} " =~ " ${codec} " ]]; then
        # Suggest FFmpeg command to convert to AV1 using SVT-AV1, audio to Opus, output MKV, strip metadata
        output_file="${abs_file%.*}_av1.mkv"
        # Set Opus bitrate based on audio channels: adaptive for quality
        if [[ "$channels" == "1" ]]; then
            audio_bitrate="48k"  # Mono
        elif [[ "$channels" == "2" ]]; then
            audio_bitrate="128k" # Stereo
        elif [[ "$channels" -ge "3" && "$channels" -le "6" ]]; then
            audio_bitrate="256k" # 5.1 surround
        else
            audio_bitrate="320k" # 7.1 or higher
        fi
        ffmpeg_cmd="ffmpeg -i '$abs_file' -map_metadata -1 -c:v libsvtav1 -preset 4 -crf 32 -c:a libopus -b:a $audio_bitrate '$output_file'"
        echo "\"$file\",\"$codec\",\"$ffmpeg_cmd\"" >> "$OUTPUT_FILE"
        echo "Processed: $file" >&2
    fi
done

echo "Results written to: $OUTPUT_FILE" >&2
