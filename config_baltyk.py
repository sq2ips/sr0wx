#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

# AKTUALNIE ZALECANE JEST UBUNTU 16.04 MATE
# Poniższy opis dotyczy tej dystrybucji

# WYMAGANE DODATKOWE PAKIETY:
#   sudo apt-get install git
#   sudo apt-get install python-pygame
#   sudo apt-get install python-tz
#   sudo apt-get install python-imaging
#   sudo apt-get install python-serial
#   sudo apt-get install curl
#   sudo apt-get install php7.0
#   sudo apt-get install php7.0-curl
#   sudo apt-get install php7.0-xml
#   sudo apt-get install ffmpeg
#
# LUB WSZYSTKO NA RAZ
#   sudo apt-get install git python-pygame python-tz python-imaging python-serial curl php7.0 php7.0-curl php7.0-xml ffmpeg

# UPRAWNIENIA USERA DO PORTU COM
#   sudo gpasswd --add ${USER} dialout

# GENEROWANIE SAMPLI
# Będąc w katalogu audio_generator:
#   php index.php
#
# Generowane są sample z tablicy $słownik z pliku slownik.php. 
# Pozostałe tablice to tylko przechowalnia fraz go wygenerowania.






import logging, logging.handlers, time
from datetime import datetime

log_line_format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
log_handlers = [{
        'log_level': logging.INFO,
        'class': logging.StreamHandler,
        'config': {'stream': None},
	},{
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

ctcss_tone = 0
serial_port = None
serial_baud_rate = 9600
serial_signal = 'DTR' # lub 'RTS'


import pl_google.pl_google as pl_google
lang = "pl_google"
pygame_bug = 0

hello_msg = ['_','sr2wxg_cw','_','tu_eksperymentalna_automatyczna_stacja_pogodowa','sr2wxg']
goodbye_msg = ['_','tu_sr2wxg',"_", "kolejny_komunikat_m", "beep2"]
read_sources_msg = False

# ---------------
# baltyk_sq2dk
# ---------------
from baltyk_sq2dk import BaltykSq2dk
baltyksq2dk = BaltykSq2dk(
    language=pl_google,
    service_url="https://baltyk.imgw.pl//getdata/forecast.php?type=sea&lang=pl",

#niepewne źródło   # service_url="http://91.220.17.153/index-maps/forecastGetData.php?type=sea&lang=pl",
    region_id="SOUTHEASTERN BALTIC"
    
#stary nie działający URL: service_url="http://baltyk.pogodynka.pl/index-maps/forecastGetData.php?type=sea&lang=pl",
#"POLISH COASTAL WATERS"

    ##"WESTERN BALTIC"
    ##"SOUTHERN BALTIC"
    ##"SOUTHEASTERN BALTIC"
    ##"CENTRAL BALTIC"
    ##"NORTHERN BALTIC"
    ##"POLISH COASTAL WATERS"
)
from baltyk_sq2ips import BaltykSq2ips
baltyksq2ips = BaltykSq2ips(
    service_url="https://baltyk.imgw.pl//getdata/forecast.php?type=sea&lang=pl",
    region_id="SOUTHEASTERN BALTIC"
)

# WŁĄCZONE MODUŁY
modules = [baltyksq2dk]
