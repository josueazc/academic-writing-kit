<div align="center">

# ScholarForge

### Give your AI a method for academic writing.

A knowledge base and Python toolkit for turning ideas and notes into structured, cited, and formatted academic documents.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Markdown](https://img.shields.io/badge/Markdown-181717?style=for-the-badge&logo=markdown&logoColor=white)
![APA 7](https://img.shields.io/badge/APA-7th_Edition-2563EB?style=for-the-badge)

</div>

## The idea

AI can generate text, but academic writing also needs structure, reliable sources, consistent citations, and attention to assignment requirements. ScholarForge brings those pieces together in a reusable workspace.

It combines writing guides, templates, and agent instructions with practical tools for finding sources, checking references, reviewing drafts, and exporting Word documents. You choose the AI model; ScholarForge provides the method.

## What it does

- Helps plan essays, research papers, literature reviews, reports, and theses.
- Guides writing around a rubric, discipline, and citation style, with APA 7 as the default.
- Searches OpenAlex and Crossref and checks DOI and URL references.
- Reviews drafts for missing references, unfinished sections, and word-count issues.
- Converts Markdown into formatted Word documents (`.docx`).

The knowledge base is primarily in Spanish and includes guidance for writing in English. Automated checks support your review; they do not replace reading the sources or assessing the argument.

## How to use it

Clone the repository and open it with an AI agent that can read local files:

```bash
git clone https://github.com/josueazc/ScholarForge.git
cd ScholarForge
```

Ask the agent to read [AGENTS.md](AGENTS.md), then share your topic, notes, and assignment requirements. For a regular chat, use [PROMPT-UNIVERSAL.md](PROMPT-UNIVERSAL.md) as context.

The Python tools use the standard library and require no external dependencies. Source searches and reference checks need internet access.

[Explore the guides](00-indice.md) · [Python tools](scripts/README.md) · [AI integrations](11-integraciones-ia/README.md)

## Built with

Python · Markdown · Office Open XML · OpenAlex · Crossref

## License

[CC BY 4.0](LICENSE) — created by [Josué Azofeifa](https://github.com/josueazc).
