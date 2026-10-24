#!/usr/bin/env bash
set -e

hri_package="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
hri_workspace="$(dirname -- "$hri_package")"

# Use the desktop ALSA configuration and PipeWire plugins with Pixi's PortAudio.
if [[ -f /usr/share/alsa/alsa.conf ]]; then
    export ALSA_CONFIG_PATH="${ALSA_CONFIG_PATH:-/usr/share/alsa/alsa.conf}"
    if [[ -z "${ALSA_PLUGIN_DIR:-}" ]]; then
        for hri_alsa_dir in /usr/lib/*/alsa-lib /usr/lib64/alsa-lib /usr/lib/alsa-lib; do
            if [[ -d "$hri_alsa_dir" ]]; then
                export ALSA_PLUGIN_DIR="$hri_alsa_dir"
                break
            fi
        done
    fi
fi

if [[ "${1:-}" == --listar-microfonos ]]; then
    exec python -m sounddevice
fi

source "$hri_workspace/install/setup.bash"

hri_interface=false
hri_args=()
for hri_arg in "$@"; do
    case "$hri_arg" in
        --interface) hri_interface=true ;;
        --keyboard)
            echo 'El modo teclado se ha eliminado. Usa --interface para elegir el pedido en la ventana.' >&2
            exit 2 ;;
        *) hri_args+=("$hri_arg") ;;
    esac
done

exec ros2 launch binary_tree waiter_behavior.py \
    "interface:=$hri_interface" \
    "preparar_modelos:=$hri_package/scripts/prepare_models.sh" \
    "modelo:=$hri_package/models/vosk-model-es-0.42" \
    "voz:=$hri_package/models/es_ES-davefx-medium.onnx" "${hri_args[@]}"
