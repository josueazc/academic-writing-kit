---
tipo: guia
tema: integraciones
---
# Agentes que abren la carpeta

Cloná el repo y abrí el agente **dentro** de la carpeta. Trabajá cada encargo en `trabajos/<fecha-tema>/` (está en `.gitignore`).

```bash
git clone https://github.com/josueazc/academic-writing-kit.git
cd academic-writing-kit
mkdir -p trabajos/2026-11-ensayo-ia
```

| Agente | Cómo arrancar | Archivo que lee |
|---|---|---|
| Claude Code | `claude` en la carpeta | `CLAUDE.md` → `AGENTS.md` |
| OpenAI Codex (CLI / app) | `codex` en la carpeta | `AGENTS.md` |
| Gemini CLI | `gemini` en la carpeta | `GEMINI.md` → `AGENTS.md` |
| GitHub Copilot (VS Code, modo agente) | Abrir la carpeta en VS Code | `.github/copilot-instructions.md`, `AGENTS.md` |
| Cursor | Abrir la carpeta | `.cursor/rules/*.mdc`, `AGENTS.md` |
| Windsurf | Abrir la carpeta | `.windsurfrules` |
| Cline / Roo Code | Extensión de VS Code | `.clinerules` |
| Continue | Extensión de VS Code/JetBrains | Agregar `AGENTS.md` como regla |
| Aider | `aider --read AGENTS.md` | `CONVENTIONS.md` |
| Zed | Abrir la carpeta | `AGENTS.md` |
| Jules (Google) / Devin / agentes en la nube | Conectar el repo de GitHub | `AGENTS.md` |
| OpenCode, Goose, Amp, Kiro y similares | Abrir la carpeta | `AGENTS.md` |

## Instalar como Agent Skill
`SKILL.md` sigue el estándar abierto de Agent Skills: el agente lee solo la descripción y carga la base cuando la tarea es académica.

| Agente | Comando |
|---|---|
| Claude Code | `git clone https://github.com/josueazc/academic-writing-kit.git ~/.claude/skills/escritura-academica` |
| Codex | `git clone … ~/.codex/skills/escritura-academica` |
| Cursor | `git clone … ~/.cursor/skills/escritura-academica` |
| GitHub Copilot | `git clone … ~/.copilot/skills/escritura-academica` |

Las rutas de skills cambian entre versiones; si tu agente usa otra carpeta, revisá su documentación. Para actualizar: `git -C <ruta> pull`.

## Pedido típico
```
Leé AGENTS.md. Trabajá en trabajos/2026-11-ensayo-ia/.
Tema: [tema]. Información: [pegar o ruta a archivos]. Rúbrica: rubrica.md.
Hacé el flujo completo de 08-agentes/flujo-multiagente.md y generá final.docx con scripts/md2docx.py.
Buscá fuentes con scripts/fuentes.py y marcá [VERIFICAR] lo que no puedas abrir.
```

## Varios agentes a la vez
Seguí [08-agentes/flujo-multiagente.md](../08-agentes/flujo-multiagente.md): un agente por rol, cada uno escribe solo su archivo (`esquema.md`, `fuentes.md`, `borrador.md`, `revision.md`). Funciona mezclando herramientas: p. ej., Perplexity como investigador, Claude como redactor, ChatGPT como revisor y Codex/Claude Code para generar el .docx.
