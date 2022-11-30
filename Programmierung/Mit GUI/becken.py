###Authored by Manuel Leutwyler


#Importieren von verschiednen Modulen
# import RPi.GPIO as GPIO

from datetime import datetime as dt
from datetime import timedelta

from time import sleep

from requests import get, post

#Importiert Zeitplan für Lampenschaltung
import timetable


class Becken:
    def __init__(self, ph_sensor_kanal, pins, ph_wert=7, ph_bereich=0.5,
                intervall_ph_minuten=4, intervall_nährstoff_stunden=24,
                einlasszeit_ph_sekunden=20, einlasszeit_nährstoff_sekunden=20,
                ummischzeit_wasser_sekunden=8):

        self.PINS = tuple(pins)

        #Konstanten für pH-Wert Anpassung
        self.PH_SENSOR_KANAL = ph_sensor_kanal

        self.PH_ZIELWERT = ph_wert
        self.PH_BEREICH = ph_bereich

        self.PH_INTERVALL = timedelta(minutes=intervall_ph_minuten)

        self.SÄURE_PIN = pins[0]
        self.BASE_PIN = pins[1]

        self.PH_EINLASSZEIT = einlasszeit_ph_sekunden

        #Konstanten für Wasserzufuhr
        self.WASSER_UMMISCHZEIT = ummischzeit_wasser_sekunden
        self.WASSER_PIN = pins[3]

        #Konstanten für Nährstoffe
        self.NÄHRSTOFFE_EINLASSZEIT = einlasszeit_nährstoff_sekunden

        self.NÄHRSTOFF_PIN = pins[2]

        self.NÄHRSTOFF_INTERVALL = timedelta(hours=intervall_nährstoff_stunden)

        #Konstanten für Lampe
        self.LICHT_PIN = pins[4]

        #Zeitspeicher
        self.ph_letzte_kontrolle = None
        self.nährstoff_letzte_anpassung = None

        #Andere Variabeln
        self.licht_ein = False
        self.letztes_licht = dt.now().time()
        self.nächstes_licht = dt.now().time()

    def init(self):
        #Setzt die Zeiten der letzten Aktionen so,
        #   dass diese direkt beim Start ausgeführt werden
        self.ph_letzte_kontrolle = dt.now() - self.PH_INTERVALL
        self.nährstoff_letzte_anpassung = dt.now() - self.NÄHRSTOFF_INTERVALL

        #Ordnet den verwendeten Pins die Funktion 'output' zu
        GPIO.setmode(GPIO.BOARD)
        for pin in self.PINS:
            GPIO.setup(pin, GPIO.OUT)


    def ph_wert(self):
        #Ist die letzte Messung schon länger als vorgesehen her?
        if dt.now() - self.PH_INTERVALL >= self.ph_letzte_kontrolle:
            ph_wert = self.ph_wert_jetzt()
            #Speichert den pH-Wert im Output-file
            self.daten_speichern(f'pH_Wert_{self.PH_SENSOR_KANAL}', f'{dt.now()}---{ph_wert}')

            #Ist der pH-Wert zu hoch?
            if ph_wert > self.PH_ZIELWERT + self.PH_BEREICH:
                self.ventil_öffnen(self.SÄURE_PIN, self.PH_EINLASSZEIT)
                #Speichert Daten in einem Output-file und postet sie auf dweet.io
                self.daten_speichern(f'pH_Anpassung_{self.PH_SENSOR_KANAL}',
                                     f'{dt.now()}---säure---{ph_wert}')
                self.daten_posten(f'Letzte_pH_{self.PH_SENSOR_KANAL}',
                                  f'{dt.now()}_säure')

            #Ist der pH-Wert zu tief?
            elif ph_wert < self.PH_ZIELWERT - self.PH_BEREICH:
                self.ventil_öffnen(self.BASE_PIN, self.PH_EINLASSZEIT)
                #Speichert Daten in einem Output-file und postet sie auf dweet.io 
                self.daten_speichern(f'pH_Anpassung_{self.PH_SENSOR_KANAL}',
                                     f'{dt.now()}---base---{ph_wert}')
                self.daten_posten(f'Letzte_pH_{self.PH_SENSOR_KANAL}',
                                  f'{dt.now()}_base')

            #Vermischt die Säure oder Base mit Wasserströmung
            self.ventil_öffnen(self.WASSER_PIN, self.WASSER_UMMISCHZEIT)

            self.ph_letzte_kontrolle = dt.now()

    def ph_wert_jetzt(self):
        #Lädt den aktuellen pH-Wert von dweet.io herunter
        #   Der pH-Wert wird von einem Windows Computer hochgeladen
        daten = get('http://dweet.io/get/latest/dweet/for/verticalfarmingkanti')
        messung = daten.json()['with'][0]['content']
        ph_wert = messung[self.PH_SENSOR_KANAL]
        return ph_wert

    def ventil_öffnen(self, pin, dauer):
        #Funktion für das öffnen von Ventilen
        GPIO.output(pin, GPIO.HIGH)
        sleep(dauer)
        GPIO.output(pin, GPIO.LOW)

    def nährstoffe(self):
        #Zur richtigen Zeit wird Nährstofflösung ins Becken gegeben
        if dt.now() - self.NÄHRSTOFF_INTERVALL >= self.nährstoff_letzte_anpassung:
            self.ventil_öffnen(self.NÄHRSTOFF_PIN, self.NÄHRSTOFFE_EINLASSZEIT)
            #Speichert Daten in einem Output-file und postet sie auf dweet.io 
            self.daten_speichern(f'Nährstoffe_Anpassung_{self.PH_SENSOR_KANAL}',
                                 f'{dt.now()}---{self.NÄHRSTOFFE_EINLASSZEIT}')
            self.daten_posten(f'Letzte_Nährstoffe_{self.PH_SENSOR_KANAL}',
                              str(dt.now()))

            self.nährstoff_letzte_anpassung = dt.now()

    def licht(self):
        #Liest die Zeit von Sonnenauf- und untergang vom
        #   entsprechenden Tag aus timetable.py
        tag_des_jahres = dt.now().timetuple().tm_yday

        arr_auf = timetable.timetable[tag_des_jahres]["sunrise"]
        arr_unter = timetable.timetable[tag_des_jahres]["sunset"]

        zeit_sonnenaufgang = dt(1,1,1,arr_auf[0], arr_auf[1], arr_auf[2]).time()
        zeit_sonnenuntergang = dt(1,1,1,arr_unter[0], arr_unter[1], arr_unter[2]).time()

        jetzt = dt.now().time()

        #Ist es Tag? Dann schalte die Lampe aus
        if (jetzt > zeit_sonnenaufgang and jetzt < zeit_sonnenuntergang):
            GPIO.output(self.LICHT_PIN, GPIO.LOW)
            #Postet Daten auf dweet.io
            self.daten_posten(f'Lampe_eingeschaltet_{self.PH_SENSOR_KANAL}', 'Nein')

        #Ist es Nacht? Dann schalte die Lampe ein
        else:
            GPIO.output(self.LICHT_PIN, GPIO.HIGH)
            #Postet Daten auf dweet.io
            self.daten_posten(f'Lampe_eingeschaltet_{self.PH_SENSOR_KANAL}', 'Ja')


    def daten_posten(self, variable, information):
        #Funktion für das Posten von Informationen auf dweet.io
        post(f'https://dweet.io/dweet/for/verticalfarmingkanti?{variable}={information}',
             timeout=10)


    def daten_speichern(self, file_name, information):
        #Funktion für das Speichern von Daten in Output-files
        file = open(file_name + '.txt', 'a')
        file.write(information + '\n')
        file.close()

    def alle_ventile_schliessen(self):
        #Funktion die Sicherstellt, dass bei
        #   Fehlermeldungen alle Ventile geschlossen werden
        for pin in self.PINS:
            GPIO.output(pin, GPIO.LOW)
        
