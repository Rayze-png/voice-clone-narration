"""Shared Whisper helper: mlx-whisper on Apple Silicon, openai-whisper elsewhere."""
import json, shutil, subprocess, tempfile
from pathlib import Path

PROMPT = {'zh': '以下是普通话的句子，使用简体中文。'}


def transcribe(audio, language='zh'):
    """Return Whisper's JSON result ({'text', 'segments'}) for one file."""
    audio = Path(audio)
    with tempfile.TemporaryDirectory() as out:
        if shutil.which('mlx_whisper'):
            cmd = ['mlx_whisper', str(audio), '--model', 'mlx-community/whisper-large-v3-turbo']
        elif shutil.which('whisper'):
            cmd = ['whisper', str(audio), '--model', 'turbo']
        else:
            raise SystemExit('No Whisper found — run scripts/setup.sh')
        cmd += ['--language', language, '--output-format', 'json', '--output-dir', out, '--verbose', 'False']
        if language in PROMPT:
            cmd += ['--initial-prompt', PROMPT[language]]
        subprocess.run(cmd, check=True, capture_output=True)
        return json.loads((Path(out) / f'{audio.stem}.json').read_text())
