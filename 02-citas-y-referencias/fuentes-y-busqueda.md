---
tipo: directorio
tema: fuentes
---
# Dónde buscar fuentes (cientos de millones de documentos)

Esta base no copia millones de fuentes: **apunta a los índices que ya las tienen** y trae una herramienta para consultarlos y obtener la referencia APA ([`scripts/fuentes.py`](../scripts/fuentes.py)).

```bash
python3 scripts/fuentes.py buscar "turistificación Costa Rica" -n 10 --desde 2018
python3 scripts/fuentes.py buscar "youth political participation" --abiertos --formato md
python3 scripts/fuentes.py doi 10.1080/1369118X.2012.670661
```
Cada resultado trae DOI/URL: **abrilo y leelo antes de citarlo**. La herramienta convierte nombres con una regla simple (último apellido = apellido); en autores hispanos con dos apellidos corregí a mano: "Ortiz Ortiz, O. L.".

## Índices generales (gratuitos)
| Índice | Qué tiene | Uso |
|---|---|---|
| [OpenAlex](https://openalex.org) | Catálogo abierto de cientos de millones de trabajos, autores e instituciones | Lo usa `fuentes.py`; filtros por año, idioma, acceso abierto |
| [Crossref](https://search.crossref.org) | Registro de DOI de la mayoría de editoriales | Referencia APA exacta desde un DOI |
| [Google Académico](https://scholar.google.com) | El más amplio; botón "Citar" → APA | Revisar siempre la cita que genera |
| [Semantic Scholar](https://www.semanticscholar.org) | Búsqueda con IA, resúmenes TLDR | Encontrar artículos relacionados |
| [CORE](https://core.ac.uk) | Textos completos de repositorios abiertos | PDF gratis |
| [BASE](https://www.base-search.net) | Repositorios institucionales del mundo | Tesis y documentos grises |
| [DOAJ](https://doaj.org) | Revistas de acceso abierto revisadas por pares | Filtrar calidad |
| [Unpaywall](https://unpaywall.org) | Versión legal gratuita de un artículo de pago | Extensión del navegador |

## Iberoamérica (en español y portugués)
| Índice | Notas |
|---|---|
| [SciELO](https://scielo.org) | Revistas científicas de América Latina, España y Portugal |
| [Redalyc](https://www.redalyc.org) | Revistas iberoamericanas de acceso abierto |
| [Dialnet](https://dialnet.unirioja.es) | Artículos, tesis y libros en español |
| [Latindex](https://www.latindex.org) | Directorio de revistas de la región (verificar si una revista es seria) |
| [LA Referencia](https://www.lareferencia.info) | Tesis y artículos de repositorios latinoamericanos |
| [CLACSO](https://biblioteca-repositorio.clacso.edu.ar) | Ciencias sociales latinoamericanas |
| [CEPAL Repositorio](https://repositorio.cepal.org) | Economía y desarrollo de la región |

## Por área
| Área | Fuentes |
|---|---|
| Salud y biología | [PubMed](https://pubmed.ncbi.nlm.nih.gov), [PMC](https://www.ncbi.nlm.nih.gov/pmc/), [BVS/LILACS](https://bvsalud.org), [Cochrane](https://www.cochranelibrary.com), OMS/OPS |
| Educación | [ERIC](https://eric.ed.gov), UNESCO, [Revista Educación UCR](https://revistas.ucr.ac.cr/index.php/educacion) |
| Ingeniería y computación | [arXiv](https://arxiv.org), [IEEE Xplore](https://ieeexplore.ieee.org), [ACM DL](https://dl.acm.org), documentación oficial |
| Economía y negocios | Banco Mundial, FMI, OCDE, CEPAL, [SSRN](https://www.ssrn.com), [RePEc](https://ideas.repec.org) |
| Derecho (CR) | [SCIJ / Sistema Costarricense de Información Jurídica](https://pgrweb.go.cr/scij/), Asamblea Legislativa |
| Datos y estadísticas | [Our World in Data](https://ourworldindata.org), [Banco Mundial – Datos](https://datos.bancomundial.org), [CEPALSTAT](https://statistics.cepal.org) |

## Costa Rica
| Fuente | Para qué |
|---|---|
| [INEC](https://inec.cr) | Censos, encuestas de hogares, empleo, empresas |
| [Programa Estado de la Nación](https://estadonacion.or.cr) | Informes de desarrollo humano, educación, región |
| [BCCR](https://www.bccr.fi.cr) | Indicadores económicos |
| [TSE](https://www.tse.go.cr) | Elecciones, Revista de Derecho Electoral |
| [CCP-UCR](https://ccp.ucr.ac.cr) | Población y salud |
| [Kérwá (UCR)](https://www.kerwa.ucr.ac.cr) · [Repositorio TEC](https://repositoriotec.tec.ac.cr) · [Repositorio UNA](https://repositorio.una.ac.cr) · [Repositorio UNED](https://repositorio.uned.ac.cr) | Tesis y artículos nacionales |
| [Portal de Revistas UCR](https://revistas.ucr.ac.cr) | Revistas académicas nacionales |
| [Kimuk](https://kimuk.conare.ac.cr) | Buscador de los repositorios de CONARE |

## Bibliotecas digitales de tu universidad
Las universidades privadas (ULACIT, Fidélitas, ULatina, etc.) suelen pagar bases como EBSCO, ProQuest, Scopus, Web of Science, JSTOR, ScienceDirect o e-Libro. Entrá desde el portal de la biblioteca con tu usuario: son fuentes de mayor calidad que la web abierta.

## Gestores de referencias (recomendado)
- **[Zotero](https://www.zotero.org)** (gratis): guarda fuentes con un clic desde el navegador, genera APA/Vancouver/IEEE y se integra con Word y Google Docs.
- Mendeley, EndNote: alternativas.
- Las IA con navegación (Perplexity, ChatGPT/Gemini/Grok con búsqueda, Claude con búsqueda web) sirven para **encontrar** fuentes, no para **inventarlas**: siempre abrí el enlace.

## Jerarquía de confiabilidad
1. Artículos revisados por pares, libros académicos, tesis aprobadas
2. Informes de organismos oficiales e internacionales, leyes
3. Prensa reconocida, sitios de instituciones y empresas expertas
4. Blogs y divulgación (solo para contexto, con cuidado)
5. ❌ Wikipedia (usarla para encontrar las fuentes que cita), foros, contenido sin autor, texto generado por IA
