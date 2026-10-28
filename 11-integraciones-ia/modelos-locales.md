---
tipo: guia
tema: integraciones
---
# Modelos locales y abiertos

Útiles sin internet o para privacidad. Su calidad en español y en formato APA varía: usalos con la base completa en contexto y revisá más.

| Herramienta | Uso |
|---|---|
| [Ollama](https://ollama.com) | `ollama run <modelo>` y pegar `PROMPT-UNIVERSAL.md` al inicio |
| [LM Studio](https://lmstudio.ai) | Interfaz gráfica; en el "system prompt" pegá `PROMPT-UNIVERSAL.md` |
| [Open WebUI](https://openwebui.com) / AnythingLLM | Permiten cargar la carpeta como base de conocimiento (RAG) |

Familias de modelos abiertos que suelen andar bien en español: Llama (Meta), Qwen (Alibaba), DeepSeek, Mistral, Gemma (Google), y **dots.llm1** (rednote hi lab; mezcla de expertos, 142 mil millones de parámetros con 14 mil millones activos, contexto de 32K, publicado en Hugging Face).

Recomendaciones:
- Modelos pequeños (≤ 8B) inventan más referencias: no les pidas fuentes, usá `scripts/fuentes.py`.
- Pasales solo los archivos necesarios (estructura + sección + estilo) si el contexto es corto.
- El .docx lo genera `scripts/md2docx.py`, no el modelo.
