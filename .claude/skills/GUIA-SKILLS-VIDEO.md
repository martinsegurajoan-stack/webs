# Guía de skills de vídeo (instaladas el 02-11-2026)

Cómo trabajan juntas las skills de edición y postproducción. Las de esta carpeta (`.claude/skills/`) se cargan solas en
cualquier sesión de este repositorio. HyperFrames y Remotion están en `~/.claude/skills/` (nivel de usuario).

## Qué skill usar para cada cosa

| Necesidad | Skill principal | Apoyo |
|---|---|---|
| Construir el vídeo (escenas, cámara, GSAP, render) | `hyperframes` (+ `hyperframes-cli`, `hyperframes-registry`) | `remotion-*` solo si el proyecto es Remotion |
| Animación con calidad de motion design (easing, anticipación, rebote, stagger) | `motion-designer`, `slow-in-out-mastery`, `follow-through-overlapping` | `video-motion-graphics`, `production-motion` |
| Gráficos y textos animados dentro de la escena | `motion-graphics` | `hyperframes-registry` (kit en `quiz-video/animado/kit/`) |
| Cámara virtual (punch-in, Ken Burns, shake, whip) | `camera-motion` | `motion-sickness` (no marear) |
| Ritmo, cortes y transiciones con sentido | `pacing` | `timing-calibration` |
| Sincronizar cortes con música | `beat-sync` | `hyperframes` (`npx hyperframes beats --json`) |
| Final en bucle sin que se note | `seamless-loop` | |
| Mezcla: voz por encima de música y efectos | `audio-ducking` | `sound-designer` |
| Subtítulos legibles en móvil | `caption-styling` | `hyperframes` (captions) |
| Cortar, unir, reencuadrar, loudness, exportar, revisar con FFmpeg | `ffmpeg-skill` | |

## Reglas para que no choquen

1. **Mandan las reglas del usuario.** `CLAUDE.md`, `quiz-video/animado/INSTRUCCIONES.md` y
   `quiz-video/animado/MEJORA_CONTINUA.md` van por encima de cualquier skill (p. ej. la mezcla «la voz manda»,
   narrador neutro, 61 s mínimo, nada de mareos).
2. **Una sola herramienta de montaje por proyecto**: HyperFrames para los vídeos animados (es lo que usa este repo);
   Remotion solo si el proyecto ya es Remotion. No mezclar las dos en el mismo vídeo.
3. **Skills de Vidmoat** (`audio-ducking`, `caption-styling`, `pacing`, `beat-sync`, `seamless-loop`, `motion-graphics`,
   `production-motion`, `camera-motion`, `sound-designer`, `motion-designer`): se usan como criterio de oficio. Si
   nombran órdenes de su editor (clipId, MCP, «@motion-designer»), traducirlas a HyperFrames/GSAP o FFmpeg. No hace
   falta Vidmoat ni ninguna cuenta.
4. **Skills de principios de animación** (`video-motion-graphics`, `timing-calibration`, `motion-sickness`,
   `slow-in-out-mastery`, `follow-through-overlapping`): hablan de After Effects; aplicarlas con GSAP (eases
   `power3`/`back`/`elastic`, `stagger`, desfases de 4-8 fotogramas a 30 fps).
5. **`ffmpeg-skill`** es para postproducción sobre archivos (cortes, loudness, exportaciones, comprobaciones).
   No sustituye a `mezcla.py` de cada proyecto; úsala para revisar o para exportar por plataforma.
   La transcripción automática es opcional y necesita `pip install faster-whisper` (no instalado).
6. **Voz**: ninguna de estas skills genera voz. La voz sigue siendo la de ElevenLabs que fija `CLAUDE.md`.

## Orígenes y licencias

| Skill | Repositorio | Licencia |
|---|---|---|
| ffmpeg-skill (v3.1.1) | https://github.com/kajisho5/ffmpeg-skill | MIT |
| audio-ducking, caption-styling, pacing, beat-sync, seamless-loop, motion-graphics, production-motion, camera-motion, sound-designer, motion-designer | https://github.com/vidmoat/skills (commit c363092) | Apache-2.0 (scripts) + CC-BY-4.0 (texto) |
| video-motion-graphics, timing-calibration, motion-sickness, slow-in-out-mastery, follow-through-overlapping | https://github.com/dylantarre/animation-principles | MIT |

Actualizar: volver a copiar la carpeta de la skill desde su repositorio (o `npx ffmpeg-skill --project` para FFmpeg).
