---
tipo: guia
tema: integraciones
---
# Usar esta base con cada IA o agente

Hay tres formas de conectar la base, según lo que permita cada herramienta:

| Modo | Qué se hace | Herramientas |
|---|---|---|
| **A. Abrir la carpeta** | El agente lee `AGENTS.md` (o su archivo propio) y navega la base | Claude Code, Codex, Gemini CLI, Copilot (VS Code), Cursor, Windsurf, Cline, Roo Code, Continue, Aider, Zed, Jules, Devin, OpenCode, Goose, Amp |
| **B. Proyecto con conocimiento** | Se suben los archivos (o el ZIP) y se pega `PROMPT-UNIVERSAL.md` como instrucciones | ChatGPT (Proyectos / GPT personalizado), Claude (Proyectos), Gemini (Gems), Grok (Proyectos), Perplexity (Espacios), Microsoft 365 Copilot (Notebooks / agentes), NotebookLM, Mistral Le Chat, Poe |
| **C. Pegar en el chat** | Se pega `PROMPT-UNIVERSAL.md` + el brief en el primer mensaje | Cualquier chat: DeepSeek, Qwen, Kimi, Meta AI, HuggingChat, modelos locales |

Para generar el .docx, el modelo necesita ejecutar Python (`scripts/md2docx.py`): agentes con terminal (modo A) o chats con intérprete de código (ChatGPT, Gemini, Claude con análisis, Grok si lo ofrece). Si no puede ejecutar código, que entregue el Markdown y lo convertís vos con `python3 scripts/md2docx.py trabajo.md`.

## Archivos de instrucciones incluidos en el repo
| Archivo | Lo lee |
|---|---|
| `AGENTS.md` | Codex, Jules, Copilot (agente), Cursor, Zed, Amp, OpenCode, Devin y la mayoría de agentes nuevos (estándar abierto) |
| `CLAUDE.md` | Claude Code |
| `GEMINI.md` | Gemini CLI / Gemini Code Assist |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.cursor/rules/escritura-academica.mdc` | Cursor |
| `.windsurfrules` | Windsurf |
| `.clinerules` | Cline / Roo Code |
| `CONVENTIONS.md` | Aider (`aider --read CONVENTIONS.md`) |
| `llms.txt` | Índice estándar para LLM que leen sitios o repos |
| `PROMPT-UNIVERSAL.md` | Todo lo que sea chat |

Todos apuntan a `AGENTS.md`: **una sola fuente de verdad**. Si cambiás una regla, cambiala ahí (y en `PROMPT-UNIVERSAL.md`, que es su versión compacta).

## Guías por herramienta
- [Asistentes de chat](chats.md): ChatGPT, Claude, Gemini, Grok, Perplexity, Copilot, NotebookLM, DeepSeek, Qwen, Kimi, Le Chat, Meta AI, Poe
- [Agentes con archivos](agentes.md): Claude Code, Codex, Gemini CLI, Copilot, Cursor, Windsurf, Cline, Aider, Jules, Devin
- [Modelos locales y abiertos](modelos-locales.md): Ollama, LM Studio, Llama, Qwen, DeepSeek, Mistral, dots.llm1
