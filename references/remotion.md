# Using the manifest in Remotion

Put generated audio under `public/` (for example `--out-dir public/voice`), so that `file` in the manifest works directly with `staticFile()`.

```ts
// timeline.ts — turn per-line seconds into frame offsets
import manifest from './manifest.json';

export const FPS = 30;
const LEAD = 0.4, GAP = 0.35, TAIL = 0.7; // seconds
const f = (s: number) => Math.round(s * FPS);

export const scenes = manifest.map((scene) => {
  let cursor = f(LEAD);
  const lines = scene.lines.map((l) => {
    const line = {text: l.text, file: l.file, from: cursor, frames: f(l.seconds)};
    cursor += line.frames + f(GAP);
    return line;
  });
  return {id: scene.id, lines, duration: cursor - f(GAP) + f(TAIL)};
});
```

Inside each scene, play each line in its own `<Sequence from={line.from}>` with `<Html5Audio src={staticFile(line.file)} />` (or `<Audio>`, depending on your Remotion version). Show the subtitle whose `[from, from + frames)` contains the current frame. Start each animation beat at `lines[i].from`, so visuals stay in sync even after you change the voice or the wording.

If you use `TransitionSeries`, subtract the transition overlap from the total duration. Keep `TAIL` longer than the transition, so that the overlap falls on silence and doesn't cut into speech.
