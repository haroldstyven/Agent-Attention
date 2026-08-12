# Matriz de decisión build/buy — agente de atención

**Estado:** instrumento vacío. Pesos **propuestos, sin firmar**.
**Autor:** Harold Lagares · **Fecha:** 12 de agosto de 2026
**Origen:** `plan.md` rev. 3, Fase 1 · **Alternativas:** Copilot Studio (*buy*) vs. solución propia mínima (*build*)

> Este documento se llena en las Fases 5 y 6. Se firma **ahora**, vacío.
> Una matriz cuyos pesos se acuerdan después de conocer los resultados no es un instrumento de decisión: es una justificación con formato de tabla.

---

## 1. Escala de puntuación

Todas las celdas se puntúan de **1 a 5**. Anclas genéricas:

| Puntaje | Significado |
|---|---|
| **5** | Cumple sin reservas. No hay trabajo pendiente en este criterio. |
| **4** | Cumple con limitaciones menores, documentadas y aceptables. |
| **3** | Cumple parcialmente. Requiere trabajo adicional identificado. |
| **2** | Cumple mal. El trabajo para corregirlo es significativo o incierto. |
| **1** | No cumple. |

### 1.1 Conversión de medida a puntaje — Bloque I

Las filas del Bloque I producen números, no juicios. **La tabla de conversión se firma junto con los pesos**, por la misma razón que ellos: convertir un 78% en un 3 o en un 4 después de saber qué track lo sacó es renegociar el resultado con otro nombre.

| Fila | 5 | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|
| Exactitud sobre banco oro (tipo A) | ≥ 90% | 80–89% | 70–79% | 60–69% | < 60% |
| Alucinaciones — conteo sobre las 70 | 0 | 1–2 | 3–5 | 6–10 | > 10 |
| Trazabilidad — % con cita verificable | ≥ 95% | 85–94% | 70–84% | 50–69% | < 50% |
| Abstención correcta ante fuera de alcance | ≥ 90% | 80–89% | 65–79% | 50–64% | < 50% |
| Consistencia — % de preguntas con la misma fuente citada en las 3 corridas | ≥ 90% | 80–89% | 65–79% | 50–64% | < 50% |

*Alucinación* = respuesta que cita una fuente que no sustenta lo afirmado. Se cuenta por respuesta, no por afirmación.

### 1.2 Anclas del Bloque II

El Bloque II se razona. Para que "razonar" no sea "opinar", cada fila lleva su ancla en la columna correspondiente de la sección 4.

---

## 2. Regla de agregación

Dos pasos, **en este orden**.

### Paso 1 — Compuerta

> Un track que puntúe **por debajo de 3** en cualquier criterio marcado *Crítico* queda **descalificado**, sin importar su puntaje total.

Es lo que impide que una ventaja de exactitud compre una violación de tratamiento de datos. Si ningún track pasa la compuerta, **ese es el resultado de la PoC** y se reporta como tal: *"ninguno de los dos, todavía"* es una conclusión válida y prevista.

### Paso 2 — Desempate ponderado

Solo entre los que pasen la compuerta:

| Peso | Valor numérico |
|---|---|
| Crítico | 5 |
| Alto | 3 |
| Medio | 1 |

**Puntaje = Σ (puntaje de celda × valor del peso)** · Máximo teórico: **160**

### 2.1 Qué está firmando quien firma

Con los pesos propuestos, el reparto de influencia queda así:

| | Peso total | Participación |
|---|---|---|
| Bloque I (medido) | 15 | 47% |
| Bloque II (razonado) | 17 | 53% |

Y la fila de exactitud —la que instintivamente se lee como "la nota"— pesa **3 de 32, un 9%**. Es deliberado y es la Regla 1 del plan hecha aritmética: la brecha de exactitud entre un producto maduro y una construcción mínima de una persona no puede decidir una arquitectura a tres años.

Si esa proporción parece equivocada, **este es el momento de discutirla.** Después de la Fase 6 ya no se toca.

---

## 3. Bloque I — Medible sobre el banco de evaluación

Se llena en la Fase 6, con calificación ciega. Banco: 70 preguntas (30 oro + 40 plata), reportadas por separado.

| Criterio | Peso propuesto | Copilot Studio | Propio | Línea base | Evidencia |
|---|---|---|---|---|---|
| Exactitud sobre el banco (tipo A) | Alto | | | | |
| Alucinaciones — compuerta en oro, conteo en el total | **Crítico** | | | | |
| Trazabilidad: cita de fuente verificable | Alto | | | | |
| Abstención correcta ante fuera de alcance | Alto | | | | |
| Consistencia entre corridas repetidas | Medio | | | | |

**Compuerta específica de esta sección:** cero respuestas con fuente citada que no la sustente, sobre las **30 preguntas oro**. Reprobarla descalifica al track vía el Paso 1.

La **línea base** (mismo modelo del Track B, sin retrieval) no compite: existe para saber si el corpus fue lo que pagó. No entra en el ponderado.

---

## 4. Bloque II — Estructural (se razona, no se mide)

Se cierra en la Fase 5. Cada celda exige el ancla, no solo el número.

| Criterio | Peso propuesto | Copilot Studio | Propio | Ancla — qué es un 5 |
|---|---|---|---|---|
| Control sobre el retrieval | Alto | | | Se inspecciona qué se recuperó y por qué, y se ajusta chunking y ranking sin salir de la plataforma |
| Residencia y tratamiento del dato personal | **Crítico** | | | El dato no sale de infraestructura ya cubierta contractualmente por la UTB; el flujo está documentado y es auditable |
| Capacidad de integrar HubSpot / Banner (tipo B) | Alto | | | Mecanismo concreto, documentado y sin licenciamiento adicional. **No medido** — proyección razonada |
| Costo total a 3 años | Alto | | | TCO menor con supuesto de volumen declarado, **incluyendo mantenimiento perpetuo del índice** |
| Dependencia de proveedor | Medio | | | Migrar a otra plataforma no obliga a rehacer el corpus ni la lógica de respuesta |
| Mantenibilidad por el equipo | Medio | | | El equipo actual lo sostiene sin contratar un perfil nuevo |
| Tiempo a producción | Medio | | | Semanas, no trimestres, para el primer despliegue asistido |

**Filas marcadas como no medidas:** integración tipo B. Se puntúa razonando la arquitectura y documentando el mecanismo de cada opción (conector personalizado / HTTP request en Copilot Studio vs. llamada directa a la API en el Track B). Va etiquetada como proyección en el informe final.

---

## 5. Confusores declarados

Se escriben antes de correr nada, para que no aparezcan en la sustentación como sorpresa.

1. **Los dos tracks no corren el mismo modelo.** Copilot Studio usa el que Microsoft despache; el Track B, el que se elija. El Bloque I compara `plataforma + retrieval + modelo` como paquete indivisible. Modelo de cada track: `________` / `________`.
2. **La línea base es asimétrica.** El modelo de Copilot no es accesible sin retrieval, así que la línea base dice si el corpus pagó **para el Track B**, no para ambos.
3. **Asimetría de implementación.** Producto maduro configurado por una persona, contra construcción mínima hecha por una persona, con el mismo tiempo.
4. **El corpus es el techo de ambos.** Las preguntas sin respuesta en el corpus salen del denominador y se reportan aparte (`plan.md` §4.4).
5. **Tiempo de atención estimado, no medido.** Se reporta como rango (`plan.md` §2.2). Todas las cifras de costo heredan ese rango.

---

## 6. Piso de viabilidad

Antecede a la comparación. Si no se cruza, **cuál track gana deja de importar**.

> **Piso: ________ horas/mes de atención direccionable.**
> Medido: ________ (rango, Fase 2) · Cruza: ☐ Sí ☐ No

Derivación sugerida: el tiempo liberado, valorado a la tarifa cargada del equipo de atención, debe superar el costo anual de la opción más barata. Si no lo hace, no hay caso para ninguna de las dos.

---

## 7. Anexo — Tercera opción no implementada

La IA nativa de HubSpot no se implementa como track (dispersaría la PoC), pero se documenta: está sentada justo donde vive el dato de atención, y una recomendación que ignora una capacidad que la institución quizá ya paga tiene un hueco visible.

Se completa en la Fase 5: disponibilidad en el tier contratado, capacidades reales, y por qué no fue evaluada.

---

## 8. Firma

Se firman **cuatro cosas**, no una. Firmar los pesos sin la aritmética deja abierto el mismo hueco con otro nombre.

| Elemento | Sección | Aprobado |
|---|---|---|
| Pesos de ambos bloques | 3 y 4 | ☐ |
| Regla de agregación (compuerta + ponderado) | 2 | ☐ |
| Conversión de medida a puntaje del Bloque I | 1.1 | ☐ |
| Piso de viabilidad | 6 | ☐ |

**Aprobado por:** ________________  **Fecha:** ____________

*Si no hay firma en 5 días hábiles, se procede con estos valores marcados como «propuestos, no firmados» y la matriz final lo declara en su encabezado (`plan.md`, tabla de Riesgos).*
