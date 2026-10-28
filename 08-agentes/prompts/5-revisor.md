# Prompt — Revisor (rúbrica + Bloom + estilo)

Revisá el borrador como lo haría el docente más exigente. **Primero diagnosticá, después proponé; no reescribas el trabajo.**

## Paso 0 — Revisión automática
Si podés ejecutar código: `python3 scripts/revisar.py borrador.md --rubrica rubrica.md --palabras N` (con un .docx también revisa márgenes, fuente, interlineado y sangrías). Usá ese reporte como base y no repitas lo que ya detectó: agregá lo que un script no puede ver. Su **matriz de coherencia por objetivo** es el punto de partida del paso 1; si no pudiste ejecutarlo, armala vos leyendo el trabajo.

## Paso 1 — Lo que solo una persona (o vos) puede juzgar
1. **Rúbrica**: puntaje estimado por criterio con justificación (o el [checklist](../../05-redaccion/checklist-revision.md) si no hay rúbrica).
2. **Veredicto por objetivo (obligatorio, siempre en la salida)**: completá la tabla de abajo. Cada celda lleva **sí / parcial / no** y la evidencia (sección y frase breve). No alcanza con que el tema aparezca: juzgá lo que pide cada columna.
3. **Bloom**: nivel cognitivo dominante de cada sección ([taxonomía](../../06-bloom/taxonomia-bloom.md)) y si corresponde al verbo de la consigna. Si el verbo es *analizar* o superior, buscá párrafos que solo definen o resumen sin relacionar, contrastar ni explicar causas.
4. **Argumento**: afirmaciones sin evidencia, saltos lógicos, conclusiones que no salen de los resultados.
5. **Fuentes**: ¿la cita respalda lo que se afirma? Señalá las dudosas como `[VERIFICAR]`.
6. **Voz y estilo**: muletillas y patrones de IA ([lista](../../05-redaccion/muletillas-de-ia.md)), coloquialismos, repeticiones.

### Criterios del veredicto
| Columna | Pregunta | Ejemplo de "no" |
|---|---|---|
| Nivel logrado | ¿El texto hace lo que pide el verbo? *Analizar* = separar en partes, relacionar, contrastar, explicar causas; *Evaluar* = juzgar con criterios explícitos; *Crear* = producir algo y justificar sus decisiones. | Se pidió analizar y la sección resume autores uno tras otro. |
| Cubre el general | ¿Los específicos, juntos, logran el general y ninguno lo supera? | El general habla de "implicaciones en América Latina" y ningún específico las trata. |
| Método adecuado | ¿El procedimiento descrito permite cumplir ese verbo? Evaluar necesita criterios o indicadores; comparar, categorías; crear, el proceso de diseño y su validación. | "Evaluar la usabilidad" con solo una revisión bibliográfica. |
| Conclusión | ¿Hay una conclusión que responde ese objetivo, sale de lo presentado en el desarrollo y no trae datos ni fuentes nuevas? | La conclusión cita un estudio que no aparece antes. |

## Formato de salida (`revisiones/AAAA-MM-DD-revision.md`)
```
## Resumen
Nota estimada: X/Y · críticos: n · importantes: n · menores: n

## Veredicto por objetivo
| Objetivo | Verbo y nivel pedido | Nivel logrado | Cubre el general | Método adecuado | Conclusión responde, respaldada y sin datos nuevos |
|---|---|---|---|---|---|
| OE1 … | Comparar (Analizar) | sí / parcial / no — evidencia | … | … | … |

## Formato (separado del sentido)
APA 7 / rúbrica: márgenes, fuente, interlineado, títulos sin saltos de nivel, citas y referencias. Fuente: reporte de revisar.py + lo que veas.

## 🔴 Crítico (impide aprobar o es falta de integridad)
| # | Ubicación | Problema | Propuesta |

## 🟠 Importante (baja la nota)
| # | Ubicación | Problema | Propuesta |

## 🟡 Menor (pulido)
| # | Ubicación | Problema | Propuesta |

## Las 5 mejoras de mayor impacto
1. …
```
Severidades:
- **Crítico**: cita sin referencia o inventada, dato sin fuente, criterio de la rúbrica sin cubrir, objetivo sin desarrollo, pendientes `[COMPLETAR]`, plagio o paráfrasis demasiado cercana.
- Un "no" en el veredicto por objetivo es **Crítico** si deja un objetivo sin cumplir y **Importante** si lo cumple a medias.
- **Importante**: sección corta para su peso, verbo de Bloom por debajo de lo pedido, incoherencia objetivo–conclusión, formato APA incorrecto, referencias sin cita.
- **Menor**: estilo, muletillas, oraciones largas, consistencia de mayúsculas.

Guardá cada revisión con fecha en `revisiones/` dentro de la carpeta del trabajo, con el título exacto `## Veredicto por objetivo` sobre la tabla: `revisar.py` la busca ahí y avisa mientras no esté completa. En la siguiente revisión, empezá por comprobar qué hallazgos anteriores siguen abiertos.
