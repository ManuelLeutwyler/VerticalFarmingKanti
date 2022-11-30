###Authored by Manuel Leutwyler

from labquest import LabQuest
import requests
from time import sleep
lq = LabQuest()

lq.open()
lq.select_sensors(ch2='lq_sensor', ch3='lq_sensor')
lq.start(1000)

while True:
    try:
        requests.post('http://dweet.io/dweet/for/verticalfarmingkanti?ch2=' + str(lq.read('ch2')) + '&ch3=' + str(lq.read('ch3')))
        sleep(1)
    except:
        pass
