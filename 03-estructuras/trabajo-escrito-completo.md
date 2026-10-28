---
tipo: estructura
---
# "Trabajo escrito completo": qué debe incluir siempre

Cuando el usuario pide un **trabajo escrito completo**, la IA entrega un documento listo para presentar, no solo el texto. Antes de empezar, pasa por el [cuestionario inicial](../07-plantillas/cuestionario-inicial.md).

## Lista de entrega
| Elemento | Cómo se resuelve | Herramienta |
|---|---|---|
| **Portada completa** con los datos del usuario | Institución, facultad/escuela, carrera, curso, título y subtítulo, tipo de trabajo, autores (y carné), docente, grupo, lugar y fecha; logo opcional | `modo: completo` en md2docx + `mi-perfil.yaml` |
| **Tabla de contenidos** real | Generada desde los títulos, con números de página al exportar | `toc: true` (incluido en `modo: completo`); `--pdf` la actualiza en Word |
| **Número de página en el pie** | Abajo a la derecha, portada sin número; texto opcional a la izquierda (título corto) | `numero_pagina: abajo-derecha`, `pie_texto:` |
| **Secciones del tipo de trabajo** | Por defecto según la tabla del cuestionario: objetivos, marco teórico, marco metodológico, conclusiones, recomendaciones, referencias, anexos… | `secciones:` en el encabezado; `revisar.py` avisa si falta alguna |
| **Cada sección principal en página nueva** | | `salto_por_seccion: true` (incluido) |
| **Anexos** | Instrumentos, tablas extensas, capturas, cadenas de búsqueda; cada anexo en página nueva con letra | `## Anexo A Título` dentro de `# Anexos` |
| **Tablas y figuras APA** | Con número, título, nota y fuente | md2docx, `figuras.py` |
| **Todo verificado** | Fuentes existentes y afirmaciones respaldadas | `verificar_referencias.py`, `verificar_afirmaciones.py` |
| **Word y PDF** | | `md2docx.py trabajo.md --pdf` |

## Encabezado mínimo del Markdown
```yaml
---
modo: completo
institucion: …        # desde mi-perfil.yaml
facultad: …
carrera: …
curso: "COD-101 Nombre del curso"
titulo: "…"
subtitulo: "…"
tipo_trabajo: "Proyecto de investigación"
autores: ["Nombre Apellido — Carné 000000"]
docente: "Prof. …"
grupo: "01"
lugar: "San José, Costa Rica"
fecha: "15 de noviembre de 2026"
pie_texto: "Título corto"
secciones: [Resumen, Introducción, Objetivos, Justificación, Marco teórico, Marco metodológico, Conclusiones, Recomendaciones, Referencias, Anexos]
---
```

## Antes de entregar (en este orden)
```bash
python3 scripts/verificar_referencias.py trabajo.md
python3 scripts/verificar_afirmaciones.py trabajo.md -o revisiones/matriz-de-lectura.md
python3 scripts/revisar.py trabajo.md --palabras N
python3 scripts/evaluar.py trabajo.md --palabras N --red
python3 scripts/md2docx.py trabajo.md --pdf
```
Ningún 🔴 puede quedar abierto, salvo los `[COMPLETAR]` que solo el usuario puede llenar (y se le informan).
