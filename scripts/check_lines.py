"""Re-transcribe every generated line and flag ones that don't match the script.

Usage: python3 check_lines.py --manifest manifest.json --audio-root public [--threshold 0.85]
Prints a score per line and a final "REDO <files>" list for gen_lines.py --only.
"""
import argparse, difflib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from whisper_util import transcribe

ap = argparse.ArgumentParser()
ap.add_argument('--manifest', required=True)
ap.add_argument('--audio-root', required=True)
ap.add_argument('--threshold', type=float, default=0.85)
ap.add_argument('--language', default='zh')
args = ap.parse_args()

# Whisper writes numbers as digits (29) while scripts often spell them out (二十九): ignore numerals on both sides
NUMERALS = r'[0-9零〇一二两三四五六七八九十百千万亿.%]'
norm = lambda s: re.sub(NUMERALS, '', re.sub(r'[^\w]', '', s)).lower()
redo = []
for scene in json.loads(Path(args.manifest).read_text()):
    for line in scene['lines']:
        wav = Path(args.audio_root) / line['file']
        heard = transcribe(wav, args.language)['text'].strip()
        score = difflib.SequenceMatcher(None, norm(line['text']), norm(heard)).ratio()
        ok = score >= args.threshold
        if not ok:
            redo.append(wav.name)
        print(f"{'OK ' if ok else 'BAD'} {score:.2f} {wav.name}  heard: {heard}")
print('REDO', ' '.join(redo))
