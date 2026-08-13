#!/bin/bash -e

# Build and run SR0WX in a container.
# Any arguments given here are passed straight to sr0wx.py, e.g.:
#   ./run-docker.sh -t -m sun_rise_set

cd "$(dirname "$(realpath "$0")")"

if [ ! -f .env ]; then
    echo "No .env file. Copy .env.example to .env and fill it in first." >&2
    exit 1
fi

# pl_google needs the pyliczba submodule, an empty directory breaks the import
git submodule update --init --recursive

docker build \
    --build-arg UID="$(id -u)" \
    --build-arg GID="$(id -g)" \
    -t sr0wx:latest .

mkdir -p logs

ARGS=(
    --rm
    --env-file .env
    -v "$(pwd)/logs:/home/sr0wx/sr0wx/logs"
)

# interactive only when there is a terminal, so cron/systemd runs work too
if [ -t 0 ]; then
    ARGS+=(-it)
fi

# audio via the host PulseAudio daemon
if [ -n "${XDG_RUNTIME_DIR}" ] && [ -S "${XDG_RUNTIME_DIR}/pulse/native" ]; then
    ARGS+=(
        -e "PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native"
        -v "${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native"
    )
else
    echo "Warning: no PulseAudio socket found, there will be no audio output." >&2
fi

# the cookie lives in the container user's home, not in /root
if [ -f "${HOME}/.config/pulse/cookie" ]; then
    ARGS+=(-v "${HOME}/.config/pulse/cookie:/home/sr0wx/.config/pulse/cookie:ro")
fi

# PTT via Raspberry Pi GPIO
if [ -e /dev/gpiomem ]; then
    ARGS+=(--device /dev/gpiomem)
fi

# PTT via serial, set SR0WX_SERIAL to the device path (e.g. /dev/ttyUSB0)
if [ -n "${SR0WX_SERIAL}" ]; then
    if [ -e "${SR0WX_SERIAL}" ]; then
        ARGS+=(--device "${SR0WX_SERIAL}")
    else
        echo "Warning: SR0WX_SERIAL=${SR0WX_SERIAL} does not exist, skipping." >&2
    fi
fi

docker run "${ARGS[@]}" sr0wx:latest "$@"
