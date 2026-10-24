#!/usr/bin/env bash
set -e

gui_package="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
gui_workspace="$(dirname -- "$gui_package")"
source "$gui_workspace/install/setup.bash"

if [[ "${1:-}" == --test ]]; then
    shift
    export QT_QPA_PLATFORM=offscreen
    exec python "$gui_package/test/gui/run_tests.py" "$@"
fi

exec bash "$gui_package/scripts/run_voice.sh" --interface "$@"
