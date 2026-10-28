---
tipo: guia
tema: integraciones
---
# Herramientas externas que se combinan bien con esta base

En vez de reinventar lo que otros proyectos hacen muy bien, esta base los recomienda. Todos son open source (licencia MIT o CC0) al momento de la revisión (2026-10-28).

| Herramienta | Qué agrega | Cuándo |
|---|---|---|
| [Zotero](https://www.zotero.org) + conectores de Word, Google Docs y LibreOffice | Biblioteca de fuentes; citas y bibliografía automáticas en cualquier estilo | Siempre que el trabajo tenga más de ~10 fuentes |
| [Zotero MCP](https://github.com/54yyyu/zotero-mcp) | La IA busca, lee (por página), anota y cita desde tu biblioteca de Zotero. Funciona como MCP (Claude Desktop, ChatGPT) o como CLI + skill (Claude Code, Codex, Cursor) | Para que la IA cite solo lo que realmente tenés y leíste |
| [Paper Search MCP](https://github.com/openags/paper-search-mcp) | Búsqueda y descarga de papers en arXiv, PubMed, bioRxiv, Semantic Scholar, Crossref, OpenAlex y más, sin claves | Revisiones de literatura, temas científicos |
| [apaquarto](https://github.com/wjschne/apaquarto) | APA 7 completo en .docx/.pdf/.html desde Quarto | Trabajos con análisis de datos en R/Python |
| [CSL styles](https://github.com/citation-style-language/styles) | Archivos de estilo para APA, Vancouver, IEEE, MLA, Chicago y miles de revistas | Con Pandoc, Quarto o Zotero |
| [Pandoc](https://pandoc.org) | Convierte Markdown a .docx/.pdf/LaTeX con citas automáticas | Ver [pandoc-y-quarto.md](../01-formato/pandoc-y-quarto.md) |

## Instalación rápida (resumen; seguí la documentación de cada proyecto)
```bash
# Zotero MCP
uv tool install zotero-mcp-server     # o: pip install zotero-mcp-server
zotero-mcp setup                      # configura Claude Desktop

# Paper Search MCP (ejemplo con Claude Code)
claude mcp add paper-search -- uvx paper-search-mcp
```
Los comandos y nombres de paquetes pueden cambiar entre versiones: verificá en el README de cada repositorio antes de instalar.

## Cómo encaja con esta base
1. **Buscar**: Paper Search MCP o `scripts/fuentes.py --todas`.
2. **Guardar y leer**: Zotero (con el conector del navegador). La IA consulta con Zotero MCP.
3. **Escribir**: la IA sigue `AGENTS.md` / `SKILL.md`.
4. **Citar**: claves de Zotero + Pandoc, o referencias APA escritas con `02-citas-y-referencias/`.
5. **Formatear**: `scripts/md2docx.py` (o Pandoc con `--reference-doc`).
6. **Revisar**: `scripts/revisar.py`.
