---
tipo: guia
tema: agentes
---
# Flujo multiagente

Sirve igual con un solo chat (cambiando de rol en cada paso) o con varios agentes/sesiones en paralelo. Cada rol tiene su prompt en `08-agentes/prompts/`.

```
Brief + rúbrica
   │
   ▼
[1] Planificador ──► esquema.md (títulos, objetivos, extensión por sección)
   │
   ├──► [2] Investigador ──► fuentes.md (fichas verificadas con cita y referencia APA)
   │
   ▼
[3] Redactor (sección por sección, usando esquema + fuentes)
   │
   ▼
[4] Citador APA ──► revisa cita↔referencia, arma la lista
   │
   ▼
[5] Revisor (Bloom + rúbrica + estilo) ──► reporte con cambios
   │
   ▼
[6] Formateador ──► trabajo.md ──► scripts/md2docx.py ──► trabajo.docx
   │
   ▼
Humano: lee, ajusta, verifica fuentes, entrega
```

## Roles
| # | Rol | Entrada | Salida | Archivos de la base que usa |
|---|---|---|---|---|
| 1 | Planificador | brief, rúbrica | `esquema.md` | 03-estructuras, 04-secciones/objetivos, 06-bloom |
| 2 | Investigador | esquema | `fuentes.md` con fichas | scripts/fuentes.py, 02-citas/fuentes-y-busqueda |
| 3 | Redactor | esquema, fuentes | `borrador.md` | 04-secciones, 05-redaccion |
| 4 | Citador | borrador, fuentes | `borrador.md` + `referencias.md` | 02-citas-y-referencias |
| 5 | Revisor | borrador, rúbrica | `revision.md` (checklist + cambios) | 05-redaccion/checklist, 06-bloom |
| 6 | Formateador | borrador final | `trabajo.md` + `.docx` | 01-formato, scripts/md2docx.py |

## Reglas de traspaso
- Cada agente escribe **solo** su archivo de salida y no reescribe el de otro.
- Todo lo no verificado lleva `[VERIFICAR]`; todo lo faltante, `[COMPLETAR]`.
- El investigador es el único que agrega fuentes. El redactor no inventa citas: si necesita una, deja `[FUENTE: tema]`.
- El revisor no redacta de cero: señala ubicación, problema y propuesta.

## Paralelizar
- Investigador por bloque del marco teórico (un agente por tema).
- Redactor por sección independiente (justificación, marco teórico, metodología) una vez que el esquema está fijo.
- Un solo citador y un solo formateador al final, para consistencia.

## Estructura de carpeta por trabajo
```
trabajos/2026-11-ensayo/
  brief.md
  rubrica.md
  esquema.md
  fuentes.md
  borrador.md
  revision.md
  final.docx
```
(La carpeta `trabajos/` está en `.gitignore` para no publicar trabajos personales.)
