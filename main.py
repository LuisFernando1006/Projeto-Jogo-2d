import pygame
import random
import json
import os
import math
import sys

# SPEED RACER - Projeto acadêmico em Pygame
# Execute: python main.py

pygame.init()
pygame.display.set_caption("SPEED RACER")
WIDTH, HEIGHT = 960, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 22, bold=True)
SMALL = pygame.font.SysFont("consolas", 16, bold=True)
BIG = pygame.font.SysFont("consolas", 48, bold=True)
TITLE = pygame.font.SysFont("consolas", 68, bold=True)

SAVE_FILE = "speed_racer_save.json"
WHITE = (245, 245, 245)
BLACK = (12, 14, 20)
YELLOW = (255, 215, 55)
RED = (235, 55, 65)
CYAN = (60, 220, 230)
GREEN = (75, 220, 130)
GRAY = (100, 108, 120)

PHASES = [
    {"name":"Cidade Inicial", "sky":(65,145,205), "ground":(45,125,65), "road":(65,68,76), "difficulty":1.00, "traffic":2, "boss":"Rex"},
    {"name":"Estrada Costeira", "sky":(80,180,220), "ground":(30,145,105), "road":(67,70,78), "difficulty":1.18, "traffic":3, "boss":"Marina"},
    {"name":"Distrito Industrial", "sky":(105,115,125), "ground":(75,85,78), "road":(55,58,65), "difficulty":1.38, "traffic":4, "boss":"Torque"},
    {"name":"Circuito Noturno", "sky":(18,25,58), "ground":(22,45,55), "road":(39,42,55), "difficulty":1.62, "traffic":4, "boss":"Vortex"},
    {"name":"Deserto Turbo", "sky":(225,145,75), "ground":(190,135,65), "road":(78,69,62), "difficulty":1.92, "traffic":5, "boss":"Scorpion"},
    {"name":"Serra Extrema", "sky":(105,165,190), "ground":(65,105,85), "road":(57,62,69), "difficulty":2.25, "traffic":5, "boss":"Falcão"},
    {"name":"Metrópole Neon", "sky":(30,20,65), "ground":(35,25,65), "road":(42,42,62), "difficulty":2.65, "traffic":6, "boss":"Cyber"},
    {"name":"Campeonato Final", "sky":(35,35,48), "ground":(65,65,72), "road":(42,44,50), "difficulty":3.15, "traffic":7, "boss":"LENDÁRIO"},
]

CAR_CATALOG = {
    "starter": {"name":"Street Compact", "color":(220,48,58), "price":0, "speed":1.00, "handling":1.00, "style":0},
    "sport": {"name":"Falcon GT", "color":(35,145,235), "price":650, "speed":1.12, "handling":1.05, "style":1},
    "muscle": {"name":"Thunder V8", "color":(238,145,35), "price":1100, "speed":1.22, "handling":0.94, "style":2},
    "super": {"name":"Neon X", "color":(155,75,220), "price":1900, "speed":1.34, "handling":1.12, "style":3},
    "hyper": {"name":"Apex Hyper", "color":(45,205,150), "price":3000, "speed":1.48, "handling":1.18, "style":4},
    "retro": {"name":"Retro Sprint", "color":(248,205,70), "price":900, "speed":1.16, "handling":1.14, "style":1},
    "drift": {"name":"Drift Phantom", "color":(230,235,245), "price":1500, "speed":1.27, "handling":1.30, "style":2},
    "rally": {"name":"Rally Storm", "color":(70,175,85), "price":1850, "speed":1.25, "handling":1.24, "style":3},
    "crimson": {"name":"Crimson R", "color":(245,55,80), "price":2500, "speed":1.38, "handling":1.16, "style":4},
    "night": {"name":"Night Shadow", "color":(80,95,125), "price":3400, "speed":1.51, "handling":1.21, "style":4},
    "solar": {"name":"Solar V12", "color":(255,165,45), "price":4200, "speed":1.56, "handling":1.19, "style":3},
    "glacier": {"name":"Glacier RS", "color":(95,215,245), "price":4800, "speed":1.53, "handling":1.35, "style":4},
    "legend": {"name":"Legend X", "color":(245,220,115), "price":6500, "speed":1.68, "handling":1.31, "style":4},
}
ROUTE_CURVE = [0.0, 0.0, 0.0, 0.0]
ROUTE_SEED = 0

INFINITE_MONEY = 999_999_999_999  # Saldo restaurado automaticamente, inclusive em saves antigos.

DEFAULT_SAVE = {
    "unlocked": 0, "completed": [], "money": INFINITE_MONEY,
    "upgrades": {"engine":0, "tires":0, "accel":0, "armor":0},
    "items": {"turbo":2, "shield":1, "repair":1},
    "best_times": {},
    "owned_cars": ["starter"],
    "selected_car": "starter"
}

def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = DEFAULT_SAVE.copy()
            merged.update(data)
            merged["unlocked"] = max(0, min(7, int(merged.get("unlocked", 0))))
            merged["upgrades"] = {**DEFAULT_SAVE["upgrades"], **data.get("upgrades", {})}
            merged["items"] = {**DEFAULT_SAVE["items"], **data.get("items", {})}
            merged["owned_cars"] = data.get("owned_cars", ["starter"])
            if "starter" not in merged["owned_cars"]:
                merged["owned_cars"].insert(0, "starter")
            merged["selected_car"] = data.get("selected_car", "starter")
            if merged["selected_car"] not in merged["owned_cars"]:
                merged["selected_car"] = "starter"
            merged["money"] = INFINITE_MONEY
            return merged
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_SAVE))

save = load_save()

def save_game():
    save["money"] = INFINITE_MONEY
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(save, f, indent=4, ensure_ascii=False)

def draw_text(surface, text, x, y, color=WHITE, font=FONT, center=False):
    img = font.render(str(text), True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)

def panel(surface, rect, color=(12,16,25,225), border=CYAN):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    s.fill(color)
    surface.blit(s, rect[:2])
    pygame.draw.rect(surface, border, rect, 2, border_radius=8)

def draw_car(surface, x, y, color, scale=1.0, player=False):
    w, h = int(42*scale), int(72*scale)
    x, y = int(x), int(y)
    # sombra e carro em blocos para lembrar pixel art
    pygame.draw.rect(surface, (15,15,18), (x-w//2+4, y-h//2+5, w, h), border_radius=7)
    pygame.draw.rect(surface, (20,20,24), (x-w//2-4, y-h//2+12, 8, 17))
    pygame.draw.rect(surface, (20,20,24), (x+w//2-4, y-h//2+12, 8, 17))
    pygame.draw.rect(surface, (20,20,24), (x-w//2-4, y+h//2-28, 8, 17))
    pygame.draw.rect(surface, (20,20,24), (x+w//2-4, y+h//2-28, 8, 17))
    pygame.draw.rect(surface, color, (x-w//2, y-h//2, w, h), border_radius=8)
    pygame.draw.rect(surface, tuple(max(0,c-35) for c in color), (x-w//2+5, y-h//2+5, w-10, 18), border_radius=4)
    pygame.draw.rect(surface, (90,190,220), (x-w//2+7, y-h//2+24, w-14, 17), border_radius=3)
    pygame.draw.rect(surface, (25,30,38), (x-w//2+6, y+h//2-15, w-12, 7))
    pygame.draw.rect(surface, YELLOW if player else (230,230,230), (x-w//2+5, y+h//2-8, 8, 4))
    pygame.draw.rect(surface, YELLOW if player else (230,230,230), (x+w//2-13, y+h//2-8, 8, 4))
    if player:
        pygame.draw.rect(surface, WHITE, (x-3, y-5, 6, 18))



def route_bend(y):
    """Deslocamento lateral suave do percurso gerado para esta corrida."""
    if not ROUTE_CURVE:
        return 0.0
    t = max(0.0, min(1.0, (y-170)/(HEIGHT-170)))
    look = (1.0-t) * 2.8
    idx = int(look)
    frac = look-idx
    left = ROUTE_CURVE[min(idx, len(ROUTE_CURVE)-1)]
    right = ROUTE_CURVE[min(idx+1, len(ROUTE_CURVE)-1)]
    return (left*(1-frac)+right*frac) * (0.35 + 0.65*t)

def road_edges(y):
    """Limites da pista em perspectiva, com curvas geradas por corrida."""
    horizon=170
    t=max(0.0,min(1.0,(y-horizon)/(HEIGHT-horizon)))
    center=480 + route_bend(y)
    half=55 + 270*t
    return center-half, center+half

def lane_center(lane,y):
    left,right=road_edges(y)
    return left+(right-left)*((lane+0.5)/4)

def draw_background(surface, phase, scroll):
    """Oito cenários próprios: litoral, indústria, noite, deserto, serra, neon e final."""
    horizon=170
    skies=[((42,55,105),(246,174,112)),((54,151,212),(179,227,245)),
           ((73,83,91),(166,146,119)),((9,13,40),(53,35,96)),
           ((144,85,63),(255,190,104)),((64,136,191),(203,226,235)),
           ((15,8,53),(100,27,116)),((15,17,28),(99,62,91))]
    top,bottom=skies[phase]
    for y in range(0,horizon+2,3):
        t=y/horizon
        col=tuple(int(top[i]*(1-t)+bottom[i]*t) for i in range(3))
        pygame.draw.rect(surface,col,(0,y,WIDTH,3))
    night=phase in (3,6,7)
    if night:
        for i in range(36):
            x=(i*137+53)%WIDTH; y=(i*61+19)%125
            pygame.draw.circle(surface,(198,209,237),(x,y),1+(i%9==0))
        pygame.draw.circle(surface,(221,224,243),(750,52),24)
    else:
        pygame.draw.circle(surface,(255,229,171),(750,84),32)
    ground=[(77,91,79),(48,139,142),(83,82,77),(26,37,65),
            (193,141,81),(77,119,83),(32,25,68),(69,72,84)][phase]
    pygame.draw.rect(surface,ground,(0,horizon,WIDTH,HEIGHT-horizon))
    if phase==1:
        # Mar, ilhas, barcos e falésias ao longo da estrada costeira.
        pygame.draw.rect(surface,(43,153,191),(0,138,WIDTH,55))
        for i in range(4):
            x=i*310-50
            pygame.draw.polygon(surface,(45,105,91),[(x,165),(x+110,116),(x+205,167)])
        for i in range(9):
            x=(i*139+30)%WIDTH
            pygame.draw.line(surface,(217,242,239),(x,187),(x+36,187),2)
    elif phase in (4,5):
        colors=(177,103,61) if phase==4 else (76,101,104)
        for i in range(7):
            x=i*172-50; height=40+(i*37)%65
            pygame.draw.polygon(surface,colors,[(x,170),(x+76,170-height),(x+160,170)])
    else:
        palettes={0:[(70,68,90),(85,75,95)],2:[(68,68,72),(94,91,83)],
                  3:[(30,33,64),(41,39,76)],6:[(31,26,75),(49,33,87)],
                  7:[(45,47,62),(69,65,81)]}
        pal=palettes.get(phase,[(55,65,75),(75,80,90)])
        for i in range(19):
            x=i*56-12; w=38+(i*11)%24; h=36+(i*43)%104
            pygame.draw.rect(surface,pal[i%2],(x,horizon-h,w,h+16))
            if phase==2 and i%4==0:
                pygame.draw.rect(surface,(96,100,102),(x+10,horizon-h-38,12,39))
                pygame.draw.ellipse(surface,(150,150,148),(x-2,horizon-h-65,37,23))
            for wy in range(horizon-h+12,horizon,18):
                for wx in range(x+8,x+w-4,14):
                    c=(251,69,221) if phase==6 and i%2 else ((76,237,245) if phase==6 else ((247,218,125) if night else (193,168,126)))
                    pygame.draw.rect(surface,c,(wx,wy,5,6))
    lt,rt=road_edges(horizon); lb,rb=road_edges(HEIGHT)
    shoulder=(206,182,128) if phase==4 else ((61,87,113) if night else (205,190,165))
    road=(70,62,58) if phase==4 else ((38,39,58) if night else (48,51,59))
    pygame.draw.polygon(surface,shoulder,[(lt-10,horizon),(rt+10,horizon),(rb+22,HEIGHT),(lb-22,HEIGHT)])
    pygame.draw.polygon(surface,road,[(lt,horizon),(rt,horizon),(rb,HEIGHT),(lb,HEIGHT)])
    edge=(255,96,185) if phase==6 else ((240,226,170) if not night else (131,173,223))
    pygame.draw.line(surface,edge,(lt,horizon),(lb,HEIGHT),5)
    pygame.draw.line(surface,edge,(rt,horizon),(rb,HEIGHT),5)
    for boundary in (1,2,3):
        for j in range(13):
            depth=((j/13)+(scroll*0.0010))%1.0
            y=horizon+int((depth**1.5)*(HEIGHT-horizon))
            l,r=road_edges(y); x=l+(r-l)*boundary/4
            pygame.draw.rect(surface,(228,220,195),(int(x-2),y,max(2,int(2+depth*4)),max(3,int(3+depth*29))))
    for i in range(12):
        depth=((i/12)+(scroll*0.0007))%1.0
        y=horizon+int((depth**1.5)*(HEIGHT-horizon))
        size=max(4,int(5+depth*27)); l,r=road_edges(y)
        for side in (-1,1):
            x=int(l-30-depth*100-size if side<0 else r+30+depth*100+size)
            if phase==4:
                # Cactos e rochas do deserto.
                pygame.draw.line(surface,(42,112,65),(x,y),(x,y-size*3),max(2,size//5))
                pygame.draw.line(surface,(42,112,65),(x,y-size*2),(x+side*size,y-size*2),max(2,size//6))
            elif phase==2:
                pygame.draw.rect(surface,(102,109,111),(x-size//2,y-size*3,size,size*3))
                pygame.draw.rect(surface,(215,160,76),(x-size,y-size*3,size*2,5))
            elif phase in (3,6,7):
                pygame.draw.line(surface,(62,63,85),(x,y),(x,y-size*3),max(2,size//6))
                pygame.draw.circle(surface,(245,74,221) if phase==6 else (255,237,155),(x,y-size*3),max(2,size//3))
            else:
                pygame.draw.rect(surface,(73,62,53),(x-3,y-size*2,6,size*2))
                pygame.draw.circle(surface,(38,108,75) if phase!=5 else (41,90,67),(x,y-size*2),size)
    return int(lb),int(rb)

def draw_rear_car(surface, x, y, color, scale=1.0, player=False, style=0, opacity=255):
    """Esportivo 2.5D visto de trás: carroceria larga, teto baixo e traseira volumosa.

    Desenho vetorial em resolução fixa para manter proporções em todas as distâncias.
    """
    scale = max(0.012, float(scale))
    W, H = 240, 160
    spr = pygame.Surface((W, H), pygame.SRCALPHA)
    def polygon(c, pts): pygame.draw.polygon(spr, c, pts)
    def line(c, a, b, width=1): pygame.draw.line(spr, c, a, b, width)
    def rect(c, xywh, radius=0): pygame.draw.rect(spr, c, xywh, border_radius=radius)
    def ellipse(c, xywh): pygame.draw.ellipse(spr, c, xywh)
    def tone(delta): return tuple(max(0, min(255, int(v+delta))) for v in color)

    shadow = tone(-90)
    dark = tone(-55)
    medium = tone(-27)
    light = tone(29)
    highlight = tone(60)
    # Sombra na pista, pneus largos parcialmente expostos.
    ellipse((0, 0, 0, 92), (20, 126, 200, 26))
    for tx in (24, 197):
        rect((11, 13, 18), (tx, 101, 19, 46), 4)
        rect((37, 40, 46), (tx+2, 110, 15, 29), 3)
        line((81, 84, 91), (tx+5, 113), (tx+5, 136), 2)

    # Teto e vidro traseiro inclinado, menor que a largura dos ombros.
    polygon(shadow, [(75, 27), (165, 27), (184, 79), (56, 79)])
    polygon(medium, [(77, 22), (163, 22), (185, 78), (55, 78)])
    polygon((22, 33, 45), [(80, 29), (160, 29), (175, 73), (65, 73)])
    polygon((45, 69, 87), [(82, 31), (105, 31), (93, 70), (69, 70)])
    polygon((29, 48, 62), [(114, 31), (156, 31), (171, 70), (103, 70)])
    line((143, 167, 176), (80, 29), (160, 29), 2)
    line((13, 24, 34), (120, 31), (120, 72), 2)

    # Ombros curvos e traseira larga, silhueta de superesportivo anos 90.
    polygon(dark, [(56, 65), (184, 65), (210, 86), (225, 113),
                   (218, 140), (22, 140), (15, 113), (30, 86)])
    polygon(color, [(57, 69), (183, 69), (205, 85), (219, 111),
                    (211, 129), (29, 129), (21, 111), (35, 85)])
    polygon(light, [(35, 85), (56, 69), (68, 72), (48, 92), (26, 113), (24, 106)])
    polygon(medium, [(183, 69), (205, 85), (219, 111), (211, 129),
                     (203, 112), (191, 91), (174, 73)])
    # Tampa do motor plana com nervuras discretas.
    polygon(medium, [(55, 77), (185, 77), (202, 100), (38, 100)])
    line(highlight, (53, 78), (186, 78), 2)
    for yy in (84, 88, 92):
        line(dark, (92, yy), (148, yy), 2)
    line(tone(-15), (40, 101), (200, 101), 2)

    # Painel preto horizontal e lanternas traseiras duplas, como na referência.
    polygon((21, 23, 29), [(24, 105), (216, 105), (212, 125), (28, 125)])
    for lx in (31, 163):
        rect((95, 13, 22), (lx, 107, 46, 15), 2)
        rect((236, 33, 43), (lx+2, 108, 42, 7), 2)
        line((255, 134, 117), (lx+4, 110), (lx+42, 110), 2)
        rect((136, 15, 26), (lx+2, 117, 42, 3), 1)
    # Pequeno emblema central e placa escura.
    ellipse((218, 223, 220), (116, 108, 8, 7))
    rect((7, 12, 26), (100, 126, 40, 13), 2)
    line((77, 82, 94), (104, 127), (136, 127), 1)

    # Para-choque, difusor, escapamentos e reflexos na pintura.
    polygon(dark, [(29, 129), (211, 129), (203, 145), (37, 145)])
    polygon((26, 29, 35), [(46, 137), (194, 137), (187, 148), (53, 148)])
    for ex in (73, 167):
        ellipse((129, 136, 144), (ex-13, 138, 26, 9))
        ellipse((13, 16, 21), (ex-9, 140, 18, 5))
    line(highlight, (42, 99), (64, 81), 2)
    line(tone(-9), (180, 83), (201, 100), 2)
    if style >= 1:
        # Aerofólio de perfil baixo com suportes.
        rect((28, 30, 35), (51, 62, 7, 17), 2)
        rect((28, 30, 35), (182, 62, 7, 17), 2)
        polygon((25, 27, 32), [(37, 56), (203, 56), (197, 67), (43, 67)])
        line(light, (48, 57), (191, 57), 2)
    if style >= 2:
        for xx in (45, 195):
            line(highlight, (xx, 87), (xx+(-6 if xx<120 else 6), 98), 2)
    if player:
        line((185, 193, 196), (118, 112), (122, 112), 2)

    # Redução contínua para o horizonte, sem saltos de detalhe por faixa.
    size = (max(2, round(W*scale)), max(2, round(H*scale)))
    spr = pygame.transform.smoothscale(spr, size)
    if opacity < 255:
        spr.set_alpha(max(0, min(255, int(opacity))))
    surface.blit(spr, (round(x-size[0]/2), round(y-size[1]/2)))

def opponent_render_params(y, boss=False):
    """Projeção contínua: carro minúsculo no horizonte, crescendo sem saltos."""
    horizon=170.0
    depth=max(0.0,min(1.0,(y-horizon)/(HEIGHT-horizon)))
    # Curva quadrática aproxima a mudança de tamanho da perspectiva.
    scale=0.035 + (depth**1.28)*(0.84 if boss else 0.73)
    # Névoa de distância: desaparece gradualmente ao se afastar do horizonte.
    opacity=round(255*min(1.0,max(0.0,(depth-0.008)/0.115)))
    return scale,opacity

def button(surface, text, rect, selected=False):
    color = (35,75,95) if selected else (24,32,45)
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, YELLOW if selected else (80,115,135), rect, 2, border_radius=8)
    draw_text(surface, text, rect[0]+rect[2]//2, rect[1]+rect[3]//2, WHITE, FONT, True)

# Arte oficial da tela inicial, carregada uma unica vez.
COVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "capa_speed_racer.png")
try:
    COVER_IMAGE = pygame.image.load(COVER_PATH).convert()
    COVER_IMAGE = pygame.transform.smoothscale(COVER_IMAGE, (WIDTH, HEIGHT))
except (pygame.error, FileNotFoundError):
    COVER_IMAGE = None

def menu_background():
    if COVER_IMAGE is not None:
        screen.blit(COVER_IMAGE, (0, 0))
    else:
        screen.fill((20, 25, 42))
    # Escurece discretamente a area dos botoes para garantir legibilidade.
    veil = pygame.Surface((330, 338), pygame.SRCALPHA)
    pygame.draw.rect(veil, (8, 12, 24, 135), veil.get_rect(), border_radius=18)
    screen.blit(veil, (315, 256))

def main_menu():
    options = ["JOGAR CAMPANHA", "GARAGEM", "LOJA", "COMO JOGAR", "SAIR"]
    selected = 0
    while True:
        menu_background()
        for i, opt in enumerate(options):
            button(screen, opt, (335, 270+i*59, 290, 46), i == selected)
        draw_text(screen, "Dinheiro: ∞", 20, 600, GREEN, SMALL)
        draw_text(screen, f"Fase liberada: {save['unlocked']+1}/8", 760, 600, WHITE, SMALL)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEMOTION:
                for i in range(len(options)):
                    if pygame.Rect(335, 270+i*59, 290, 46).collidepoint(event.pos):
                        selected = i
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(len(options)):
                    if pygame.Rect(335, 270+i*59, 290, 46).collidepoint(event.pos):
                        selected = i
                        if selected == 0: phase_select()
                        elif selected == 1: garage()
                        elif selected == 2: shop()
                        elif selected == 3: instructions()
                        else: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w): selected = (selected-1) % len(options)
                if event.key in (pygame.K_DOWN, pygame.K_s): selected = (selected+1) % len(options)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if selected == 0: phase_select()
                    elif selected == 1: garage()
                    elif selected == 2: shop()
                    elif selected == 3: instructions()
                    else: pygame.quit(); sys.exit()
        clock.tick(60)

def instructions():
    while True:
        screen.fill((12,18,30))
        draw_text(screen, "COMO JOGAR", 480, 70, YELLOW, BIG, True)
        lines = [
            "A / D ou SETAS: mover o carro",
            "W ou SETA PARA CIMA: acelerar",
            "S ou SETA PARA BAIXO: frear",
            "ESPAÇO: usar TURBO (se possuir)",
            "E: ativar ESCUDO (se possuir)",
            "Colete moedas e desvie dos obstáculos.",
            "Complete a prova e vença o chefe para liberar",
            "a próxima fase. Cada fase é mais difícil!",
            "ESC: voltar"
        ]
        for i, line in enumerate(lines): draw_text(screen, line, 170, 165+i*39, WHITE, FONT)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN): return
        clock.tick(60)

def phase_select():
    while True:
        screen.fill((10,16,27))
        draw_text(screen, "SELECIONE A REGIÃO", 480, 55, YELLOW, BIG, True)
        for i,p in enumerate(PHASES):
            col = i % 2
            row = i // 2
            x, y = 125+col*370, 125+row*105
            unlocked = i <= save["unlocked"]
            label = f"{i+1}. {p['name']}" if unlocked else f"{i+1}. ??? BLOQUEADA"
            button(screen, label, (x,y,330,68), False)
            draw_text(screen, "LIBERADA" if unlocked else "VENÇA O CHEFE ANTERIOR", x+165, y+48,
                      GREEN if unlocked else GRAY, SMALL, True)
        draw_text(screen, "ESC: voltar", 20, 600, WHITE, SMALL)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx in range(8):
                    col, row = idx % 2, idx // 2
                    rect = pygame.Rect(125+col*370, 125+row*105, 330, 68)
                    if rect.collidepoint(event.pos) and idx <= save["unlocked"]:
                        event_select(idx)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return
                if pygame.K_1 <= event.key <= pygame.K_8:
                    idx = event.key - pygame.K_1
                    if idx <= save["unlocked"]:
                        event_select(idx)
        clock.tick(60)

def unlocked_screen(next_idx):
    """Tela especial exibida somente quando uma região inédita é liberada."""
    phase=PHASES[next_idx]
    while True:
        screen.fill((9,15,29))
        pygame.draw.rect(screen,(20,34,55),(95,85,770,470),border_radius=25)
        pygame.draw.rect(screen,YELLOW,(95,85,770,470),4,border_radius=25)
        draw_text(screen,"NOVA FASE LIBERADA!",480,150,YELLOW,BIG,True)
        draw_text(screen,f"FASE {next_idx+1}",480,232,CYAN,FONT,True)
        draw_text(screen,phase['name'].upper(),480,290,WHITE,BIG,True)
        draw_text(screen,f"Novo chefe: {phase['boss']}",480,363,GREEN,FONT,True)
        draw_text(screen,"ENTER: escolher nova fase   |   ESC: voltar",480,474,WHITE,SMALL,True)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_RETURN: return True
                if event.key==pygame.K_ESCAPE: return False
        clock.tick(60)

def event_select(idx):
    # A classificatória libera o chefe; somente vencê-lo em 1º libera a próxima região.
    while True:
        screen.fill((12,18,30))
        p=PHASES[idx]
        draw_text(screen,f"FASE {idx+1}: {p['name']}",480,90,YELLOW,BIG,True)
        draw_text(screen,f"Dificuldade: {p['difficulty']:.2f}x",480,155,CYAN,FONT,True)
        button(screen,"1 - CORRIDA CLASSIFICATÓRIA",(265,235,430,58),False)
        button(screen,f"2 - DESAFIAR CHEFE: {p['boss']}",(265,310,430,58),False)
        draw_text(screen,"Chefe: duelo 1x1. Vença em 1º para liberar a próxima fase.",480,390,GRAY,SMALL,True)
        draw_text(screen,"ESC: voltar",20,600,WHITE,SMALL)
        pygame.display.flip()
        action=None
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: return
                if event.key==pygame.K_1: action='normal'
                if event.key==pygame.K_2: action='boss'
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if pygame.Rect(265,235,430,58).collidepoint(event.pos): action='normal'
                if pygame.Rect(265,310,430,58).collidepoint(event.pos): action='boss'
        if action=='normal':
            if race(idx,False):
                if f"{idx}-normal" not in save['completed']:
                    save['completed'].append(f"{idx}-normal")
                save_game()
        elif action=='boss':
            if f"{idx}-normal" not in save['completed']:
                result_screen("PROVA BLOQUEADA","Complete a classificatória primeiro.",False)
            elif race(idx,True):
                first_win=f"{idx}-boss" not in save['completed']
                if first_win:
                    save['completed'].append(f"{idx}-boss")
                    bonus=250+idx*100
                    save['money']+=bonus
                    previous=save['unlocked']
                    save['unlocked']=max(previous,min(7,idx+1))
                    save_game()
                    result_screen("CHEFE DERROTADO!",f"Região conquistada! Bônus: $ {bonus}",True)
                    if idx==7:
                        result_screen("CAMPEÃO!","Você venceu o Campeonato Speed Racer!",True)
                    elif save['unlocked']>previous:
                        if unlocked_screen(idx+1): return
                else:
                    result_screen("CHEFE DERROTADO!","Você já conquistou esta região.",True)
        clock.tick(60)

def garage():
    names = [("engine","Motor"),("tires","Pneus"),("accel","Aceleração"),("armor","Resistência")]
    selected = 0
    while True:
        screen.fill((12,18,30))
        draw_text(screen, "GARAGEM", 480, 65, YELLOW, BIG, True)
        current=CAR_CATALOG.get(save.get("selected_car","starter"),CAR_CATALOG["starter"])
        draw_rear_car(screen,480,205,current["color"],1.05,True,current["style"])
        draw_text(screen, f"{current['name']}  |  Saldo: ∞", 480, 285, GREEN, FONT, True)
        for i,(key,label) in enumerate(names):
            lvl = save["upgrades"][key]
            price = 180 + lvl*170
            button(screen, f"{label}: nível {lvl}/5  |  $ {price}", (245,330+i*52,470,42), i == selected)
        draw_text(screen, "ENTER: comprar melhoria   ESC: voltar", 480, 590, WHITE, SMALL, True)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEMOTION:
                for i in range(4):
                    if pygame.Rect(245,330+i*52,470,42).collidepoint(event.pos): selected=i
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i,(key,label) in enumerate(names):
                    if pygame.Rect(245,330+i*52,470,42).collidepoint(event.pos):
                        selected=i; lvl=save["upgrades"][key]; price=180+lvl*170
                        if lvl < 5 and save["money"] >= price:
                            save["money"] -= price; save["upgrades"][key] += 1; save_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: save_game(); return
                if event.key in (pygame.K_UP,pygame.K_w): selected=(selected-1)%4
                if event.key in (pygame.K_DOWN,pygame.K_s): selected=(selected+1)%4
                if event.key == pygame.K_RETURN:
                    key,_=names[selected]; lvl=save["upgrades"][key]; price=180+lvl*170
                    if lvl < 5 and save["money"] >= price:
                        save["money"] -= price; save["upgrades"][key] += 1; save_game()
        clock.tick(60)

def shop():
    """Loja com abas independentes, navegação por páginas e compra persistente."""
    tabs = ["CARROS", "HABILIDADES"]
    skills = [("turbo", "TURBO", 100, "Aceleração extra por alguns segundos"),
              ("shield", "ESCUDO", 130, "Proteção temporária contra colisões"),
              ("repair", "REPARO", 90, "Recupera a resistência do carro")]
    cars = list(CAR_CATALOG.items())
    tab = 0
    selection = [0, 0]
    page_size = 4
    message = "Clique para comprar/equipar. TAB alterna as abas."

    def activate():
        nonlocal message
        if tab == 0:
            key, car = cars[selection[0]]
            if key in save["owned_cars"]:
                save["selected_car"] = key
                message = car["name"] + " equipado!"
            else:
                save["owned_cars"].append(key)
                save["selected_car"] = key
                message = car["name"] + " comprado e equipado!"
        else:
            key, name, price, desc = skills[selection[1]]
            save["items"][key] += 1
            message = name + " comprado! Total: " + str(save["items"][key])
        save_game()

    while True:
        screen.fill((13, 18, 30))
        button(screen, "< VOLTAR", (18, 18, 156, 47), False)
        draw_text(screen, "LOJA SPEED RACER", WIDTH//2, 36, YELLOW, BIG, True)
        draw_text(screen, "SALDO: INFINITO", WIDTH//2, 85, GREEN, SMALL, True)
        for i, label in enumerate(tabs):
            button(screen, label, (205+i*280, 111, 270, 47), tab == i)
        if tab == 0:
            page = selection[0] // page_size
            start = page * page_size
            for row, (key, car) in enumerate(cars[start:start+page_size]):
                y = 176 + row*96
                active = (selection[0] == start+row)
                panel(screen, (100,y,760,84), (21,31,45,240), YELLOW if active else (70,95,115))
                draw_rear_car(screen, 176, y+48, car["color"], 0.40, False, car["style"])
                draw_text(screen, car["name"], 254, y+10, WHITE, FONT)
                draw_text(screen, "Velocidade: %.2fx   Controle: %.2fx" % (car["speed"],car["handling"]), 254, y+42, CYAN, SMALL)
                if key == save["selected_car"]:
                    status = "EQUIPADO"
                elif key in save["owned_cars"]:
                    status = "EQUIPAR"
                else:
                    status = "COMPRAR $ %s" % car["price"]
                draw_text(screen, status, 835, y+31, GREEN if key in save["owned_cars"] else YELLOW, SMALL, True)
            draw_text(screen, "Página %d/%d  |  A/D ou ←/→: trocar página" % (page+1,(len(cars)+page_size-1)//page_size), 480, 578, WHITE, SMALL, True)
        else:
            for row, (key, name, price, desc) in enumerate(skills):
                y = 188 + row*122
                panel(screen, (120,y,720,104), (21,31,45,240), YELLOW if selection[1]==row else (70,95,115))
                draw_text(screen, name, 150, y+13, YELLOW, FONT)
                draw_text(screen, desc, 150, y+44, WHITE, SMALL)
                draw_text(screen, "Possui: %d   |   Comprar: $ %d" % (save["items"][key], price), 150, y+74, GREEN, SMALL)
        draw_text(screen, message, 480, 613, CYAN, SMALL, True)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: save_game(); return
                if event.key == pygame.K_TAB:
                    tab = 1-tab
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selection[tab] = (selection[tab]-1) % (len(cars) if tab==0 else len(skills))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selection[tab] = (selection[tab]+1) % (len(cars) if tab==0 else len(skills))
                elif tab==0 and event.key in (pygame.K_RIGHT, pygame.K_d):
                    selection[0] = min(len(cars)-1, (selection[0]//page_size+1)*page_size)
                elif tab==0 and event.key in (pygame.K_LEFT, pygame.K_a):
                    selection[0] = max(0, (selection[0]//page_size-1)*page_size)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE): activate()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(18,18,156,47).collidepoint(event.pos):
                    save_game()
                    return
                if pygame.Rect(205,111,270,47).collidepoint(event.pos): tab=0
                elif pygame.Rect(485,111,270,47).collidepoint(event.pos): tab=1
                elif tab==0:
                    start=(selection[0]//page_size)*page_size
                    for row in range(min(page_size,len(cars)-start)):
                        if pygame.Rect(100,176+row*96,760,84).collidepoint(event.pos):
                            index=start+row
                            if selection[0]==index: activate()
                            else: selection[0]=index
                else:
                    for row in range(len(skills)):
                        if pygame.Rect(120,188+row*122,720,104).collidepoint(event.pos):
                            selection[1]=row; activate()
        clock.tick(60)

def draw_minimap(surface,traffic,player_x,player_y,player_lane):
    """Mini mapa acompanha o traçado gerado; vermelho = jogador, azul = rivais."""
    rect=pygame.Rect(WIDTH-178,142,158,150)
    panel(surface,rect,(10,14,24,225),(235,185,115))
    draw_text(surface,"MAPA DA PISTA",rect.centerx,rect.y+13,YELLOW,SMALL,True)
    top=rect.y+31; bottom=rect.bottom-10
    # Desenha o traçado sinuoso em miniatura usando a mesma curva da corrida.
    path=[]
    for i in range(18):
        yy=top+i*(bottom-top)/17
        world_y=190+(i/17)*(HEIGHT-190)
        bend=route_bend(world_y)*0.22
        path.append((int(rect.centerx+bend),int(yy)))
    pygame.draw.lines(surface,(205,205,195),False,path,19)
    pygame.draw.lines(surface,(72,76,84),False,path,15)
    pygame.draw.lines(surface,(225,218,195),False,path,1)
    # Linha central tracejada do mapa.
    for i in range(0,len(path)-1,2):
        pygame.draw.line(surface,(190,185,170),path[i],path[min(i+1,len(path)-1)],1)
    def map_point(world_y,lane):
        rel=max(0.0,min(1.0,(world_y-190)/(HEIGHT-190)))
        yy=int(top+rel*(bottom-top))
        center=rect.centerx+route_bend(world_y)*0.22
        xx=int(center+(lane-1.5)*7)
        return xx,yy
    # Rivais: azul; chefe: roxo; jogador: vermelho.
    for rival in traffic:
        xx,yy=map_point(rival["y"],rival["lane"])
        col=(190,90,235) if rival.get("boss") else (70,185,255)
        pygame.draw.circle(surface,col,(xx,yy),4)
    player_rel=max(0.0,min(1.0,(player_y-190)/(HEIGHT-190)))
    player_center=rect.centerx+route_bend(player_y)*0.22
    player_offset=(player_x-(480+route_bend(player_y)))*0.055
    pygame.draw.circle(surface,(255,65,70),(int(player_center+player_offset),int(top+player_rel*(bottom-top))),5)
    draw_text(surface,"VOCÊ",rect.x+8,rect.bottom-23,(255,105,105),SMALL)




def draw_speedometer(surface, speed_kmh, max_kmh, turbo_active=False):
    """Mostrador semicircular com ponteiro animado no canto inferior direito."""
    cx, cy = WIDTH-119, HEIGHT-105
    radius = 77
    plate = pygame.Surface((222,203),pygame.SRCALPHA)
    pygame.draw.rect(plate,(9,14,25,215),(0,0,222,203),border_radius=24)
    pygame.draw.rect(plate,(80,110,135,210),(1,1,220,201),2,border_radius=24)
    surface.blit(plate,(WIDTH-230,HEIGHT-207))
    pygame.draw.circle(surface,(14,20,33),(cx,cy),radius+6)
    pygame.draw.circle(surface,(46,64,82),(cx,cy),radius+6,3)
    pygame.draw.circle(surface,(26,35,48),(cx,cy),radius-4)
    start=math.radians(145)
    sweep=math.radians(250)
    fraction=max(0.0,min(1.0,speed_kmh/max(1.0,max_kmh)))
    for i in range(51):
        a=start+sweep*i/50
        p1=(int(cx+math.cos(a)*(radius-9)),int(cy+math.sin(a)*(radius-9)))
        p2=(int(cx+math.cos(a)*(radius-2)),int(cy+math.sin(a)*(radius-2)))
        color=(255,180,65) if turbo_active else (60,215,225)
        pygame.draw.line(surface,color if i/50<=fraction else (63,78,94),p1,p2,4)
    for i in range(6):
        a=start+sweep*i/5
        p1=(int(cx+math.cos(a)*(radius-19)),int(cy+math.sin(a)*(radius-19)))
        p2=(int(cx+math.cos(a)*(radius-27)),int(cy+math.sin(a)*(radius-27)))
        pygame.draw.line(surface,(224,234,240),p1,p2,2)
    angle=start+sweep*fraction
    tip=(int(cx+math.cos(angle)*(radius-32)),int(cy+math.sin(angle)*(radius-32)))
    pygame.draw.line(surface,(255,91,85),(cx,cy),tip,4)
    pygame.draw.circle(surface,(235,239,242),(cx,cy),6)
    draw_text(surface,'VELOCIDADE',cx,HEIGHT-194,(175,205,225),SMALL,True)
    draw_text(surface,str(int(speed_kmh)),cx,cy+26,WHITE,BIG,True)
    draw_text(surface,'KM/H',cx,cy+55,(145,195,210),SMALL,True)
    if turbo_active:
        draw_text(surface,'TURBO',cx,HEIGHT-26,YELLOW,SMALL,True)


def draw_skills(surface,items,turbo_timer,shield_timer,durability,max_durability):
    """Habilidades agrupadas verticalmente à esquerda e no meio da tela."""
    x=12
    y=HEIGHT//2-116
    w=156
    panel(surface,(x,y,w,230),(10,16,28,228),(80,125,155))
    draw_text(surface,'HABILIDADES',x+w//2,y+18,YELLOW,SMALL,True)
    abilities=[
        ('TURBO','ESPAÇO',items.get('turbo',0),turbo_timer>0,(250,182,65)),
        ('ESCUDO','E',items.get('shield',0),shield_timer>0,(65,210,235)),
        ('REPARO','R',items.get('repair',0),False,(105,225,145)),
    ]
    for i,(name,key,count,active,color) in enumerate(abilities):
        yy=y+38+i*62
        available=count>0 and (name!='REPARO' or durability<max_durability)
        bg=(34,68,65) if active else (27,37,52)
        pygame.draw.rect(surface,bg,(x+8,yy,w-16,55),border_radius=9)
        pygame.draw.rect(surface,color if active else (70,85,103),(x+8,yy,w-16,55),2,border_radius=9)
        pygame.draw.rect(surface,(43,55,69),(x+14,yy+12,36,30),border_radius=6)
        draw_text(surface,key if key!='ESPAÇO' else 'SPC',x+32,yy+27,color,pygame.font.SysFont('consolas',12,bold=True),True)
        draw_text(surface,name,x+58,yy+8,WHITE,SMALL)
        status='ATIVO' if active else f'X{count}' if available else 'INDISP.' if count==0 else 'CHEIO'
        draw_text(surface,status,x+58,yy+30,color if active or available else GRAY,SMALL)

def draw_finish_line(surface, remaining, player_y):
    """Desenha um pórtico e faixa quadriculada que se aproximam até a travessia."""
    horizon = 170
    progress = max(0.0,min(1.0,1.0-remaining/820.0))
    y = int(horizon + (player_y-horizon)*(progress**1.65))
    left,right = road_edges(y)
    depth = max(0.08,(y-horizon)/(HEIGHT-horizon))
    thick = max(2,int(7*depth))
    tile_w = (right-left)/12
    # Faixa de chegada em dois níveis, respeitando a perspectiva da pista.
    for row in range(2):
        yy=y+row*thick
        for i in range(12):
            col=(242,241,225) if (i+row)%2==0 else (24,27,33)
            pygame.draw.polygon(surface,col,[
                (int(left+i*tile_w),yy), (int(left+(i+1)*tile_w),yy),
                (int(left+(i+1)*tile_w),yy+thick),(int(left+i*tile_w),yy+thick)])
    post_h=int(35+depth*150)
    post_w=max(3,int(5+depth*9))
    pygame.draw.rect(surface,(230,230,228),(int(left)-post_w,y-post_h,post_w,post_h))
    pygame.draw.rect(surface,(230,230,228),(int(right),y-post_h,post_w,post_h))
    bar_h=max(7,int(8+depth*22))
    pygame.draw.rect(surface,(27,31,40),(int(left)-post_w,y-post_h,int(right-left)+post_w*2,bar_h))
    if depth>0.23:
        draw_text(surface,"CHEGADA",int((left+right)/2),int(y-post_h+bar_h/2),YELLOW,SMALL,True)

def result_screen(title, subtitle, won):
    while True:
        screen.fill((10,16,28))
        draw_text(screen, title, 480, 220, GREEN if won else RED, BIG, True)
        draw_text(screen, subtitle, 480, 290, WHITE, FONT, True)
        draw_text(screen, "ENTER ou ESC para continuar", 480, 390, YELLOW, SMALL, True)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN,pygame.K_ESCAPE): return
        clock.tick(60)


def race(idx, boss):
    global ROUTE_CURVE, ROUTE_SEED
    ROUTE_SEED=random.randrange(1,10**9)
    rng=random.Random(ROUTE_SEED)
    # Cada tentativa recebe um traçado próprio, com curvas suaves e alternadas.
    ROUTE_CURVE=[0.0]
    for _ in range(10):
        ROUTE_CURVE.append(max(-115,min(115,ROUTE_CURVE[-1]+rng.randint(-65,65))))
    ROUTE_CURVE.append(0.0)
    phase = PHASES[idx]
    selected_car=CAR_CATALOG.get(save.get("selected_car","starter"),CAR_CATALOG["starter"])
    player_color=selected_car["color"]
    car_style=selected_car["style"]
    diff = phase["difficulty"] * (1.28 if boss else 1.0)
    distance_goal = 9000 + idx*900 + (1200 if boss else 0)

    player_y = HEIGHT-100
    player_lane = 1
    player_x = lane_center(player_lane, player_y)
    player_speed = 0.0
    max_speed = (8.0 + save["upgrades"]["engine"]*0.55) * selected_car["speed"]
    handling = (4.2 + save["upgrades"]["tires"]*0.45) * selected_car["handling"]
    accel = 0.014 + save["upgrades"]["accel"]*0.0035
    durability = min(100, 75 + save["upgrades"]["armor"]*5)
    max_durability = durability

    distance = 0.0
    scroll = 0.0
    coins = 0
    overtakes = 0
    traffic = []
    pickups = []
    obstacles = []
    turbo_timer = 0
    shield_timer = 0
    invuln = 0
    spawn_timer = 90
    pickup_timer = 145
    obstacle_timer = 180
    race_started_at = None
    countdown_start = pygame.time.get_ticks()
    finish = False
    won = False

    # Pista com 4 faixas: classificatória com 4 pilotos em faixas separadas; duelo 1x1 em faixas distintas.
    rival_colors = [(55,145,235),(245,170,45),(65,190,125),
                    (155,75,210),(230,80,95),(70,205,195),
                    (245,210,85),(130,155,245),(230,115,180),
                    (95,200,100),(220,135,65)]
    racers = []
    if boss:
        # O Street Compact sem melhorias atinge 8.0 unidades/tick.
        # O chefe atinge 8.3: é um pouco mais rápido que o carro padrão,
        # mas um upgrade de motor (8.55) já permite vencê-lo sem turbo.
        # A IA tem aceleração gradual, sem velocidade artificial crescente
        # com o carro selecionado pelo jogador.
        racers.append({
            "racer_id": 1, "lane": rng.choice((0, 2, 3)), "y": player_y,
            "color": (155,60,220), "ai_speed": 0.0,
            "target_speed": 8.3, "ai_accel": 0.020,
            "boss": True, "progress": 0.0,
            "finished": False, "finish_order": None,
            "collision_cooldown": 0.0
        })
    else:
        for number in range(1, 4):
            # Cada piloto larga em uma pista diferente, sem carros sobrepostos.
            starting_lane = (0, 2, 3)[number-1]
            racers.append({
                "racer_id": number, "lane": starting_lane,
                "y": player_y,
                "color": rival_colors[number-1],
                "ai_speed": 0.0,
                "target_speed": max_speed * (0.64 + 0.025*(number%7))
                    * (0.95 + min(0.16, idx*0.018)),
                "ai_accel": 0.028,
                "boss": False, "progress": 0.0,
                "finished": False, "finish_order": None,
                "collision_cooldown": 0.0
            })
    traffic = racers
    total_racers = len(racers) + 1
    finish_order = []
    previous_position = total_racers
    position_notice = ""
    position_notice_timer = 0.0
    start_ticks = pygame.time.get_ticks()
    camera_shift = 0.0
    world = pygame.Surface((WIDTH,HEIGHT))

    while not finish:
        dt = min(2.0, clock.tick(60)/16.666)
        now = pygame.time.get_ticks()
        elapsed_countdown = (now-countdown_start)/1000
        started = elapsed_countdown >= 3.8
        if started and race_started_at is None:
            race_started_at = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if started and event.key == pygame.K_SPACE and save["items"]["turbo"]>0 and turbo_timer<=0:
                    save["items"]["turbo"]-=1; turbo_timer=190
                if started and event.key == pygame.K_e and save["items"]["shield"]>0 and shield_timer<=0:
                    save["items"]["shield"]-=1; shield_timer=260
                if started and event.key == pygame.K_r and save["items"]["repair"]>0 and durability<max_durability:
                    save["items"]["repair"]-=1
                    durability=min(max_durability,durability+35)

        keys=pygame.key.get_pressed()
        if started:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_speed=min(max_speed,player_speed+accel*dt*(0.85 + 0.15*(1.0-player_speed/max_speed)))
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player_speed=max(0.0,player_speed-0.095*dt)
            # Sem acelerar, o carro reduz até parar, nunca começa andando sozinho.
            else:
                player_speed=max(0.0,player_speed-0.012*dt)

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x-=handling*dt*(0.55+player_speed/8)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x+=handling*dt*(0.55+player_speed/8)

            if turbo_timer>0:
                turbo_timer-=dt
                current_speed=player_speed*1.45
            else:
                current_speed=player_speed

            if shield_timer>0: shield_timer-=dt
            if invuln>0: invuln-=dt

            left_limit,right_limit=road_edges(player_y)
            player_x=max(left_limit+58,min(right_limit-58,player_x))
            # Determina a faixa ocupada para o mini mapa e para leitura da posição.
            player_lane=min(3,max(0,int((player_x-left_limit)/max(1,right_limit-left_limit)*4)))
            distance += current_speed*dt*1.30
            scroll += current_speed*dt*8

            # IA e classificação usam a MESMA distância percorrida.
            # A posição na tela é derivada da diferença de progresso, evitando
            # adversários que desaparecem e continuam correndo invisíveis.
            for rival in racers:
                if not rival["finished"]:
                    rival["ai_speed"] = min(rival["target_speed"],
                        rival["ai_speed"] + rival.get("ai_accel", 0.028)*dt)
                    rival["progress"] = min(distance_goal,
                        rival["progress"] + rival["ai_speed"]*dt*1.30)
                    if rival["progress"] >= distance_goal:
                        rival["finished"] = True
                        finish_order.append(rival["racer_id"])
                        rival["finish_order"] = len(finish_order)
                # Projeção de distância: surgem pequenos no horizonte e
                # crescem suavemente conforme o jogador se aproxima.
                ahead = rival["progress"] - distance
                rival["y"] = player_y - ahead*0.38
                rival["x"] = lane_center(rival["lane"], rival["y"])
                rival["collision_cooldown"] = max(0.0,
                    rival["collision_cooldown"] - dt)

            # Atualiza o placar a cada ultrapassagem real, incluindo quando
            # o jogador perde posições para os demais pilotos.
            ranking_now = sorted(
                [(0, min(distance, distance_goal))] +
                [(r["racer_id"], r["progress"]) for r in racers],
                key=lambda entry: (
                    1 if entry[0] in finish_order else 0,
                    -finish_order.index(entry[0]) if entry[0] in finish_order
                    else entry[1]
                ), reverse=True)
            current_position = next(i for i, (rid, _) in enumerate(ranking_now, 1)
                                    if rid == 0)
            if current_position != previous_position:
                if current_position < previous_position:
                    overtakes += previous_position-current_position
                    position_notice = f"ULTRAPASSAGEM! {current_position}º LUGAR"
                else:
                    position_notice = f"VOCÊ CAIU PARA {current_position}º"
                position_notice_timer = 115.0
                previous_position = current_position
            position_notice_timer = max(0.0, position_notice_timer-dt)

            pickup_timer-=dt
            if pickup_timer<=0:
                lane=random.choice((0,1,2,3))
                pickups.append({"lane":lane,"y":220.0})
                pickup_timer=150

            obstacle_timer-=dt
            if obstacle_timer<=0 and idx>=2:
                lane=random.choice((0,1,2,3))
                obstacles.append({"lane":lane,"y":220.0})
                obstacle_timer=max(95,175/diff)

            # Itens acompanham a faixa e avançam conforme a velocidade relativa.
            for item in pickups:
                item["y"] += max(0.0,current_speed*3.8)*dt
            pickups=[it for it in pickups if it["y"]<HEIGHT+35]

            for obs in obstacles:
                obs["y"] += max(0.0,current_speed*3.8)*dt
            obstacles=[ob for ob in obstacles if ob["y"]<HEIGHT+40]

            player_rect=pygame.Rect(int(player_x-37),int(player_y-43),74,86)
            for car in racers:
                if car["finished"] or car["collision_cooldown"]>0:
                    continue
                if not (190 < car["y"] < HEIGHT+70):
                    continue
                scale,_=opponent_render_params(car["y"],car.get("boss",False))
                car_w=max(3,int(132*scale))
                car_h=max(4,int(155*scale))
                rect=pygame.Rect(int(car["x"]-car_w/2),int(car["y"]-car_h/2),car_w,car_h)
                if player_rect.colliderect(rect):
                    car["collision_cooldown"] = 75.0
                    if shield_timer>0:
                        shield_timer=max(0,shield_timer-45)
                    elif invuln<=0:
                        durability-=22 if car.get("boss") else 16
                        invuln=55
                        player_speed=max(0.0,player_speed-1.0)

            for item in pickups[:]:
                item_x=lane_center(item["lane"],item["y"])
                if abs(item_x-player_x)<42 and abs(item["y"]-player_y)<52:
                    coins+=1
                    pickups.remove(item)

            for obs in obstacles[:]:
                obs_x=lane_center(obs["lane"],obs["y"])
                if abs(obs_x-player_x)<42 and abs(obs["y"]-player_y)<52 and invuln<=0:
                    durability-=12
                    invuln=35
                    obstacles.remove(obs)

            if durability<=0:
                finish=True; won=False
            if distance>=distance_goal:
                # A corrida do jogador termina somente quando cruza a chegada.
                finish_order.append(0)
                final_position = len(finish_order)
                finish=True; won=True
        else:
            current_speed=0.0

        # Câmera traseira dinâmica: acompanha suavemente o movimento lateral.
        camera_target = (WIDTH/2-player_x)*0.50
        camera_shift += (camera_target-camera_shift)*min(1.0,0.09*dt)
        world.fill((65,80,86))
        draw_background(world,idx,scroll)

        # Pórtico e faixa de chegada: surgem ao longe e avançam até o carro.
        remaining = distance_goal-distance
        if 0 <= remaining <= 820:
            draw_finish_line(world, remaining, player_y)

        # Objetos de pista com posição coerente em perspectiva
        for obs in obstacles:
            x=lane_center(obs["lane"],obs["y"])
            depth=max(0.15,min(1.0,(obs["y"]-190)/(HEIGHT-190)))
            size=int(8+24*depth)
            pygame.draw.rect(world,(225,125,45),
                (int(x-size/2),int(obs["y"]-size/2),size,size),border_radius=4)
            pygame.draw.rect(world,(255,220,150),
                (int(x-size/4),int(obs["y"]-size/4),max(2,size//2),max(2,size//2)))

        for item in pickups:
            x=lane_center(item["lane"],item["y"])
            depth=max(0.15,min(1.0,(item["y"]-190)/(HEIGHT-190)))
            radius=int(3+8*depth)
            pygame.draw.circle(world,YELLOW,(int(x),int(item["y"])),radius)
            pygame.draw.circle(world,(255,245,160),(int(x-radius//3),int(item["y"]-radius//3)),max(2,radius//3))

        # Carros da IA desenhados do mais distante ao mais próximo.
        for car in sorted(racers,key=lambda c:c["y"]):
            if not (170 < car["y"] < HEIGHT+130):
                continue
            car_scale,car_alpha=opponent_render_params(car["y"],car.get("boss",False))
            if car_alpha:
                draw_rear_car(world,lane_center(car["lane"],car["y"]),car["y"],
                              car["color"],car_scale,False,1 if car.get("boss") else 0,car_alpha)

        if not (invuln>0 and int(invuln)%8<4):
            draw_rear_car(world,player_x,player_y,player_color,1.16,True,car_style)

        # Deslocamento do cenário com a câmera, mantendo o carro em primeiro plano.
        screen.fill((65,80,86))
        screen.blit(world,(int(camera_shift),0))

        # Mini mapa em tempo real: jogador em vermelho e rivais em azul.
        draw_minimap(screen,[r for r in racers if 190 < r["y"] < HEIGHT],player_x,player_y,player_lane)

        # Contagem regressiva e sinal de largada
        if not started:
            panel(screen,(300,245,360,150),(8,12,22,220),YELLOW)
            if elapsed_countdown < 1:
                countdown_text="3"
            elif elapsed_countdown < 2:
                countdown_text="2"
            elif elapsed_countdown < 3:
                countdown_text="1"
            else:
                countdown_text="LARGADA!"
            draw_text(screen,countdown_text,480,305,
                      GREEN if countdown_text=="LARGADA!" else YELLOW,
                      BIG if countdown_text!="LARGADA!" else FONT,True)
            draw_text(screen,"PREPARE-SE!",480,355,WHITE,SMALL,True)

        # Ranking em tempo real: 12 na classificatória, 2 no duelo de chefe.
        ranking = [(0, min(distance, distance_goal))] + [
            (r["racer_id"], r["progress"]) for r in racers
        ]
        # Pilotos que terminaram ficam a frente, na ordem de chegada.
        ranking.sort(key=lambda entry: (
            1 if entry[0] in finish_order else 0,
            -finish_order.index(entry[0]) if entry[0] in finish_order else entry[1]
        ), reverse=True)
        player_position = next(i for i, (rid, _) in enumerate(ranking, 1) if rid == 0)
        panel(screen,(WIDTH//2-100,12,200,83))
        draw_text(screen,f"{player_position}º / {len(ranking)}",WIDTH//2,37,YELLOW,BIG,True)
        draw_text(screen,"POSIÇÃO NA CORRIDA",WIDTH//2,76,WHITE,SMALL,True)

        if position_notice_timer > 0:
            notice_color = GREEN if "ULTRAPASSAGEM" in position_notice else RED
            panel(screen,(WIDTH//2-200,105,400,48))
            draw_text(screen,position_notice,WIDTH//2,129,notice_color,FONT,True)

        # HUD
        panel(screen,(12,12,275,126))
        draw_text(screen,f"FASE {idx+1} - {'CHEFE' if boss else 'CORRIDA'}",25,22,YELLOW,SMALL)
        draw_text(screen,f"Percurso: {int(min(distance,distance_goal))}/{distance_goal} m",25,48,WHITE,SMALL)
        draw_text(screen,f"Carro: {selected_car['name']}",25,72,WHITE,SMALL)
        draw_text(screen,f"Moedas: {coins}   Ultrapassagens: {overtakes}",25,98,GREEN,SMALL)
        panel(screen,(WIDTH-235,12,220,112))
        draw_text(screen,"DURABILIDADE",WIDTH-220,22,WHITE,SMALL)
        pygame.draw.rect(screen,(65,30,35),(WIDTH-220,49,185,16),border_radius=5)
        pygame.draw.rect(screen,GREEN if durability>45 else RED,
            (WIDTH-220,49,int(185*max(0,durability/max_durability)),16),border_radius=5)
        draw_text(screen,f"{max(0,int(durability))}%",WIDTH-125,78,WHITE,SMALL,True)
        draw_text(screen,'INTEGRIDADE DO CARRO',WIDTH-220,99,CYAN,SMALL)
        draw_skills(screen,save['items'],turbo_timer,shield_timer,durability,max_durability)
        draw_speedometer(screen,current_speed*22,max_speed*1.45*22,turbo_timer>0)
        if shield_timer>0: draw_text(screen,"ESCUDO ATIVO",480,525,CYAN,SMALL,True)
        draw_text(screen,"A/D DIREÇÃO  •  W ACELERAR  •  S FREAR  •  ESC SAIR",
                  470,620,WHITE,SMALL,True)
        pygame.display.flip()

    elapsed=(pygame.time.get_ticks()-(race_started_at or start_ticks))/1000
    if won:
        # Somente o pódio recebe dinheiro. A premiação cresce com a fase.
        podium_prizes = {1: 600 + idx*130 + (200 if boss else 0),
                         2: 350 + idx*90 + (120 if boss else 0),
                         3: 180 + idx*55 + (60 if boss else 0)}
        reward = podium_prizes.get(final_position, 0) if (not boss or final_position == 1) else 0
        save["money"] += reward
        if final_position <= 3 and (not boss or final_position == 1):
            key = f"{idx}_{'boss' if boss else 'normal'}"
            best = save["best_times"].get(key)
            if best is None or elapsed < best:
                save["best_times"][key] = round(elapsed, 2)
        save_game()
        if reward:
            result_screen("CHEFE DERROTADO!" if boss else "PÓDIO!",f"Posição: {final_position}º/{total_racers} | Prêmio: $ {reward} | Tempo: {elapsed:.1f}s",True)
        else:
            result_screen("CHEFE VENCEU!" if boss else "CHEGADA!",f"Posição: {final_position}º/{total_racers} | Sem premiação | Tempo: {elapsed:.1f}s",False)
    else:
        save_game()
        result_screen("CORRIDA ENCERRADA","Durabilidade esgotada. Sem premiação.",False)
    # Classificatória com 4 pilotos: Top 3 avança. Duelo: só 1º libera a fase.
    return won and (final_position == 1 if boss else final_position <= 3)

if __name__ == "__main__":
    main_menu()
