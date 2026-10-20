---
name: voice-clone-narration
description: Clone a consenting speaker's voice from a short reference clip (or from a video/podcast they appear in) and generate sentence-by-sentence narration with F5-TTS, auto-verified by Whisper, with a timing manifest ready for Remotion or any video timeline. Use this whenever the user wants a video, explainer, 科普动画, audiobook or slideshow narrated "in X's voice", wants to reuse/clone a voice, build a voice profile, swap the TTS voice of an existing video, or extract a clean voice sample from a Bilibili/YouTube video — even if they never say "voice cloning" or "F5-TTS".
---

# Voice-clone narration

Turn a script into narration spoken in a specific person's voice:

```
source audio/video ──► vocals (demucs) ──► pick clean segments ──► reference clip + exact transcript  = voice profile
script.json ──► F5-TTS per sentence ──► Whisper check ──► fix & redo ──► manifest.json (text, file, seconds)
```

Everything runs locally. Scripts live in `scripts/` next to this file; call them by absolute path.

## 0. Consent comes first

A cloned voice can make a real person "say" anything, so before building a profile, confirm with the user that the **voice owner agreed to having their voice cloned** for this use. Rights in one's own voice are protected in many places (e.g. Article 1023 of China's Civil Code, US right-of-publicity laws), and the audio itself is usually copyrighted.

- If the user has no consent for a real, identifiable person, offer alternatives: their own voice, a stock TTS voice, or asking the owner.
- Don't help pass the voice off as the real person saying things they didn't say (fake statements, endorsements, scams). Suggest labeling output as "AI 克隆配音 / AI-generated voice".
- Reference clips are personal data. Keep voice profiles out of public repos unless the owner explicitly agreed to public distribution.
- F5-TTS pretrained weights are **CC BY-NC** (non-commercial). For monetized videos (ads, paid content, creator funds), tell the user and point to a commercially licensed model (e.g. CosyVoice).

## 1. Setup (once)

```bash
bash scripts/setup.sh
```

Installs ffmpeg, yt-dlp (Homebrew), and with `uv`: `f5-tts`, `demucs`, and `mlx-whisper` on Apple Silicon (or `openai-whisper` elsewhere). The first F5-TTS run downloads about 1.3 GB of weights. On Macs generation runs on CPU at roughly 30–60 s per sentence, so run big batches in the background.

## 2. Build a voice profile

Skip this if a profile already exists. A profile is a folder containing `voice.json`, `ref.wav` and `ref_text.txt` (template: `assets/voice.template.json`).

**Best source:** ask the speaker for 10–20 s of dry speech with no music, plus its exact transcript. Then just run step 2c on it.

**From a video or podcast** (only with consent):

a. Extract vocals:
```bash
bash scripts/extract_vocals.sh "<url or local file>" <workdir>
```
This writes `<workdir>/orig.wav`, `<workdir>/vocals.wav` and `<workdir>/no_vocals.wav`.

b. Find clean segments:
```bash
python3 scripts/find_segments.py <workdir>
```
It transcribes the vocals and measures how loud the leftover music is under each segment. Pick ranges where `bgm` is about **-45 dB or quieter**: separation artifacts are least audible there. Aim for 8–12 s in total. Two or three contiguous runs are fine. Avoid laughter, shouting, overlapping voices and clips the speaker is quoting.

c. Build the reference clip:
```bash
python3 scripts/build_ref.py <workdir>/vocals.wav <voice_dir> --range 87.35-93.05 --range 310.7-315.4 --name "Speaker"
```
This joins the ranges, converts to mono 24 kHz, normalizes loudness, **adds 0.6 s of trailing silence**, re-transcribes the clip into `ref_text.txt`, and writes `voice.json`.

d. **Proofread `ref_text.txt` against the audio.** Whisper often outputs traditional characters, homophones or a stray leading word (it really may be in the clip). The transcript has to match what is spoken word for word. A mismatch is the most common cause of mumbled or garbled output.

## 3. Generate narration

The script format is JSON: one entry per scene, one line per sentence. Short lines (≤ 30 Chinese characters or ≤ 25 English words) clone more reliably and give natural cut points.

```json
[{"id": "intro", "lines": ["天空为什么是蓝色的？", "太阳光明明是白色的呀。"]}]
```

```bash
~/.local/share/uv/tools/f5-tts/bin/python scripts/gen_lines.py \
  --voice-dir <voice_dir> --script script.json --out-dir public/voice --manifest manifest.json
# redo specific lines only:
...gen_lines.py ... --only intro-1.wav formula-1.wav
```

The manifest lists `{id, lines: [{text, file, seconds}]}`, where `file` is relative to the parent of `--out-dir`. That makes it work directly with Remotion's `staticFile()` when `--out-dir` sits inside `public/`.

## 4. Verify — don't skip this

```bash
python3 scripts/check_lines.py --manifest manifest.json --audio-root public
```

Each line is transcribed again and compared with the script. Lines scoring below 0.85 are printed after `REDO`. Read the flagged ones yourself:

- **Homophones** (瑞利/锐利, 厚/后) are just Whisper mishearing. Ignore them.
- **Dropped syllables** (差不多 → 差多) are real. Fast speakers swallow them, and a new seed usually produces the same result because the duration is estimated from text length. **Reword the line** (差不多 → 大约), regenerate with `--only`, and check again. Update the subtitle text to match, since it comes from the same script.
- **Garbage at the very start** means the reference clip bled into the output. Make sure `ref.wav` ends in silence and `ref_text.txt` ends with a full stop.

You can't judge timbre or naturalness yourself, so tell the user it needs a listen.

## 5. Use the timings

See `references/remotion.md` for turning the manifest into scene durations, per-line `<Audio>` sequences and synced subtitles. A cloned speaker's pace can differ a lot from stock TTS (often 20 % faster), so derive every duration from `seconds` and never hard-code it.
