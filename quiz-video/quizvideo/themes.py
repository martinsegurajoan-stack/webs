"""Paletas de colores. Cada tema define fondo, acentos y colores de opciones."""

THEMES = {
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
