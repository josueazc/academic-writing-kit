---
tipo: plantilla
uso: lo hace la IA ANTES de escribir cualquier trabajo
---
# Cuestionario inicial

**Regla:** antes de planear o redactar, la IA pregunta lo que no sepa de esta lista. Si la herramienta permite preguntas con opciones (por ejemplo, AskUserQuestion en Claude Code), las usa; si no, hace una sola lista numerada y espera. Lo que ya está en el perfil (`mi-perfil.yaml`), en la rúbrica o en el pedido **no se vuelve a preguntar**. Máximo dos rondas de preguntas.

## Ronda 1 — lo indispensable (siempre)
1. **Tipo de trabajo:** ensayo · proyecto de investigación · revisión de literatura · artículo · informe · estudio de caso · anteproyecto · TFG/tesis · otro.
2. **¿Trabajo escrito completo o solo el texto?**
   - *Completo* (por defecto si dice "trabajo escrito completo"): portada completa con sus datos, tabla de contenidos, número de página en el pie, todas las secciones del tipo de trabajo, anexos y Word final.
   - *Solo texto*: el contenido en Markdown, sin portada ni índice.
3. **Formato:** APA 7 · APA 7 con ajustes de la institución · otro estilo (Vancouver, IEEE, MLA, Chicago) · lo que diga la rúbrica (pegarla).
4. **Secciones:** mostrar la lista por defecto del tipo de trabajo (abajo) y preguntar cuáles quitar o agregar.
5. **Extensión:** páginas o palabras (sin contar portada, índice, referencias ni anexos).
6. **Datos de portada:** si no hay perfil guardado — institución, facultad/escuela, carrera, curso (código y nombre), autores (y carné si lo piden), docente, grupo, ciudad, fecha de entrega, logo (opcional).

## Ronda 2 — afinar (solo si aplica o no se dedujo)
7. **Tema exacto y enfoque** (pregunta o postura que quiere defender).
8. **Información propia:** apuntes, datos de encuestas o entrevistas, enlaces, fuentes que ya tiene.
9. **Fuentes:** cantidad mínima, antigüedad máxima, idioma, tipo (solo artículos revisados por pares, libros…).
10. **Detalles de formato:** fuente y tamaño, interlineado (doble/1.5), alineación (izquierda/justificada), márgenes, numeración de títulos, idioma del resumen (¿abstract en inglés?).
11. **Entrega:** Word · Google Docs · PDF.
12. **Modo:** que la IA redacte · modo mentor (que lo guíe sin escribir por él).
13. **Uso de IA permitido** por el docente (para saber si hay que declararlo).

## Secciones por defecto de un "trabajo escrito completo"
| Tipo | Secciones por defecto |
|---|---|
| Proyecto de investigación | Portada · Tabla de contenidos · Resumen · Introducción · Planteamiento del problema · Objetivos (general y específicos) · Justificación · Marco teórico · Marco metodológico · Resultados y análisis · Conclusiones · Recomendaciones · Referencias · Anexos |
| Revisión de literatura | Portada · Tabla de contenidos · Resumen · Introducción (con objetivos) · Método de búsqueda · Desarrollo por temas · Discusión · Conclusiones · Recomendaciones · Referencias · Anexos (cadenas de búsqueda, tabla de extracción) |
| Ensayo | Portada · (Tabla de contenidos si > 8 páginas) · Introducción con tesis · Desarrollo por argumentos · Contraargumento y refutación · Conclusión · Referencias |
| Informe técnico | Portada · Tabla de contenidos · Resumen · Introducción y alcance · Objetivos · Marco teórico/normativo · Metodología · Resultados · Análisis · Conclusiones · Recomendaciones · Referencias · Anexos |
| Estudio de caso | Portada · Tabla de contenidos · Introducción · Descripción del caso · Problema · Marco teórico · Análisis · Alternativas · Recomendación · Plan de implementación · Conclusiones · Referencias · Anexos |

## Al terminar las preguntas
- Guardá los datos de portada en `mi-perfil.yaml` (si el usuario acepta) para no volver a preguntarlos.
- Escribí el `brief.md` del trabajo con todas las respuestas.
- Mostrá el esquema y esperá aprobación antes de redactar.
