#!/usr/bin/env bash
set -euo pipefail

hri_models="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)/models"
mkdir -p "$hri_models"

if [[ "${1:-}" != --tts-only && ! -f "$hri_models/vosk-model-es-0.42/.download-complete" ]]; then
    echo "Descargando el modelo completo de español (aproximadamente 1,4 GB)..."
    curl --fail --location --retry 3 --connect-timeout 20 --continue-at - \
        https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip \
        --output "$hri_models/vosk-model-es-0.42.zip.part"
    mv -- "$hri_models/vosk-model-es-0.42.zip.part" \
        "$hri_models/vosk-model-es-0.42.zip"
    unzip -q -o "$hri_models/vosk-model-es-0.42.zip" -d "$hri_models"
    touch "$hri_models/vosk-model-es-0.42/.download-complete"
fi

if [[ ! -f "$hri_models/es_ES-davefx-medium.onnx" ||
      ! -f "$hri_models/es_ES-davefx-medium.onnx.json" ]]; then
    echo "Descargando la voz en español..."
    python -m piper.download_voices es_ES-davefx-medium --download-dir "$hri_models"
fi

echo "Modelos de voz preparados en $hri_models"
