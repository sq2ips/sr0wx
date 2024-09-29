import socket
from multiprocessing import Process, Pipe

from sr0wx_module import SR0WXModule

import logging


class MeteoStationSq2ips(SR0WXModule):
    """Moduł pobierający dane o pogodzie ze stacji przez UDP"""

    def __init__(self, language, ip, port):
        self.__logger = logging.getLogger(__name__)
        self.__language = language
        self.__ip = ip
        self.__port = port
        self.__coms = [
            "atemp\n",
            "ahum\n",
            "awin_dir\n",
            "awin_avr\n",
            "awin_gus\n",
            "rain\n",
            "win_qual\n",
            "apress\n",
            "rssi\n",
            "last\n",
            "atime\n",
        ]

    def downloadData(self, con, ip, port):
        w = True
        counter = 0
        while w:
            try:
                data = []
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
                sock.settimeout(30)
                for i in self.__coms:
                    sock.sendto(i.encode("UTF-8"), (ip, port))
                    d = sock.recvfrom(1024)[0].decode("UTF-8")
                    if d == "\n":
                        data.append(0.0)
                    else:
                        data.append(float(d))
                con.send(data)
                w = False
                con.close()
            except Exception as e:
                if counter < 3:
                    self.__logger.warning(
                        "Exception when getting data from %s: %s. Trying again...",
                        ip,
                        e,
                    )
                    counter += 1
                else:
                    self.__logger.error(
                        "Exception when getting data from %s: %s", ip, e
                    )
                    con.send(None)
                    con.close()

    def compare(self):
        data = []
        processes = []
        conn = []
        for ip in self.__ip:
            parent_conn, child_conn = Pipe()
            conn.append(parent_conn)
            processes.append(
                Process(target=self.downloadData, args=(child_conn, ip, self.__port))
            )
            processes[-1].start()
        for pro in processes:
            pro.join()
        for con in conn:
            rec = con.recv()
            if rec is not None:
                data.append(rec)
        if data == []:
            raise Exception("No functioning stations")
        self.__logger.info("Parameters got:")
        self.__logger.info("IP: " + str(self.__coms))
        for i in range(len(data)):
            self.__logger.info(f"{self.__ip[i]}: {str(data[i])}")

        self.__logger.info("Starting comparison...")
        dataf = []
        for i in range(len(data)):
            if (
                data[i][self.__coms.index("atemp\n")] == 0
                and data[i][self.__coms.index("ahum\n")] == 0
                and data[i][self.__coms.index("awin_dir\n")] == 0
                and data[i][self.__coms.index("awin_gus\n")] == 0
                and data[i][self.__coms.index("rain\n")] == 0
            ):
                self.__logger.warning(
                    f"Station {self.__ip[i]} reported only zeros, skipping..."
                )
            else:
                dataf.append(data[i])

        prefered_index = 0
        prefered_atime = dataf[0][self.__coms.index("atime\n")]
        for i in range(1, len(dataf) - 1):
            if dataf[i][self.__coms.index("atime\n")] < prefered_atime:
                prefered_index = i
                prefered_atime = dataf[i][self.__coms.index("atime\n")]
        apress = 0
        c = 0
        for d in dataf:
            if d != 0.0:
                apress += d[self.__coms.index("apress\n")]
                c += 1
        apress = apress / c
        for i in range(len(dataf)):
            if d == 0.0:
                dataf[i][self.__coms.index("apress\n")] = apress

        if dataf == []:
            raise Exception("No functioning stations")
        else:
            self.__logger.info(f"Using station {self.__ip[prefered_index]}")
            return dataf[prefered_index]

    def angleProcess(self, ang):
        if ang >= 337.5 or ang < 22.5:
            return "polnocny"
        elif ang >= 22.5 and ang < 67.5:
            return "po_l_nocno wschodni"
        elif ang >= 67.5 and ang < 112.5:
            return "wschodni"
        elif ang >= 112.5 and ang < 157.5:
            return "pol_udniowo wschodni"
        elif ang >= 157.5 and ang < 202.5:
            return "poludniowy"
        elif ang >= 202.5 and ang < 247.5:
            return "pol_udniowo zachodni"
        elif ang >= 247.5 and ang < 292.5:
            return "zachodni"
        elif ang >= 292.5 and ang < 337.5:
            return "po_l_nocno zachodni"

    def get_data(self):
        data = self.compare()
        message = "aktualny_stan_pogody _ "
        message += (
            "temperatura " + self.__language.read_temperature(round(data[0])) + " "
        )
        if data[7] != 0.0:
            message += (
                "cisnienie " + self.__language.read_pressure(round(data[7])) + " "
            )
        message += (
            "wilgotnosc " + self.__language.read_percent(round(data[1])) + " _ "
        )
        if round(data[3] * 3.6) < 1:
            message += " brak_wiatru "
        else:
            if data[6] > 0.7:
                message += f"wiatr {self.angleProcess(data[2])} "
            else:
                message += f"wiatr zmienny {self.angleProcess(data[2])} "
            if data[4] - data[3] > 2.0:
                message += (
                    self.__language.read_speed(
                        round(data[3] * 3.6), "kmph"
                    ).split()[:-1][0]
                    + " w_porywach do "
                    + self.__language.read_gust(round(data[4] * 3.6))
                    + " "
                )
            else:
                message += (
                    self.__language.read_speed(round(data[3] * 3.6), "kmph") + " "
                )
        return(
            {
                "message": message,
                "source": "",
            }
        )