"""Rank speech segments by how little background music remains under them.

Usage: python3 find_segments.py <workdir> [--language zh]
Needs <workdir>/vocals.wav and no_vocals.wav from extract_vocals.sh.
"""
import argparse, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from whisper_util import transcribe


def mean_db(path, start, dur):
    err = subprocess.run(['ffmpeg', '-v', 'info', '-ss', f'{start}', '-t', f'{dur}', '-i', str(path),
                          '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    for line in err.splitlines():
        if 'mean_volume' in line:
            return float(line.split(':')[1].split()[0])
    return 0.0


ap = argparse.ArgumentParser()
ap.add_argument('workdir')
ap.add_argument('--language', default='zh')
ap.add_argument('--clean-db', type=float, default=-45.0, help='bgm level counted as clean')
args = ap.parse_args()
work = Path(args.workdir)

segs = transcribe(work / 'vocals.wav', args.language)['segments']
rows = []
for s in segs:
    dur = s['end'] - s['start']
    rows.append((s['start'], s['end'], dur, mean_db(work / 'no_vocals.wav', s['start'], dur), s['text'].strip()))
    print(f"{s['start']:8.2f}-{s['end']:8.2f} {dur:5.2f}s bgm={rows[-1][3]:6.1f}dB  {rows[-1][4]}")

# Merge adjacent clean segments (gap < 0.8 s) into candidate runs
runs, cur = [], None
for start, end, dur, db, text in rows:
    if db <= args.clean_db:
        if cur and start - cur[1] < 0.8:
            cur = [cur[0], end, cur[2] + text]
        else:
            cur and runs.append(cur)
            cur = [start, end, text]
    else:
        cur and runs.append(cur)
        cur = None
cur and runs.append(cur)

print(f'\nClean runs (bgm <= {args.clean_db} dB), longest first — pad each by ~0.15 s when building the ref:')
for start, end, text in sorted(runs, key=lambda r: r[0] - r[1]):
    print(f'  --range {start:.2f}-{end:.2f}   ({end - start:.1f}s)  {text}')
