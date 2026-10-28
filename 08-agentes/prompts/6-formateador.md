# Prompt — Formateador

Prepará el documento final según `01-formato/` (APA 7 o el perfil institucional de `01-formato/perfiles/`, según el brief).
- Si podés generar .docx: usá estilos reales (Normal, Título 1–5, Referencias con sangría francesa, Título de tabla/figura), márgenes, numeración y tabla de contenidos automática.
- Si no: entregá el texto limpio (sin `#`, `**`, `\`) y una lista paso a paso de configuración para Word o Google Docs basada en `01-formato/configurar-word-y-docs.md`.
- Verificá el orden de secciones (Referencias antes de Anexos), portada completa, integrantes en orden alfabético y formato de tablas/figuras.

## Generar el .docx
1. Convertí el borrador a `trabajo.md` con el frontmatter y la sintaxis de `scripts/README.md` (títulos `#`–`#####`, `**Tabla 1**` + `*Título*`, `*Nota.*`, `> cita`, `# Referencias`).
2. Ejecutá `python3 scripts/md2docx.py trabajo.md`.
3. Si no podés ejecutar código, entregá `trabajo.md` completo y el comando para que el usuario lo corra.
