import logging
from colorcodes import *
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from sr0wx_module import SR0WXModule

class FiresSq2ips(SR0WXModule):
    def __init__(self, language, service_url, zone):
        self.__service_url = service_url
        self.__language = language
        self.__zone = zone
        self.__logger = logging.getLogger(__name__)
        self.__codes = {"0": "brak_zagroz_enia", "1": "mal_e_zagroz_enie", "2": "s_rednie_zagroz_enie", "3": "duz_e_zagroz_enie"}
    def parseTable(self, table):


        rows = []
        for i, row in enumerate(table.find_all('tr')):
            if i > 0:
                els = []
                for el in row.find_all('td'):
                    els.append(el.text)
                rows.append(els)

        for row in rows:
            if len(row) > 1 and self.__zone in row[0]:
                return(row[1:])
    def parseLabel(self, label, l):
        rows = []
        for i, row in enumerate(label.find_all('tr')):
            els = []
            for el in row.find_all('th'):
                els.append(el.text)
            rows.append(els)
        return(rows[-1][-l:])
    def processDate(self, text):
        date = datetime.strptime(text[-15:], "%Y-%m-%d%H:%M")
        if date.date() == datetime.now().date():
            return("dzis")
        elif date.date() == datetime.now().date()+timedelta(days=1):
            return("jutro")
        elif date.date() == datetime.now().date()+timedelta(days=2):
            return("po_jutrze")
        else:
            raise Exception("Invalid date")

    def processData(self, row):

        if row == "brak danych":
            return None
            self.__logger.warning(COLOR_WARNING + "Brak danych z obszaru" + COLOR_ENDC)
        elif " - " in row and len(row.split()) == 3:
            return(row.split()[0])
        else:
            self.__logger.warning(COLOR_WARNING + "Nieprawidłowe dane" + COLOR_ENDC)
            return None
    
    def get_data(self, connection):
        try:
            html = self.requestData(self.__service_url, self.__logger, 20, 3).text

            soup = BeautifulSoup(html, 'html.parser')

            table = soup.find_all('table')[0]
            warnings_raw = self.parseTable(table)
            if warnings_raw is None:
                self.__logger.error(COLOR_FAIL + "Brak danych ze źródła" + COLOR_ENDC)
                connection.send({
                    "message": None,
                    "source": "",
                })
            else:
                warnings = []
                for c in warnings_raw:
                    warnings.append(self.processData(c))
                
                if set(warnings) == {None}:
                    self.__logger.error(COLOR_FAIL + "Brak żadnych danych z czujników" + COLOR_ENDC)
                    connection.send({
                        "message": None,
                        "source": "",
                    })
                else:
                    label_table = soup.find_all('table')[1]
                    label = self.parseLabel(label_table, len(warnings))

                    dates = []
                    for l in label:
                        dates.append(self.processDate(l))

                    dictmsg = {}
                    for warn, date in zip(warnings, dates):
                        if date in dictmsg:
                            if warn > dictmsg[date]:
                                dictmsg[date] = warn
                        else:
                            dictmsg[date] = warn

                    message = "zagroz_enie_poz_arowe_laso_w _ "
                    for msg in dictmsg:
                        message += " ".join([msg, self.__codes[dictmsg[msg]], "_ "])

                    connection.send({
                        "message": message,
                        "source": "swpc",
                    })
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())
