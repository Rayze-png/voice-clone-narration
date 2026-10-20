"""Build a voice profile from one or more time ranges of a clean vocals file.

Usage: python3 build_ref.py vocals.wav <voice_dir> --range 87.35-93.05 [--range 310.7-315.4] --name "Speaker"
Writes ref.wav (mono 24 kHz, loudness-normalized, 0.6 s trailing silence), ref_text.txt and voice.json.
Proofread ref_text.txt afterwards — it must match the audio word for word.
"""
import argparse, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from whisper_util import transcribe

ap = argparse.ArgumentParser()
ap.add_argument('vocals')
ap.add_argument('voice_dir')
ap.add_argument('--range', action='append', required=True, dest='ranges')
ap.add_argument('--name', default='Speaker')
ap.add_argument('--language', default='zh')
ap.add_argument('--source', default='')
args = ap.parse_args()

out = Path(args.voice_dir)
out.mkdir(parents=True, exist_ok=True)
parts, labels = [], []
for i, r in enumerate(args.ranges):
    a, b = r.split('-')
    parts.append(f'[0]atrim={a}:{b},asetpts=N/SR/TB,pan=mono|c0=c0,aresample=24000[p{i}]')
    labels.append(f'[p{i}]')
    if i < len(args.ranges) - 1:
        parts.append(f'anullsrc=r=24000:cl=mono,atrim=0:0.35[g{i}]')
        labels.append(f'[g{i}]')
graph = ';'.join(parts) + ';' + ''.join(labels) + f'concat=n={len(labels)}:v=0:a=1,loudnorm=I=-18:TP=-2,aresample=24000,apad=pad_dur=0.6'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', args.vocals, '-filter_complex', graph, '-ac', '1', str(out / 'ref.wav')], check=True)

text = transcribe(out / 'ref.wav', args.language)['text'].strip()
if text and text[-1] not in '。！？.!?':
    text += '。' if args.language == 'zh' else '.'
(out / 'ref_text.txt').write_text(text + '\n')

template = json.loads((Path(__file__).parent.parent / 'assets/voice.template.json').read_text())
template.update(name=args.name, source=args.source or f'{args.vocals} {args.ranges}')
if not (out / 'voice.json').exists():
    (out / 'voice.json').write_text(json.dumps(template, ensure_ascii=False, indent=2) + '\n')

dur = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(out / 'ref.wav')])
print(f'ref.wav {float(dur):.1f}s\nref_text: {text}\nNow proofread {out / "ref_text.txt"} and fill in "consent" in voice.json.')
