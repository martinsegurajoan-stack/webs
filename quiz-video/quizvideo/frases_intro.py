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

# Frases para el QUIZ DE PAREJAS: picantes, románticas y bromistas.
FRASES_PAREJA = [
    "Si fallas más de tres, esta noche duermes en el sofá. ¡Vamos a comprobarlo!",
    "Dicen que os conocéis de memoria… Eso ya lo veremos. ¡Empieza el quiz!",
    "Hoy se descubre quién presta atención y quién solo dice «sí, cariño». ¡Vamos allá!",
    "Ojo, que alguna pregunta puede acabar en discusión. ¡Jugad con cuidado!",
    "Si aciertas todas, tu pareja te debe una cena. Si no… la pagas tú. ¡Empezamos!",
    "Mira a tu pareja a los ojos y prepárate, que hoy no se miente. ¡Vamos!",
    "El que menos acierte friega los platos una semana. ¡Que empiece el juego!",
    "Esto no es un test de amor… pero casi. ¡A ver cuánto os conocéis!",
    "Hoy vamos a ver si sois pareja de verdad o solo compartís la contraseña del wifi. ¡Vamos!",
    "Respuestas sinceras, nada de quedar bien. ¡Que os estoy viendo! ¡Empezamos!",
    "Si te equivocas en la primera, mejor ve preparando las disculpas. ¡Vamos allá!",
    "Años juntos y aún no sabes esto… A ver si me equivoco. ¡Empieza el quiz!",
    "Ponte cómodo, coge la mano de tu pareja… y que gane el que más se fije. ¡Vamos!",
    "Aquí se mide el amor en aciertos. ¿Aprobaréis o habrá drama? ¡Empezamos!",
    "Etiqueta a tu pareja antes de empezar, que luego no vale poner excusas. ¡Vamos!",
    "Hoy toca demostrar que escuchas cuando te hablan. ¡Suerte, la vas a necesitar!",
    "Si sacáis un pleno, ya podéis casaros. Si no… seguid practicando. ¡Vamos allá!",
    "Prohibido mirar a tu pareja para copiar. ¡Cada uno con su respuesta!",
    "Las parejas que aciertan todo no existen… demostradme que me equivoco. ¡Empezamos!",
    "Advertencia: este quiz puede provocar risas, celos y alguna que otra mirada asesina. ¡Vamos!",
]

# Frases para quiz de HALLOWEEN: terroríficas y con humor.
FRASES_HALLOWEEN = [
    "Si fallas más de dos, esta noche el fantasma de tu profe de historia te visita. ¡Vamos a comprobarlo!",
    "Prepárate, que estas preguntas dan más miedo que tu cuenta del banco a final de mes. ¡Empezamos!",
    "Si no aciertas ninguna, mejor disfrázate de zombi: ya tienes el cerebro a juego. ¡Vamos allá!",
    "Las brujas ya están volando y los vampiros afilando los colmillos. ¿Tú estás listo? ¡Empieza el quiz!",
    "Dicen que quien falla este quiz se queda sin caramelos un año entero. ¡Mucho cuidado!",
    "Apaga la luz, sube el volumen y que empiece el quiz más terrorífico del año. ¡Vamos!",
    "Este quiz tiene trampas más escondidas que un esqueleto en el armario. ¡A por ello!",
    "Truco o trato: si aciertas todas, trato. Si no… te toca el truco. ¡Empezamos!",
    "Hasta Drácula ha fallado alguna de estas. A ver qué tal se te da a ti. ¡Vamos allá!",
    "Coge tu escoba, que esta noche toca volar entre preguntas. ¡Arranca el quiz de Halloween!",
]

# Frases GANCHO para quiz de FÚTBOL (van ANTES de "¡Es hora del quiz de fútbol!"): reto fuerte.
FRASES_FUTBOL = [
    "Solo un futbolero de verdad acierta las cinco… y la extra no la sabe casi nadie.",
    "Si aciertas todas, eres una leyenda del fútbol. Si fallas una… vuelve a ver los resúmenes.",
    "Estas preguntas separan a los que ven fútbol de los que lo VIVEN.",
    "Tu cuñado dice que sabe de fútbol. Vamos a comprobar si tú sabes más.",
    "Pita el árbitro, empieza el partido… y solo los cracks llegan al final.",
    "Aquí no vale el VAR: o te lo sabes, o te lo sabes.",
]

LISTAS = {"trivial": FRASES_INTRO, "pareja": FRASES_PAREJA, "halloween": FRASES_HALLOWEEN, "futbol": FRASES_FUTBOL}
REGISTROS = {
    "trivial": os.path.join(os.path.dirname(__file__), "..", "assets", "frases_usadas.json"),
    "pareja": os.path.join(os.path.dirname(__file__), "..", "assets", "frases_pareja_usadas.json"),
    "halloween": os.path.join(os.path.dirname(__file__), "..", "assets", "frases_halloween_usadas.json"),
    "futbol": os.path.join(os.path.dirname(__file__), "..", "assets", "frases_futbol_usadas.json"),
}


def _leer(modo):
    try:
        with open(REGISTROS[modo], encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def elegir_frase(video, modo="trivial"):
    """Frase para `video`: la que ya tenía, o la primera que no se ha usado en ningún vídeo."""
    lista, reg = LISTAS[modo], _leer(modo)
    if video in reg:
        return lista[reg[video] % len(lista)]
    usadas = set(reg.values())
    libres = [i for i in range(len(lista)) if i not in usadas]
    return lista[libres[0] if libres else len(reg) % len(lista)]


def registrar_frase(video, frase, modo="trivial"):
    reg = _leer(modo)
    reg[video] = LISTAS[modo].index(frase)
    with open(REGISTROS[modo], "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2, sort_keys=True)
