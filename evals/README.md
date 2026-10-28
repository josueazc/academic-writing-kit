# Evals: comparar IAs (y versiones del kit) con las mismas tareas

Sirve para responder con datos "¿qué IA hace mejores trabajos con este kit?" y para detectar si un cambio en el kit empeora los resultados.

## Cómo correrlo
1. Elegí una tarea de [tareas.md](tareas.md).
2. Dale a cada IA **exactamente** el mismo pedido (modo A con la carpeta, o modo B/C con `PROMPT-UNIVERSAL.md`), incluido el bloque de respuestas del cuestionario inicial que trae la tarea, para que no tenga que preguntar.
3. Guardá cada resultado como `evals/resultados/<tarea>/<ia>.md` (el Markdown con encabezado de md2docx). Esta carpeta no se publica.
4. Puntuá:
   ```bash
   python3 scripts/evaluar.py evals/resultados/T01/chatgpt.md --palabras 1500 --red
   ```
5. Anotá el puntaje en la tabla de abajo y, aparte, una nota humana de 1 a 10 sobre la calidad del argumento (el script no la mide).

## Qué se mide
| Herramienta | Mide |
|---|---|
| `evaluar.py` | Estructura, citas↔referencias, pendientes, datos sin fuente, estilo, extensión, fuentes reales y afirmaciones respaldadas |
| Nota humana | Profundidad, originalidad, coherencia del argumento |

## Resultados
| Tarea | IA / modelo | Fecha | Puntaje evaluar.py | Nota humana | Observaciones |
|---|---|---|---|---|---|
| T01 | Claude (Claude Code + skill) | | | | |
| T01 | ChatGPT (Proyecto + prompt universal) | | | | |
| T01 | Gemini (Gem) | | | | |
| T01 | Grok | | | | |
| T01 | Perplexity (Espacio) | | | | |
