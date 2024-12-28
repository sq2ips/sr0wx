docker build -t sr0wx:latest .
docker run -it \
 -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
 -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native \
 -v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
 sr0wx:latest