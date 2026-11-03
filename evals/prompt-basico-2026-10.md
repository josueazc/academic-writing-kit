# Prueba con prompt básico (octubre de 2026)

Cinco personas usaron el kit pidiendo solo el tema, sin responder el cuestionario ni dar sus datos. Se revisaron los PDF y Word que entregaron. Los nombres se omiten; cada trabajo se identifica por su tema.

## Resultado por trabajo
| Trabajo | Páginas · fuentes | Lo mejor | Lo que falló |
|---|---|---|---|
| A. Generaciones del K-pop | 27 · 25 | Objetivos → método por objetivo → conclusiones por objetivo; matriz y cronología en anexos; portada con `[COMPLETAR]` | Índice sin números de página; la Tabla 1 mezcla categorías en dos filas; un período del título no coincide con el texto; base de prensa y blogs más que académica |
| B. IA generativa en secundaria | 19 · 4 | Estructura completa con índice paginado; criterios de diseño claros | 3 de 4 fuentes del mismo autor; ninguna fuente de Costa Rica pese a mencionarla; descargos en casi cada párrafo (4,4 por cada 1000 palabras); portada "Muestra elaborada con asistencia de IA" |
| C. Práctica de recuperación | 14 · 6 | Argumento fino, referencias reales con DOI, método de búsqueda documentado | Sin índice; portada "Muestra elaborada con IA / sin afiliación"; nombra el kit y a su autor en la declaración; descargos repetidos (5,7 por cada 1000); fuentes leídas solo por el resumen |
| D. Inteligencia artificial (general) | 19 · 10 | Abarca historia, técnica, ética y regulación con fuentes clave reales | Chips de cita del chat pegados al texto ("Stanford HAI", "NIST", "EUR-Lex +1"); secciones enteras sin citas (salud, Costa Rica); metodología después del desarrollo; "y colaboradores" en vez de "et al."; tema enciclopédico sin acotar; objetivos con verbos bajos (describir, explicar); sin portada ni índice |
| E. IA generativa en la educación | 17 · 4 | El mejor formato: salió por `md2docx.py` con portada (nombre del autor y `[COMPLETAR]`), índice paginado y pie; objetivos de nivel alto bien cerrados; datos exactos según la fuente | 2 de 4 fuentes del mismo autor; cuatro secciones sin citas (andamiaje, detectores, evaluación, gobernanza); sin anexos; mismo tema y casi el mismo corpus que B |

No apareció ninguna fuente inventada: 43 de los 45 DOI y enlaces responden (los otros dos sitios bloquean consultas automáticas). Los libros sin enlace no se comprobaron, y esto confirma que las fuentes existen, no que cada dato esté en ellas.

## Causas en el kit
1. **Sin respuestas al cuestionario, cada IA improvisó la portada**: dos dejaron `[COMPLETAR]` (lo correcto) y tres pusieron "muestra" o nada.
2. **La regla de no exagerar se aplicó de más**: sin un lugar fijo para los límites, la IA los repitió en cada párrafo.
3. **No había mínimo de fuentes por defecto** ni límite de concentración por autor.
4. **Con el mismo pedido, la IA converge en las mismas fuentes**: B y E tratan casi el mismo tema con Bastani et al. (2025) y las guías de UNESCO, sin buscar más.
5. **Nada detectaba lo que queda al copiar desde un chat con búsqueda web** ni las secciones de contenido sin citas.

## Cambios
- `cuestionario-inicial.md`: valores por defecto cuando el usuario no responde.
- `AGENTS.md`, `SKILL.md`, `PROMPT-UNIVERSAL.md`: prompt básico, portada con `[COMPLETAR]`, límites una sola vez, chips de cita, citas en cada sección de contenido, metodología antes del desarrollo.
- `revisar.py`: avisa de portada de "muestra", mención del kit, chips de cita, descargos repetidos, secciones de contenido sin citas, pocas fuentes, un autor con el 40 % o más de las referencias, metodología fuera de lugar y "y colaboradores".
- `evals/tareas.md`: T11 repite esta prueba.
