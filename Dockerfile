# Dockerfile for SR0WX
FROM debian:12

RUN apt-get update && apt-get upgrade
RUN apt-get install -y python3 python3-pip python3-venv
RUN apt-get install -y pulseaudio
RUN apt-get install -y git

RUN useradd --create-home --shell /bin/bash -G audio sr0wx

USER sr0wx

WORKDIR /home/sr0wx

RUN mkdir ./sr0wx/
RUN mkdir -p ./logs/pogoda

WORKDIR /home/sr0wx/sr0wx

COPY requirements.txt ./
COPY sr0wx.py config.py .env colorcodes.py sr0wx_module.py ./
COPY modules/ ./modules/
COPY pl_google/ ./pl_google/
COPY pyliczba/ ./pyliczba/
COPY .git/ ./.git/

RUN python3 -m venv ./wxenv

RUN . ./wxenv/bin/activate && pip install --upgrade pip
RUN . ./wxenv/bin/activate && pip install -r requirements.txt

CMD ["./wxenv/bin/python3", "sr0wx.py"]