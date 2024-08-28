import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from sr0wx_module import SR0WXModule


class FiresSq2ips(SR0WXModule):
    """Moduł pobierający informacje o stopniu zagrożenia pożarowego lasów"""

    def __init__(self, language, service_url, zone):
        self.__service_url = service_url
        self.__language = language
        self.__zone = zone
        self.__logger = logging.getLogger(__name__)
        self.__codes = {
            "0": "brak_zagroz_enia",
            "1": "mal_e_zagroz_enie",
            "2": "s_rednie_zagroz_enie",
            "3": "duz_e_zagroz_enie",
        }

    def parseTable(self, table):
        rows = []
        for i, row in enumerate(table.find_all("tr")):
            if i > 0:
                els = []
                for el in row.find_all("td"):
                    els.append(el.text)
                rows.append(els)

        for row in rows:
            if len(row) > 1 and self.__zone in row[0]:
                return row[1:]

    def parseLabel(self, label, l):
        rows = []
        for i, row in enumerate(label.find_all("tr")):
            els = []
            for el in row.find_all("th"):
                els.append(el.text)
            rows.append(els)
        return rows[-1][-l:]

    def processDate(self, text):
        date = datetime.strptime(text[-15:], "%Y-%m-%d%H:%M")
        if date.date() == datetime.now().date():
            return "dzis"
        elif date.date() == datetime.now().date() + timedelta(days=1):
            return "jutro"
        elif date.date() == datetime.now().date() + timedelta(days=2):
            return "po_jutrze"
        else:
            raise Exception("Invalid date")

    def processData(self, row):
        if row == "brak danych":
            return None
            self.__logger.warning("Brak danych z obszaru")
        elif " - " in row and len(row.split()) == 3:
            return row.split()[0]
        else:
            self.__logger.warning("Nieprawidłowe dane")
            return None

    def get_data(self):
        self.__logger.info("::: Pobieranie danych o zagrożeniu pożarowym lasów...")
        html = self.requestData(self.__service_url, self.__logger, 20, 3).text
        self.__logger.info("::: Przetwarzanie danych...")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find_all("table")[0]
        warnings_raw = self.parseTable(table)
        if warnings_raw is None:
            raise ValueError("Brak danych ze źródła")
        else:
            warnings = []
            for c in warnings_raw:
                warnings.append(self.processData(c))
            if set(warnings) == {None}:
                raise ValueError("Brak żadnych danych z czujników")
            else:
                label_table = soup.find_all("table")[1]
                label = self.parseLabel(label_table, len(warnings))
                dates = []
                for l in label:
                    dates.append(self.processDate(l))
                dictmsg = {}
                for warn, date in zip(warnings, dates):
                    if warn is not None:
                        if date in dictmsg:
                            if warn > dictmsg[date]:
                                dictmsg[date] = warn
                        else:
                            dictmsg[date] = warn
                message = "zagroz_enie_poz_arowe_laso_w _ "
                sk = 0
                for i in range(len(dictmsg)):
                    if sk > 0:
                        sk -= 0
                        continue
                    ind = []
                    for j in range(i, len(dictmsg)):
                        if list(dictmsg.values())[i] == list(dictmsg.values())[j]:
                            ind.append(j)
                    sk = len(ind) - 1
                    msglist = []
                    for i in ind:
                        msglist.append(list(dictmsg.keys())[i])
                    if len(msglist) > 1:
                        msglist.insert(len(msglist) - 1, "i")
                    message += " ".join(
                        msglist + [self.__codes[list(dictmsg.values())[i]], "_ "]
                    )
                return(
                    {
                        "message": message,
                        "source": "traxelektronik",
                    }
                )