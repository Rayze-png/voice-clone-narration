#!/usr/bin/env bash
# Usage: extract_vocals.sh <url-or-audio/video-file> <workdir>
# Produces <workdir>/orig.wav, vocals.wav, no_vocals.wav
set -euo pipefail
src="$1"; work="$2"
mkdir -p "$work"

if [[ "$src" =~ ^https?:// ]]; then
  yt-dlp -f bestaudio -x --audio-format wav --no-playlist -o "$work/orig.%(ext)s" "$src"
else
  ffmpeg -v error -y -i "$src" -vn "$work/orig.wav"
fi

device=cpu
[[ "$(uname -s)-$(uname -m)" == "Darwin-arm64" ]] && device=mps
demucs --two-stems=vocals -n htdemucs -d "$device" -o "$work/sep" "$work/orig.wav"
mv "$work/sep/htdemucs/orig/vocals.wav" "$work/sep/htdemucs/orig/no_vocals.wav" "$work/"
rm -rf "$work/sep"
echo "Vocals: $work/vocals.wav"
