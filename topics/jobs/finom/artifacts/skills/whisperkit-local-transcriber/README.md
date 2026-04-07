# WhisperKit Local Transcriber

Reusable local-only transcription skill for Apple Silicon Macs using WhisperKit.

## Files
- `SKILL.md` - trigger description and workflow
- `scripts/transcribe_local.sh` - helper script for one file or a folder
- `evals/evals.json` - realistic prompts for testing and trigger tuning

## Default local model path
- `~/Documents/huggingface/models/argmaxinc/whisperkit-coreml/openai_whisper-large-v3`

## Example
```bash
scripts/transcribe_local.sh \
  --audio /path/to/audio.m4a \
  --model-path ~/Documents/huggingface/models/argmaxinc/whisperkit-coreml/openai_whisper-large-v3 \
  --language en \
  --overwrite
```
