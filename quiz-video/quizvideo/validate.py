"""Comprueba que un quiz es válido antes de montar el vídeo."""

import json

LETTERS = "ABCD"
MAX_Q = 120  # caracteres de la pregunta (legibilidad)
MAX_OPT = 48  # caracteres por opción


def load_quiz(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        quiz = json.load(f)
    errors = validate(quiz)
    if errors:
        raise SystemExit("Quiz no válido:\n  - " + "\n  - ".join(errors))
    return quiz


def validate(quiz: dict) -> list[str]:
    errors = []
    if not str(quiz.get("tema", "")).strip():
        errors.append("Falta 'tema'.")
    qs = quiz.get("preguntas")
    if not isinstance(qs, list) or not qs:
        return errors + ["'preguntas' debe ser una lista no vacía."]
    for i, q in enumerate(qs, 1):
        p = f"Pregunta {i}:"
        text = str(q.get("pregunta", "")).strip()
        if not text:
            errors.append(f"{p} texto vacío.")
        elif len(text) > MAX_Q:
            errors.append(f"{p} demasiado larga ({len(text)} > {MAX_Q} caracteres).")
        opts = q.get("opciones")
        if not isinstance(opts, list) or len(opts) != 4:
            errors.append(f"{p} necesita exactamente 4 opciones.")
            continue
        clean = [str(o).strip() for o in opts]
        if any(not o for o in clean):
            errors.append(f"{p} hay una opción vacía.")
        if len({o.lower() for o in clean}) != 4:
            errors.append(f"{p} hay opciones repetidas.")
        for o in clean:
            if len(o) > MAX_OPT:
                errors.append(f"{p} opción demasiado larga: '{o}'.")
        c = str(q.get("correcta", "")).strip().upper()
        if not c and (q.get("sin_respuesta") or quiz.get("modo") == "pareja"):
            continue
        if c not in LETTERS or len(c) != 1:
            errors.append(f"{p} 'correcta' debe ser A, B, C o D.")
    return errors
