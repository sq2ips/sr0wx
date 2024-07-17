#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pl_google.pl_google as pl_google
import logging
import logging.handlers
import os
from dotenv import load_dotenv
from datetime import datetime

log_line_format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
log_handlers = [{
    'log_level': logging.INFO,
    'class': logging.StreamHandler,
    'config': {'stream': None},
}, {
    'log_level': logging.DEBUG,
    'class': logging.handlers.TimedRotatingFileHandler,
    'config': {
        'filename': '../logs/baltyk/' + str(datetime.now().strftime("%Y-%m-%d_%H:%M")) + '.log',
        'when': 'D',
        'interval': 1,
        'backupCount': 30,
        'delay': True,
        'utc': True,
    }
}]

# dane z pliku .env
if os.path.exists(".env"):
    load_dotenv()
    hello_msg = os.getenv("HELLO_MSG_BALTYK").split(",")
    goodbye_msg = os.getenv("GOODBYE_MSG_BALTYK").split(",")
    map_call = os.getenv("MAP_CALL")
    map_lat = os.getenv("MAP_LAT")
    map_lon = os.getenv("MAP_LON")
    map_info_baltyk = os.getenv("MAP_INFO_BALTYK")
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
serial_signal = 'DTR'  # lub 'RTS'
# nadawanie przez GPIO w Raspberry Pi
rpi_pin = 40
# wieloprocesowość dla modułów
multi_processing = True

lang = "pl_google" # język
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

# Usatwiensia zapisu komunikatu do pliku audio
saveAudio = False
# Ścieżka zapisu pliku wraz z nazwą i rozszerzeniem
audioPath = "./sr0wx.wav"

#hello_msg = ['_', 'tu_eksperymentalna_automatyczna_stacja_pogodowa', 'sr0wx']
#goodbye_msg = ['_', 'tu_sr2wxg', "_", "kolejny_komunikat_m", "beep2"]
read_sources_msg = False

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
    callsign=map_call,
    latitude=map_lat,
    longitude=map_lon,
    hour_quarter=10,
    above_sea_level=35,
    above_ground_level=20,
    station_range=25,
    additional_info=map_info_baltyk,
)

# ---------------
# baltyk_sq2ips
# ---------------
from baltyk_sq2ips import BaltykSq2ips
baltyksq2ips = BaltykSq2ips(
    language=pl_google,
    service_url="https://baltyk.imgw.pl//getdata/forecast.php?type=sea&lang=pl",
    #service_url="http://91.220.17.153/index-maps/forecastGetData.php?type=sea&lang=pl", # niepewne źródło
    #service_url="http://baltyk.pogodynka.pl/index-maps/forecastGetData.php?type=sea&lang=pl", # stary, nie działający URL
    region_id="SOUTHEASTERN BALTIC",

    #"POLISH COASTAL WATERS"
    #"WESTERN BALTIC"
    #"SOUTHERN BALTIC"
    #"SOUTHEASTERN BALTIC"
    #"CENTRAL BALTIC"
    #"NORTHERN BALTIC"
)

# WŁĄCZONE MODUŁY
modules = [
    activitymap,
    baltyksq2ips
]
offline_modules = []
aux_modules = {}