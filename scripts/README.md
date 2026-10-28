# Herramientas

Python 3.8+ sin dependencias externas. Funcionan en macOS, Windows, Linux y en el intérprete de código de ChatGPT, Gemini o Claude.

## md2docx.py — de Markdown a Word con formato APA 7

```bash
python3 scripts/md2docx.py trabajo.md            # crea trabajo.docx
python3 scripts/md2docx.py trabajo.md -o final.docx
```

### Frontmatter (todo opcional; valores por defecto = APA 7 de estudiante)
```yaml
---
titulo: "Título del Trabajo"
autores: [Nombre Apellido, Nombre Apellido]
afiliacion: Escuela de X, Universidad Y
curso: ABC-101 Nombre del curso
docente: Prof. Nombre Apellido
fecha: 15 de mayo de 2026
fuente: Times New Roman      # o Arial, Calibri…
tamano: 12
interlineado: 2              # 1.5 si la institución lo pide
alineacion: izquierda        # o justificada
margen_cm: 2.54
sangria_cm: 1.27
numero_pagina: arriba-derecha  # abajo-derecha | abajo-centro | ninguno
numerar_portada: true
portada: apa                 # o ninguna (si la institución da su propia portada)
toc: false                   # true = tabla de contenidos automática
repetir_titulo: true         # APA: título repetido en la primera página del texto
salto_por_seccion: false     # true = cada título de nivel 1 en página nueva (tesis)
papel: carta                 # o a4
---
```

### Sintaxis del cuerpo
| Markdown | Resultado en Word |
|---|---|
| `# Título` … `### Título` | Títulos APA nivel 1–3 (estilos Título 1–3, aparecen en la tabla de contenidos) |
| `#### Título` + párrafo en la línea siguiente | Nivel 4: título en negrita en la misma línea del párrafo |
| `##### Título` + párrafo | Nivel 5: negrita cursiva en línea |
| Párrafo normal | Sangría de primera línea, interlineado configurado |
| `# Introducción` (primer título) | Se reemplaza por el título del trabajo (APA) |
| `# Resumen` / `# Abstract` | Página nueva, párrafo sin sangría |
| `# Referencias` | Página nueva, sangría francesa |
| `**Tabla 1**` + `*Título*` + tabla con `\|` + `*Nota.* …` | Tabla APA (solo líneas horizontales) |
| `**Figura 1**` + `*Título*` + `![alt](imagen.png)` + `*Nota.* …` | Figura APA (PNG o JPG, ruta relativa al .md) |
| `> texto` | Cita en bloque (40+ palabras) |
| `- item` / `1. item` | Listas |
| `**negrita**`, `*cursiva*` | Igual en Word |
| `[SALTO]` | Salto de página |

Ejemplo completo: [07-plantillas/ejemplo-md2docx.md](../07-plantillas/ejemplo-md2docx.md).

Si `toc: true`, Word pregunta al abrir si actualizar los campos: aceptá y aparece la tabla de contenidos con números de página.

## fuentes.py — buscar fuentes reales y obtener la referencia APA

```bash
python3 scripts/fuentes.py buscar "tema" -n 10 --desde 2018 --idioma es --abiertos
python3 scripts/fuentes.py buscar "tema" --formato md > trabajos/x/fuentes.md
python3 scripts/fuentes.py doi 10.xxxx/yyyy
```
Consulta OpenAlex (y Crossref si falla). Ver [02-citas-y-referencias/fuentes-y-busqueda.md](../02-citas-y-referencias/fuentes-y-busqueda.md). Revisá a mano: apellidos compuestos, mayúsculas del título y cursivas.

## revisar.py — verificación automática antes de entregar

```bash
python3 scripts/revisar.py trabajo.md
python3 scripts/revisar.py trabajo.docx --rubrica rubrica.md --palabras 2500 -o revisiones/2026-11-01.md
```
Lee .md o .docx (cualquier .docx con estilos de título de Word, no solo los de md2docx) y reporta en **Crítico / Importante / Menor**:

| Revisa | Severidad |
|---|---|
| Cita en el texto sin referencia (parentéticas, narrativas, "et al.", siglas como `(ICT, 2024)` resueltas con `[ICT]`) | Crítico |
| `[COMPLETAR]`, `[VERIFICAR]`, `[FUENTE]`, `TODO` sin resolver | Crítico |
| Criterio de la rúbrica sin sección que lo cubra | Crítico |
| Referencia que nadie cita · año distinto entre cita y referencia · orden alfabético · fechas "(6 de marzo de 2024)" | Importante |
| Sección corta para su peso en la rúbrica · extensión total fuera de lo pedido | Importante |
| Artefactos (`\%`, `**`, `#`) en el .docx | Importante |
| Muletillas de IA (importante si superan 4 por cada 1000 palabras) | Menor / Importante |
| Apellidos casi iguales · oraciones de más de 40 palabras | Menor |

**Rúbrica:** un Markdown con una tabla. Columnas reconocidas: `ID`, `Criterio`, `Puntaje`/`Puntos`/`Peso`, y opcional `Sección` (si no está, se empareja por palabras del título). Criterios de ortografía, formato, APA o referencias se marcan como transversales.
```markdown
| ID | Criterio | Puntaje | Sección |
|---|---|---|---|
| C1 | Justificación del problema | 10 | Justificación |
| C2 | Marco teórico con autores actuales | 20 | |
| C3 | Referencias en APA 7 | 5 | |
```
Sale con código 1 si hay críticos. No juzga la calidad del argumento ni si la fuente dice lo que se afirma: eso es trabajo del [revisor](../08-agentes/prompts/5-revisor.md).

Ideas tomadas de [rubric-driven](https://github.com/JosephBano/rubric-driven) y [RefMatch](https://github.com/zhongzhengshen/RefMatch-Skill) (MIT); implementación propia sin dependencias.
