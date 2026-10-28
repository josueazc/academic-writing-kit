---
tipo: guia
tema: integraciones
---
# Asistentes de chat

**¿Querés el Word ya formateado desde el navegador?** Seguí [navegador.md](navegador.md): GPT personalizado, skill de Claude.ai y Colab para las IAs que no ejecutan Python.

Patrón común: **(1)** crear un proyecto/espacio, **(2)** subir los `.md` de la base (o un ZIP del repo), **(3)** pegar `PROMPT-UNIVERSAL.md` como instrucciones, **(4)** en cada trabajo, mandar el brief + la rúbrica + tu información. Revisado el 2026-10-28; los nombres de menús cambian seguido; si algo no coincide, buscá "instrucciones personalizadas" o "conocimiento/archivos del proyecto".

| Herramienta | Dónde va la base | Busca en la web | Ejecuta Python (→ .docx) | Notas |
|---|---|---|---|---|
| **ChatGPT** (OpenAI) | Proyectos (archivos + instrucciones) o GPT personalizado | Sí | Sí | Pedile: "ejecutá md2docx.py con mi trabajo y dame el .docx". Subí `scripts/md2docx.py`. |
| **Claude** (Anthropic) | Proyectos (conocimiento + instrucciones) | Sí | Sí (análisis/archivos) | Bueno para textos largos y revisión. Claude Code: modo carpeta. |
| **Gemini** (Google) | Gems (instrucciones + archivos) | Sí | Sí | Integra Google Docs: puede exportar directo a Docs. |
| **Grok** (xAI) | Proyectos o instrucciones personalizadas | Sí (web y X) | Según plan | Útil para actualidad; verificá fuentes académicas aparte. |
| **Perplexity** | Espacios (instrucciones + archivos) | Sí, siempre con citas | Limitado | El mejor para **encontrar** fuentes; pedile DOI y abrí cada enlace. Modo Académico filtra artículos. |
| **Microsoft Copilot** (365) | Notebooks o agentes de Copilot con archivos | Sí | Limitado | Dentro de Word puede aplicar estilos al documento abierto. |
| **NotebookLM** (Google) | Fuentes del cuaderno | No (solo tus fuentes) | No | Ideal para estudiar y resumir **tus** PDFs con citas a la página. |
| **DeepSeek** | Pegar prompt + adjuntar archivos | Sí (búsqueda) | No | Modo C. Buen razonamiento, revisá formato. |
| **Qwen** (Alibaba) | Pegar prompt / proyectos | Sí | Según versión | Modo C. |
| **Kimi** (Moonshot) | Pegar prompt + archivos largos | Sí | Según versión | Contexto muy largo: puede leer la base entera. |
| **Mistral Le Chat** | Bibliotecas / agentes | Sí | Sí | Modo B. |
| **Meta AI** | Pegar prompt | Sí | No | Modo C. |
| **Poe** | Bot propio con instrucciones + archivos | Según modelo | Según modelo | Permite crear un bot con la base y elegir el modelo de fondo. |

## Prompt de arranque para cualquier chat
```
[pegar PROMPT-UNIVERSAL.md]

Brief:
[pegar 07-plantillas/brief-del-trabajo.md lleno]

Rúbrica / consigna:
[pegar]

Mi información / tema:
[pegar apuntes, datos, fuentes]

Entregá: esquema primero. Cuando lo apruebe, redactá en Markdown con el frontmatter de md2docx.
```

## Si un nombre no aparece aquí
Cualquier IA nueva funciona en modo C (pegar el prompt). Si acepta archivos o instrucciones permanentes, usá el modo B. Si abre carpetas o repos, el modo A con `AGENTS.md`.
