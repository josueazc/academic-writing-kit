---
name: escritura-academica
description: Redacta, cita en APA 7, formatea como .docx y revisa trabajos académicos en español (ensayos, proyectos de investigación, proyectos aplicados, artículos, informes, monografías, TFG/tesis) a partir de un tema o información en bruto, adaptándose a cualquier rúbrica. Usar cuando el usuario pida hacer, estructurar, citar, formatear o revisar un trabajo escrito académico, una tesis, un ensayo o referencias APA.
---

# Escritura académica

Base de conocimiento + herramientas para convertir un tema o información en un trabajo académico completo, citado y en Word. Las reglas completas están en [AGENTS.md](AGENTS.md); este archivo es la entrada corta. Cargá cada guía **solo cuando la necesites**.

## Flujo
1. **Tipo de trabajo** → abrí su estructura en `03-estructuras/`. ¿Hay rúbrica? → `01-formato/adaptador-de-rubricas.md`.
2. **Planear** con `08-agentes/prompts/1-planificador.md`: perspectivas → objetivos (Bloom: `06-bloom/taxonomia-bloom.md`) → esquema → mapa afirmación-evidencia. Pedir aprobación.
3. **Fuentes reales**: `python3 scripts/fuentes.py buscar "<tema>" --formato md` y `python3 scripts/fuentes.py doi <DOI>`. Más índices en `02-citas-y-referencias/fuentes-y-busqueda.md`.
4. **Redactar** sección por sección con `04-secciones/<sección>.md` y `05-redaccion/estilo-academico.md`.
5. **Citar** con `02-citas-y-referencias/apa7-citas.md` y `apa7-referencias.md` (otro estilo: `01-formato/perfiles/otros-estilos.md`).
6. **Revisar**: `python3 scripts/revisar.py trabajo.md [--rubrica rubrica.md] [--palabras N]` y luego `08-agentes/prompts/5-revisor.md`. Corregir todo lo crítico.
7. **Generar Word**: `python3 scripts/md2docx.py trabajo.md` (sintaxis en `scripts/README.md`).

## Reglas duras
- Nunca inventar fuentes, DOI, URL, cifras, citas ni resultados: `[VERIFICAR]` / `[COMPLETAR: …]`.
- La rúbrica o reglamento del usuario manda sobre APA 7.
- Impersonal, registro académico, sin muletillas de IA (`05-redaccion/muletillas-de-ia.md`).
- Conclusiones y recomendaciones por objetivo, sin información nueva.

## Dónde está cada cosa
Índice completo: [00-indice.md](00-indice.md).
