# quiz-video — índice corto (para gastar pocos tokens)

Todo el detalle está en archivos que SOLO se leen cuando toca (no leerlos enteros si no hace falta):
- `FORMATOS.md`: cada formato de quiz con sus reglas (secciones `## Modo "…"` / `## Formato "…"`). Buscar con grep la
  sección del formato pedido y leer solo esa + «ENTREGA OBLIGATORIA», «GANCHO INICIAL» y «Pasos para un vídeo nuevo».
- `REGLAS_USUARIO_COMPLETAS.md`: copia íntegra de todas las reglas del usuario hasta el 08-11-2026.
- Vídeos animados (@mundo.supuesto): `animado/INSTRUCCIONES.md` + `animado/MEJORA_CONTINUA.md`.
  «¿Qué pasaría si…?» INFORMATIVO (formato actual preferido): `animado/PLANTILLA_INFORMATIVO.md` (copia de `animado/burbuja5/`).
- Política «¿Y si gana…?»: `animado/vox29n/PLANTILLA.md`. Geopolítico: `animado/marruecos/PLANTILLA.md`.

Rama: `claude/tiktok-quiz-video-generator-nub6w6`. Vídeos en `salida/` o `animado/<proyecto>/salida/video-FINAL.mp4`.
Portadas: `portada.py` → `portadas/`. Textos de redes: `descripciones/`.
