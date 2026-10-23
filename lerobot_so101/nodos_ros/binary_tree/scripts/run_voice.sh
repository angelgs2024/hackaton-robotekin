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

hri_keyboard=false
hri_args=()
for hri_arg in "$@"; do
    if [[ "$hri_arg" == --keyboard ]]; then
        hri_keyboard=true
    else
        hri_args+=("$hri_arg")
    fi
done

if "$hri_keyboard"; then
    # Keep Piper speaking normally; keyboard input does not need the Vosk model.
    bash "$hri_package/scripts/prepare_models.sh" --tts-only
    hri_executables="$(ros2 pkg prefix binary_tree)/lib/binary_tree"
    hri_pids=()
    limpiar() {
        trap - EXIT INT TERM
        if ((${#hri_pids[@]})); then
            kill "${hri_pids[@]}" 2>/dev/null || true
            wait "${hri_pids[@]}" 2>/dev/null || true
        fi
    }
    trap limpiar EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM

    echo 'Escucha al robot. Cuando aparezca 🧑, escribe el pedido y pulsa Enter; confirma con «sí».'
    ros2 launch binary_tree waiter_behavior.py \
        "voz:=$hri_package/models/es_ES-davefx-medium.onnx" \
        "${hri_args[@]}" escucha_externa:=true &
    hri_pids+=("$!")
    # ros2 launch does not forward stdin to input(): run escucha directly.
    "$hri_executables/escucha" --ros-args -p modo:=teclado <&0 &
    hri_pids+=("$!")

    hri_status=0
    wait -n "${hri_pids[@]}" || hri_status=$?
    exit "$hri_status"
fi

bash "$hri_package/scripts/prepare_models.sh"
echo 'Habla cuando aparezca «🎤 escuchando...». Confirma el pedido diciendo «sí».'
exec ros2 launch binary_tree waiter_behavior.py \
    "modelo:=$hri_package/models/vosk-model-es-0.42" \
    "voz:=$hri_package/models/es_ES-davefx-medium.onnx" "${hri_args[@]}"
