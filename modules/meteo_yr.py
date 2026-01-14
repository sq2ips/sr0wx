# by SQ2IPS
import logging

from sr0wx_module import SR0WXModule

from datetime import datetime, timezone, timedelta

class MeteoYr(SR0WXModule):
    """Klasa pobierająca informacje o prognozie pogody z yr.no"""

    def __init__(self, language, service_url, lat, lon, alt, forecast_intervals):
        self.__service_url = service_url
        self.__language = language
        self.__lat = lat
        self.__lon = lon
        self.__alt = alt
        self.__logger = logging.getLogger(__name__)

        self.__times = forecast_intervals
        self.__codes = {"clearsky:":"bezchmurnie","fair":"lekkie_zachmurzenie","partlycloudy":"czesciowe_zachmurzenie","cloudy":"pochmurno","rainshowers":"przelotne_opady_deszczu","rainshowersandthunder":"przelotna_burza","sleetshowers":"przelotne_opady_s_niegu_z_deszczem","snowshowers":"przelotne_opady_s_niegu","rain":"opady_deszczu","heavyrain":"intensywne_opady_deszczu","heavyrainandthunder":"burza_z_intensywnymi_opadami_deszczu","sleet":"snieg_z_deszczem","snow":"opady_sniegu","snowandthunder":"burza_z_opadami_s_niegu","fog":"zamglenia","sleetshowersandthunder":"przelotna_burza_z_opadami_deszczu_ze_s_niegiem","rainandthunder":"burza","sleetandthunder":"burza_z_opadami_deszczu_ze_s_niegiem","lightrainshowersandthunder":"burza_z_lekkimi_opadami_deszczu","heavyrainshowersandthunder":"przelotna_burza_z_intensywnymi_opadami_deszczu","lightssleetshowersandthunder":"przelotna_burza_z_lekkimi_opadami_deszczu_ze_s_niegiem","heavysleetshowersandthunder":"przelotna_burza_z_intensywnymi_opadami_deszczu_ze_s_niegiem","lightssnowshowersandthunder":"przelotna_burza_z_lekkimi_opadami_s_niegu","heavysnowshowersandthunder":"przelotna_burza_z_intensywnymi_opadami_s_niegu","lightrainandthunder":"burza_z_lekkimi_opadami_deszczu","lightsleetandthunder":"burza_z_lekkimi_opadami_deszczu_ze_s_niegiem","heavysleetandthunder":"burza_z_intensywnymi_opadami_deszczu_ze_s_niegiem","lightsnowandthunder":"burza_z_lekkimi_opadami_deszczu","heavysnowandthunder":"burza_z_intensywnymi_opadami_s_niegu","lightrainshowers":"lekka_mzawka","heavyrainshowers":"silna_mzawka","lightsleetshowers":"lekkie_przelotne_opady_deszczu_ze_s_niegiem","heavysleetshowers":"intensywne_przelotne_opady_deszczu_ze_s_niegiem","lightsnowshowers":"przelotne_lekkie_opady_s_niegu","heavysnowshowers":"./_opady_s_niegu","lightrain":"lekkie_opady_deszczu","lightsleet":"lekkie_opady_deszczu_ze_s_niegiem","heavysleet":"intensywne_opady_deszczu_ze_s_niegiem","lightsnow":"lekkie_opady_s_niegu","heavysnow":"intensywne_opady_sniegu"}
    
    def getForecasts(self, timeseries):
        mesurements = []
        for mes in timeseries:
            date = datetime.strptime(mes["time"], "%Y-%m-%dT%H:%M:%SZ")
            date = date.replace(tzinfo=timezone.utc)
            mesurements.append((date,mes))
        
        forecasts = []
        for time in self.__times:
            td = []
            for mes in [m[0] for m in mesurements]:
                td.append(abs(abs(mes-(datetime.now(timezone.utc)+timedelta(hours=time)))))
            self.__logger.info(f"Prognoza na nastepne {time}h z {mesurements[td.index(min(td))][0]}")
            forecasts.append((time, mesurements[td.index(min(td))][1]))
        return forecasts

    def getMessage(self, forecasts):
        message = ""

        for i, forecast in enumerate(forecasts):
            time = forecast[0]

            code = self.__codes[forecast[1]["data"]["next_1_hours"]["summary"]["symbol_code"].split('_')[0]]
            
            meteo = forecast[1]["data"]["instant"]["details"]
            
            temp = self.__language.read_temperature(round(meteo["air_temperature"]))
            wind = self.__language.read_speed(round(meteo["wind_speed"]*3.6), "kmph")
            wind_dir = self.wind_direction_name(int(meteo["wind_from_direction"]))
            hum = self.__language.read_percent(round(meteo["relative_humidity"]))
            clouds = self.__language.read_percent(round(meteo["cloud_area_fraction"]))
            press = self.__language.read_pressure(round(meteo["air_pressure_at_sea_level"]))

            message += f"prognoza_na_nastepne {self.__language.read_validity_hour(time)} _ {code} _ pokrywa_chmur {clouds} _ temperatura {temp} cisnienie {press} wilgotnosc {hum}  _ wiatr {wind_dir} {wind} _ "

        return message[0:-2]

    def get_data(self):
        url = f"{self.__service_url}?lat={self.__lat}&lon={self.__lon}&altitude={self.__alt}"
        data = self.requestData(url, self.__logger, 15, 3).json()

        self.__logger.info(f'Dane prognozy z {data["properties"]["meta"]["updated_at"]}')
        forecasts = self.getForecasts(data["properties"]["timeseries"])
        message = self.getMessage(forecasts)

        return(
            {
                "message": message,
                "source": "open_weather_map",
            }
        )