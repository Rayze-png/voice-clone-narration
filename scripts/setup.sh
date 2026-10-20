#!/usr/bin/env bash
# One-time setup: ffmpeg, yt-dlp, demucs, F5-TTS, Whisper
set -euo pipefail

if command -v brew >/dev/null; then
  brew install ffmpeg yt-dlp uv
else
  echo "Install ffmpeg, yt-dlp and uv with your package manager first." >&2
fi

uv tool install --python 3.11 f5-tts
uv tool install --python 3.11 demucs --with numpy --with soundfile

if [[ "$(uname -s)-$(uname -m)" == "Darwin-arm64" ]]; then
  uv tool install mlx-whisper
else
  uv tool install --python 3.11 openai-whisper
fi

echo "F5-TTS python: $(uv tool dir)/f5-tts/bin/python"
