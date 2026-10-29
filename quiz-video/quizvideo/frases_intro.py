"""Frases "salseantes" para abrir los quiz. Se usa una distinta en cada vídeo (registro en
assets/frases_usadas.json). Para añadir más, escríbelas al final de la lista."""

import json
import os

FRASES_INTRO = [
    "Si no aciertas ni 3 de 5, hoy tu cerebro ha venido de vacaciones. ¡Vamos a comprobarlo!",
    "Mucho listo veo yo por aquí… ¡A ver si luego no fallas las más fáciles! ¡Empieza el quiz!",
    "Si sacas un cero, no pasa nada… pero hoy no presumas de inteligencia. ¡Vamos allá!",
    "Hoy vamos a separar a los que saben de los que hablan por hablar. ¡Demuestra lo que vales!",
    "No vale decir «esa me la sabía» después de ver la respuesta. ¡Contesta rápido y sin llorar!",
    "Si aciertas las cinco, haz captura, porque eso no te vuelve a pasar. ¡Vamos!",
    "Tu profesor de primaria está mirando este vídeo… no le decepciones. ¡Empezamos!",
    "Cinco segundos por pregunta. Ni Google, ni comodín de la llamada. ¡A ver qué tal!",
    "Solo un 10 % acierta todas. Spoiler: seguramente tú no. ¡Demuéstrame lo contrario!",
    "Prepárate, que hoy hay alguna trampa escondida… ¡y vas a caer! ¡Vamos allá!",
    "Si fallas la primera, cierra la app y vete a dormir. ¡Es broma… o no! ¡Empieza el quiz!",
    "Hoy descubrimos si eres un genio o simplemente tienes buena suerte. ¡Al lío!",
    "Saca papel y boli, que aquí no se perdona ni una. ¡Arrancamos!",
    "Mándaselo a ese amigo que se cree el más listo del grupo. ¡Empezamos!",
    "Las preguntas parecen fáciles… eso es lo que quieren que pienses. ¡Vamos!",
    "Aquí se viene a pensar, no a mirar. ¡Ponte las pilas que empezamos!",
    "Si aciertas más de tres, ya puedes presumir en la cena familiar. ¡Vamos allá!",
    "Hoy tu cerebro va a sudar. Calienta, que empezamos. ¡Tres, dos, uno!",
    "El que pierda invita a cenar. Ya estás tardando en jugar. ¡Empieza el quiz!",
    "Ni trampas, ni pausar el vídeo, que te estoy viendo. ¡Vamos a ello!",
    "Dicen que este quiz lo aprueba cualquiera. Yo no estaría tan seguro. ¡Adelante!",
    "Si te equivocas, échale la culpa al wifi como todo el mundo. ¡Empezamos!",
    "Esto no es un examen… pero si suspendes, lo sabrá todo TikTok. ¡Vamos!",
    "Hoy toca demostrar que el colegio sirvió para algo. ¡Arrancamos el quiz!",
    "Cuidado con la última, que es de las que pican. ¡Vamos allá!",
    "Respira hondo, concéntrate y no te pongas nervioso… que los nervios fallan. ¡Empezamos!",
    "Si aciertas todas, eres oficialmente la persona más lista de tu casa. ¡A por ello!",
    "Cinco preguntas y una extra para los valientes. ¿Te atreves? ¡Vamos!",
    "Aquí no gana el que más sabe, gana el que no se equivoca. ¡Empieza el quiz!",
    "Hoy se mide el cerebro, no el ego. ¡Vamos a ver de qué estás hecho!",
]

REGISTRO = os.path.join(os.path.dirname(__file__), "..", "assets", "frases_usadas.json")


def _leer():
    try:
        with open(REGISTRO, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def elegir_frase(video):
    """Frase para `video`: la que ya tenía, o la primera que no se ha usado en ningún vídeo."""
    reg = _leer()
    if video in reg:
        return FRASES_INTRO[reg[video] % len(FRASES_INTRO)]
    usadas = set(reg.values())
    libres = [i for i in range(len(FRASES_INTRO)) if i not in usadas]
    i = libres[0] if libres else len(reg) % len(FRASES_INTRO)
    return FRASES_INTRO[i]


def registrar_frase(video, frase):
    reg = _leer()
    reg[video] = FRASES_INTRO.index(frase)
    with open(REGISTRO, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2, sort_keys=True)
