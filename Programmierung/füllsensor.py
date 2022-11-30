###Authored by Manuel Leutwyler

import RPi.GPIO as GPIO
from requests import post

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11, GPIO.IN)

while True:
    #Ist der Stromkreis geschlossen?
    if GPIO.input(11):
        #Dann sende die Nachricht 'Behälter_nachfüllen=Nein'
        post('https://dweet.io/dweet/for/verticalfarmingkanti?Behälter_nachfüllen=Nein')
    else:
        #Andernfalls sende die Nachricht 'Behälter_nachfüllen=Ja'
        post('https://dweet.io/dweet/for/verticalfarmingkanti?Behälter_nachfüllen=Ja')
