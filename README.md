# voice-clone-narration

A [Claude Code](https://claude.com/claude-code) skill that turns a script into narration in a **consenting speaker's** cloned voice. Everything runs locally:

1. **Extract** vocals from a video or podcast with yt-dlp and demucs, or start from a clean recording.
2. **Pick** the cleanest stretches of speech automatically, ranked by how much background music is left under them.
3. **Build** a reusable voice profile: a reference clip plus its exact transcript.
4. **Generate** one audio file per sentence with [F5-TTS](https://github.com/SWivid/F5-TTS).
5. **Verify** every line with Whisper and flag dropped or garbled words for regeneration.
6. **Export** a timing manifest (`text`, `file`, `seconds`) that drives scene timing and subtitles in Remotion or any editor.

Built for Chinese science-explainer videos (科普动画). The pipeline itself works for any language F5-TTS supports.

## Install

```bash
git clone https://github.com/<you>/voice-clone-narration ~/.claude/skills/voice-clone-narration
bash ~/.claude/skills/voice-clone-narration/scripts/setup.sh
```

Then ask Claude something like *"用我授权的声音给这个视频配音"* or *"build a voice profile from my podcast episode and narrate script.json"*.

## No voices included

This repo contains **no voice samples**. Bring your own voice profile (see `assets/voice.template.json`) and keep it out of public repos. The `.gitignore` already excludes audio files and `voices/`.

## Responsible use

- Only clone a voice whose owner has agreed to it. Many jurisdictions protect a person's voice (for example Article 1023 of China's Civil Code and US right-of-publicity laws).
- Label output as AI-generated (AI 克隆配音). Never use it to impersonate someone or make them appear to say things they didn't.
- F5-TTS pretrained weights are **CC BY-NC**, so they are for non-commercial use only. For monetized content, switch to a commercially licensed model.

## License

The scripts and instructions in this repo are MIT-licensed. Third-party tools and model weights keep their own licenses.
