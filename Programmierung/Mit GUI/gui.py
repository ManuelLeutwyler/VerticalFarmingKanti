###Authored by Manuel Leutwyler

from datetime import timedelta
from datetime import datetime as dt
import pylab
import matplotlib.backends.backend_agg as agg
import pygame
import pygame_gui
import verticalfarming
import timetable

import matplotlib
matplotlib.use("Agg")


pygame.init()

becken_angezeigt = verticalfarming.becken_rosmarin
becken_running = False
is_day = True
letzt_stream = dt.now()
ph_stream_intervall = timedelta(seconds=10)

def getSurf(date_start, date_end):
    w = (SEC_COL_WID//50)*50
    h = ((GRAPH_HEIGHT-50)//50)*50
    fig = pylab.figure(figsize=[w//50, h//50], dpi=50)

    xpoints, ypoints = getPhData(date_start, date_end)

    ax = fig.gca()
    ax.plot(xpoints, ypoints)

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    surf = pygame.image.fromstring(raw_data, (w, h), 'RGB')
    return surf


def getPhData(date_start, date_end):
    xp = []
    yp = []
    try:
        with open('pH_Wert_'+becken_angezeigt.PH_SENSOR_KANAL+'.txt', 'r') as datafile:
            for line in datafile:
                if line[:10] > date_start and line[:10] < date_end:
                    xp.append(line[:10])
                    yp.append(float(line[26:]))

        return (xp, yp)
    except FileNotFoundError and Exception:
        pygame_gui.windows.UIMessageWindow(rect=pygame.Rect(100, 100, 200, 300),
                                           html_message="Keine Datei vorhanden. ",
                                           manager=manager)
        return ([1, 2, 3], [1, 2, 3])


pygame.display.set_caption('Autonomic Vertical Farming')
window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#333333'))

manager = pygame_gui.UIManager((800, 600))

clock = pygame.time.Clock()
is_running = True

MAIN_TEXT_COLOR = '#FFFFFF'
SECOND_TEXT_COLOR = '#CCCCAC'
DYNAMIC_COLOR = '#4EC990'

LEFT_PAD = 50
MID_PAD = 50
TOP_PAD = 50
FIR_COL_WID = 350
SEC_COL_WID = 350
NAHR_Y = TOP_PAD
WASSER_Y = TOP_PAD + 180
LICHT_Y = WASSER_Y + 140
GRAPH_HEIGHT = 300
BUTTON_Y = 500
BUTTON_SIZE = (200, 75)
VERT_PAD = 40

TEXT_SPACING = 40

INPUT_SIZE = (80, 30)
INPUT_X_FIR_COL = 200
INPUT_X_SEC_COL = 540

TITEL_FONT = pygame.font.SysFont('consolas', 28)
TEXT_FONT = pygame.font.SysFont('consolas', 20)
KLEIN_FONT = pygame.font.SysFont('consolas', 15)

BECKEN_WÄHLEN = pygame_gui.elements.UIDropDownMenu(options_list=['rosmarin', 'peterli'],
                                                   starting_option='rosmarin', relative_rect=pygame.Rect(0, 0, 120, 25),
                                                   manager=manager)

NAHR_TITEL = TITEL_FONT.render(
    'Nährstoffe', True, pygame.Color(MAIN_TEXT_COLOR))
NAHR_INTERVALL = TEXT_FONT.render(
    'Intervall:', True, pygame.Color(SECOND_TEXT_COLOR))
NAHR_INTERVALL_INPUT = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(
    (INPUT_X_FIR_COL-35, TOP_PAD + TEXT_SPACING-5), INPUT_SIZE),
    manager=manager, object_id='nahr_intervall')
NAHR_INTERVALL_WERT = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (INPUT_X_FIR_COL-35 + 75, TOP_PAD + TEXT_SPACING-5), INPUT_SIZE),
    text=str(int(becken_angezeigt.NÄHRSTOFF_INTERVALL.total_seconds()//3600))+'h',
    manager=manager)
NAHR_MENGE = TEXT_FONT.render(
    'Einlassmenge:', True, pygame.Color(SECOND_TEXT_COLOR))
NAHR_MENGE_INPUT = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(
    (INPUT_X_FIR_COL, TOP_PAD + 2*TEXT_SPACING-5), INPUT_SIZE),
    manager=manager, object_id='nahr_menge')
NAHR_MENGE_WERT = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (INPUT_X_FIR_COL + 75, TOP_PAD + 2*TEXT_SPACING-5), INPUT_SIZE),
    text=str(becken_angezeigt.NÄHRSTOFFE_EINLASSZEIT)+'s',
    manager=manager)

WASSER_TITEL = TITEL_FONT.render(
    'Ummischwasser', True, pygame.Color(MAIN_TEXT_COLOR))
WASSER_DAUER = TEXT_FONT.render(
    'Mischdauer:', True, pygame.Color(SECOND_TEXT_COLOR))
WASSER_DAUER_INPUT = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(
    (INPUT_X_FIR_COL - 25, WASSER_Y + TEXT_SPACING-5), INPUT_SIZE),
    manager=manager, object_id='wasser_dauer')
WASSER_DAUER_WERT = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (INPUT_X_FIR_COL - 25 + 75, WASSER_Y + TEXT_SPACING-5), INPUT_SIZE),
    text=str(becken_angezeigt.WASSER_UMMISCHZEIT)+'s',
    manager=manager)


LICHT_TITEL = TITEL_FONT.render('Licht', True, pygame.Color(MAIN_TEXT_COLOR))
LICHT_ZUSTAND_1 = TEXT_FONT.render(
    'Zustand:', True, pygame.Color(SECOND_TEXT_COLOR))
LICHT_ZUSTAND_2 = TEXT_FONT.render(
    '    seit', True, pygame.Color(SECOND_TEXT_COLOR))
LICHT_ZUSTAND_ANSW_1 = TEXT_FONT.render(
    'OFF', True, pygame.Color(DYNAMIC_COLOR))
LICHT_ZUSTAND_ANSW_2 = TEXT_FONT.render(
    '09:55', True, pygame.Color(DYNAMIC_COLOR))

LICHT_SCHALT = TEXT_FONT.render(
    'Nächste Schaltung:', True, pygame.Color(SECOND_TEXT_COLOR))
LICHT_SCHALT_ANSW = TEXT_FONT.render(
    '17:55', True, pygame.Color(DYNAMIC_COLOR))


PH_TITEL = TITEL_FONT.render('pH-Wert', True, pygame.Color(MAIN_TEXT_COLOR))

PH_LIVE = TITEL_FONT.render(str(6.6), True, pygame.Color('#FFFFFF'))

PH_GRAFIK = getSurf(10, 10)

PH_GRAFIK_ZEITRAUM = KLEIN_FONT.render(
    'Zeitraum', True, pygame.Color(SECOND_TEXT_COLOR))
PH_GRAFIK_START = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(
    (FIR_COL_WID + MID_PAD + 90, TOP_PAD + GRAPH_HEIGHT-2), (90, 25)),
    manager=manager)

PH_GRAFIK_ENDE = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(
    (FIR_COL_WID + MID_PAD + 180, TOP_PAD + GRAPH_HEIGHT-2), (90, 25)),
    manager=manager)
PH_GRAFIK_REFRESH = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (FIR_COL_WID + MID_PAD + 300, TOP_PAD + GRAPH_HEIGHT-2), (90, 25)), text='Refresh', manager=manager)


PH_ZIELBEREICH = TEXT_FONT.render(
    'Zielbereich:', True, pygame.Color(SECOND_TEXT_COLOR))
PH_ZIELBEREICH_INPUT_1 = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(
    (INPUT_X_SEC_COL, TOP_PAD + GRAPH_HEIGHT-5 + VERT_PAD), (INPUT_SIZE[0]//2, INPUT_SIZE[1])),
    manager=manager, object_id='ph_ziel')
PH_ZIELBEREICH_INPUT_2 = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(
    (INPUT_X_SEC_COL + INPUT_SIZE[0]//2+20, TOP_PAD + GRAPH_HEIGHT-5 + VERT_PAD), (INPUT_SIZE[0]//2, INPUT_SIZE[1])),
    manager=manager, object_id='ph_bereich')
PH_ZIELBEREICH_WERT = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (INPUT_X_SEC_COL + INPUT_SIZE[0]//2+20 + 60, TOP_PAD + GRAPH_HEIGHT-5 + VERT_PAD), INPUT_SIZE),
    text=str(becken_angezeigt.PH_ZIELWERT)+' ± ' +
    str(becken_angezeigt.PH_BEREICH),
    manager=manager)

PH_INTERVALL = TEXT_FONT.render(
    'Intervall:', True, pygame.Color(SECOND_TEXT_COLOR))
PH_INTERVALL_INPUT = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(
    (INPUT_X_SEC_COL-25, TOP_PAD + GRAPH_HEIGHT + TEXT_SPACING-5 + VERT_PAD), INPUT_SIZE),
    manager=manager, object_id='ph_intervall')
PH_INTERVALL_WERT = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (INPUT_X_SEC_COL-25 + 75, TOP_PAD + GRAPH_HEIGHT + TEXT_SPACING-5 + VERT_PAD), INPUT_SIZE),
    text=str(int(becken_angezeigt.PH_INTERVALL.total_seconds()//60))+'m',
    manager=manager)

PH_MENGE = TEXT_FONT.render('Einlassmenge:', True,
                            pygame.Color(SECOND_TEXT_COLOR))
PH_MENGE_INPUT = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(
    (INPUT_X_SEC_COL+10, TOP_PAD + GRAPH_HEIGHT + 2*TEXT_SPACING-5 + VERT_PAD), INPUT_SIZE),
    manager=manager, object_id='ph_menge')
PH_MENGE_WERT = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (INPUT_X_SEC_COL+10 + 75, TOP_PAD + GRAPH_HEIGHT + 2*TEXT_SPACING-5 + VERT_PAD), INPUT_SIZE),
    text=str(int(becken_angezeigt.PH_EINLASSZEIT))+'s',
    manager=manager)

START_STOP_BUTTON = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (FIR_COL_WID + MID_PAD, BUTTON_Y), BUTTON_SIZE), text='START',
    manager=manager, object_id='start_stop')


while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame.USEREVENT:
            if event.user_type == 32852:
                if event.ui_element == START_STOP_BUTTON:
                    becken_running = not becken_running
                    if becken_running:
                        verticalfarming.setup()
                    else:
                        verticalfarming.safe_exit()
                    START_STOP_BUTTON.set_text(
                        'STOP' if becken_running else 'START')
                if event.ui_element == PH_GRAFIK_REFRESH:
                    start_time = PH_GRAFIK_START.text
                    end_time = PH_GRAFIK_ENDE.text

                    PH_GRAFIK = getSurf(start_time, end_time)

            if event.user_type == 32861:
                if event.text == 'rosmarin':
                    becken_angezeigt = verticalfarming.becken_rosmarin
                elif event.text == 'peterli':
                    becken_angezeigt = verticalfarming.becken_peterli
                NAHR_INTERVALL_WERT.set_text(
                    str(int(becken_angezeigt.NÄHRSTOFF_INTERVALL.total_seconds()//3600))+'h')
                NAHR_MENGE_WERT.set_text(
                    str(becken_angezeigt.NÄHRSTOFFE_EINLASSZEIT)+'s')
                WASSER_DAUER_WERT.set_text(
                    str(becken_angezeigt.WASSER_UMMISCHZEIT)+'s')
                PH_INTERVALL_WERT.set_text(
                    str(int(becken_angezeigt.PH_INTERVALL.total_seconds()//60))+'m')
                PH_ZIELBEREICH_WERT.set_text(
                    str(becken_angezeigt.PH_ZIELWERT)+' ± '+str(becken_angezeigt.PH_BEREICH))
                PH_MENGE_WERT.set_text(
                    str(becken_angezeigt.PH_EINLASSZEIT)+'s')

            if event.user_type == 32858:
                try:
                    id = event.ui_element.object_ids[0]
                    if id == 'nahr_intervall':
                        becken_angezeigt.NÄHRSTOFF_INTERVALL = timedelta(
                            hours=float(event.text))
                        NAHR_INTERVALL_INPUT.set_text('')
                        a = int(becken_angezeigt.NÄHRSTOFF_INTERVALL.total_seconds()//3600)
                        NAHR_INTERVALL_WERT.set_text(
                            str(a)+'h' if a != 0 else str(1)+'h')
                    elif id == 'nahr_menge':
                        becken_angezeigt.NÄHRSTOFFE_EINLASSZEIT = int(
                            event.text)
                        NAHR_MENGE_INPUT.set_text('')
                        NAHR_MENGE_WERT.set_text(
                            str(becken_angezeigt.NÄHRSTOFFE_EINLASSZEIT)+'s')
                    elif id == 'wasser_dauer':
                        becken_angezeigt.WASSER_UMMISCHZEIT = int(event.text)
                        WASSER_DAUER_INPUT.set_text('')
                        WASSER_DAUER_WERT.set_text(
                            str(becken_angezeigt.WASSER_UMMISCHZEIT)+'s')
                    elif id == 'ph_intervall':
                        becken_angezeigt.PH_INTERVALL = timedelta(
                            minutes=float(event.text))
                        PH_INTERVALL_INPUT.set_text('')
                        PH_INTERVALL_WERT.set_text(
                            str(int(becken_angezeigt.PH_INTERVALL.total_seconds()//60))+'m')
                    elif id == 'ph_ziel':
                        becken_angezeigt.PH_ZIELWERT = float(event.text)
                        PH_ZIELBEREICH_INPUT_1.set_text('')
                        PH_ZIELBEREICH_WERT.set_text(
                            str(becken_angezeigt.PH_ZIELWERT)+' ± '+str(becken_angezeigt.PH_BEREICH))
                    elif id == 'ph_bereich':
                        becken_angezeigt.PH_BEREICH = float(event.text)
                        PH_ZIELBEREICH_INPUT_2.set_text('')
                        PH_ZIELBEREICH_WERT.set_text(
                            str(becken_angezeigt.PH_ZIELWERT)+' ± '+str(becken_angezeigt.PH_BEREICH))
                    elif id == 'ph_menge':
                        becken_angezeigt.PH_EINLASSZEIT = int(event.text)
                        PH_MENGE_INPUT.set_text('')
                        PH_MENGE_WERT.set_text(
                            str(becken_angezeigt.PH_EINLASSZEIT)+'s')
                except:
                    pygame_gui.windows.UIMessageWindow(rect=pygame.Rect(100, 100, 200, 300),
                                                       html_message="Bitte nur Zahlen eingeben.",
                                                       manager=manager)

        manager.process_events(event)

    window_surface.blit(background, (0, 0))

    window_surface.blit(NAHR_TITEL, (LEFT_PAD, TOP_PAD))
    window_surface.blit(NAHR_INTERVALL, (LEFT_PAD, TOP_PAD + TEXT_SPACING))
    window_surface.blit(NAHR_MENGE, (LEFT_PAD, TOP_PAD + 2*TEXT_SPACING))

    window_surface.blit(WASSER_TITEL, (LEFT_PAD, WASSER_Y))
    window_surface.blit(WASSER_DAUER, (LEFT_PAD, WASSER_Y + TEXT_SPACING))

    window_surface.blit(LICHT_TITEL, (LEFT_PAD, LICHT_Y))
    window_surface.blit(LICHT_ZUSTAND_1, (LEFT_PAD, LICHT_Y + TEXT_SPACING))
    window_surface.blit(LICHT_ZUSTAND_ANSW_1,
                        (LEFT_PAD, LICHT_Y + 2*TEXT_SPACING-10))
    window_surface.blit(
        LICHT_ZUSTAND_2, (LEFT_PAD, LICHT_Y + 2*TEXT_SPACING-10))
    window_surface.blit(LICHT_ZUSTAND_ANSW_2, (LEFT_PAD +
                        100, LICHT_Y + 2*TEXT_SPACING-10))
    window_surface.blit(LICHT_SCHALT, (LEFT_PAD, LICHT_Y + 3*TEXT_SPACING))
    window_surface.blit(LICHT_SCHALT_ANSW, (LEFT_PAD,
                        LICHT_Y + 4*TEXT_SPACING-10))

    window_surface.blit(PH_TITEL, (FIR_COL_WID + MID_PAD, TOP_PAD))
    window_surface.blit(PH_GRAFIK_ZEITRAUM, (FIR_COL_WID +
                        MID_PAD, TOP_PAD + GRAPH_HEIGHT))

    window_surface.blit(PH_ZIELBEREICH, (FIR_COL_WID +
                        MID_PAD, TOP_PAD + GRAPH_HEIGHT + VERT_PAD))
    window_surface.blit(PH_INTERVALL, (FIR_COL_WID + MID_PAD,
                        TOP_PAD + GRAPH_HEIGHT + TEXT_SPACING + VERT_PAD))
    window_surface.blit(PH_MENGE, (FIR_COL_WID + MID_PAD,
                        TOP_PAD + GRAPH_HEIGHT + 2*TEXT_SPACING + VERT_PAD))

    window_surface.blit(PH_GRAFIK, (FIR_COL_WID + MID_PAD, TOP_PAD+35))
    window_surface.blit(PH_LIVE, (FIR_COL_WID + MID_PAD + 150, TOP_PAD))
    

    manager.update(time_delta)
    manager.draw_ui(window_surface)
    pygame.display.update()

    if becken_running:
        verticalfarming.loop()
    
    if dt.now() - letzt_stream > ph_stream_intervall:
        ph_wert_live = becken_angezeigt.ph_wert_jetzt()
        if ph_wert_live < becken_angezeigt.PH_ZIELWERT + becken_angezeigt.PH_BEREICH:
            if ph_wert_live > becken_angezeigt.PH_ZIELWERT - becken_angezeigt.PH_BEREICH:
                LIVE_COLOR = '#00FF00'
            else:
                LIVE_COLOR = '#FF0000'
        else:
            LIVE_COLOR = '#FF0000'

        PH_LIVE = TITEL_FONT.render(str(becken_angezeigt.ph_wert_jetzt()), True, pygame.Color(LIVE_COLOR))

    tag_des_jahres = dt.now().timetuple().tm_yday

    arr_auf = timetable.timetable[tag_des_jahres]["sunrise"]
    arr_unter = timetable.timetable[tag_des_jahres]["sunset"]

    zeit_sonnenaufgang = dt(
        1, 1, 1, arr_auf[0], arr_auf[1], arr_auf[2]).time()
    zeit_sonnenuntergang = dt(
        1, 1, 1, arr_unter[0], arr_unter[1], arr_unter[2]).time()

    jetzt = dt.now().time()

    if (jetzt > zeit_sonnenaufgang and jetzt < zeit_sonnenuntergang):
        if is_day:
            LICHT_ZUSTAND_ANSW_1 = TEXT_FONT.render(
                'OFF', True, pygame.Color(DYNAMIC_COLOR))
            LICHT_ZUSTAND_ANSW_2 = TEXT_FONT.render(
                str(zeit_sonnenaufgang), True, pygame.Color(DYNAMIC_COLOR))
            LICHT_SCHALT_ANSW = TEXT_FONT.render(
                str(zeit_sonnenuntergang), True, pygame.Color(DYNAMIC_COLOR))
            is_day = False
    else:
        if not is_day:
            LICHT_ZUSTAND_ANSW_1 = TEXT_FONT.render(
                'ON', True, pygame.Color(DYNAMIC_COLOR))
            LICHT_ZUSTAND_ANSW_2 = TEXT_FONT.render(
                str(zeit_sonnenuntergang), True, pygame.Color(DYNAMIC_COLOR))
            LICHT_SCHALT_ANSW = TEXT_FONT.render(
                str(zeit_sonnenaufgang), True, pygame.Color(DYNAMIC_COLOR))
            is_day = True


verticalfarming.safe_exit()
