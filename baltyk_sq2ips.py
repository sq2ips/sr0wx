# -*- coding: UTF-8 -*-

import requests
from datetime import datetime

def request(url):

    r = requests.get(url=url)
    r.encoding = r.apparent_encoding #kodowanie polskich znaków
    data = r.json()
    return(data)

region='WESTERN BALTIC'

data = request("https://baltyk.imgw.pl//getdata/forecast.php?type=sea&lang=pl")
val = list(data['validity'])

if(str(data['validity'][35:37])=='24'):
    val[35]='0'
    val[36]='0'
w_od = datetime.strptime(data['validity'][11:31], '%H:%M UTC %d.%m.%Y')

if(str(data['validity'][35:37])=='24'):
    val[35]='0'
    val[36]='0'
w_do = datetime.strptime(''.join(val[35:]), '%H:%M UTC %d.%m.%Y')
data_m = data['regions'][region]
print(data_m)