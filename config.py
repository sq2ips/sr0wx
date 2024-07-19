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

# język
import pl_google.pl_google as pl_google

# logger
log_line_format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
log_handlers = [{
    'log_level': logging.INFO,
    'class': logging.StreamHandler,
    'config': {'stream': None},
}, {
    'log_level': logging.INFO,
    'class': logging.handlers.TimedRotatingFileHandler,
    'config': {
        'filename': '../logs/pogoda/' + str(datetime.now().strftime("%Y-%m-%d_%H:%M")) + '.log',
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
    hello_msg = os.getenv("HELLO_MSG").split(",")
    goodbye_msg = os.getenv("GOODBYE_MSG").split(",")
    airly_key = os.getenv("AIRLY_KEY")
    openweather_key = os.getenv("OPENWEATHER_KEY")
    meteostation_ip = os.getenv("METEOSTATION_IP").split(",")
    map_call = os.getenv("MAP_CALL")
    map_lat = os.getenv("MAP_LAT")
    map_lon = os.getenv("MAP_LON")
    map_info = os.getenv("MAP_INFO")
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

# wiadomość początkowa i końcowa jest pliku .env
#hello_msg = ['_', 'test']
#goodbye_msg = ['_', "beep2"]
# informacja gdy nie ma internetu
data_sources_error_msg = ['_', 'zrodlo_danych_niedostepne']
# czytanie informacji o źródłach danych
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
    additional_info=map_info,
)

# ---------------
# openweather_sq9atk
# ---------------
# https://openweathermap.org/api pod tym adresem można uzyskac klucz API
# wystarczy sie zarejestrować
from openweather_sq9atk import OpenWeatherSq9atk
openweathersq9atk = OpenWeatherSq9atk(
    language=pl_google,
    api_key=openweather_key,
    lat=54.5237904,
    lon=18.5129878,
    service_url='http://api.openweathermap.org/data/2.5/',
    current = True,
    saytime = False,
    start_message="aktualny_stan_pogody"
)

# ---------------
# meteo_sq9atk
# ---------------
from meteo_sq9atk import MeteoSq9atk
meteosq9atk = MeteoSq9atk(
    language=pl_google,
    service_url="https://pogoda.onet.pl/prognoza-pogody/gdynia-287798",
    current=True,
    saytime = False
)

# ---------------
# imgw_podest_sq2ips
# ---------------
from imgw_podest_sq2ips import ImgwPodestSq2ips
imgwpodestsq2ips = ImgwPodestSq2ips(
    language=pl_google,
    service_url="https://hydro-back.imgw.pl/list/hydrologic",
    wodowskazy=[], # id poszczegulnych wodowskazów
    zlewnie=[184, 14, 292, 48, 183, 268, 174, 2149, 16], # id całej zlewni
    use_outdated=False,
    custom_names = {},
    custom_rivers = {"Morze Bałtyckie": "baltyk"}
)

# ---------------
# airly_sq9atk
# ---------------
# https://developer.airly.org/ pod tym adresem można uzyskac klucz API
# wystarczy sie zarejestrować
from airly_sq9atk import AirlySq9atk
airlysq9atk = AirlySq9atk(
    language=pl_google,
    api_key=airly_key,
    service_url='https://airapi.airly.eu/v2/measurements',  # location
    mode='nearest',  # point|nearest|installationId
    lat=54.519813,
    lon=18.537679,
    maxDistanceKM=5,
    installationId=3476,  # Gdynia
)

# ---------------
# air_pollution_sq9atk
# ---------------
from air_pollution_sq9atk import AirPollutionSq9atk
airpollutionsq9atk = AirPollutionSq9atk(
    language=pl_google,
    service_url="http://api.gios.gov.pl/pjp-api/rest/",
    station_id=732,
    city_id=219,
    # LISTA STACJI Z NUMERAMI Z CAŁEJ POLSKI
    # http://api.gios.gov.pl/pjp-api/rest/station/findAll

    # poniższe TYLKO DLA KRAKOWA!!!!!
    # do station_id wpada co 20 minut inna cyfra z przedziału 0,1,2
    # dzięki czemu za każdym razem wybieramy inną stację pomiarową
    # station_id = 400 + (int(datetime.now().strftime('%M')))/20,
    # 400 Kraków, Aleja Krasińskiego
    # 401 Kraków, ul. Bujaka
    # 402 Kraków, ul. Bulwarowa
    # 10121 Kraków, ul. Dietla
    # 10123 Kraków, ul. Złoty Róg
    # 10139 Kraków, os. Piastów
    # 10435 Kraków, ul. Telimeny
    # 10447 Kraków, os. Wadów
)

# ---------------
# geomagnetic_sq9atk
# ---------------
from geo_magnetic_sq9atk import GeoMagneticSq9atk
geomagneticsq9atk = GeoMagneticSq9atk(
    language=pl_google,
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
# radioactive_sq9atk
# ---------------
from radioactive_sq9atk import RadioactiveSq9atk
radioactivesq9atk = RadioactiveSq9atk(
    language=pl_google,
    service_url="http://radioactiveathome.org/map/",
    sensor_id=39306  # czujnik w centrum Gdyni
    # więcej czujników na stronie http://radioactiveathome.org/map/
)

# ---------------
# radioactive_sq2ips
# ---------------
from radioactive_sq2ips import RadioactiveSq2ips
radioactivesq2ips = RadioactiveSq2ips(
    language=pl_google,
    service_url='https://monitoring.paa.gov.pl/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=paa:kcad_siec_pms_moc_dawki_mapa&outputFormat=application/json',
    sensor_id='d2e87d20-28e2-47ea-860d-98a4e98d8726',
    service_url_sr="https://monitoring.paa.gov.pl/_api/maps/MapLayer/15d20873-f8a7-8899-5d69-960cc9ebbbb6/DetailsTable/f5af6ec4-d759-3163-344e-cbf147d28e28/Data/"
)

from fires_sq2ips import FiresSq2ips
firessq2ips = FiresSq2ips(
    language=pl_google,
    service_url="https://www.traxelektronik.pl/pogoda/las/zbiorcza.php",
    zone="15_B", # tutaj należy znaleźć strefę https://www.traxelektronik.pl/pogoda/las/ zaznaczając granice i numery stref oraz zagrożenie pożarowe
)

# ---------------
# propagation_sq9atk
# ---------------
from propagation_sq9atk import PropagationSq9atk
propagationsq9atk = PropagationSq9atk(
    language=pl_google,
    service_url="https://rigreference.com/solar/img/tall",
)
# ---------------
# propagation_sq2ips
# ---------------
from propagation_sq2ips import PropagationSq2ips
propagationsq2ips = PropagationSq2ips(
    language=pl_google,
    service_url="https://www.hamqsl.com/solarxml.php",
    radioNoise = True
)
# ---------------
# vhf_propagation_sq9atk
# ---------------
from vhf_tropo_sq9atk import VhfTropoSq9atk
vhftroposq9atk = VhfTropoSq9atk(
    language=pl_google,
    service_url="https://www.dxinfocentre.com/tropo_eur.html",
    qthLon=18.537679,
    qthLat=54.519813
)
# ---------------
# calendar_sq9atk
# ---------------
from calendar_sq9atk import CalendarSq9atk
calendarsq9atk = CalendarSq9atk(
    language=pl_google,
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
    language=pl_google,
    lat='54.52379',
    lon='18.51298',
    ele=15,
    pre=1010,
    temp=20,
    hori=0,
)

# ----------------
# meteoalert_sq2ips
# ----------------
from meteoalert_sq2ips import MeteoAlertSq2ips
meteoalertsq2ips = MeteoAlertSq2ips(
    language=pl_google,
    service_url="https://meteo.imgw.pl/api/meteo/messages/v1/",
    city_id=["2262"],  # Gdynia
    #start_message="ostrzezenia_meteorologiczne_i_hydrologiczne_imgw",
    start_message="",
    hydronames=["W_G_6_PM", "Z_G_22_PM"],  # Gdynia i bałtyk
    short_validity=True,
)

# ---------------
# spaceweather_sq2ips
# ---------------
from spaceweather_sq2ips import SpaceWeatherSq2ips
spaceweathersq2ips = SpaceWeatherSq2ips(
    language=pl_google,
    # burze geomagnetyczne
    urlG="https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json",
    # zakłucenia radiowe
    urlR="https://services.swpc.noaa.gov/json/goes/secondary/xrays-6-hour.json",
    # Burze radiacyjne
    urlS="https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json",
    # Chwilowe burze geomagnetyczne
    geomagneticShort = True,
    radioNoise = False
)

# ---------------
# meteostation_sq2ips
# ---------------
from meteostation_sq2ips import MeteoStationSq2ips
meteostationsq2ips = MeteoStationSq2ips(
    language=pl_google,
    ip=meteostation_ip,
    port=4210,
)

from meteo_yr_sq2ips import MeteoYrSq2ips
meteoyrsq2ips = MeteoYrSq2ips(
    language=pl_google,
    service_url="https://www.yr.no",
    id="2-3099424", # Gdynia
    current=True,
    intervals=[6, 12]
)

# ---------------
# time_sq2ips
# ---------------
from time_sq2ips import TimeSq2ips
timesq2ips = TimeSq2ips(
    language=pl_google,
    start_message=[" _ ", "raport_meteorologiczny", "z_godziny"]
)
# WSZYSTKIE MODUŁY
modules_all = [
    activitymap,            # marker na mapie wx.ostol.pl
    timesq2ips,             # godzina
    meteoalertsq2ips,       # ostrzeżenia meteorologiczne imgw
    meteostationsq2ips,     # dane ze stacji meteo
    meteoyrsq2ips,          # pogoda z yr
    openweathersq9atk,      # pogoda openweathermap
    meteosq9atk,            # pogoda alternatywa
    imgwpodestsq2ips,        # wodowskazy z hydro.imgw.pl
    airpollutionsq9atk,     # zanieczyszczenia powietrza z GIOŚ
    airlysq9atk,            # zanieczyszczenia powietrza z Airly
    firessq2ips,            # informacja o stopniu zagrożenia pożarowego lasów
    spaceweathersq2ips,     # pogoda kosmiczna
    propagationsq9atk,      # propagacja KF
    propagationsq2ips,      # propagacja KF z hamqsl.com
    vhftroposq9atk,         # propagacja tropo
    geomagneticsq9atk,      # zaburzenia geomagnetyczne 
    radioactivesq9atk,      # promieniowanie jonizujące
    radioactivesq2ips,      # promieniowanie jonizujące z paa
    calendarsq9atk,         # wschód i zachód słońca
    calendarsq2ips,         # wschód i zachód słońca bez internetu
]
# WŁĄCZONE MODUŁY
modules = [
    activitymap,            # marker na mapie wx.ostol.pl
    timesq2ips,             # godzina
    meteoalertsq2ips,       # ostrzeżenia meteorologiczne imgw
    # meteostationsq2ips,   # dane ze stacji meteo
    # meteoyrsq2ips,        # pogoda z yr
    openweathersq9atk,      # pogoda openweathermap
    # meteosq9atk,          # pogoda alternatywa
    # imgwpodestsq2ips,     # wodowskazy z hydro.imgw.pl
    # airpollutionsq9atk,   # zanieczyszczenia powietrza z GIOŚ
    airlysq9atk,            # zanieczyszczenia powietrza z Airly
    # firessq2ips,          # informacja o stopniu zagrożenia pożarowego lasów
    spaceweathersq2ips,     # pogoda kosmiczna
    # propagationsq9atk,    # propagacja KF
    propagationsq2ips,      # propagacja KF z hamqsl.com
    vhftroposq9atk,         # propagacja tropo
    # geomagneticsq9atk,    # zaburzenia geomagnetyczne 
    # radioactivesq9atk,    # promieniowanie jonizujące
    radioactivesq2ips,      # promieniowanie jonizujące z paa
    # calendarsq9atk,       # wschód i zachód słońca
    calendarsq2ips,         # wschód i zachód słońca bez internetu
]
# MODUŁY OFFLINE
offline_modules = [
    calendarsq2ips,
]
# MODUŁY AWARYJNE
aux_modules = {
    openweathersq9atk: meteosq9atk,
    meteoyrsq2ips: openweathersq9atk,
    airlysq9atk: airpollutionsq9atk,
    spaceweathersq2ips: geomagneticsq9atk,
    radioactivesq2ips: radioactivesq9atk,
    calendarsq2ips: calendarsq9atk,
    propagationsq2ips: propagationsq9atk
}
