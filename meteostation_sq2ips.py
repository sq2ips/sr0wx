import socket

from sr0wx_module import SR0WXModule

import logging
from colorcodes import *

class MeteoStationSq2ips(SR0WXModule):
    def __init__(self, language, ip, port):
        self.__logger = logging.getLogger(__name__)
        self.__language = language
        self.__ip = ip
        self.__port=port
        self.__coms = ["atemp\n", "ahum\n", "awin_dir\n", "awin_avr\n", "awin_gus\n", "rain\n", "win_qual\n", "rssi\n", "last\n", "atime\n"]
    def downloadData(self):
        data = []
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
        sock.settimeout(10)
        for i in self.__coms:
            sock.sendto(i.encode("UTF-8"), (self.__ip, self.__port))
            data.append(float(sock.recvfrom(1024)[0].decode("UTF-8")))
        self.__logger.info("Parameters got:")
        self.__logger.info(self.__coms)
        self.__logger.info(data)
        data = [0.0, 0.0, 0.0, 0.0, 0.0, 550.4, 0.0, -71.0, 5.0, 184124.0]
        if data[0] == 0 and data[1] == 0 and data[2] == 0 and data[3] == 0 and data[4] == 0:
            raise Exception("received zeros from station")
        else:
            return(data)
    def angleProcess(self, ang):
        if ang>=337.5 or ang<22.5:
            return "polnocny"
        elif ang>=22.5 and ang<67.5:
            return "po_l_nocno wschodni"
        elif ang>=67.5 and ang<112.5:
            return "wschodni"
        elif ang>=112.5 and ang<157.5:
            return "pol_udniowo wschodni"
        elif ang>=157.5 and ang<202.5:
            return "poludniowy"
        elif ang>=202.5 and ang<247.5:
            return "pol_udniowo zachodni"
        elif ang>=247.5 and ang<292.5:
            return "zachodni"
        elif ang>=292.5 and ang<337.5:
            return "po_l_nocno zachodni"
    def odm(self, f):
        f = str(f)
        d = {"1":"jeden",
            "2":"dwoch",
            "3":"trzech",
            "4":"czterech",
            "5":"pieciu",
            "6":"szesciu",
            "7":"siedmiu",
            "8":"osmiu",
            "9":"dziewieciu",
            "10":"dziesieciu",
            "11":"jedenastu",
            "12":"dwunastu",
            "13":"trzynastu",
            "14":"czternastu",
            "15":"pietnastu",
            "16":"szesnastu",
            "17":"siedemnastu",
            "18":"osiemnastu",
            "19":"dziewietnastu",
            "20":"dwudziestu",
            "30":"trzydziestu",
            "40":"czterdziestu",
            "50":"piecdziesieciu",
            "60":"szejscdziesieciu",
            "70":"siedemdziesieciu",
            "80":"osiemdziesieciu",
            "90":"dziewiecdziesieciu",
            "100":"stu",
            "200":"dwustu",
            "300":"trzystu",
            "400":"czterystu",
            "500":"pieciuset",
            "600":"szesciuset",
            "700":"siedmiuset",
            "800":"osmiuset",
            "900":"dziewieciuset"}
        if len(f) == 1:
            if f == "1":
                return("jednego kilometra_na_godzine")
            else:
                return(d[f]+" kilometrow_na_godzine")
        elif len(f) == 2:
            if f[1]=="0" or f[0]=="1":
                return(d[f]+" kilometrow_na_godzine")
            else:
                return(d[f[0]+"0"]+" "+d[f[1]]+" kilometrow_na_godzine")
        elif len(f) == 3:
            if f[1]=="0" and f[2]=="0":
                return(d[f]+" kilometrow_na_godzine")
            else:
                if f[2] != "0":
                    if f[1] == "0":
                        return(d[f[0]+"00"]+" "+d[f[2]]+" kilometrow_na_godzine")
                    else:
                        return(d[f[0]+"00"]+" "+d[f[1]+"0"]+" "+d[f[2]]+" kilometrow_na_godzine")
                else:
                    if f[1] == "0":
                        return(d[f[0]+"00"]+" kilometrow_na_godzine")
                    else:
                        return(d[f[0]+"00"]+" "+d[f[1]+"0"]+" kilometrow_na_godzine")

    def get_data(self, connection):
        try:
            data = self.downloadData()
            message = "aktualny_stan_pogody _ "
            #if data[5]>
            message += f"temperatura " + self.__language.read_temperature(round(data[0])) + " "
            message += f"wilgotnosc "+self.__language.read_percent(round(data[1]))+" _ "
            if round(data[3]*3.6) < 1:
                message+=" brak_wiatru "
            else:
                if data[6]>0.7:
                    message += f"wiatr {self.angleProcess(data[2])} "
                else:
                    message += f"wiatr zmienny {self.angleProcess(data[2])} "
                if data[4]-data[3]>2.0:
                    message += self.__language.read_speed(round(data[3]*3.6), 'kmph').split()[:-1][0]+" w_porywach do "+ self.odm(round(data[4]*3.6))+ " "
                else:
                    message += self.__language.read_speed(round(data[3]*3.6),'kmph')+ " "
            message += " _ "
            connection.send({
                "message": message,
                "source": "",
            })
            return {
                "message": message,
                "source": "",
            }
        except Exception as e:
            self.__logger.exception(COLOR_FAIL + "Exception when running %s: %s"+ COLOR_ENDC, str(self), e)
            connection.send(dict())