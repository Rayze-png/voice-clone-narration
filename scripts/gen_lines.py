"""Generate one audio file per script line in a cloned voice (run with the f5-tts tool's python).

Usage:
  python gen_lines.py --voice-dir voices/alice --script script.json --out-dir public/voice --manifest manifest.json [--only a-0.wav b-1.wav]
script.json: [{"id": "intro", "lines": ["sentence", ...]}, ...]
manifest:    [{"id", "lines": [{"text", "file", "seconds"}]}], file relative to out-dir's parent.
"""
import argparse, json, random, subprocess
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--voice-dir', required=True)
ap.add_argument('--script', required=True)
ap.add_argument('--out-dir', required=True)
ap.add_argument('--manifest', required=True)
ap.add_argument('--only', nargs='*', default=[])
ap.add_argument('--speed', type=float, default=1.0)
args = ap.parse_args()

voice = Path(args.voice_dir)
profile = json.loads((voice / 'voice.json').read_text())
ref = str(voice / profile['ref_audio'])
ref_text = (voice / profile['ref_text_file']).read_text().strip()
out = Path(args.out_dir)
out.mkdir(parents=True, exist_ok=True)
scenes = json.loads(Path(args.script).read_text())

from f5_tts.api import F5TTS  # imported late: slow to load
tts = F5TTS(model=profile.get('model', 'F5TTS_v1_Base'))

manifest = []
for scene in scenes:
    lines = []
    for i, text in enumerate(scene['lines']):
        path = out / f"{scene['id']}-{i}.wav"
        if not args.only or path.name in args.only or not path.exists():
            tts.infer(ref_file=ref, ref_text=ref_text, gen_text=text, file_wave=str(path),
                      speed=args.speed, seed=random.randint(0, 2**31), show_info=lambda *a: None)
        seconds = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)]))
        print(f'{path.name} {seconds:.2f}s {text}', flush=True)
        lines.append({'text': text, 'file': f'{out.name}/{path.name}', 'seconds': seconds})
    manifest.append({'id': scene['id'], 'lines': lines})

Path(args.manifest).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
