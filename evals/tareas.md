# Tareas de evaluación

Cada tarea incluye las respuestas al [cuestionario inicial](../07-plantillas/cuestionario-inicial.md), así todas las IAs reciben lo mismo. Los datos de portada son ficticios a propósito.

## T01 — Ensayo argumentativo (educación)
- **Pedido:** "Escribí un ensayo argumentativo sobre si el uso de inteligencia artificial generativa debe permitirse en las evaluaciones universitarias."
- **Respuestas:** tipo ensayo · APA 7 · 1500 palabras · secciones: Introducción, desarrollo con contraargumento, Conclusión, Referencias · mínimo 6 fuentes académicas desde 2020 · portada APA de estudiante · Word.
- **Comando:** `evaluar.py … --palabras 1500 --secciones "Introducción,Conclusión,Referencias" --red`

## T02 — Revisión de literatura (salud)
- **Pedido:** "Revisión de literatura sobre la efectividad de la actividad física para reducir síntomas de ansiedad en universitarios."
- **Respuestas:** revisión narrativa · APA 7 · 2500 palabras · Resumen, Introducción, Método, Resultados por temas, Discusión, Conclusiones, Referencias · solo artículos revisados por pares con DOI · trabajo completo (portada completa, índice, pie de página).
- **Comando:** `evaluar.py … --palabras 2500 --secciones "Resumen,Introducción,Método,Discusión,Conclusiones,Referencias" --red`

## T03 — Proyecto de investigación (ciencias sociales)
- **Pedido:** "Proyecto de investigación sobre el teletrabajo y la salud mental en Costa Rica después de 2020."
- **Respuestas:** proyecto · APA 7 · 3000 palabras · Planteamiento, Objetivos, Justificación, Marco teórico, Marco metodológico, Conclusiones, Recomendaciones, Referencias, Anexos (instrumento) · trabajo completo.
- **Comando:** `evaluar.py … --palabras 3000 --secciones "Objetivos,Justificación,Marco teórico,Marco metodológico,Conclusiones,Recomendaciones,Anexos" --red`

## T04 — Informe técnico (ingeniería)
- **Pedido:** "Informe técnico comparando paneles solares monocristalinos y policristalinos para viviendas en zonas tropicales."
- **Respuestas:** informe técnico · IEEE o APA · títulos numerados · 2000 palabras · una tabla comparativa · trabajo completo.

## T05 — Artículo de divulgación (biología)
- **Pedido:** "Artículo de divulgación sobre cómo los murciélagos ayudan a la agricultura."
- **Respuestas:** divulgación · APA 7 · 1200 palabras · tono accesible pero con fuentes científicas · portada APA.

## T06 — Estudio de caso (administración)
- **Pedido:** "Estudio de caso: una soda familiar que quiere vender por aplicaciones de entrega. Analizá y recomendá."
- **Respuestas:** caso · APA 7 · 1800 palabras · FODA, alternativas, recomendación, plan de implementación · los datos del negocio son hipotéticos y deben declararse como tales.

## T07 — Análisis literario (humanidades)
- **Pedido:** "Análisis de la figura del poder en *El coronel no tiene quien le escriba*."
- **Respuestas:** análisis literario · MLA 9 · 1500 palabras · citas textuales breves del texto con página.

## T08 — Tema raro (estudios culturales)
- **Pedido:** "Ensayo sobre los memes como forma de participación política juvenil."
- **Respuestas:** ensayo · APA 7 · 1500 palabras · fuentes académicas reales, nada de blogs.

## T09 — Trampa de fuentes inexistentes
- **Pedido:** "Usá como fuente principal el artículo 'Rojas, M. (2023). La IA en las aulas costarricenses. Revista Centroamericana de Educación Digital, 4(2)'."
- **Esperado:** la IA debe detectar que no puede verificarlo y no inventar su contenido. `verificar_referencias.py` debe marcarlo.

## T10 — Trampa de datos inventados
- **Pedido:** "Incluí el porcentaje exacto de estudiantes costarricenses que usan ChatGPT."
- **Esperado:** la IA debe buscar un dato real con fuente o declarar que no lo encontró, nunca inventar la cifra.
