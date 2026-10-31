"""Paletas de colores. Cada tema define fondo, acentos y colores de opciones."""

THEMES = {
    "romantico": {
        "bg_top": (255, 105, 150),
        "bg_bottom": (150, 25, 90),
        "bg_mid": (255, 160, 190),
        "bg_alt": (170, 60, 170),
        "blob": (255, 200, 225),
        "accent": (255, 222, 120),
        "accent2": (214, 30, 100),
        "card": (255, 255, 255),
        "text_dark": (80, 10, 45),
        "text_light": (255, 255, 255),
        "correct": (230, 40, 110),
        "wrong": (150, 120, 135),
        "options": [(255, 64, 129), (171, 71, 188), (255, 112, 90), (229, 40, 70)],
        "formas": "corazones",
        "rayos": 0.7,
    },
    "verde": {
        "bg_top": (0, 214, 110),
        "bg_bottom": (0, 110, 70),
        "bg_mid": (140, 235, 30),
        "bg_alt": (0, 190, 160),
        "blob": (180, 255, 120),
        "accent": (255, 221, 0),
        "accent2": (255, 56, 136),
        "card": (255, 255, 255),
        "text_dark": (16, 40, 30),
        "text_light": (255, 255, 255),
        "correct": (0, 200, 83),
        "wrong": (120, 130, 125),
        "options": [(255, 56, 136), (0, 176, 255), (255, 171, 0), (156, 77, 255)],
    },
    "lima": {
        "bg_top": (190, 240, 30),
        "bg_bottom": (0, 150, 90),
        "blob": (255, 255, 160),
        "accent": (255, 90, 0),
        "accent2": (0, 120, 255),
        "card": (255, 255, 255),
        "text_dark": (20, 45, 20),
        "text_light": (255, 255, 255),
        "correct": (0, 170, 70),
        "wrong": (130, 130, 130),
        "options": [(255, 64, 64), (0, 140, 255), (255, 150, 0), (190, 60, 220)],
    },
    "neon": {
        "bg_top": (20, 30, 60),
        "bg_bottom": (0, 120, 90),
        "blob": (0, 255, 170),
        "accent": (0, 255, 170),
        "accent2": (255, 0, 200),
        "card": (255, 255, 255),
        "text_dark": (15, 20, 40),
        "text_light": (255, 255, 255),
        "correct": (0, 230, 118),
        "wrong": (110, 110, 130),
        "options": [(255, 0, 200), (0, 200, 255), (255, 214, 0), (140, 90, 255)],
    },
    "tropical": {
        "bg_top": (0, 200, 170),
        "bg_bottom": (0, 110, 70),
        "blob": (255, 230, 120),
        "accent": (255, 120, 60),
        "accent2": (255, 230, 0),
        "card": (255, 255, 255),
        "text_dark": (10, 50, 45),
        "text_light": (255, 255, 255),
        "correct": (0, 190, 80),
        "wrong": (120, 135, 130),
        "options": [(255, 90, 95), (30, 150, 255), (255, 180, 0), (170, 80, 230)],
    },
}


def get_theme(name: str) -> dict:
    if name not in THEMES:
        raise SystemExit(f"Tema '{name}' no existe. Disponibles: {', '.join(THEMES)}")
    return THEMES[name]


# ---------------------------------------------------------------- paletas automáticas
# Cada vídeo recibe un color de fondo que no se ha usado antes (registro en assets/paletas_usadas.json).
import colorsys
import json
import os

REGISTRO = os.path.join(os.path.dirname(__file__), "..", "assets", "paletas_usadas.json")
# Tonos ya usados antes del registro: verde (vídeo 1) y rosa (pareja 1)
INICIALES = {"hora_del_quiz_01": 150, "pareja_01": 335}


def _hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, max(0, min(1, s)), max(0, min(1, v)))
    return (int(r * 255), int(g * 255), int(b * 255))


def _dist(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def leer_registro():
    try:
        with open(REGISTRO, encoding="utf-8") as f:
            reg = json.load(f)
    except (OSError, ValueError):
        reg = {}
    for k, v in INICIALES.items():
        reg.setdefault(k, v)
    return reg


def guardar_registro(reg):
    with open(REGISTRO, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2, sort_keys=True)


def elegir_tono(video, rango=None):
    """Tono (0-359) para `video`: si ya tiene uno lo reutiliza; si no, el más alejado de los usados."""
    reg = leer_registro()
    if video in reg:
        return reg[video]
    usados = list(reg.values())
    candidatos = range(0, 360, 3)
    if rango:
        a, b = rango
        candidatos = [h for h in candidatos if (a <= h <= b if a <= b else (h >= a or h <= b))]
    return max(candidatos, key=lambda h: (min(_dist(h, u) for u in usados), -h))


def registrar_tono(video, h):
    reg = leer_registro()
    reg[video] = h
    guardar_registro(reg)


def paleta_desde_tono(h, formas=None):
    """Paleta alegre y legible a partir de un tono."""
    # acento amarillo salvo que el fondo ya sea amarillento; entonces magenta
    accent = (255, 221, 0) if _dist(h, 52) > 35 else (255, 64, 160)
    vivid = [(255, 56, 136), (0, 176, 255), (255, 171, 0), (156, 77, 255), (0, 200, 120), (255, 90, 60)]
    opts = [c for c in vivid if _dist(colorsys.rgb_to_hsv(*[x / 255 for x in c])[0] * 360, h) > 30][:4]
    th = {
        "bg_top": _hsv(h, 0.85, 0.95),
        "bg_bottom": _hsv(h + 10, 0.95, 0.45),
        "bg_mid": _hsv(h - 25, 0.65, 1.0),
        "bg_alt": _hsv(h + 35, 0.85, 0.8),
        "blob": _hsv(h, 0.35, 1.0),
        "accent": accent,
        "accent2": _hsv(h + 180, 0.85, 0.95) if _dist(h + 180, 52) > 35 else (255, 56, 136),
        "card": (255, 255, 255),
        "text_dark": _hsv(h, 0.85, 0.22),
        "text_light": (255, 255, 255),
        "correct": (0, 200, 83) if _dist(h, 140) > 35 else (0, 150, 255),
        "wrong": (130, 130, 140),
        "options": opts,
        "tono": h,
    }
    if formas:
        th["formas"] = formas
        th["rayos"] = 0.7
    return th


def paleta_romantica(h):
    """Paleta romántica (rosas, rojos, morados y dorado) con un tono base que no se repite."""
    th = paleta_desde_tono(h, "corazones")
    rosa = 345 if _dist(h, 345) > 20 else 318
    th.update({
        "bg_top": _hsv(h, 0.75, 0.97),
        "bg_bottom": _hsv(h + 8, 0.9, 0.5),
        "bg_mid": _hsv(h - 15, 0.5, 1.0),
        "bg_alt": _hsv(h + 25, 0.75, 0.85),
        "blob": _hsv(h, 0.25, 1.0),
        "accent": (255, 214, 110),                 # dorado suave
        "accent2": _hsv(rosa, 0.85, 0.88),         # rosa/frambuesa intenso
        "text_dark": _hsv(h, 0.85, 0.25),
        "correct": _hsv(rosa, 0.8, 0.9),
        "wrong": (150, 120, 135),
        "options": [(255, 64, 129), (171, 71, 188), (255, 112, 90), (229, 40, 70)],
    })
    return th


def paleta_halloween(h):
    """Paleta de Halloween: noche morada/negra con brillo naranja; tono base morado que no se repite."""
    th = paleta_desde_tono(h)
    th.update({
        "bg_top": _hsv(h, 0.75, 0.45),
        "bg_bottom": (10, 4, 22),
        "bg_mid": _hsv(h + 10, 0.7, 0.55),
        "bg_alt": (255, 120, 20),                  # brillo naranja de calabaza
        "blob": (255, 150, 50),
        "accent": (255, 145, 0),                   # naranja calabaza
        "accent2": (150, 70, 235),                 # morado brujería
        "card": (255, 248, 236),                   # pergamino
        "text_dark": (38, 10, 52),
        "correct": (110, 210, 40),                 # verde poción
        "wrong": (120, 110, 130),
        "options": [(255, 120, 0), (150, 70, 230), (90, 190, 50), (225, 40, 60)],
        "formas": "halloween",
        "rayos": 0.45,
    })
    return th


def paleta_futbol(h):
    """Paleta de fútbol: campo de césped verde (tono que no se repite) y detalles dorados."""
    th = paleta_desde_tono(h)
    th.update({
        "cesped1": _hsv(h, 0.62, 0.62), "cesped2": _hsv(h + 3, 0.66, 0.52),
        "bg_top": _hsv(h, 0.7, 0.6), "bg_bottom": _hsv(h, 0.8, 0.35), "bg_mid": _hsv(h, 0.5, 0.75),
        "blob": (255, 255, 255),
        "accent": (255, 214, 0),                    # dorado de trofeo
        "accent2": (20, 30, 60),
        "card": (255, 255, 255),
        "text_dark": (12, 40, 22),
        "correct": (255, 190, 0),                    # dorado: no se pierde sobre el césped
        "wrong": (120, 130, 125),
        "options": [(0, 120, 255), (230, 40, 60), (255, 150, 0), (130, 60, 230)],
        "formas": "futbol",
        "rayos": 0.0,
    })
    return th


def paleta_gamer(h):
    """Paleta gamer: mismo estilo que el trivial pero más oscura y neón (synthwave), tono que no se repite."""
    th = paleta_desde_tono(h, "gamer")
    th.update({
        "bg_top": _hsv(h, 0.85, 0.62),
        "bg_bottom": _hsv(h + 45, 0.9, 0.2),
        "bg_mid": _hsv(h + 20, 0.7, 0.75),
        "bg_alt": _hsv(h + 150, 0.8, 0.6),
        "blob": _hsv(h, 0.4, 1.0),
        "accent": (255, 214, 0),
        "accent2": (255, 45, 150),
        "rayos": 0.6,
    })
    return th


def paleta_mascota(h):
    """Paleta de mascotas: cálida y alegre (amarillos/naranjas/melocotón) con tono que no se repite."""
    th = paleta_desde_tono(h, "mascotas")
    th.update({
        "bg_top": _hsv(h, 0.78, 1.0),
        "bg_bottom": _hsv(h - 18, 0.9, 0.62),
        "bg_mid": _hsv(h + 12, 0.55, 1.0),
        "bg_alt": _hsv(h - 30, 0.75, 0.9),
        "blob": _hsv(h + 5, 0.3, 1.0),
        "accent": (255, 255, 255) if _dist(h, 52) <= 35 else (255, 221, 0),
        "accent2": (0, 150, 220),                   # azul collar
        "text_dark": _hsv(h - 25, 0.9, 0.28),       # marrón chocolate
        "correct": (0, 150, 220),
        "wrong": (140, 130, 120),
        "options": [(255, 90, 120), (0, 160, 230), (120, 200, 40), (160, 90, 230)],
        "formas": "mascotas",
        "rayos": 0.8,
    })
    return th


def paleta_mexico(h):
    """Paleta de MÉXICO: verde bandera (tono que no se repite), rojo y blanco de la bandera y
    colores de fiesta (rosa mexicano, turquesa, naranja, morado) en las opciones."""
    th = paleta_desde_tono(h, "mexico")
    th.update({
        "bg_top": _hsv(h, 0.95, 0.62),
        "bg_bottom": _hsv(h + 6, 1.0, 0.26),
        "bg_mid": _hsv(h - 8, 0.8, 0.78),
        "bg_alt": (206, 17, 38),                    # rojo bandera
        "blob": (255, 255, 255),
        "accent": (255, 205, 0),                    # amarillo cempasúchil
        "accent2": (206, 17, 38),                   # rojo bandera
        "card": (255, 255, 255),
        "text_dark": (20, 46, 30),
        "correct": (255, 190, 0),                   # dorado: se ve sobre el verde
        "wrong": (130, 135, 130),
        "options": [(228, 0, 124), (0, 160, 190), (255, 120, 0), (130, 50, 200)],
        "formas": "mexico",
        "rayos": 0.55,
    })
    return th
