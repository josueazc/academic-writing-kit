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
Lee .md, .docx (cualquier .docx con estilos de título de Word, no solo los de md2docx) o **.pdf** (con `pdftotext` o, en macOS, sin instalar nada; en un PDF los títulos se deducen y no se ven cursivas ni formato de página) y reporta en **Crítico / Importante / Menor**:

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
| Objetivos: verbo no medible, verbos repetidos, objetivo específico sin procedimiento en la metodología o sin conclusión | Importante |
| Cita o cifra que aparece por primera vez en Conclusiones | Importante |
| Verbo *analizar* o superior y desarrollo con pocos conectores de análisis (posible texto descriptivo) | Importante (pista) |
| Salto de nivel de título (del 1 al 3) · un solo subtítulo dentro de una sección | Importante / Menor |
| Forma APA de cada referencia: fecha, «Apellido, A.», «et al.», DOI viejo, «Recuperado de», cursivas (.md), punto final | Importante / Menor |
| (.docx) márgenes, fuente y tamaño, interlineado, espacio entre párrafos, sangrías, sangría francesa, número de página, títulos hechos con negrita | Importante / Menor |

**Rúbrica:** un Markdown con una tabla. Columnas reconocidas: `ID`, `Criterio`, `Puntaje`/`Puntos`/`Peso`, y opcional `Sección` (si no está, se empareja por palabras del título). Criterios de ortografía, formato, APA o referencias se marcan como transversales.
```markdown
| ID | Criterio | Puntaje | Sección |
|---|---|---|---|
| C1 | Justificación del problema | 10 | Justificación |
| C2 | Marco teórico con autores actuales | 20 | |
| C3 | Referencias en APA 7 | 5 | |
```
Sale con código 1 si hay críticos. Si el trabajo tiene objetivos y no encuentra en la carpeta del trabajo (o en `revisiones/`) un `## Veredicto por objetivo` completado por el revisor, avisa y agrega la plantilla al final del reporte. El reporte incluye una **matriz de coherencia por objetivo** (verbo, nivel de Bloom, si aparece en metodología y en conclusiones).

**Qué no puede decidir:** si el texto realmente analiza, si el método sirve para cada objetivo, si los específicos cubren el general o si la conclusión sale del desarrollo. Esas son pistas; el veredicto lo da el [revisor](../08-agentes/prompts/5-revisor.md), que es obligatorio. Tampoco juzga si la fuente dice lo que se afirma (`verificar_afirmaciones.py`).

Los objetivos se leen del texto (frase "objetivo general…" y la lista numerada tras "objetivos específicos", o secciones con esos títulos) o del encabezado:
```yaml
objetivo_general: Analizar …
objetivos:
  - Comparar …
  - Clasificar …
```
Opciones para .docx según la rúbrica: `--fuente Arial --interlineado 1.5 --margen 3 --justificado`.

### Por separado
```bash
python3 scripts/coherencia.py trabajo.md        # objetivos, cobertura, conclusiones, títulos y matriz
python3 scripts/apa_referencias.py trabajo.md   # forma APA de cada referencia
python3 scripts/formato_docx.py trabajo.docx    # formato de página de cualquier .docx (Word, Google Docs, LibreOffice)
```

Ideas tomadas de [rubric-driven](https://github.com/JosephBano/rubric-driven) y [RefMatch](https://github.com/zhongzhengshen/RefMatch-Skill) (MIT); implementación propia sin dependencias.

## Novedades
- `md2docx.py`: `numerar_titulos: true` numera títulos (1., 1.1, 1.1.1) para ingeniería, informes técnicos e IEEE (no numera Resumen, Referencias ni Anexos). El .docx incluye además los estilos que usa Pandoc (`Body Text`, `First Paragraph`, `Bibliography`), así que sirve como `--reference-doc` ([pandoc-y-quarto.md](../01-formato/pandoc-y-quarto.md)).
- `fuentes.py buscar … --todas`: combina OpenAlex y Crossref y quita duplicados por DOI.
- `revisar.py`: detecta citas textuales sin página o párrafo, citas de 40+ palabras entre comillas (deben ir en bloque) y exceso de citas textuales (> 20 % del texto).

## verificar_referencias.py — ¿existen las fuentes?

```bash
python3 scripts/verificar_referencias.py trabajo.md        # o trabajo.docx
python3 scripts/verificar_referencias.py trabajo.docx -o revisiones/referencias.md
```
Para cada referencia: si tiene **DOI**, lo consulta en Crossref y avisa si no existe (🔴, posible referencia inventada) o si pertenece a otro trabajo o año (🟠); si tiene **URL**, comprueba que responda (404 = enlace roto); si no tiene ninguno, la busca en Crossref y sugiere el DOI cuando coinciden título, autor y año. Libros, leyes y sitios locales suelen no estar en Crossref: quedan como "verificar a mano". Necesita internet.

## tareas.py — seguimiento de entregas

```bash
python3 scripts/tareas.py nueva ensayo-ia --fecha 2026-11-15 --tipo ensayo --tema "IA en educación" --materia Educación
python3 scripts/tareas.py estado
```
Crea `trabajos/<nombre>/` con brief, rúbrica y carpeta de revisiones, y lista los trabajos por fecha de entrega con su etapa y los críticos de la última revisión (⚠️ a 3 días o menos). `trabajos/` no se publica.

## Más opciones nuevas
- `revisar.py --rubrica rubrica.docx`: lee la rúbrica directo del Word del docente (primera tabla).
- `revisar.py --anterior revisiones/2026-11-01.md`: compara con la revisión anterior (resueltos, nuevos, siguen).
- `fuentes.py buscar … --descargar carpeta/`: baja los PDF de acceso abierto (solo PDF reales).

**PDF con Word:** si Word no responde (casi siempre por un diálogo abierto), `--pdf` se corta a los 2,5 minutos y deja el .docx listo; `MD2DOCX_PDF_TIMEOUT=300` da más tiempo.

## Pruebas
`python3 -m unittest discover -s tests` (sin red). Corren solas en GitHub Actions en cada push.

## Trabajo escrito completo (md2docx)
Con `modo: completo` en el encabezado se activan: **portada completa** (institución, facultad, escuela, carrera, curso, título, subtítulo, tipo de trabajo, autores, docente, grupo, lugar, fecha y `logo` opcional), **tabla de contenidos** con los títulos ya escritos (Word agrega los números de página; `--pdf` los actualiza solo), **número de página en el pie** (portada sin número), cada sección principal en página nueva y cada `## Anexo …` en página nueva.

Otras opciones nuevas: `pie_texto: "Título corto"` (texto a la izquierda del pie), `comillas: inglesas | latinas | rectas` (convierte "…" en “…” o «…», sin tocar URLs), `secciones: [...]` (lista que `revisar.py` exige), y los valores entre comillas se respetan tal cual ("01").

`mi-perfil.yaml` (copiá `07-plantillas/perfil-ejemplo.yaml`): datos fijos de portada y preferencias; md2docx los lee solo desde la carpeta del trabajo, sus superiores o la raíz del kit. No se publica.

`python3 scripts/md2docx.py trabajo.md --pdf`: genera también el PDF con LibreOffice o, en macOS, con Microsoft Word (actualiza la tabla de contenidos antes de exportar).

## verificar_afirmaciones.py — matriz de lectura
```bash
python3 scripts/verificar_afirmaciones.py trabajo.md -o revisiones/matriz-de-lectura.md
```
Para cada oración con cita busca, en el resumen (OpenAlex) y en el texto completo de acceso abierto de la fuente, la oración más parecida (compara raíces de palabras, así funciona entre español e inglés) y comprueba que los **números** de la afirmación estén en la fuente. Veredictos: ✅ probable respaldo · 🟡 revisar · 🔴 sin respaldo aparente (cifra que no aparece) · ⚪ no verificable (sin DOI o sin texto). Es una ayuda: cada fila trae la evidencia para que la IA o vos confirmen.

## figuras.py — gráficos con datos reales
```bash
python3 scripts/figuras.py barras --datos "Sí:29.3,No:70.7" --titulo "…" --eje-y "Porcentaje" --nota "Elaboración propia (n = 249)." -o figuras/fig1.png
```
Tipos: `barras`, `barras-h`, `pastel`, `lineas` (con `--csv`, `--x`, `--y`). Imprime el bloque de figura APA para pegar en el Markdown. Necesita `python3 -m pip install matplotlib`.

## evaluar.py — puntaje 0–100
```bash
python3 scripts/evaluar.py trabajo.md --palabras 2500 --red
```
Estructura, citas y referencias, pendientes y datos sin fuente, estilo, extensión y (con `--red`) fuentes reales y afirmaciones respaldadas. Mide control de calidad, no la calidad del argumento.

## revisar.py: novedades
- **Dato sin cita**: cifras y porcentajes sin fuente en la misma oración (excepto en métodos y resultados propios).
- **Secciones exigidas**: `--secciones "Objetivos,Marco teórico,…"` o la lista `secciones:` del encabezado.
- `--ortografia`: ortografía y gramática con LanguageTool. **Envía el texto a api.languagetool.org**; usalo solo si estás de acuerdo.
