---
name: whisperkit-local-transcriber
description: Create local-only source records from audio files using WhisperKit on Apple Silicon. Use this whenever the user wants to transcribe `.m4a`, `.mp3`, `.wav`, or similar audio locally, wants to avoid cloud APIs, wants WhisperKit or Apple Silicon optimized capture, wants to overwrite or refresh source record text files next to audio files, or asks how to batch-transcribe a folder of captured materials. This skill should also trigger when the user cares about offline capture, cached local models, NotebookLM audio exports, interview captured materials, or converting audio into `.txt` files for later analysis.
---

# WhisperKit Local Transcriber

Use this skill to transcribe audio with `WhisperKit` while keeping inference local to the machine.

## What this skill does

- Uses `whisperkit-cli` instead of remote speech APIs.
- Prefers cached local models via `--model-path` so capture can run fully offline after the model exists.
- Writes plain `.txt` source records next to the source audio unless the user asks for another location.
- Preserves the user's naming scheme and only overwrites source records when the user explicitly asks.
- Uses a helper script so the source record extraction is consistent and not reimplemented every time.

## When to use which mode

### Mode 1: strict local-only
Use this when the user says `local only`, `offline`, `no API`, or anything equivalent.

Requirements:
- `whisperkit-cli` must already be installed.
- A local model folder must already exist.

Default model path:
- `~/Documents/huggingface/models/argmaxinc/whisperkit-coreml/openai_whisper-large-v3`

Run with `--model-path` in this mode. Do not use `--model` unless the user explicitly allows an initial download.

### Mode 2: local inference with one-time model fetch
Use this when the user wants WhisperKit but has not cached a model yet.

- Explain that audio stays local during capture.
- Explain that the model may need a one-time download.
- After the download, recommend switching to `--model-path` for future runs.

## Default decisions

- Prefer `large-v3` for source record quality.
- Prefer `--language en` when the audio is clearly English; otherwise omit language unless the user specifies it.
- Prefer `--without-timestamps` for clean reading source records.
- Write one `.txt` file per input audio with the same basename.
- If the user wants timestamps or diarization, add them only when asked.

## Workflow

1. Confirm whether the user wants strict offline behavior or allows a one-time model download.
2. Check that `whisperkit-cli` exists.
3. Check whether the local model directory exists.
4. If the model exists, use `--model-path`.
5. If the model does not exist and strict local-only is required, stop and tell the user what model path is missing.
6. If the model does not exist and download is allowed, use `--model large-v3` once, then tell the user where it was cached.
7. Use the bundled script to transcribe one file or a folder.
8. Store `.txt` outputs next to the audio files unless the user asks otherwise.
9. Report what was written, what model was used, and whether the run was fully offline.

## Commands

### Single file, strict local-only
```bash
scripts/transcribe_local.sh \
  --audio /path/to/audio.m4a \
  --model-path ~/Documents/huggingface/models/argmaxinc/whisperkit-coreml/openai_whisper-large-v3
```

### Batch folder, strict local-only
```bash
scripts/transcribe_local.sh \
  --audio-folder /path/to/folder \
  --model-path ~/Documents/huggingface/models/argmaxinc/whisperkit-coreml/openai_whisper-large-v3
```

### One-time model download, then local inference
```bash
/opt/homebrew/bin/whisperkit-cli transcribe \
  --audio-path /path/to/audio.m4a \
  --model large-v3 \
  --language en \
  --without-timestamps
```

## Output contract

When you use this skill, report back with:
- the files transcribed
- the source record files written
- whether existing source records were overwritten
- whether the run used `--model-path` and was fully offline
- any missing prerequisites

## Guardrails

- Do not claim `fully local` if the run used `--model` and had to fetch a model.
- Do not silently overwrite source records unless the user asked for overwrite or replacement.
- Do not switch to OpenAI Whisper API or any hosted capture service as a fallback.
- Do not assume `turbo` naming from stock Whisper maps directly to WhisperKit; prefer working WhisperKit model names.
- If `large-v3` is too slow and the user explicitly wants speed over quality, explain the tradeoff before choosing a smaller or distilled model.

## Notes for Apple Silicon

- `WhisperKit` runs inference locally through Apple-optimized model execution.
- On first use, model initialization can take noticeable time.
- Subsequent runs are typically smoother once the model is cached.

## Bundled script

Use `scripts/transcribe_local.sh` for repeatable execution. It:
- supports one file or a full folder
- extracts only the source record body from WhisperKit CLI output
- writes `.txt` next to each audio file
- can overwrite existing source records when `--overwrite` is provided

