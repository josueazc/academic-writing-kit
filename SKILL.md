---
name: escritura-academica
description: Redacta, cita (APA 7, MLA, Chicago, Vancouver, IEEE), formatea para Word o Google Docs y revisa trabajos académicos en español de cualquier materia (ensayos, proyectos, revisiones de literatura, artículos, estudios de caso, informes, anteproyectos, TFG/tesis) a partir de un tema o información en bruto, adaptándose a cualquier rúbrica; también puede guiar como mentor sin escribir por el usuario. Usar cuando el usuario pida hacer, estructurar, citar, formatear o revisar un trabajo escrito académico, una tesis, un ensayo o referencias.
---

# Escritura académica

Base de conocimiento + herramientas para convertir un tema o información en un trabajo académico completo, citado y en Word. Las reglas completas están en [AGENTS.md](AGENTS.md); este archivo es la entrada corta. Cargá cada guía **solo cuando la necesites**.

## Flujo
1. **Tipo de trabajo** → estructura en `03-estructuras/`. **Materia** → `12-materias/guia-por-area.md` (estilo de cita y convenciones). ¿Hay rúbrica? → `01-formato/adaptador-de-rubricas.md`. ¿Quiere aprender en vez de recibir el texto? → `08-agentes/prompts/7-mentor.md`.
2. **Planear** con `08-agentes/prompts/1-planificador.md`: perspectivas → objetivos (Bloom: `06-bloom/taxonomia-bloom.md`) → esquema → mapa afirmación-evidencia. Pedir aprobación.
3. **Fuentes reales**: `python3 scripts/fuentes.py buscar "<tema>" --todas --formato md` y `python3 scripts/fuentes.py doi <DOI>`. Más índices en `02-citas-y-referencias/fuentes-y-busqueda.md`.
4. **Redactar** sección por sección con `04-secciones/<sección>.md` y `05-redaccion/estilo-academico.md`.
5. **Citar** con `02-citas-y-referencias/tipos-de-citas.md` (directa/indirecta, parentética/narrativa, corta/bloque, casos especiales), `apa7-referencias.md` y `apa7-referencias-por-tipo.md` (otro estilo: `01-formato/perfiles/otros-estilos.md`).
6. **Revisar**: `python3 scripts/revisar.py trabajo.md [--rubrica rubrica.md] [--palabras N]` y luego `08-agentes/prompts/5-revisor.md`. Corregir todo lo crítico.
7. **Generar Word**: `python3 scripts/md2docx.py trabajo.md` (sintaxis en `scripts/README.md`). Para Google Docs, LibreOffice, Pages u Overleaf: `01-formato/procesadores-de-texto.md`.

## Reglas duras
- Nunca inventar fuentes, DOI, URL, cifras, citas ni resultados: `[VERIFICAR]` / `[COMPLETAR: …]`.
- La rúbrica o reglamento del usuario manda sobre APA 7.
- Impersonal, registro académico, sin muletillas de IA (`05-redaccion/muletillas-de-ia.md`).
- Conclusiones y recomendaciones por objetivo, sin información nueva.

## Dónde está cada cosa
Índice completo: [00-indice.md](00-indice.md).
