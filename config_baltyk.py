#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

# Main config file for sr0wx.py

# biblioteki
from dotenv import load_dotenv
import os
import logging
import logging.handlers
from datetime import datetime

from colorcodes import *


def my_import(name):
    mod = __import__(name)
    components = name.split(".")
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


# logger
dict_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },
    },
    "formatters": {
        "colored_console": {
            "()": "coloredlogs.ColoredFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s: %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "format_for_file": {
            "format": "%(asctime)s %(name)s %(levelname)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "colored_console",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "format_for_file",
            "filename": "../logs/baltyk/"
            + str(datetime.now().strftime("%Y-%m-%d_%H:%M"))
            + ".log",
            "maxBytes": 500000,
            "backupCount": 30,
        },
    },
}

# dane z pliku .env
if os.path.exists(".env"):
    load_dotenv()
    latitude = float(os.getenv("LATITUDE"))
    longitude = float(os.getenv("LONGITUDE"))
else:
    raise FileNotFoundError("No .env file present.")

#####################

# KONFIGURACJA OGÓLNA

# CTCSS
ctcss_tone = None
ctcss_volume = 25000
# nadawanie przez port szeregowy
serial_port = None
serial_baud_rate = 9600
serial_signal = "DTR"  # lub 'RTS'
# nadawanie przez GPIO w Raspberry Pi
rpi_pin = 40
# wieloprocesowość dla modułów
multi_processing = True
pool_workers = 4
general_timeout = 60
marginDelay = 500

lang_name = "pl_google"  # język
pygame_bug = 0

# ustawienie wartości pygame.time.Clock().tick()
clockTick = 250
timeDelay = 300
# długość ciszy dla tekstu "_"
delayValue = 500
# pygame samplerate
samplerate = 22050
# wyświetlanie nazw sampli w trakcie odtważania
showSamples = False

# maksymalny czas oczekiwania do komunikatu (w minutach)
maxWaitTime = 10

# Usatwiensia zapisu komunikatu do pliku audio
saveAudio = False
# Ścieżka zapisu pliku wraz z nazwą i rozszerzeniem
audioPath = "./sr0wx.wav"

# inwersja modułów awaryjnych
aux_modules_inversion = False

upstream_url = "https://github.com/sq2ips/sr0wx"

# Sprawdzanie dostępności aktualizacji
check_for_updates = True

hello_msg = ['_', 'tu_eksperymentalna_automatyczna_stacja_pogodowa', 'sr0wx']
goodbye_msg = ['_', 'tu_sr0wx', "_", "kolejny_komunikat_m", "beep2"]
read_sources_msg = False

#####################

# INICJALIZACJA JĘZYKA
lang = my_import(".".join((lang_name, lang_name)))

#####################

# INICJALIZACJA I KONFIGURACJA MODUŁÓW

import sys

sys.path.append("modules/")

#####################

# ---------------
# activity_map
# ---------------
from activity_map import ActivityMap

activitymap = ActivityMap(
    service_url="http://wx.vhf.com.pl/map_requests?base=",
    callsign="TEST",
    latitude=latitude,
    longitude=longitude,
    hour_quarter=10,
    above_sea_level=35,
    above_ground_level=20,
    station_range=25,
    additional_info="test",
)

# ---------------
# baltyk_sq2ips
# ---------------
from baltyk_sq2ips import BaltykSq2ips

baltyksq2ips = BaltykSq2ips(
    language=lang,
    service_url="https://baltyk.imgw.pl/getdata/forecast.php?type=sea&lang=pl",
    # service_url="http://91.220.17.153/index-maps/forecastGetData.php?type=sea&lang=pl", # niepewne źródło
    # service_url="http://baltyk.pogodynka.pl/index-maps/forecastGetData.php?type=sea&lang=pl", # stary, nie działający URL
    region_id="SOUTHEASTERN BALTIC",
    # "POLISH COASTAL WATERS"
    # "WESTERN BALTIC"
    # "SOUTHERN BALTIC"
    # "SOUTHEASTERN BALTIC"
    # "CENTRAL BALTIC"
    # "NORTHERN BALTIC"
)

# WŁĄCZONE MODUŁY
modules = [activitymap, baltyksq2ips]
offline_modules = []
aux_modules = {}
