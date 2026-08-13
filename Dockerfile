# Dockerfile for SR0WX
FROM debian:12

# UID/GID of the host user, so that the mounted logs directory and the
# PulseAudio socket stay writable from inside the container
ARG UID=1000
ARG GID=1000

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv pulseaudio \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd -g ${GID} sr0wx \
 && useradd --create-home --shell /bin/bash -u ${UID} -g ${GID} -G audio,dialout sr0wx

USER sr0wx
WORKDIR /home/sr0wx/sr0wx

RUN mkdir -p logs cache

# requirements first, so that a code change does not invalidate the
# (slow) dependency layer
COPY --chown=sr0wx:sr0wx requirements.txt ./
RUN python3 -m venv wxenv \
 && ./wxenv/bin/pip install --no-cache-dir --upgrade pip \
 && ./wxenv/bin/pip install --no-cache-dir -r requirements.txt

COPY --chown=sr0wx:sr0wx sr0wx.py config.py colorcodes.py sr0wx_module.py ./
COPY --chown=sr0wx:sr0wx modules/ ./modules/
COPY --chown=sr0wx:sr0wx pl_google/ ./pl_google/
COPY --chown=sr0wx:sr0wx pyliczba/ ./pyliczba/

# .env is deliberately not copied -- image layers are readable by anyone who
# can pull the image. Pass the secrets at runtime with `docker run --env-file`.
# .git is not copied either, so the update check in sr0wx.py will log a single
# error and carry on; set check_for_updates = False in config.py to silence it.

ENTRYPOINT ["./wxenv/bin/python3", "sr0wx.py"]
CMD []
