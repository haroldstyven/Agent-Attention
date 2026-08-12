# PoC agente de atención — cuatro decisiones antes de arrancar

**De:** Harold Lagares · **Fecha:** 12 de agosto de 2026
**Se pide:** tres firmas y un compromiso de 8 horas. Ninguna requiere reunión larga; todas vienen con respuesta propuesta.

---

## Por qué antes y no después

La PoC compara construir un agente de atención contra comprarlo (Copilot Studio). El entregable que autoriza —o descarta— la inversión es una matriz de decisión.

Esa matriz solo tiene valor si sus criterios se fijan **antes** de conocer los resultados. Si se fijan después, cualquiera de las dos conclusiones se puede sustentar, y el ejercicio entero deja de ser evidencia para volverse presentación. Por eso estas cuatro decisiones bloquean el arranque en vez de ir apareciendo sobre la marcha.

---

## Decisión 1 — Pesos y aritmética de la matriz

**Documento:** `matriz_decision.md` (adjunto, 2 páginas, ya diligenciado con la propuesta).

Lo que hay que mirar son dos números de la sección 2.1:

- El bloque **medido** pesa 47%; el bloque **estructural razonado** —datos personales, costo a 3 años, integración, dependencia— pesa 53%.
- La fila de **exactitud** pesa **9% del total**.

Ese 9% suele ser lo primero que sorprende, y es deliberado: Copilot Studio es un producto maduro que se configura, y el track propio es una construcción mínima hecha por una persona en semanas. La diferencia de exactitud entre esos dos mide sobre todo esa asimetría, no cuál arquitectura le sirve a la UTB a tres años. Lo que sí decide es el bloque estructural.

Además hay una **compuerta**: cualquier track que falle en tratamiento de dato personal o en alucinaciones queda descalificado, sin importar su puntaje. No se compensa con nada.

> ☐ Apruebo los pesos y la regla propuestos  ☐ Apruebo con estos ajustes: ______________

---

## Decisión 2 — Piso de viabilidad

Hay un resultado posible que ninguna comparación resuelve: **que el volumen no dé para ninguna de las dos opciones.**

Si el tiempo de atención que un agente podría absorber vale menos que la licencia que habría que pagar, la respuesta correcta no es "Copilot" ni "propio", es "todavía no". Ese umbral hay que fijarlo antes de medir, por la misma razón que los pesos.

> **Piso propuesto: el equivalente en horas/mes cuyo costo, a tarifa cargada del equipo de atención, supere el costo anual de la opción más barata.**
> Cifra concreta a completar cuando confirmemos la tarifa: ________ horas/mes.

> ☐ De acuerdo con el criterio  ☐ Prefiero este otro piso: ______________

---

## Decisión 3 — Semanas disponibles

El plan completo —caracterización, auditoría del corpus, banco de evaluación, dos implementaciones, corrida ciega y prototipo asistido— son **8 a 12 semanas** para una persona.

Si hay menos, el recorte se decide ahora y no sobre la marcha. Orden de sacrificio propuesto:

| Se recorta primero | Qué se pierde |
|---|---|
| 1. Prototipo asistido en HubSpot | Nada de la decisión build/buy: el artefacto que autoriza es la matriz |
| 2. Banco reducido de 70 a 30 preguntas | Robustez estadística; los resultados siguen siendo interpretables |
| 3. Una sola corrida en vez de tres | La métrica de consistencia, que es la de menor peso |

**Lo que no se recorta bajo ninguna presión de cronograma:** la auditoría del corpus, congelar el banco antes de construir, y la calificación ciega. Sin esas tres la PoC deja de ser comparación y pasa a ser opinión con tablas.

> **Semanas disponibles: ________**  ☐ Plan completo  ☐ Recortar hasta el nivel ____

---

## Decisión 4 — Referente de atención: 8 horas

Se necesita **una persona nombrada** del equipo de atención, con 8 horas comprometidas y repartidas así:

| Actividad | Horas | Cuándo |
|---|---|---|
| Verificar las respuestas correctas de 30 preguntas reales | 4,0 | Semana 3–4 |
| Cronometrar la atención de ~20 tickets, para estimar tiempo real de manejo | 0,5 | Semana 2 |
| Calificar a ciegas 210 respuestas de los sistemas | 3,5 | Semana 8–10 |
| **Total** | **8,0** | |

Las 8 horas están calculadas, no estimadas a ojo: la calificación son 210 ítems a un minuto cada uno. **La calificación es a ciegas** —esa persona no sabrá qué sistema produjo cada respuesta— porque es la defensa más barata y creíble contra que la PoC se incline hacia la solución propia por sesgo de su autor.

> **Persona:** ________________  **Confirmado con su jefe directo:** ☐

---

## Si no hay respuesta

Para no bloquear el cronograma indefinidamente: si en **5 días hábiles** no hay firma, se procede con los valores propuestos marcados como *«propuestos, no firmados»*, y la matriz final lo declara en su encabezado. Es peor que una firma, pero es mejor que renegociarlos cuando los números ya estén sobre la mesa.

---

**Adjunto:** `matriz_decision.md` — el instrumento completo, vacío.
**Plan completo:** https://github.com/haroldstyven/Agent-Attention
