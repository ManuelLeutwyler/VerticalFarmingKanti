###Authored by Manuel Leutwyler

import becken

becken_rosmarin = becken.Becken('ch2', [35, 37, 33, 32, 10], ph_wert=6.5, ph_bereich=0.5)
becken_peterli = becken.Becken('ch3', [40, 38, 36, 31, 8], ph_wert=6, ph_bereich=0.5)

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
    #Funktion für das sichere schliessen
    #   des Programms
    becken_rosmarin.alle_ventile_schliessen()
    becken_peterli.alle_ventile_schliessen()


if __name__ == '__main__':
    running = True
    
    setup()
    while running:
        try:
            loop()
        except (Exception, KeyboardInterrupt):
            safe_exit()
            running = False

    safe_exit()
