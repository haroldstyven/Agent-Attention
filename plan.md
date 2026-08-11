# PoC 2 — Agente de atención (Copilot Studio vs. solución propia)

**Autor:** Harold Lagares
**Fecha:** 10 de agosto de 2026 · *revisión 2: 11 de agosto de 2026*
**Naturaleza:** problema abierto y exploratorio — riesgo técnico medio, riesgo de datos medio
**CRM:** HubSpot · **Track A:** Copilot Studio · **Población:** estudiantes actuales
**Repositorio:** https://github.com/haroldstyven/Agent-Attention

---

## 1. Objetivo

Producir una **matriz de decisión build/buy sustentada en evidencia** que avale —o descarte— la construcción de un agente de atención para estudiantes, y un prototipo asistido que demuestre la ruta recomendada.

El entregable que autoriza la inversión es la matriz. Todo lo demás en este plan existe para llenarla con números en vez de opiniones.

**Consecuencia de diseño:** la matriz no se escribe al final. Se define como instrumento vacío en la Fase 1, con sus pesos aprobados **antes** de que existan los números, y cada fase posterior llena filas específicas. Así no hay nada que refactorizar después.

---

## 2. Alcance

**Dentro del alcance**
- Caracterización cuantitativa del volumen y tipología de solicitudes en HubSpot.
- Auditoría del corpus documental que alimentará a ambos tracks.
- Banco de evaluación con preguntas reales y rúbrica de calificación ciega.
- Implementación comparativa: Copilot Studio vs. RAG propio mínimo.
- Matriz de decisión diligenciada + recomendación.
- Prototipo asistido con humano en el ciclo, embebido en HubSpot.

**Fuera del alcance de esta PoC**
- Exposición directa a estudiantes.
- Consultas transaccionales con autenticación de identidad (tipo B).
- Integración productiva con Banner.
- Canal de voz / telefonía automatizada.
- **Orquestación multi-agente (LangGraph) y capa MCP.** Ver Fase 8: son ruta posterior, no PoC.

### 2.1 Por qué el Track B es mínimo

La pregunta de esta PoC no es *"¿se puede construir un buen agente?"*, es *"¿sobre qué plataforma debe construir la UTB?"*. La orquestación con LangGraph y la exposición de sistemas vía MCP no mueven ninguna fila de la matriz; sí consumen la mayor parte del tiempo disponible.

El Track B es entonces: **retrieval sobre el corpus + cita obligatoria de fuente + compuerta de abstención.** Nada más. Lo que se está evaluando es el control sobre el retrieval y la trazabilidad, y eso se demuestra con la versión mínima.

---

## Fase 0 — Verificación de arranque

Los accesos están resueltos (CRM y licencia de Copilot). Esta fase ya no es escalamiento de bloqueos; es **verificar que los accesos sirven para lo que se necesita**, que es distinto a tenerlos.

| Verificación | Criterio de éxito |
|---|---|
| API de HubSpot | Se lee `/crm/v3/objects/tickets` con asociaciones y propiedades de tiempo. Scopes confirmados. |
| Entorno de Copilot Studio | Se crea un agente de prueba con una knowledge source y responde citando. Se documenta el plan de licenciamiento y el modelo de consumo por mensajes. |
| Referente de atención | Persona nombrada, con horas comprometidas por escrito (ver Fase 4 para la cifra). |
| Repositorio | `git init`. Todo artefacto de este plan versionado desde el día 1. |

**Riesgo real que reemplaza al de accesos:** que el ticket de HubSpot **no tenga tipología poblada**. Si nadie ha venido llenando una propiedad de categoría, la Fase 2 pasa de "agrupar" a "derivar la taxonomía por clustering de asuntos". Se detecta en la primera hora de la Fase 0, no en la Fase 2.

### 0.1 Manejo de datos — proporcionado al riesgo real

Se descarta el pipeline de anonimización (regex + NER + revisión). Para una PoC cuya responsabilidad recae en la UTB y cuyos datos no salen de sistemas que la institución ya tiene contratados, es desproporcionado y se come el cronograma.

Se sustituye por **dos reglas duras y una página de documentación**:

1. **El índice de recuperación contiene únicamente documentos institucionales.** Reglamentos, calendarios, FAQ, instructivos. Cero datos personales. Esto es gratis: las consultas tipo A son documentales por definición, así que el corpus nunca necesitó datos de estudiantes.
2. **Las 50–100 preguntas del banco pasan por revisión manual** mientras se están curando de todas formas. Un humano las lee y quita nombres, cédulas, correos y teléfonos. Son ~2 horas, no una tubería de ingeniería.
3. **Se documenta el flujo de datos de cada track** — una página. No es trámite: es la fila *"Residencia y tratamiento del dato"* de la matriz, y hay que llenarla igual.

**Advertencia honesta, sin prejuzgar:** conviene no asumir que el habeas data juega a favor del *build*. El procesamiento dentro del tenant de M365 de la UTB ya está cubierto contractualmente; una solución propia que llama a un modelo externo por API es un **flujo de datos nuevo**. Ese criterio puede terminar puntuando a favor de Copilot. La matriz debe poder llegar a esa conclusión.

Nota de precisión, porque quien revise protección de datos la va a hacer: *anonimizar* no es *pseudonimizar*. Si es reversible, sigue siendo dato personal bajo la Ley 1581.

---

## Fase 1 — La matriz como instrumento (pesos firmados)

**Se hace primero.** Antes de mirar un solo dato.

Se define la matriz completa, se separa en dos bloques, y **el jefe aprueba la columna de pesos antes de que existan los números**. Es la misma lógica de "el banco se define antes de construir", aplicada a los criterios: si los pesos se negocian después, se renegocian para justificar la respuesta que alguien ya prefería.

### Bloque I — Medible sobre el banco de evaluación

| Criterio | Peso | Copilot Studio | Propio | Se llena en |
|---|---|---|---|---|
| Exactitud sobre el banco (tipo A) | | | | Fase 6 |
| Alucinaciones (conteo, no tasa) | **Crítico** | | | Fase 6 |
| Trazabilidad: cita de fuente verificable | Alto | | | Fase 6 |
| Abstención correcta ante fuera de alcance | Alto | | | Fase 6 |
| Consistencia entre corridas repetidas | Medio | | | Fase 6 |

### Bloque II — Estructural (se razona, no se mide)

| Criterio | Peso | Copilot Studio | Propio | Se llena en |
|---|---|---|---|---|
| Control sobre el retrieval | Alto | | | Fase 5 |
| Residencia y tratamiento del dato personal | **Crítico** | | | Fase 0.1 / 5 |
| Capacidad de integrar HubSpot / Banner (tipo B) | Alto | | | Fase 5 |
| Costo total a 3 años (licencias + consumo vs. desarrollo + inferencia + mantenimiento) | Alto | | | Fase 5 |
| Dependencia de proveedor | Medio | | | Fase 5 |
| Mantenibilidad por el equipo | Medio | | | Fase 5 |
| Tiempo a producción | Medio | | | Fase 5 |

### 1.1 Las dos reglas que hacen honesta la matriz

**Regla 1 — Un bloque no contamina al otro.** Copilot Studio es un producto maduro que se configura; el Track B es una construcción mínima hecha por una persona. La brecha de exactitud que se mida puede no tener nada que ver con la pregunta arquitectónica de fondo. Un 85% contra un 72% sobre 50 preguntas **no mueve** una fila marcada como *Crítico* en el Bloque II.

**Regla 2 — Lo que no se puede medir se declara como proyección.** La fila de integración con HubSpot/Banner solo muerde en las consultas **tipo B**, que están fuera del alcance. Se puntúa razonando la arquitectura y documentando el mecanismo concreto de cada opción (conector personalizado / HTTP request en Copilot Studio vs. llamada directa a la API en el Track B), marcada explícitamente como *no medida*.

### 1.2 El costo sube de peso

En el plan original el costo era *Medio*. Sube a *Alto*: es lo que la dirección va a escrutinar. Exige un TCO a 3 años con un supuesto de volumen declarado (sale de la Fase 2), y **el costo del build debe incluir a alguien manteniendo la frescura del índice para siempre** — no solo el desarrollo inicial.

**Entregable:** `matriz_decision.md` con estructura completa, pesos aprobados y celdas vacías. Es el esqueleto que las demás fases llenan.

---

## Fase 2 — Caracterización del caso en HubSpot

Llena las filas de volumen y el supuesto de costo. Es el primer resultado presentable y no depende de la licencia de Copilot.

**Objetos y propiedades a extraer:**

| Qué | Dónde en HubSpot |
|---|---|
| Volumen y canal | `Tickets` + `Conversations` (inbox), por `hs_pipeline_stage` y fuente |
| Tipología | propiedad de categoría del ticket — **o derivada por clustering de asuntos si no está poblada** |
| Tiempo de atención | `time_to_close`, `hs_first_response_time` |
| Estacionalidad | `createdate` agrupado por semana (matrículas, cierres de periodo) |
| Resoluciones históricas | cuerpo de la última respuesta del hilo → insumo del banco *plata* (Fase 4) |

**Clasificación por tipo de resolución:**
- **A — Informativa.** Se responde con documentos: reglamentos, calendarios, requisitos. *Valor inmediato, riesgo bajo.*
- **B — Transaccional con dato personal.** Estado de mi solicitud, mi cuenta, mis notas. *Requiere integración y control de identidad.*
- **C — Excepción / criterio humano.** *Escala siempre.*

### 2.1 El ROI se mide en minutos, no en porcentaje de tickets

El plan original decía que el % del volumen tipo A *es* el ROI. No lo es. Las consultas tipo A suelen ser las de 30 segundos; las caras son las B y C. Un 60% de tickets tipo A puede ser un 20% del tiempo del equipo.

La cifra correcta es:

> **minutos direccionables = Σ (volumen × tiempo medio de atención)** sobre las tipologías tipo A

Ese es el número que sustenta el caso, y HubSpot ya tiene las dos columnas que hacen falta.

**Pendiente de precisar:** el denominador de población. La cifra de referencia es **~20.000 registros agregando aspirantes, estudiantes vigentes y egresados**. Hay que desagregarla en esta fase: los tres grupos preguntan cosas distintas, y solo los estudiantes vigentes son la población objetivo de esta PoC. El volumen de solicitudes y el TCO se calculan sobre ese subconjunto, no sobre los 20.000.

**Entregable:** caracterización de 3–4 páginas con volumetría, tipología, estacionalidad y **minutos direccionables**, integrando los archivos de contexto del caso de telefonía.

---

## Fase 3 — Corpus documental auditado

En el plan original esto era una fila del registro de riesgos. Es una fase, por dos razones:

1. **Es el techo de calidad de ambos tracks.** Ninguno puede responder mejor de lo que el corpus permite. Si los dos sacan 70%, sin esta auditoría no se sabrá si el problema fue la tecnología o los documentos.
2. **Es insumo compartido.** El mismo corpus alimenta a Copilot Studio y al Track B. Eso elimina un factor de confusión de la comparación — y por lo tanto es obligatorio que sea idéntico en los dos.

**Para cada documento:** dueño, fecha de vigencia, frecuencia de actualización, y **contradicciones detectadas contra otros documentos**.

Un RAG sobre reglamentos vencidos es peor que no tener nada: responde con autoridad y se equivoca. Auditar antes de indexar, no después de que un asesor le mande a un estudiante un requisito derogado.

**Entregable:** inventario del corpus con vigencias, dueños y lista de contradicciones a resolver. Corpus congelado y versionado — misma versión para ambos tracks.

---

## Fase 4 — Banco de evaluación y protocolo de calificación

> La fase que casi siempre se salta, y la que convierte la exploración en ingeniería.

**Antes de construir cualquier agente, construir con qué juzgarlo.**

### 4.1 Banco en dos niveles

No depender de la agenda de una sola persona:

- **30 preguntas oro** — extraídas del CRM, respuesta correcta **verificada por el referente de atención**. Costo real: ~4 horas de esa persona. Esa cifra va comprometida en la Fase 0.
- **40 preguntas plata** — extraídas del CRM con su resolución histórica *como* respuesta de referencia. Menor confianza, cero costo de agenda. Se marcan como tales y se reportan por separado.

**Incluir a propósito casos difíciles:** preguntas ambiguas, preguntas fuera de alcance, preguntas con datos personales, y preguntas cuya respuesta correcta es *"no sé, escala a un humano"*.

### 4.2 La métrica de alucinación cambia de forma

La meta original —≤2%— es **inmedible** con este tamaño de muestra: 2% de 50 preguntas es *una*, y con un solo fallo el intervalo de confianza al 95% va de 0% a ~10%. Un número no verificable en un criterio marcado *Crítico* es peor que no tener número.

Se reemplaza por una compuerta contable:

> **Cero respuestas con fuente citada que no sustente la respuesta, en las preguntas tipo A.**

Es más exigente, más honesta y sí se puede verificar leyendo 50 respuestas.

### 4.3 Protocolo de calificación — ciego

Es la mitigación más barata y creíble contra el sesgo hacia la solución propia:

- El referente califica **sin saber qué sistema produjo cada respuesta**. Salidas mezcladas y etiquetadas A/B al azar.
- Rúbrica escrita antes de la corrida: exactitud, fundamentación en la fuente citada, alucinación, abstención correcta.
- **Cada pregunta se corre 2–3 veces.** Estos sistemas no son deterministas y la varianza es un hallazgo, no ruido.
- **Línea base incluida en la mezcla:** el modelo sin retrieval, respondiendo a pelo. Es casi gratis y es lo único que dice si la inversión en corpus fue la que pagó. Sin ella, dos tracks en 85% no se pueden interpretar.

**Entregable:** `banco_evaluacion.jsonl` + `rubrica.md` + protocolo de calificación ciega. **Congelado antes de la Fase 5.**

---

## Fase 5 — Dos tracks en paralelo

Misma tarea, mismo corpus (Fase 3), mismo banco (Fase 4), mismo contrato de comportamiento.

### Contrato común — obligatorio en ambos

Sin esto la comparación no es válida:
- Toda respuesta cita la fuente.
- Existe una condición explícita de abstención, con la misma definición de "fuera de alcance" en los dos.
- Mismo alcance: solo tipo A.

### Track A — Copilot Studio (*buy*)

- Agente en Copilot Studio con el corpus de la Fase 3 como knowledge source (SharePoint).
- Configurar topics y comportamiento de abstención hasta donde la plataforma lo permita — **el techo de ese "hasta donde" es un hallazgo de primera línea para la matriz.**
- Documentar: control efectivo sobre el retrieval, formato y verificabilidad de las citas, límites de personalización, comportamiento cuando falla (¿se puede diagnosticar por qué recuperó mal?), y el **modelo de consumo por mensajes** para el TCO.

### Track B — Propio mínimo (*build*)

- Retrieval sobre el mismo corpus + cita obligatoria + compuerta de abstención basada en fundamentación.
- Sin LangGraph. Sin MCP. Sin conexión a HubSpot en esta fase.
- Documentar: qué se puede inspeccionar y ajustar del retrieval que en Copilot Studio no, y a qué costo de mantenimiento.

### 5.1 La asimetría de la abstención es el hallazgo más valioso

Ninguna de las dos plataformas se juzga solo por lo que responde bien. En el Track B se puede implementar una compuerta explícita de fundamentación; en Copilot Studio el control sobre cuándo el agente **debe callarse** es mucho más indirecto.

Para un agente que eventualmente hablará con estudiantes, *cuándo se calla* importa más que *qué tan bonito responde*. Trátese como experimento explícito, no como una fila de métrica.

### 5.2 Nota sobre una tercera opción que no se implementa

Copilot Studio no integra nativamente con HubSpot: requiere conector personalizado o HTTP request. HubSpot, en cambio, tiene capacidades de IA propias sentadas justo donde vive el dato de atención.

**No se implementa como tercer track** — dispersaría la PoC. Se documenta en un anexo de la matriz, porque una recomendación que ignora la IA del CRM que la institución ya paga tiene un hueco visible.

---

## Fase 6 — Corrida ciega, matriz diligenciada, recomendación

- Corrida de ambos tracks + línea base contra el banco congelado.
- Calificación ciega por el referente según la rúbrica.
- Llenado del Bloque I. Cierre del Bloque II con la evidencia de la Fase 5.
- Aplicación de los pesos aprobados en la Fase 1 — **sin renegociarlos.**

**Resultado esperado:** el escenario más probable no es "uno u otro" sino **híbrido** — Copilot Studio para consultas informativas internas donde la licencia ya está pagada y el dato no sale del tenant, y solución propia para lo que toca datos de estudiantes e integración con HubSpot. La matriz debe poder sustentar eso con evidencia, no con preferencia técnica.

Si la evidencia apunta a otra parte, se reporta lo que dice la evidencia.

**Entregable:** matriz diligenciada + recomendación de una página. **Este es el artefacto que autoriza —o no— la construcción.**

---

## Fase 7 — Prototipo asistido, embebido en HubSpot

Primer despliegue: **el agente le responde al asesor, no al estudiante.**

### 7.1 Superficie de entrega: dentro del ticket

Si el asesor tiene que salir de HubSpot para consultar el agente, la adopción es cero y el log —que es el punto entero de esta fase— queda vacío.

- **Opción principal:** UI extension de HubSpot (tarjeta en el registro de ticket / conversación). El asesor ve la respuesta sugerida y sus fuentes sin cambiar de pestaña.
- **Respaldo:** aplicación web interna mínima, si la extensión no se alcanza.

La superficie se decide **antes** de esta fase, no dentro de ella.

### 7.2 El principio anti-refactorización

Es lo que evita rehacer trabajo si la recomendación cambia:

> **Contrato delgado entre el motor de respuesta y la superficie de entrega.**

La tarjeta de HubSpot le pide a un endpoint `pregunta → {respuesta, fuentes[], confianza, ¿abstenerse?}`. Qué hay detrás —Copilot Studio o solución propia— es intercambiable. Si la Fase 6 recomienda híbrido, el enrutamiento vive detrás del contrato y la tarjeta no se toca.

### 7.3 Qué se mide aquí, honestamente

- Humano en el ciclo: el asesor valida cada respuesta antes de enviarla.
- Cada respuesta incluye la fuente citada.
- Cada interacción se registra: pregunta, respuesta sugerida, si el asesor la usó, la editó o la descartó.

**El criterio de éxito de esta fase no es una métrica de calidad.** Con un puñado de asesores se obtienen decenas de interacciones: eso es señal cualitativa, no medición. La fase está hecha cuando **el log existe, es analizable, y los asesores dijeron qué les falta.** Ese log es el insumo para ampliar el banco.

Coincide con lo planteado en la reunión: *"puede servir primero para ayudar a contestar"*. Es la ruta de menor riesgo reputacional.

---

## Fase 8 — Ruta posterior (fuera de alcance, documentada)

Para que la decisión de hoy no cierre puertas:

1. **Cobertura tipo B** con autenticación del estudiante. Aquí sí entran **MCP** (exponer HubSpot y Banner como herramientas) y **orquestación con LangGraph** (flujos multipaso, verificación de identidad, escalamiento condicional). Estaban en la PoC original; su lugar es acá.
2. **Política de escalamiento y de "no sé"** — cuándo el agente *debe* callarse, formalizado.
3. **Piloto cerrado** con un grupo acotado de estudiantes.
4. **Métricas de satisfacción y desvío de tickets.**

---

## Métricas de éxito

| Métrica | Meta |
|---|---|
| Exactitud sobre banco oro (tipo A) | ≥ 80% |
| Respuestas con fuente citada que no la sustenta | **0** en tipo A |
| Abstención correcta ante fuera de alcance | ≥ 90% |
| Minutos de atención direccionables | Cuantificado con evidencia de HubSpot |
| Matriz | Diligenciada con pesos aprobados *antes* de los números |
| Decisión build/buy | Sustentada en la matriz, no en preferencia técnica |

---

## Orden y dependencias

Las fechas son secundarias; el orden no. Lo que gatilla cada fase:

```
0 Verificación ──> 1 Matriz + pesos firmados
                        │
                        ├──> 2 Caracterización HubSpot ──┐
                        │                                 ├──> 6 Corrida + matriz ──> 7 Prototipo
                        ├──> 3 Corpus auditado ──┐        │
                        │                         ├──> 5 Tracks A/B ──┘
                        └──> 4 Banco + rúbrica ───┘
```

**Cortes duros:**
- La Fase 1 va antes que todo. Los pesos se firman sin números sobre la mesa.
- La Fase 3 va antes que la 5. No se indexa un corpus sin auditar.
- La Fase 4 se **congela** antes de que arranque la 5. Es la única defensa contra el sesgo.
- La Fase 7 no arranca sin la recomendación de la 6.

---

## Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| El referente de atención no aparece | **Alto** | Horas comprometidas por escrito en Fase 0. Banco en dos niveles: las 40 *plata* no dependen de su agenda. |
| Tickets de HubSpot sin tipología poblada | Alto | Se detecta en Fase 0. Plan B: derivar taxonomía por clustering de asuntos. |
| Corpus documental vencido o contradictorio | Alto | Fase 3 propia. Auditar antes de indexar. |
| Comparación sesgada hacia la solución propia | Alto | Banco congelado antes de construir + calificación ciega + pesos firmados antes de los números. |
| Track A queda como espantapájaros | Alto | Copilot Studio (no Copilot chat) con conector, no solo grounding en SharePoint. |
| Se confunde medición con proyección | Medio | Matriz en dos bloques; lo no medido se marca como tal. |
| PoC de una sola persona | Medio | Todo versionado desde el día 1; artefactos legibles sin acompañamiento. |
| El alcance se desborda hacia "el agente para estudiantes" | Medio | Banco fija el alcance. LangGraph/MCP explícitamente en Fase 8. |

---

## Definición de "hecho"

Una fase está hecha cuando:
1. Existe un artefacto ejecutable o un documento revisable, no una explicación verbal.
2. Se probó contra un caso real, no solo contra el caso feliz.
3. Los supuestos están escritos y marcados como tales.
4. Alguien distinto al autor pudo usarlo o entenderlo sin acompañamiento.
5. Las filas de la matriz que le correspondían quedaron llenas o marcadas como no medibles con la razón.

---

## Preguntas abiertas

1. **¿Cómo se desagregan los ~20.000 registros entre aspirantes, estudiantes vigentes y egresados?** Cada grupo consulta cosas distintas y solo uno es la población objetivo. Define el denominador del volumen y de la fila de costo. Se resuelve en Fase 2.
2. **¿Qué plan de Copilot Studio hay disponible y bajo qué modelo de consumo?** Determina si el Track A es comparación justa y alimenta el TCO.
3. **¿Hay restricción institucional para que consultas de estudiantes salgan del tenant de la UTB?** Determina si el Track B necesita modelo local o si un proveedor externo es aceptable.
4. **¿Hay iniciativa previa de chatbot en la UTB?** Sus resultados son evidencia gratis, y su fracaso —si lo hubo— es un riesgo político a nombrar antes, no después.
5. **¿Quién es el dueño del contenido documental y con qué frecuencia se actualiza?** Es un costo permanente del *build* que va en la fila de TCO.
