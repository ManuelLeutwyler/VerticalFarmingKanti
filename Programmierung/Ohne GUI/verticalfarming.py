###Authored by Manuel Leutwyler

import becken

running = True

becken_rosmarin = becken.Becken('ch2', [35, 37, 33, 32, 8], ph_wert=6.5, ph_bereich=0.5)
becken_peterli = becken.Becken('ch3', [40, 38, 36, 31, 10], ph_wert=6, ph_bereich=0.5)

def setup():
    #Setzt verschiedene zeitabhängige
    #   Parameter der Becken
    becken_rosmarin.init()
    becken_peterli.init()

def loop():
    #Beinhaltet alle wiederholt
    #   durchgeführten Aktionen
    becken_rosmarin.ph_wert()
    becken_peterli.ph_wert()

    becken_rosmarin.nährstoffe()
    becken_peterli.nährstoffe()

    becken_rosmarin.licht()
    becken_peterli.licht()

def safe_exit():
    #Funktion für das sichere Schliessen
    #   des Programms
    becken_rosmarin.alle_ventile_schliessen()
    becken_peterli.alle_ventile_schliessen()
    running = False


setup()
while running:
    try:
        loop()
    except (Exception, KeyboardInterrupt):
        safe_exit()

safe_exit()
