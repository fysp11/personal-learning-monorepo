#!/bin/zsh
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  transcribe_local.sh --audio <file> --model-path <dir> [--language <code>] [--overwrite]
  transcribe_local.sh --audio-folder <dir> --model-path <dir> [--language <code>] [--overwrite]

Notes:
- Uses WhisperKit locally with an already-downloaded model.
- Writes .txt source records next to each audio file.
- Refuses to overwrite existing source records unless --overwrite is set.
USAGE
}

audio_file=""
audio_folder=""
model_path=""
language=""
overwrite=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --audio)
      audio_file="$2"
      shift 2
      ;;
    --audio-folder)
      audio_folder="$2"
      shift 2
      ;;
    --model-path)
      model_path="$2"
      shift 2
      ;;
    --language)
      language="$2"
      shift 2
      ;;
    --overwrite)
      overwrite=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$model_path" ]]; then
  echo "Missing required --model-path" >&2
  exit 1
fi

if [[ ! -d "$model_path" ]]; then
  echo "Model path does not exist: $model_path" >&2
  exit 1
fi

if [[ -z "$audio_file" && -z "$audio_folder" ]]; then
  echo "Provide --audio or --audio-folder" >&2
  exit 1
fi

if [[ -n "$audio_file" && -n "$audio_folder" ]]; then
  echo "Use either --audio or --audio-folder, not both" >&2
  exit 1
fi

if ! command -v /opt/homebrew/bin/whisperkit-cli >/dev/null 2>&1; then
  echo "whisperkit-cli not found at /opt/homebrew/bin/whisperkit-cli" >&2
  exit 1
fi

transcribe_one() {
  local source_file="$1"
  local output_file="${source_file%.*}.txt"
  local tmp_file
  tmp_file="$(mktemp)"

  if [[ -f "$output_file" && "$overwrite" -ne 1 ]]; then
    echo "Skipping existing source record: $output_file" >&2
    rm -f "$tmp_file"
    return 0
  fi

  local -a cmd
  cmd=(/opt/homebrew/bin/whisperkit-cli transcribe --audio-path "$source_file" --model-path "$model_path" --without-timestamps)

  if [[ -n "$language" ]]; then
    cmd+=(--language "$language")
  fi

  "${cmd[@]}" > "$tmp_file"

  perl -pe 's/\e\[[0-9;]*[[:alpha:]]//g' "$tmp_file" \
    | awk 'found { print } /^Capture of .*: *$/ { found=1; next }' \
    | sed '1{/^[[:space:]]*$/d;}' > "$output_file"

  rm -f "$tmp_file"
  echo "Wrote $output_file"
}

if [[ -n "$audio_file" ]]; then
  transcribe_one "$audio_file"
else
  while IFS= read -r source_file; do
    transcribe_one "$source_file"
  done < <(find "$audio_folder" -maxdepth 1 -type f \( -iname '*.m4a' -o -iname '*.mp3' -o -iname '*.wav' -o -iname '*.aac' -o -iname '*.flac' \) | sort)
fi
