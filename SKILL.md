---
name: escritura-academica
description: Redacta, cita (APA 7, MLA, Chicago, Vancouver, IEEE), formatea para Word o Google Docs y revisa trabajos académicos en español de cualquier materia (ensayos, proyectos, revisiones de literatura, artículos, estudios de caso, informes, anteproyectos, TFG/tesis) a partir de un tema o información en bruto, adaptándose a cualquier rúbrica; también puede guiar como mentor sin escribir por el usuario. Usar cuando el usuario pida hacer, estructurar, citar, formatear o revisar un trabajo escrito académico, una tesis, un ensayo o referencias.
---

# Escritura académica

Base de conocimiento + herramientas para convertir un tema o información en un trabajo académico completo, citado y en Word. Las reglas completas están en [AGENTS.md](AGENTS.md); este archivo es la entrada corta. Cargá cada guía **solo cuando la necesites**.

## Paso 0 — Preguntar primero
Antes de escribir, hacé el cuestionario de `07-plantillas/cuestionario-inicial.md` (usá preguntas con opciones si tu herramienta las tiene): tipo de trabajo, ¿trabajo escrito completo?, formato, secciones a incluir o quitar, extensión y datos de portada (o leé `mi-perfil.yaml`). Un **trabajo escrito completo** lleva portada completa con los datos del usuario, tabla de contenidos, número de página en el pie, objetivos, marco teórico, marco metodológico, conclusiones, recomendaciones, referencias y anexos (`03-estructuras/trabajo-escrito-completo.md`).

## Flujo
1. **Tipo de trabajo** → estructura en `03-estructuras/`. **Materia** → `12-materias/guia-por-area.md` (estilo de cita y convenciones). ¿Hay rúbrica? → `01-formato/adaptador-de-rubricas.md`. ¿Quiere aprender en vez de recibir el texto? → `08-agentes/prompts/7-mentor.md`.
2. **Planear** con `08-agentes/prompts/1-planificador.md`: perspectivas → objetivos (Bloom: `06-bloom/taxonomia-bloom.md`) → esquema → mapa afirmación-evidencia. Pedir aprobación.
3. **Fuentes reales**: `python3 scripts/fuentes.py buscar "<tema>" --todas --formato md` y `python3 scripts/fuentes.py doi <DOI>`. Más índices en `02-citas-y-referencias/fuentes-y-busqueda.md`.
4. **Redactar** sección por sección con `04-secciones/<sección>.md` y `05-redaccion/estilo-academico.md`.
5. **Citar** con `02-citas-y-referencias/tipos-de-citas.md` (directa/indirecta, parentética/narrativa, corta/bloque, casos especiales), `apa7-referencias.md` y `apa7-referencias-por-tipo.md` (otro estilo: `01-formato/perfiles/otros-estilos.md`).
6. **Revisar**: `python3 scripts/verificar_referencias.py trabajo.md` (¿existen los DOI/URL?), `python3 scripts/verificar_afirmaciones.py trabajo.md -o revisiones/matriz.md` (leé cada fila: ¿la fuente respalda la frase? ¿aparecen los números?), `python3 scripts/revisar.py trabajo.md [--rubrica rubrica.md|.docx] [--palabras N] [--anterior previa.md]` y luego `08-agentes/prompts/5-revisor.md`. Corregir todo lo crítico.
7. **Generar Word y PDF**: `python3 scripts/md2docx.py trabajo.md --pdf` (sintaxis en `scripts/README.md`; `modo: completo` para trabajos completos; gráficos con `scripts/figuras.py`). Puntaje final: `python3 scripts/evaluar.py trabajo.md --palabras N --red`. Para Google Docs, LibreOffice, Pages u Overleaf: `01-formato/procesadores-de-texto.md`.

## Otros modos
Mentor (`7-mentor`), revisión por pares (`8-revision-por-pares`), responder correcciones (`9-responder-correcciones`), integrar apuntes (`10-integrar-apuntes`) en `08-agentes/prompts/`; revista o congreso: `03-estructuras/publicar-en-revista.md`; inglés: `05-redaccion/escribir-en-ingles.md`; seguimiento de entregas: `scripts/tareas.py`.

## Reglas duras
- Todo lo citado o afirmado como hecho debe ser real y verificado; nunca inventar fuentes, DOI, URL, cifras, citas ni resultados: `[VERIFICAR]` / `[COMPLETAR: …]`. Los supuestos se declaran como supuestos.
- No prometer pasar detectores de IA ni intentar engañarlos; escribir con datos concretos, fuentes reales y voz propia del usuario (`05-redaccion/voz-propia-y-detectores.md`).
- La rúbrica o reglamento del usuario manda sobre APA 7.
- Impersonal, registro académico, sin muletillas de IA (`05-redaccion/muletillas-de-ia.md`).
- Conclusiones y recomendaciones por objetivo, sin información nueva.

## Dónde está cada cosa
Índice completo: [00-indice.md](00-indice.md).
