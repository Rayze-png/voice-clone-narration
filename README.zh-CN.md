# voice-clone-narration

[English](README.md) | 简体中文

这是一个 [Claude Code](https://claude.com/claude-code) skill：拿到声音本人同意后，克隆他的声音，把文稿配成旁白。整个流程都在本机运行：

1. **提取人声**：用 yt-dlp 和 demucs 从视频或播客里分离出人声，也可以直接用一段干净的录音。
2. **挑选片段**：自动给各段讲话打分，背景音乐残留越少排得越靠前。
3. **建立音色包**：参考音频加上和它逐字对应的文本，以后可以反复使用。
4. **逐句生成**：用 [F5-TTS](https://github.com/SWivid/F5-TTS) 给每句文稿单独生成一个配音文件。
5. **自动检查**：用 Whisper 回听每一句，找出吞字、念错的句子，方便重新生成。
6. **输出时间轴**：生成一份清单，记录每句的文本、文件和时长，可以直接驱动 Remotion 或其他剪辑软件里的分镜时长和字幕。

这个流程最初是为中文科普动画做的，F5-TTS 支持的其他语言也能用。

## 安装

```bash
git clone https://github.com/Rayze-png/voice-clone-narration ~/.claude/skills/voice-clone-narration
bash ~/.claude/skills/voice-clone-narration/scripts/setup.sh
```

`setup.sh` 会安装 ffmpeg、yt-dlp、demucs、F5-TTS 和 Whisper。Apple 芯片的 Mac 装的是 mlx-whisper，其他电脑装的是 openai-whisper。第一次生成配音时会下载约 1.3 GB 的模型。

装好后，在 Claude Code 里直接说你要做什么就行，比如：

- 「用我授权的声音给这个视频配音」
- 「从这期播客里提取主播的声音，做成音色包」
- 「把 script.json 里的文稿用这个音色配出来，再检查一遍有没有念错」

## 使用流程

| 步骤 | 脚本 | 做什么 |
|---|---|---|
| 准备 | `scripts/setup.sh` | 一次性安装所有依赖 |
| 提取 | `scripts/extract_vocals.sh <链接或文件> <工作目录>` | 下载或读取音频，分离人声和背景音乐 |
| 挑选 | `scripts/find_segments.py <工作目录>` | 转写人声，列出背景最干净的连续片段 |
| 建音色 | `scripts/build_ref.py vocals.wav <音色目录> --range 起-止 ...` | 拼接片段、统一音量、末尾加静音，生成参考音频和文本 |
| 生成 | `scripts/gen_lines.py --voice-dir ... --script ... --out-dir ... --manifest ...` | 逐句克隆配音，用 `--only` 可以只重做某几句 |
| 检查 | `scripts/check_lines.py --manifest ... --audio-root ...` | 回听比对文稿，列出需要重做的句子 |

文稿格式是一个 JSON：每个场景一项，每句话一行。

```json
[{"id": "intro", "lines": ["天空为什么是蓝色的？", "太阳光明明是白色的呀。"]}]
```

## 经验总结

- **参考音频文本必须逐字对应**：Whisper 转出来的常有繁体字、同音字，开头还可能多一个字，一定要对照音频校对。文本对不上，是生成结果含糊不清最常见的原因。
- **参考音频末尾要留静音**：不留的话，参考音频的尾音会混进生成内容的开头，`build_ref.py` 已经自动加了 0.6 秒。
- **挑背景音乐残留在 -45 dB 以下的片段**，总长 8～12 秒最合适。
- **语速快的人会吞字**，比如把「差不多」读成「差多」。重新生成往往还是一样，因为时长是按字数估算的，把措辞改掉（比如改成「大约」）就好了。
- **只是同音字的不用管**：比如「瑞利」被识别成「锐利」，这是识别的问题，配音本身没错。
- **时长全部用清单里的 `seconds`**：克隆音色的语速可能比普通 TTS 快两成左右，不要在动画里写死时长。

Remotion 怎么接入，见 [`references/remotion.md`](references/remotion.md)。

## 不含任何声音

仓库里**没有任何声音样本**。请用你自己的音色包（模板见 `assets/voice.template.json`），也不要把音色包放进公开仓库。`.gitignore` 已经排除了音频文件和 `voices/` 目录。

## 负责任地使用

- **只克隆本人同意的声音。** 很多地方的法律都保护个人的声音，比如《民法典》第 1023 条，以及美国的公开权法律。授权最好写明允许 AI 克隆和具体用途，并留下书面记录。
- **标注 AI 生成。** 发布时注明「AI 克隆配音，已获授权」。不要用它冒充本人，也不要让本人「说」他没说过的话。
- **F5-TTS 预训练模型是 CC BY-NC 许可，只能用于非商业用途。** 视频要接广告、做付费内容或参加平台创作激励时，请换用允许商用的模型（比如 CosyVoice）。

## 许可证

本仓库的脚本和说明采用 MIT 许可证。用到的第三方工具和模型权重，以它们各自的许可证为准。
