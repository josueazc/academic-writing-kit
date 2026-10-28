---
tipo: guia
tema: formato
---
# Procesadores de texto: Word, Google Docs, LibreOffice, Pages, Overleaf

`scripts/md2docx.py` genera un **.docx** con estilos reales (Normal, Título 1–5, Referencia, Cita en bloque). Ese archivo se abre en todos los programas de abajo; lo que cambia es cómo se ve y cómo se ajusta.

## Qué programa usar
| Programa | Ventajas | Cuidado con |
|---|---|---|
| **Microsoft Word** (Windows, Mac, web) | El estándar de las universidades; estilos, tabla de contenidos, títulos de figura y citas completas | Word web no tiene todas las opciones de tabla de contenidos |
| **Google Docs** | Colaboración en tiempo real, historial, comentarios; gratis | Estilos limitados (no hay estilo "Referencia"), sangría francesa manual, solo 6 niveles de título; fuentes distintas cambian la paginación |
| **LibreOffice Writer** | Gratis y completo; exporta PDF de calidad | La paginación puede variar levemente al volver a Word |
| **Apple Pages** | Integrado en Mac/iPad | Pierde parte de los estilos al importar/exportar .docx; revisá la tabla de contenidos |
| **Overleaf (LaTeX)** | Ideal para matemáticas, ingeniería y tesis largas; plantillas APA (`apa7`), IEEE | Curva de aprendizaje; el docente puede pedir .docx |
| **Notion / Obsidian** | Para tomar notas y borradores | No sirven para la entrega final: exportá a .docx |

## Google Docs
**Importar el .docx de md2docx:** Drive → Nuevo → Subir archivo → abrir con Google Docs (o activar "Convertir archivos subidos" en la configuración de Drive). Los títulos llegan como Título 1–5 y la tabla de contenidos se puede insertar.

**Ajustes después de importar**
1. Revisá que Archivo → Configuración de página tenga tamaño Carta y márgenes 2.54 cm.
2. Formato → Estilos de párrafo: si un título cambió de aspecto, ajustalo una vez y "Actualizar Título 1 para que coincida".
3. Referencias: seleccioná la lista → Formato → Alinear y aplicar sangría → Opciones de sangría → Especial: **Francesa 1.27 cm**.
4. Números de página: Insertar → Números de página (arriba a la derecha).
5. Índice: Insertar → Índice → con números de página.

**Escribir APA directamente en Docs:** ver [los pasos de configuración](#google-docs-1).

**Complementos útiles:** Zotero tiene conector para Google Docs (insertar citas y bibliografía); la herramienta "Explorar/Citas" de Docs genera APA pero revisala siempre.

**Exportar:** Archivo → Descargar → .docx o PDF. Si el docente abre el .docx en Word, usá fuentes estándar (Times New Roman, Arial, Calibri) para que no cambie la paginación.

## Microsoft Word
- **Windows/Mac:** configuración completa en [los pasos de configuración](#microsoft-word-1).
- **Citas integradas:** Referencias → Estilo: APA séptima edición → Insertar cita / Bibliografía. Funciona, pero el formato en español suele necesitar correcciones; Zotero (complemento de Word) es más confiable.
- **Word web (gratis con correo universitario):** abre el .docx de md2docx sin problemas; la tabla de contenidos se actualiza desde Referencias → Tabla de contenido → Actualizar.
- **Al abrir un .docx de md2docx con `toc: true`,** Word pregunta si actualizar campos: aceptá.

## LibreOffice Writer
- Abrí el .docx directamente. Estilos: F11 (panel de estilos).
- Tabla de contenidos: Insertar → Índice y tablas → Índice.
- Sangría francesa: Formato → Párrafo → Sangría antes del texto 1.27 cm, primera línea −1.27 cm.
- Exportar PDF: Archivo → Exportar como PDF (marcar "PDF/A" si piden archivo de preservación).
- Zotero también tiene complemento para LibreOffice.

## Apple Pages
- Abrí el .docx con Pages; revisá títulos y tabla de contenidos (Documento → Tabla de contenido).
- Para entregar en .docx: Archivo → Exportar a → Word. Verificá el resultado abriéndolo en Word o Google Docs.
- Mejor práctica: si el docente pide .docx, terminá en Word o Docs, no en Pages.

## Overleaf / LaTeX
- Clase `apa7` (`\documentclass[stu]{apa7}`) para APA de estudiante; `IEEEtran` para IEEE; plantillas de tesis de universidades en la galería de Overleaf.
- Bibliografía con BibLaTeX (`style=apa`) y un archivo `.bib` exportado desde Zotero.
- Si tenés que entregar .docx, convertí con Pandoc o rehacé el formato; el resultado no es perfecto.

## Pandoc y Quarto (citas automáticas desde Zotero)
Ver [pandoc-y-quarto.md](pandoc-y-quarto.md): escribís `[@castells2012]` y las citas y la lista de referencias en APA salen solas.

## Comprobación final en cualquier programa
1. Exportá a PDF y revisá página por página.
2. `python3 scripts/revisar.py trabajo.docx` (lee .docx de Word, Docs, LibreOffice o Pages).
3. Abrí el .docx en otro programa si el docente usa uno distinto al tuyo.

## Configurar los estilos una sola vez (paso a paso)

La clave es **modificar estilos**, no formatear a mano. Así la tabla de contenidos, los títulos y la consistencia salen solos.

### Microsoft Word
1. **Diseño → Márgenes → Márgenes personalizados**: 2.54 cm los cuatro (o los del docente). Tamaño: Carta.
2. **Inicio → Estilos → Normal → Modificar**: fuente Times New Roman 12; Formato → Párrafo: sangría especial "Primera línea" 1.27 cm, espaciado anterior/posterior 0 pt, interlineado Doble (o 1.5), alineación Izquierda (o Justificada si lo piden). Marcar "Nuevos documentos basados en esta plantilla" si querés reutilizar.
3. **Título 1**: Normal + negrita, centrado, sin sangría, color automático (negro), 12 pt. **Título 2**: negrita, izquierda, sin sangría. **Título 3**: negrita cursiva, izquierda. Título 4/5: aplicá manualmente negrita (y cursiva) al inicio del párrafo.
4. Para cada Título: Párrafo → Líneas y saltos → "Conservar con el siguiente". Para Título 1 además "Salto de página anterior".
5. **Número de página**: Insertar → Número de página → Principio de página → Derecha (APA) o donde indique la institución. Si la portada no se numera: Diseño de encabezado → "Primera página diferente".
6. **Referencias**: crear estilo "Referencias" basado en Normal, sangría Francesa 1.27 cm.
7. **Tabla de contenido**: Referencias → Tabla de contenido → Tabla personalizada → 3 niveles.
8. **Títulos de tabla/figura**: Referencias → Insertar título (permite generar "Lista de figuras").
9. Guardar como plantilla (.dotx) para el próximo trabajo.

### Google Docs
1. Archivo → Configuración de página: Carta, márgenes 2.54 cm. "Establecer como predeterminado".
2. Escribí un párrafo con el formato normal y luego **Formato → Estilos de párrafo → Texto normal → Actualizar "Texto normal" para que coincida**. Igual con Título 1, 2, 3.
3. Sangría: Formato → Alinear y aplicar sangría → Opciones de sangría → Primera línea 1.27 cm (referencias: Francesa 1.27 cm).
4. Interlineado: Formato → Interlineado y espaciado de párrafo → Doble; quitar "Agregar espacio antes/después".
5. Número de página: Insertar → Números de página (elegí arriba-derecha y, si aplica, sin número en la primera página).
6. Índice: Insertar → Índice → con números de página. Actualizar antes de exportar.
7. Exportar: Archivo → Descargar → PDF. Revisar el PDF (fuentes como Lexend o Montserrat se ven distintas en Word: usá Times/Calibri/Arial si el docente abre el .docx).

### Antes de exportar
- Actualizar tabla de contenidos.
- Mostrar marcas de formato (¶) para cazar dobles espacios, Tabs y líneas vacías.
- Quitar resaltados, comentarios y control de cambios.
- Exportar a PDF y revisar cada página (figuras, tablas partidas, páginas en blanco).
