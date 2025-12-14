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
            "filename": "logs/"
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
    airly_key = os.getenv("AIRLY_KEY")
    openweather_key = os.getenv("OPENWEATHER_KEY")
    meteostation_ip = os.getenv("METEOSTATION_IP").split(",")
    LATITUDE = float(os.getenv("LATITUDE"))
    LONGITUDE = float(os.getenv("LONGITUDE"))
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
# ogólny limit czasu uruchomienia wszystkich modułów
general_timeout = 120

lang_name = "pl_google"  # język
pygame_bug = 0

# maksymalny czas oczekiwania do komunikatu (w minutach)
maxWaitTime = 10

# czas odczekany między uruchomieniem i wyłączeniem PTT a odtwarzaniem audio
marginDelay = 500

# ustawienie wartości pygame.time.Clock().tick()
clockTick = 250
timeDelay = 200
# długość ciszy dla tekstu "_"
delayValue = 500
# pygame samplerate
samplerate = 22050
# wyświetlanie nazw sampli w trakcie odtważania
showSamples = False

# inwersja modułów awaryjnych
aux_modules_inversion = False

# Usatwiensia zapisu komunikatu do pliku audio
saveAudio = False
# Ścieżka zapisu pliku wraz z nazwą i rozszerzeniem
audioPath = "./sr0wx.wav"

# Sprawdzanie dostępności aktualizacji
check_for_updates = True

# Adres url do sprawdzania aktualizacji
upstream_url = "https://github.com/sq2ips/sr0wx"

# czytanie informacji o źródłach danych
read_sources_msg = False

# wiadomość początkowa i końcowa
hello_msg = ["tu_eksperymentalna_automatyczna_stacja_pogodowa", "sr0wx"]
goodbye_msg = ["tu_sr0wx", "kolejny_komunikat", "_", "beep2"]
# informacja gdy nie ma internetu
data_sources_error_msg = ["_", "internetowe_zrodlo_danych_niedostepne"]


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
    hour_quarter=10,
    above_sea_level=35,
    above_ground_level=20,
    station_range=25,
    additional_info="test",
)

# ---------------
# openweather_sq9atk
# ---------------
# https://openweathermap.org/api pod tym adresem można uzyskac klucz API
# wystarczy sie zarejestrować
from openweather_sq9atk import OpenWeatherSq9atk
openweathersq9atk = OpenWeatherSq9atk(
    language=lang,
    api_key=openweather_key,
    service_url="http://api.openweathermap.org/data/2.5/",
    current=True,
    saytime=False,
    start_message="aktualny_stan_pogody",
)

# ---------------
# meteo_sq9atk
# ---------------
from meteo_sq9atk import MeteoSq9atk
meteosq9atk = MeteoSq9atk(
    language=lang,
    service_url="https://pogoda.onet.pl/prognoza-pogody/gdynia-287798",
    current=True,
    saytime=False,
)

# ---------------
# imgw_podest_sq2ips
# ---------------
from imgw_podest_sq2ips import ImgwPodestSq2ips
imgwpodestsq2ips = ImgwPodestSq2ips(
    language=lang,
    service_url="https://hydro-back.imgw.pl/list/hydro",
    wodowskazy=[],  # id poszczegulnych wodowskazów
    zlewnie=["47", "48"],  # id całej zlewni (w cudzysłowach)
    use_outdated=False,
    read_level=False,
    read_diff_level=True,
    custom_names={},
    custom_rivers={},
)

# ---------------
# airly_sq9atk
# ---------------
# https://developer.airly.org/ pod tym adresem można uzyskac klucz API
# wystarczy sie zarejestrować
from airly_sq9atk import AirlySq9atk
airlysq9atk = AirlySq9atk(
    language=lang,
    api_key=airly_key,
    service_url="https://airapi.airly.eu/v2/measurements",  # location
    mode="nearest",  # point|nearest|installationId
    maxDistanceKM=5,
    installationId=3476,  # Gdynia
)

# ---------------
# air_gios
# ---------------
from air_gios import AirGios
airgios = AirGios(
    language = lang,
    service_url="https://api.gios.gov.pl/pjp-api/v1/rest/",
    uri_index="aqindex/getIndex/",
    uri_all="station/findAll?size=500",
    sensor_id=52,
)

# ---------------
# geomagnetic_sq9atk
# ---------------
from geo_magnetic_sq9atk import GeoMagneticSq9atk
geomagneticsq9atk = GeoMagneticSq9atk(
    language=lang,
    service_url="https://www.gismeteo.pl/weather-gdynia-3041/gm/",
)
# https://www.gismeteo.pl/weather-warsaw-3196/gm/
# https://www.gismeteo.pl/weather-gdansk-3046/gm/
# https://www.gismeteo.pl/weather-szczecin-3101/gm/
# https://www.gismeteo.pl/weather-krakow-3212/gm/
# https://www.gismeteo.pl/weather-rzeszow-3215/gm/
# https://www.gismeteo.pl/weather-suwaki-269290/gm/
# https://www.gismeteo.pl/weather-jelenia-gora-3206/gm/
# https://www.gismeteo.pl/weather-poznan-3194/gm/
# https://www.gismeteo.pl/weather-lublin-3205/gm/
# https://www.gismeteo.pl/weather-gorzow-wielkopolski-3192/gm/
# https://www.gismeteo.pl/weather-tarnowskie-gory-3152/gm/
# https://www.gismeteo.pl/weather-ptakowice-280575/gm/
# więcej miejscowości po wejściu na dowolny z powyższych adresów w przeglądarce...

# ---------------
# radioactive_sq2ips
# ---------------
from radioactive_sq2ips import RadioactiveSq2ips
radioactivesq2ips = RadioactiveSq2ips(
    language=lang,
    service_url="https://monitoring.paa.gov.pl/_api/maps/MapLayer/15d20873-f8a7-8899-5d69-960cc9ebbbb6/DetailsTable/f5af6ec4-d759-3163-344e-cbf147d28e28/Data",
    sensor_id="d2e87d20-28e2-47ea-860d-98a4e98d8726",
)
from fires_sq2ips import FiresSq2ips
firessq2ips = FiresSq2ips(
    language=lang,
    service_url="https://www.traxelektronik.pl/pogoda/las/zbiorcza.php",
    zone="15_A",  # tutaj należy znaleźć strefę https://www.traxelektronik.pl/pogoda/las/ zaznaczając granice i numery stref oraz zagrożenie pożarowe
)

# ---------------
# propagation_sq9atk
# ---------------
from propagation_sq9atk import PropagationSq9atk
propagationsq9atk = PropagationSq9atk(
    language=lang,
    service_url="https://rigreference.com/solar/img/tall",
)
# ---------------
# propagation_sq2ips
# ---------------
from propagation_sq2ips import PropagationSq2ips
propagationsq2ips = PropagationSq2ips(
    language=lang, service_url="https://www.hamqsl.com/solarxml.php", radioNoise=True
)
# ---------------
# vhf_tropo_sq9atk
# ---------------
from vhf_tropo_sq9atk import VhfTropoSq9atk
vhftroposq9atk = VhfTropoSq9atk(
    language=lang,
    service_url="https://www.dxinfocentre.com/tropo_eur.html",
    onlyAlerts=True
)
# ---------------
# calendar_sq9atk
# ---------------
from calendar_sq9atk import CalendarSq9atk
calendarsq9atk = CalendarSq9atk(
    language=lang,
    service_url="http://calendar.zoznam.sk/sunset-pl.php?city=",
    city_id=3099424,  # Gdyna
)
# 776069 Białystok
# 3102014 Bydgoszcz
# 3100946 Częstochowa
# 3099434 Gdańsk
# 3099424 Gdynia
# 3096472 Katowice
# 3094802 Kraków
# 3093133 Lodz
# 765876 Lublin
# 3088171 Poznań
# 760778 Radom
# 3085128 Sosnowiec
# 3083829 Szczecin
# 756135 Warsaw
# 3081368 Wrocław


# ----------------
# calendar_sq2ips
# ----------------
from calendar_sq2ips import CalendarSq2ips
calendarsq2ips = CalendarSq2ips(
    language=lang,
    ele=15,
    pre=1013,
    temp=10,
    hori=0,
)

# ----------------
# meteoalert_sq2ips
# ----------------
from meteoalert_sq2ips import MeteoAlertSq2ips
meteoalertsq2ips = MeteoAlertSq2ips(
    language=lang,
    service_url="https://meteo.imgw.pl/api/meteo/messages/v1/",
    city_id=["2262"],  # Gdynia
    # start_message="ostrzezenia_meteorologiczne_i_hydrologiczne_imgw",
    start_message="",
    hydronames=["W_G_6_PM", "Z_G_22_PM"],  # Gdynia i bałtyk
    short_validity=True,
    read_probability=False,
)

# ----------------
# antistorm_sq2ips
# ----------------
from antistorm_sq2ips import AntistormSq2ips
antistormsq2ips = AntistormSq2ips(
    language=lang,
    service_url="http://antistorm.eu/webservice.php",
    city_id=73,  # Gdynia
)

# ---------------
# spaceweather_sq2ips
# ---------------
from spaceweather_sq2ips import SpaceWeatherSq2ips
spaceweathersq2ips = SpaceWeatherSq2ips(
    language=lang,
    # burze geomagnetyczne
    urlG="https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json",
    # zakłucenia radiowe
    urlR="https://services.swpc.noaa.gov/json/goes/secondary/xrays-6-hour.json",
    # Burze radiacyjne
    urlS="https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json",
    # Chwilowe burze geomagnetyczne
    geomagneticShort=True,
    radioNoise=False,
)

# ---------------
# meteostation_sq2ips
# ---------------
from meteostation_sq2ips import MeteoStationSq2ips
meteostationsq2ips = MeteoStationSq2ips(
    language=lang,
    ip=meteostation_ip,
    port=4210,
)

# ---------------
# meteo_yr_sq2ips
# ---------------
from meteo_yr_sq2ips import MeteoYrSq2ips
meteoyrsq2ips = MeteoYrSq2ips(
    language=lang,
    service_url="https://www.yr.no",
    id="2-3099424",  # Gdynia
    current=True,
    intervals=[6, 12],
)

# ---------------
# kse_sq2ips
# ---------------
from kse_sq2ips import KseSq2ips
ksesq2ips = KseSq2ips(
    language=lang,
    service_url="https://www.pse.pl/transmissionMapService"
)

# ---------------
# time_sq2ips
# ---------------
from time_sq2ips import TimeSq2ips
timesq2ips = TimeSq2ips(
    language=lang,
    maxwaittime=maxWaitTime,
    start_message=["raport_meteorologiczny", "z_godziny"],
    round_minutes=True,
    round_part=15,
)

#####################

# USTAWIENIA URUCHAMIANIA MOUŁÓW

# WŁĄCZONE MODUŁY
modules = [
#    activitymap,            # marker na mapie wx.vhf.com.pl
    timesq2ips,             # godzina
    meteoalertsq2ips,       # ostrzeżenia meteorologiczne IMGW
    # antistormsq2ips,      # radar pogodowy
    # meteostationsq2ips,   # dane ze stacji meteo
    # meteoyrsq2ips,        # pogoda z yr
    openweathersq9atk,      # pogoda openweathermap
    # meteosq9atk,          # pogoda alternatywa
    imgwpodestsq2ips,       # wodowskazy z hydro.imgw.pl
    airlysq9atk,            # zanieczyszczenia powietrza z Airly
    #airgios,                # zanieczyszczenia powietrza z GIOŚ
    # firessq2ips,          # informacja o stopniu zagrożenia pożarowego lasów
    # ksesq2ips,            # dane systemowe z pse.pl
    spaceweathersq2ips,     # pogoda kosmiczna
    # geomagneticsq9atk,    # zaburzenia geomagnetyczne
    # propagationsq9atk,    # propagacja KF
    propagationsq2ips,      # propagacja KF z hamqsl.com
    vhftroposq9atk,         # propagacja troposferyczna
    radioactivesq2ips,      # promieniowanie jonizujące z PAA
    # calendarsq9atk,       # wschód i zachód słońca
    calendarsq2ips,         # wschód i zachód słońca bez internetu
]

# MODUŁY OFFLINE
offline_modules = [
    calendarsq2ips,
]

# WSZYSTKIE MODUŁY
modules_all = [
    activitymap,                # marker na mapie wx.vhf.com.pl
    timesq2ips,                 # godzina
    meteoalertsq2ips,           # ostrzeżenia meteorologiczne IMGW
    antistormsq2ips,            # radar pogodowy
    #meteostationsq2ips,         # dane ze stacji meteo
    meteoyrsq2ips,              # pogoda z yr
    openweathersq9atk,          # pogoda openweathermap
    meteosq9atk,                # pogoda alternatywa
    imgwpodestsq2ips,           # wodowskazy z hydro.imgw.pl
    airlysq9atk,                # zanieczyszczenia powietrza z Airly
    airgios,                    # zanieczyszczenia powietrza z GIOŚ
    firessq2ips,                # informacja o stopniu zagrożenia pożarowego lasów
    ksesq2ips,                  # dane systemowe z pse.pl
    spaceweathersq2ips,         # pogoda kosmiczna
    geomagneticsq9atk,          # zaburzenia geomagnetyczne
    propagationsq9atk,          # propagacja KF
    propagationsq2ips,          # propagacja KF z hamqsl.com
    vhftroposq9atk,             # propagacja troposferyczna
    radioactivesq2ips,          # promieniowanie jonizujące z PAA
    calendarsq9atk,             # wschód i zachód słońca
    calendarsq2ips,             # wschód i zachód słońca bez internetu
]

# MODUŁY AWARYJNE
aux_modules = {
    openweathersq9atk: meteosq9atk,
    meteosq9atk: openweathersq9atk,
    meteoyrsq2ips: openweathersq9atk,
    airgios: airlysq9atk,
    airlysq9atk: airgios,
    spaceweathersq2ips: geomagneticsq9atk,
    geomagneticsq9atk: spaceweathersq2ips,
    calendarsq2ips: calendarsq9atk,
    calendarsq9atk: calendarsq2ips,
    propagationsq2ips: propagationsq9atk,
    propagationsq9atk: propagationsq2ips
}
