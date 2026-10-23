#!/bin/bash
# Lanza los 3 nodos y empieza la conversación. Uso: bash hri.sh [voz|teclado]
set -e
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

# En Linux, el ALSA de Pixi no incluye los plugins de PipeWire del sistema.
# Usar la configuración del escritorio permite acceder al micro y altavoz
# predeterminados y convertir sus frecuencias de muestreo.
if [[ "$(uname -s)" == Linux && -f /usr/share/alsa/alsa.conf ]]; then
    export ALSA_CONFIG_PATH="${ALSA_CONFIG_PATH:-/usr/share/alsa/alsa.conf}"
    if [[ -z "${ALSA_PLUGIN_DIR:-}" ]]; then
        for directorio in /usr/lib/*/alsa-lib /usr/lib64/alsa-lib /usr/lib/alsa-lib; do
            if [[ -d "$directorio" ]]; then
                export ALSA_PLUGIN_DIR="$directorio"
                break
            fi
        done
    fi
fi

source install/setup.bash

# Ejecutar los nodos directamente: matar el wrapper «ros2 run» dejaba
# sus procesos Python vivos, que recibían las preguntas de la siguiente sesión.
nodos="$(ros2 pkg prefix hri)/lib/hri"
pids=()
limpiar() {
    trap - EXIT INT TERM
    if ((${#pids[@]})); then
        kill "${pids[@]}" 2>/dev/null || true
        wait "${pids[@]}" 2>/dev/null || true
    fi
}
trap limpiar EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

"$nodos/pregunta" &
pids+=("$!")
"$nodos/confirma" &
pids+=("$!")
(sleep 3 && ros2 topic pub --once /hri/empezar std_msgs/msg/Empty > /dev/null) &
pids+=("$!")
"$nodos/escucha" --ros-args -p modo:="${1:-voz}" <&0 &
escucha_pid=$!
pids+=("$escucha_pid")
wait "$escucha_pid"
