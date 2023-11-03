# -*- coding: UTF-8 -*-

import requests
from datetime import datetime

def request(url):

    r = requests.get(url=url)
    r.encoding = r.apparent_encoding #kodowanie polskich znaków
    data = r.json()
    return(data)
def process(data):
    region='WESTERN BALTIC'
    alert_level = data['regions'][region]['alert_level']
    forecast_now = data['regions'][region]['forecast_now']
    forecast_next = data['regions'][region]['forecast_next']
    return [alert_level, forecast_now, forecast_next]
def process_time(data):
    val = list(data['validity'])
    if(str(data['validity'][11:13])=='24'):
        val[11]='0'
        val[13]='0'
    od = datetime.strptime(data['validity'][11:31], '%H:%M UTC %d.%m.%Y')

    val = list(data['validity'])
    if(str(data['validity'][35:37])=='24'):
        val[35]='0'
        val[36]='0'
    do = datetime.strptime(data['validity'][35:], '%H:%M UTC %d.%m.%Y')
    return [od, do]
def say_data(text):
    keywords = {
        "B":"b",
        "°C":" stopni_celsjusza",
    }
    frazy = {
        "w skali b", "w_skali_b",
    }
    for i in range(len(keywords)):
        try:
            text = text.replace(list(keywords.keys())[i], keywords[list(keywords.keys())[i]])
        except KeyError:
            pass
    
    
    
    text = text\
            .replace(("ą"), "a_").replace(("Ą"), "a_")\
            .replace(("ć"), "c_").replace(("Ć"), "c_")\
            .replace(("ę"), "e_").replace(("Ę"), "e_")\
            .replace(("ł"), "l_").replace(("Ł"), "l_")\
            .replace(("ń"), "n_").replace(("Ń"), "n_")\
            .replace(("ó"), "o_").replace(("Ó"), "o_")\
            .replace(("ś"), "s_").replace(("Ś"), "s_")\
            .replace(("ź"), "z_").replace(("Ź"), "z_")\
            .replace(("ż"), "z_").replace(("Ż"), "z_")\
            .replace(":","")\
            .replace(",","")\
            .replace("."," _ ")\
            .lower()
    return(text)




data = request("https://baltyk.imgw.pl//getdata/forecast.php?type=sea&lang=pl")


print(say_data(process(data)[1]))