import logging
import re
import time

from sr0wx_module import SR0WXModule


class GeoMagneticSq9atk(SR0WXModule):
    """Moduł pobierająca info o sytuacji geomagnetycznej"""

    def __init__(self, language, service_url):
        self.__language = language
        self.__service_url = service_url
        self.__logger = logging.getLogger(__name__)

        self.__days = ['dzis', 'jutro', 'po_jutrze']
        self.__conditions = {
            0: ' ',
            1: 'brak_istotnych_zaburzen__geomagnetycznych',   2: 'lekkie_zaburzenia_geomagnetyczne',
            3: 'umiarkowane_zabuz_enia_geomagnetyczne',      4: 'mal_a_burza_geomagnetyczna',
            5: 'umiarkowana_burza_geomagnetyczna',           6: 'silna_burza_geomagnetyczna',
            7: 'sztorm_geomagnetyczny',                      8: 'duz_y_sztorm_geomagnetyczny'
        }
        self.__seasons = {
            0: 'kro_tko_po_po_l_nocy',    3: 'nad_ranem',              6: 'rano',
            9: 'przed_pol_udniem',       12: 'wczesnym_popol_udniem', 15: 'po_pol_udniu',
            18: 'wieczorem',              21: 'przed_po_l_noca_',
        }
        self.__fluctuations = {
            0: 'niezauwaz_alne', 1: 'znikome', 2: 'lekkie',       3: 'podwyz_szone',
            4: 'umiarkowane',    5: 'duz_e',   6: 'bardzo_duz_e', 7: 'ekstremalne'
        }

    def downloadDataFromUrl(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:10.0.1) Gecko/20100101 Firefox/10.0.1',
        }
        data = self.requestData(url, self.__logger, 10, 3, headers=headers)
        return data.text


    def getDataParsedHtmlData(self):
        self.__logger.info("::: Pobieram informacje...")

        html = self.downloadDataFromUrl(self.__service_url)
        r = re.compile(r'<use href="#gm_(\d+)".*?>')

        res = r.findall(html)
        res = res[1:] # omijamy pierwszy element bo nie jest on częścią kontenera z danymi

        return res


    def groupValuesByDays(self, data):
        hour = 0
        dayNum = 1
        current_hour = int(time.strftime("%H"))

        output = {1: {}, 2: {}, 3: {}}

        for i, val in enumerate(data):
            if dayNum > 1 or hour > current_hour-1:  # omijamy godziny z przeszłości
                if dayNum < 4 and i < 24:
                    value = data[i+1]
                    output[dayNum][hour] = value

            hour += 3
            if hour > 21:
                hour = 0
                dayNum += 1

        return output

    def getStrongestConditionOfDay(self, data):
        maxValue = {
            'value': 0,
            'at': 0,
        }
        for key, row in data.items():
            row = int(row)
            key = int(key)
            if row > maxValue['value']:
                maxValue['value'] = row
                maxValue['at'] = key

        return maxValue

    def getDailyFluctuation(self, data):
        values = list(data.values())
        return int(max(values)) - int(min(values))

    def get_data(self, connection):
        try:
            values = self.getDataParsedHtmlData()
            daysValues = self.groupValuesByDays(values)
            message = ' _ sytuacja_geomagnetyczna_w_regionie '

            self.__logger.info("::: Przetwarzam dane...")
            for d, day in daysValues.items():
                if len(day) > 0:
                    message += " ".join([" _",self.__days[d-1],""])
                    condition = self.getStrongestConditionOfDay(day)

                    message += " ".join([self.__seasons[condition['at']],""])
                    message += " ".join([self.__conditions[int(condition['value'])],""])
                    message += " ".join([self.__fluctuations[self.getDailyFluctuation(day)],"wahania_dobowe "])

            connection.send({
                "message": message + "_",
                "source": "gis_meteo",
            })
        except Exception as e:
            self.__logger.exception(f"Exception when running {self}: {e}")
            connection.send(dict())