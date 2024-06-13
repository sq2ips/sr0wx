#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pl_google.pl_google as pl_google
import logging
import logging.handlers
import time
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

#ctcss_tone = 67.0
serial_port = None
serial_baud_rate = 9600
serial_signal = 'DTR'  # lub 'RTS'
rpi_pin = 40
multi_processing = True

lang = "pl_google"
pygame_bug = 0

hello_msg = ['_', 'sr2wxg_cw', '_',
             'tu_eksperymentalna_automatyczna_stacja_pogodowa', 'sr2wxg']
goodbye_msg = ['_', 'tu_sr2wxg', "_", "kolejny_komunikat_m", "beep2"]
read_sources_msg = False


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
modules = [baltyksq2ips]
aux_modules = {}