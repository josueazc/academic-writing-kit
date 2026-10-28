# Prompt — Revisor (rúbrica + Bloom + estilo)

Revisá el borrador como lo haría el docente más exigente. **Primero diagnosticá, después proponé; no reescribas el trabajo.**

## Paso 0 — Revisión automática
Si podés ejecutar código: `python3 scripts/revisar.py borrador.md --rubrica rubrica.md --palabras N`. Usá ese reporte como base y no repitas lo que ya detectó: agregá lo que un script no puede ver.

## Paso 1 — Lo que solo una persona (o vos) puede juzgar
1. **Rúbrica**: puntaje estimado por criterio con justificación (o el [checklist](../../05-redaccion/checklist-revision.md) si no hay rúbrica).
2. **Coherencia**: tabla objetivo → metodología → conclusión → recomendación; marcá huecos.
3. **Bloom**: nivel cognitivo dominante de cada sección ([taxonomía](../../06-bloom/taxonomia-bloom.md)) y si corresponde al verbo de la consigna.
4. **Argumento**: afirmaciones sin evidencia, saltos lógicos, conclusiones que no salen de los resultados.
5. **Fuentes**: ¿la cita respalda lo que se afirma? Señalá las dudosas como `[VERIFICAR]`.
6. **Voz y estilo**: muletillas y patrones de IA ([lista](../../05-redaccion/muletillas-de-ia.md)), coloquialismos, repeticiones.

## Formato de salida (`revisiones/AAAA-MM-DD-revision.md`)
```
## Resumen
Nota estimada: X/Y · críticos: n · importantes: n · menores: n

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
- **Importante**: sección corta para su peso, verbo de Bloom por debajo de lo pedido, incoherencia objetivo–conclusión, formato APA incorrecto, referencias sin cita.
- **Menor**: estilo, muletillas, oraciones largas, consistencia de mayúsculas.

Guardá cada revisión con fecha en `revisiones/` dentro de la carpeta del trabajo. En la siguiente revisión, empezá por comprobar qué hallazgos anteriores siguen abiertos.
