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
    MAP_CALL = os.getenv("MAP_CALL")
    MAP_INFO = os.getenv("MAP_INFO")
    HEALTHCHECK_UUID = os.getenv("HEALTHCHECK_UUID")
    APRS_CALL = os.getenv("APRS_CALL")
    APRS_PASSWD = os.getenv("APRS_PASSWD")
    APRS_COMMENT = os.getenv("APRS_COMMENT")
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
# Marker na mapie http://wx.vhf.com.pl/
from activity_map import ActivityMap
activitymap = ActivityMap(
    service_url="http://wx.vhf.com.pl/map_requests?base=",
    callsign=MAP_CALL,
    lat=LATITUDE,
    lon=LONGITUDE,
    hour_quarter=10,
    above_sea_level=35,
    above_ground_level=20,
    station_range=25,
    additional_info=MAP_INFO,
)
# ---------------
# healthchecks_io
# ---------------
from healthchecks_io import HealthChecksIo
healthchecksio = HealthChecksIo(
    service_url="https://hc-ping.com/",
    uuid=HEALTHCHECK_UUID
)
# ---------------
# aprs_id
# ---------------
from aprs_is import AprsIs
aprsis = AprsIs(
    passwd=APRS_PASSWD,
    call=APRS_CALL,
    lat=LATITUDE,
    lon=LONGITUDE,
    comment=APRS_COMMENT
)

# ---------------
# openweather
# ---------------
# pogoda z openweathermap.org
# https://openweathermap.org/api pod tym adresem można uzyskac klucz API
# wystarczy sie zarejestrować
from openweather import OpenWeather
openweather = OpenWeather(
    language=lang,
    lat=LATITUDE,
    lon=LONGITUDE,
    api_key=openweather_key,
    service_url="http://api.openweathermap.org/data/2.5/",
    current=True,
    saytime=False,
    start_message="aktualny_stan_pogody",
)

# ---------------
# meteo_onet
# ---------------
# pogoda z pogoda.onet.pl
from meteo_onet import MeteoOnet
meteoonet = MeteoOnet(
    language=lang,
    service_url="https://pogoda.onet.pl/prognoza-pogody/gdynia-287798",
    current=True,
    saytime=False,
)
# TODO get ID

# ---------------
# water_imgw
# ---------------
# wodowzkazy z hydro.imgw.pl
from water_imgw import WaterImgw
waterimgw = WaterImgw(
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
# TODO get ID

# ---------------
# airly
# ---------------
# Zanieczyszczenia powietrza z airly.com
# https://developer.airly.org/ pod tym adresem można uzyskac klucz API
# wystarczy sie zarejestrować
from airly import Airly
airly = Airly(
    language=lang,
    lat=LATITUDE,
    lon=LONGITUDE,
    api_key=airly_key,
    service_url="https://airapi.airly.eu/v2/measurements/",  # location
    mode="nearest",  # point|nearest|installationId
    maxDistanceKM=5,
    installationId=3476,  # Gdynia
)
# TODO get ID

# ---------------
# air_gios
# ---------------
from air_gios import AirGios
airgios = AirGios(
    language = lang,
    service_url="https://api.gios.gov.pl/pjp-api/v1/rest/",
    uri_index="aqindex/getIndex/",
    uri_all="station/findAll?size=500",
    sensor_id=732,
    onlyAlerts=True
)

# ---------------
# geo_magnetic
# ---------------
from geo_magnetic import GeoMagnetic
geomagnetic = GeoMagnetic(
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
# radioactive_paa
# ---------------
from radioactive_paa import RadioactivePaa
radioactivepaa = RadioactivePaa(
    language=lang,
    service_url="https://monitoring.paa.gov.pl/_api/maps/MapLayer/15d20873-f8a7-8899-5d69-960cc9ebbbb6/DetailsTable/f5af6ec4-d759-3163-344e-cbf147d28e28/Data",
    sensor_id="d2e87d20-28e2-47ea-860d-98a4e98d8726",
)

# ---------------
# fires
# ---------------
from fires import Fires
fires = Fires(
    language=lang,
    service_url="https://www.traxelektronik.pl/pogoda/las/zbiorcza.php",
    zone="15_A",  # tutaj należy znaleźć strefę https://www.traxelektronik.pl/pogoda/las/ zaznaczając granice i numery stref oraz zagrożenie pożarowe
)

# ---------------
# propagation_rigref
# ---------------
from propagation_rigref import PropagationRigRef
propagationrigref = PropagationRigRef(
    language=lang,
    service_url="https://rigreference.com/solar/img/tall",
)
# ---------------
# propagation_hamqsl
# ---------------
from propagation_hamqsl import PropagationHamqsl
propagationhamqsl = PropagationHamqsl(
    language=lang, service_url="https://www.hamqsl.com/solarxml.php", radioNoise=True
)
# ---------------
# vhf_tropo
# ---------------
from vhf_tropo import VhfTropo
vhftropo = VhfTropo(
    language=lang,
    service_url="https://www.dxinfocentre.com/tropo_eur.html",
    onlyAlerts=False
)
# ---------------
# calendar_zoznam
# ---------------
from calendar_zoznam import CalendarZoznam
calendarzoznam = CalendarZoznam(
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
# calendar
# ----------------
from sun_rise_set import SunRiseSet
sunriseset = SunRiseSet(
    language=lang,
    lat=LATITUDE,
    lon=LONGITUDE,
    ele=15,
    pre=1013,
    temp=10,
    hori=0,
)

# ----------------
# meteoalert_imgw
# ----------------
from meteoalert_imgw import MeteoAlertImgw
meteoalertimgw = MeteoAlertImgw(
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
# antistorm
# ----------------
from antistorm import Antistorm
antistorm = Antistorm(
    language=lang,
    service_url="http://antistorm.eu/webservice.php",
    city_id=73,  # Gdynia
)

# ---------------
# spaceweather
# ---------------
from spaceweather import SpaceWeather
spaceweather = SpaceWeather(
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
# meteostation
# ---------------
from meteostation import MeteoStation
meteostation = MeteoStation(
    language=lang,
    ip=meteostation_ip,
    port=4210,
)

# ---------------
# meteo_yr
# ---------------
from meteo_yr import MeteoYr
meteoyr = MeteoYr(
    language=lang,
    service_url="https://api.met.no/weatherapi/locationforecast/2.0/compact",
    lat=LATITUDE,
    lon=LONGITUDE,
    alt=56,
    forecast_intervals=[4,12]
)
# ---------------
# meteo_imgw # TODO
# ---------------
from meteo_imgw import MeteoImgw
meteoimgw = MeteoImgw(
    language=lang,
    service_url="https://danepubliczne.imgw.pl/api/data/meteo/",
    lat=LATITUDE,
    lon=LONGITUDE,
    station_name="",
)

# ---------------
# kse
# ---------------
from kse import Kse
kse = Kse(
    language=lang,
    service_url="https://www.pse.pl/transmissionMapService"
)

# ---------------
# time_info
# ---------------
from time_info import TimeInfo
timeinfo = TimeInfo(
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
    aprsis,              # APRS-IS position report
    #healthchecksio,     # healthcheck ping
#    activitymap,       # marker na mapie wx.vhf.com.pl
    timeinfo,           # godzina
    meteoalertimgw,     # ostrzeżenia meteorologiczne z meteo.imgw.pl
    #antistorm,         # radar pogodowy z antistorm.eu
    #meteostation,      # dane ze stacji meteo (lokalnie UDP)
    #meteoyr,           # pogoda z yr.no
    openweather,        # pogoda openweathermap.org
    #meteoonet,         # pogoda z pogoda.onet.pl
    waterimgw,          # wodowskazy z hydro.imgw.pl
    #airly,             # zanieczyszczenia powietrza z airly.com
    airgios,            # zanieczyszczenia powietrza z powietrze.gios.gov.pl
    #fires,             # zagrożenie pożarowe lasów z traxelektronik.pl
    #kse,               # aktualne dane energetyczne KSE z pse.pl
    spaceweather,       # pogoda kosmiczna
    #geomagnetic,       # zaburzenia geomagnetyczne z gismeteo.pl
    #propagationrigref, # propagacja KF z rigreference.com
    propagationhamqsl,  # propagacja KF z hamqsl.com
    vhftropo,           # propagacja troposferyczna z dxinfocentre
    radioactivepaa,     # promieniowanie jonizujące z monitoring.paa.gov.pl
    #calendarzoznam,    # wschód i zachód słońca z calendar.zoznam.sk
    sunriseset,         # wschód i zachód słońca obliczane przed moduł ephem
]

# MODUŁY OFFLINE
offline_modules = [
    sunriseset,
]

# WSZYSTKIE MODUŁY
modules_all = [
    aprsis,              # APRS-IS position report
    healthchecksio,     # healthcheck ping
    activitymap,        # marker na mapie wx.vhf.com.pl
    timeinfo,           # godzina
    meteoalertimgw,     # ostrzeżenia meteorologiczne z meteo.imgw.pl
    antistorm,          # radar pogodowy z antistorm.eu
    #meteostation,      # dane ze stacji meteo (lokalnie UDP)
    #meteoimgw,         # TODO
    meteoyr,            # pogoda z yr.no
    openweather,        # pogoda openweathermap.org
    meteoonet,          # pogoda z pogoda.onet.pl
    waterimgw,          # wodowskazy z hydro.imgw.pl
    airly,              # zanieczyszczenia powietrza z airly.com
    airgios,            # zanieczyszczenia powietrza z powietrze.gios.gov.pl
    fires,              # zagrożenie pożarowe lasów z traxelektronik.pl
    kse,                # aktualne dane energetyczne KSE z pse.pl
    spaceweather,       # pogoda kosmiczna
    geomagnetic,        # zaburzenia geomagnetyczne z gismeteo.pl
    propagationrigref,  # propagacja KF z rigreference.com
    propagationhamqsl,  # propagacja KF z hamqsl.com
    vhftropo,           # propagacja troposferyczna z dxinfocentre
    radioactivepaa,     # promieniowanie jonizujące z monitoring.paa.gov.pl
    calendarzoznam,     # wschód i zachód słońca z calendar.zoznam.sk
    sunriseset,         # wschód i zachód słońca obliczane przed moduł ephem
]

# MODUŁY AWARYJNE
aux_modules = {
    openweather: meteoonet,
    meteoonet: openweather,
    meteoyr: openweather,
    airgios: airly,
    airly: airgios,
    spaceweather: geomagnetic,
    geomagnetic: spaceweather,
    sunriseset: calendarzoznam,
    calendarzoznam: sunriseset,
    propagationhamqsl: propagationrigref,
    propagationrigref: propagationhamqsl
}
