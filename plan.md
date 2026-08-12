# PoC 2 — Agente de atención (Copilot Studio vs. solución propia)

**Autor:** Harold Lagares
**Fecha:** 10 de agosto de 2026 · *rev. 2: 11 de agosto · rev. 3: 12 de agosto de 2026*
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
| API de HubSpot — tickets | Se lee `/crm/v3/objects/tickets` con asociaciones y propiedades de tiempo. Scope `tickets` confirmado. |
| API de HubSpot — conversaciones | **Scope aparte.** Los cuerpos de hilo no viven en el objeto ticket sino en la Conversations API, con su propio scope de lectura. Sin él **no existen las 40 preguntas plata** de la Fase 4 y el banco colapsa a 30. Verificar acceso real leyendo un hilo, no solo el scope declarado. |
| Entorno de Copilot Studio | Se crea un agente de prueba con una knowledge source y responde citando. Se documenta el plan de licenciamiento y el modelo de consumo por mensajes. |
| Cuota de mensajes de Copilot | La Fase 6 consume del orden de **200–600 mensajes** solo en evaluación. Confirmar que la capacidad contratada los cubre. Un trial o un pack limitado que se agota a mitad de corrida invalida la comparación. |
| Portal de HubSpot con proyectos | La UI extension de la Fase 7 no es configuración: es despliegue de app y requiere cuenta de desarrollador y portal habilitado. Saberlo en la semana 1, no en la 10, porque decide entre la opción principal y el respaldo. |
| Tier de HubSpot / IA nativa | Determina si el anexo de 5.2 se sustenta en capacidades que la UTB ya paga o es especulación. |
| Referente de atención | Persona nombrada, con horas comprometidas por escrito — **~8 horas**, no 4. Ver 4.5 para el desglose. |
| Repositorio | `git init`. Todo artefacto de este plan versionado desde el día 1. |

**Riesgo real que reemplaza al de accesos:** que el ticket de HubSpot no tenga tipología utilizable. Ver 0.1 — es la primera consulta que se corre.

### 0.1 La primera consulta: estado de la tipología

Se ejecuta **antes que cualquier otra cosa del plan**, porque define si la Fase 2 es aritmética o es un ejercicio de clustering.

En HubSpot las propiedades del ticket son de dos clases. Las **automáticas** — `createdate`, `time_to_close`, `hs_first_response_time` — las llena HubSpot y siempre están. Las **manuales** —la categoría del ticket: *consulta de certificados*, *problema de pago*, *cambio de horario*— las tiene que llenar un asesor o un workflow, y pueden simplemente no estar.

Toda la Fase 2 depende de las manuales. Sin categoría no hay top-20 de solicitudes, no hay reparto A/B/C, y no hay minutos direccionables — que es una suma **por tipología**. El número que sustenta la PoC entera se queda sin denominador.

**El caso más probable no es que esté vacía, es que esté sucia.** Lo típico: cuarenta valores de categoría donde tres son `Otro` / `Otros` / `OTRO`, el 60% de los tickets cayendo en el cajón de sastre, y la propiedad poblada solo desde que alguien la volvió obligatoria hace ocho meses. Eso *parece* poblado y pasa cualquier revisión superficial, pero la tipología que produce no sirve.

Por eso la verificación no es *"¿existe la propiedad?"* sino:

> ¿Qué **porcentaje** de tickets la tiene llena, cuál es la **distribución** de valores, y cuánto cae en el **cajón de sastre**?

| Resultado | Consecuencia para la Fase 2 |
|---|---|
| Poblada y limpia | Agrupar y sumar. ~1 día. |
| Sucia o parcial | Derivar la taxonomía agrupando por similitud semántica el campo `subject`. Cuesta 1–2 días más, pero produce una taxonomía que refleja lo que los estudiantes preguntan de verdad, no las categorías que alguien eligió hace dos años. |

**El corte se fija ahora, antes de ver los datos.** Si el umbral se decide después, se racionaliza la ruta barata: siempre habrá un argumento para llamar "suficientemente limpia" a una propiedad que ahorra dos días de trabajo.

> **Limpia** = ≥70% de los tickets con categoría poblada **y** el valor más frecuente ≤35% del total **y** sin variantes duplicadas del mismo concepto por mayúsculas o tildes.
> Cualquier condición que falle ⇒ ruta de clustering. Sin discusión posterior.

**Cómo se lee:** private app token con scope de tickets + API v3 (`/crm/v3/objects/tickets`). Nota para no perder tiempo: el MCP de HubSpot disponible en el entorno de desarrollo es el del CLI `hs` —proyectos, apps, módulos de CMS— y **no lee datos del CRM**. Sirve para la Fase 7, no para esta.

### 0.2 Manejo de datos — proporcionado al riesgo real

Se descarta el pipeline de anonimización (regex + NER + revisión). Para una PoC cuya responsabilidad recae en la UTB y cuyos datos no salen de sistemas que la institución ya tiene contratados, es desproporcionado y se come el cronograma.

Se sustituye por **dos reglas duras y una página de documentación**:

1. **El índice de recuperación contiene únicamente documentos institucionales.** Reglamentos, calendarios, FAQ, instructivos. Cero datos personales. Esto es gratis: las consultas tipo A son documentales por definición, así que el corpus nunca necesitó datos de estudiantes.
2. **Las 70 preguntas del banco pasan por revisión manual** mientras se están curando de todas formas. Un humano las lee y quita nombres, cédulas, correos y teléfonos. Son ~2 horas, no una tubería de ingeniería.
3. **Se documenta el flujo de datos de cada track** — una página. No es trámite: es la fila *"Residencia y tratamiento del dato"* de la matriz, y hay que llenarla igual.

**Advertencia honesta, sin prejuzgar:** conviene no asumir que el habeas data juega a favor del *build*. El procesamiento dentro del tenant de M365 de la UTB ya está cubierto contractualmente; una solución propia que llama a un modelo externo por API es un **flujo de datos nuevo**. Ese criterio puede terminar puntuando a favor de Copilot. La matriz debe poder llegar a esa conclusión.

Nota de precisión, porque quien revise protección de datos la va a hacer: *anonimizar* no es *pseudonimizar*. Si es reversible, sigue siendo dato personal bajo la Ley 1581.

Y una segunda, del mismo revisor: las preguntas del banco salen de tickets reales de estudiantes. Aunque queden depuradas, la página de flujo de datos debe declarar **la base bajo la cual se usan** —previsiblemente uso compatible con la finalidad original de atención al estudiante, dentro de sistemas que la institución ya opera para eso mismo— y no solo por dónde pasan los datos. Es una frase, pero es la primera que piden.

---

## Fase 1 — La matriz como instrumento (pesos y aritmética firmados)

**Se hace primero.** Antes de mirar un solo dato.

Se define la matriz completa, se separa en dos bloques, y **el jefe aprueba la columna de pesos antes de que existan los números**. Es la misma lógica de "el banco se define antes de construir", aplicada a los criterios: si los pesos se negocian después, se renegocian para justificar la respuesta que alguien ya prefería.

**Se firman dos cosas, no una: los pesos y la regla de agregación.** Congelar los pesos sin congelar la aritmética deja abierto el mismo hueco con otro nombre y más difícil de detectar — en la Fase 6 ya no se discute cuánto pesa un criterio, se discute cómo se suman, que es la misma negociación disfrazada de tecnicismo. Ver 1.3.

### Bloque I — Medible sobre el banco de evaluación

| Criterio | Peso | Copilot Studio | Propio | Se llena en |
|---|---|---|---|---|
| Exactitud sobre el banco (tipo A) | Alto *(propuesto)* | | | Fase 6 |
| Alucinaciones — compuerta en oro, conteo en el total | **Crítico** | | | Fase 6 |
| Trazabilidad: cita de fuente verificable | Alto | | | Fase 6 |
| Abstención correcta ante fuera de alcance | Alto | | | Fase 6 |
| Consistencia entre corridas repetidas | Medio | | | Fase 6 *(medición automática)* |

La fila de exactitud es la única sin peso definido en la revisión anterior, y no por descuido inocente: es justo la que la Regla 1 argumenta que **no** debe dominar. Dejarla en blanco significaba llenarla cuando los números ya existieran — el error exacto que esta fase existe para prevenir. Se propone *Alto* y se marca como la fila más disputable de la firma; con la regla de agregación de 1.3 puede ser *Alto* sin atropellar al Bloque II.

### Bloque II — Estructural (se razona, no se mide)

| Criterio | Peso | Copilot Studio | Propio | Se llena en |
|---|---|---|---|---|
| Control sobre el retrieval | Alto | | | Fase 5 |
| Residencia y tratamiento del dato personal | **Crítico** | | | Fase 0.2 / 5 |
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

### 1.3 La regla de agregación se firma junto con los pesos

*Crítico / Alto / Medio* son etiquetas ordinales. **No se puede calcular un puntaje ponderado con etiquetas.** Mientras la aritmética no esté escrita, la Fase 6 la inventa — y quien la invente después de ver los números elegirá, sin mala fe, la que produce el resultado que ya prefería.

Regla propuesta, en dos pasos y en este orden:

1. **Compuerta.** Todo criterio marcado *Crítico* se evalúa primero. Un track que puntúe por debajo de 3 sobre 5 en cualquier *Crítico* queda descalificado, sin importar su puntaje total. Esto es lo que impide que una brecha de exactitud compre una violación de tratamiento de datos.
2. **Desempate ponderado** entre los que pasen la compuerta: celdas de 1 a 5, pesos numéricos **Crítico = 5, Alto = 3, Medio = 1**, suma ponderada.

Si ningún track pasa la compuerta, ese *es* el resultado de la PoC y se reporta como tal. La matriz debe poder decir "ninguno de los dos, todavía".

### 1.4 Confusores que la matriz declara de entrada

El Bloque I no mide plataformas. Mide paquetes. Escrito antes de correr nada, para que no se descubra en la sustentación:

- **Los dos tracks no corren el mismo modelo.** Copilot Studio usa el que Microsoft despache; el Track B usa el que se elija. Lo que el Bloque I compara es `plataforma + retrieval + modelo` como bloque indivisible. La Regla 1 ya amortigua la consecuencia, pero el confusor se nombra aquí, no se insinúa.
- **La línea base solo aísla la contribución del corpus para el Track B.** El modelo de Copilot no es accesible sin retrieval, así que no hay línea base equivalente del lado A. Decirlo evita que el número se lea como algo que no es.
- **Peso de la asimetría de implementación.** Producto maduro configurado por una persona contra construcción mínima hecha por una persona. Ya está en la Regla 1; se repite aquí porque es la limitación que más fácilmente se olvida al leer solo la matriz.

### 1.5 El umbral de "esto no se hace" también va firmado

El plan pre-compromete pesos, banco y rúbrica, pero hasta esta revisión no comprometía el corte de viabilidad — la única aplicación de su propia lógica que faltaba. Si los minutos direccionables de la Fase 2 salen por debajo de cierto piso, **ninguna** de las dos opciones se justifica y la comparación es un ejercicio académico.

> **Piso de viabilidad: _______ horas/mes de atención direccionable.** Se llena y se firma en la Fase 1, antes de correr la primera consulta de la Fase 2.

Se sugiere derivarlo del costo anual más barato de las dos opciones: si el tiempo liberado vale menos que la licencia, no hay caso. Ese cálculo se puede hacer hoy, con la tarifa del equipo de atención y el precio de lista de Copilot.

**Entregable:** `matriz_decision.md` con estructura completa, pesos aprobados, **regla de agregación escrita**, piso de viabilidad firmado y celdas vacías. Es el esqueleto que las demás fases llenan.

---

## Fase 2 — Caracterización del caso en HubSpot

Llena las filas de volumen y el supuesto de costo. Es el primer resultado presentable y no depende de la licencia de Copilot.

**Objetos y propiedades a extraer:**

| Qué | Dónde en HubSpot |
|---|---|
| Volumen y canal | `Tickets` + `Conversations` (inbox), por `hs_pipeline_stage` y fuente |
| Tipología | propiedad de categoría del ticket — **o derivada por clustering de asuntos si no está poblada** |
| Tiempo de atención | **No existe como columna.** Se estima — ver 2.2. `hs_first_response_time` es insumo, no respuesta |
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

### 2.2 El tiempo de atención no está en HubSpot — y es la mitad de la fórmula

Ésta es la corrección más consecuente de la revisión 3, porque toca el número que sustenta la PoC entera.

`time_to_close` **no es tiempo de atención.** Es reloj de pared entre creación y cierre: incluye colas, fines de semana, y sobre todo la espera de que el estudiante conteste. Un ticket de certificado que le cuesta 3 minutos a un asesor puede tener un `time_to_close` de dos días. HubSpot **no guarda nativamente el tiempo de manejo del agente** — esa columna simplemente no existe.

Si se usa `time_to_close` como el factor de tiempo, los minutos direccionables quedan inflados uno o dos órdenes de magnitud. Y es exactamente el número que la dirección va a auditar primero.

Se estima por triangulación, con el supuesto escrito como supuesto:

| Fuente | Qué aporta |
|---|---|
| `hs_first_response_time` | Piso. Acota por debajo, no resuelve. |
| Número de mensajes del hilo × minutos por mensaje | Estructura. Los minutos por mensaje se calibran preguntándole al referente por tipología. |
| Muestreo cronometrado de ~20 tickets reales | Ancla empírica. Es media jornada del referente y convierte la estimación en algo defendible. |

**El resultado se reporta como rango, no como cifra puntual**, y la fila de la matriz que dependa de él lleva el rango, no el punto medio.

### 2.3 Qué denominador es cuál

La cifra de referencia de **~20.000 registros agregando aspirantes, estudiantes vigentes y egresados** hay que desagregarla en esta fase: los tres grupos preguntan cosas distintas y solo los estudiantes vigentes son la población objetivo.

Precisión que evita que esa cifra cargue más peso del que soporta: **los 20.000 no entran en la fórmula de minutos direccionables.** Esa fórmula corre sobre *tickets por periodo*, no sobre registros de contacto. El conteo de población sirve para normalizar per cápita y para escalar el TCO — nada más. Tratarla como el denominador del ROI es un error de categoría.

**Entregable:** caracterización de 3–4 páginas con volumetría, tipología, estacionalidad y **minutos direccionables**, integrando los archivos de contexto del caso de telefonía.

---

## Fase 3 — Corpus documental auditado

En el plan original esto era una fila del registro de riesgos. Es una fase, por dos razones:

1. **Es el techo de calidad de ambos tracks.** Ninguno puede responder mejor de lo que el corpus permite. Si los dos sacan 70%, sin esta auditoría no se sabrá si el problema fue la tecnología o los documentos.
2. **Es insumo compartido.** El mismo corpus alimenta a Copilot Studio y al Track B. Eso elimina un factor de confusión de la comparación — y por lo tanto es obligatorio que sea idéntico en los dos.

**Para cada documento:** dueño, fecha de vigencia, frecuencia de actualización, y **contradicciones detectadas contra otros documentos**.

Un RAG sobre reglamentos vencidos es peor que no tener nada: responde con autoridad y se equivoca. Auditar antes de indexar, no después de que un asesor le mande a un estudiante un requisito derogado.

### 3.1 "Mismo corpus" es una aserción hasta que se verifica

El Track A indexa desde SharePoint con un chunking que no se controla; el Track B indexa local. Decir que ambos ven lo mismo es una hipótesis, y si es falsa contamina toda la comparación de forma invisible — parecerá diferencia de plataforma.

Tres verificaciones, ninguna cara:

1. **Manifiesto con hash por archivo**, versionado en el repo. Antes de cada corrida se confirma que los dos tracks apuntan a las mismas versiones.
2. **Legibilidad por máquina, documento por documento.** El caso que hay que buscar a propósito: **reglamentos en PDF escaneado sin OCR** — enteramente plausible en una universidad, y quedan invisibles para uno o ambos tracks sin emitir ningún error. Un documento que no rinde texto extraíble se OCR-iza o se marca como fuera del corpus, pero no se deja pasar en silencio.
3. **Confirmación de indexación completa** en Copilot Studio antes de correr. La indexación de SharePoint tiene latencia propia y puede excluir tipos de archivo; correr sobre un índice a medias mide la impaciencia, no la plataforma.

**Entregable:** inventario del corpus con vigencias, dueños, lista de contradicciones a resolver y **manifiesto de hashes**. Corpus congelado y versionado — misma versión verificada para ambos tracks.

---

## Fase 4 — Banco de evaluación y protocolo de calificación

> La fase que casi siempre se salta, y la que convierte la exploración en ingeniería.

**Antes de construir cualquier agente, construir con qué juzgarlo.**

### 4.1 Banco en dos niveles

No depender de la agenda de una sola persona. **El tamaño del banco queda fijo en 70**; en revisiones anteriores derivaba entre 50 y 70 según el párrafo, y es el denominador de todos los números del Bloque I.

- **30 preguntas oro** — extraídas del CRM, respuesta correcta **verificada por el referente de atención**. ~4 horas de esa persona, solo para esta parte.
- **40 preguntas plata** — extraídas del CRM con su resolución histórica *como* respuesta de referencia. Requieren lectura de hilos de conversación, que es un scope de API distinto al de tickets: si no está disponible (Fase 0), esta mitad del banco no existe. Menor confianza, cero costo de agenda. Se marcan como tales y se reportan por separado.

**Incluir a propósito casos difíciles:** preguntas ambiguas, preguntas fuera de alcance, preguntas con datos personales, y preguntas cuya respuesta correcta es *"no sé, escala a un humano"*.

### 4.2 La métrica de alucinación cambia de forma

La meta original —≤2%— es **inmedible** con este tamaño de muestra: 2% de 50 preguntas es *una*, y con un solo fallo el intervalo de confianza al 95% va de 0% a ~10%. Un número no verificable en un criterio marcado *Crítico* es peor que no tener número.

Se reemplaza por una compuerta contable. Y hay que ser preciso en qué es compuerta y qué es conteo, porque la revisión 2 usaba las dos lecturas en párrafos distintos del mismo documento — con un criterio marcado *Crítico*, esa ambigüedad decide sola el resultado de la PoC:

> **Compuerta:** cero respuestas con fuente citada que no sustente la respuesta, sobre las **30 preguntas oro**. Reprobarla descalifica al track, vía la regla de 1.3.
> **Conteo comparativo:** el número absoluto de esas respuestas sobre las 70. No descalifica; discrimina entre tracks que hayan pasado la compuerta.

Así el criterio sirve para las dos cosas que se le piden —vetar y comparar— sin que una lectura se coma a la otra. Es más exigente que un porcentaje, más honesto, y se verifica leyendo respuestas.

### 4.3 Protocolo de calificación — ciego

Es la mitigación más barata y creíble contra el sesgo hacia la solución propia:

- El referente califica **sin saber qué sistema produjo cada respuesta**. Salidas mezcladas y etiquetadas A/B al azar.
- Rúbrica escrita antes de la corrida: exactitud, fundamentación en la fuente citada, alucinación, abstención correcta.
- **Cada pregunta se corre 2–3 veces.** Estos sistemas no son deterministas y la varianza es un hallazgo, no ruido. Pero **solo una corrida se califica a mano** — ver 4.5.
- **La consistencia entre corridas se mide sola.** Comparar programáticamente las salidas repetidas y las fuentes citadas no necesita humano. Esa fila del Bloque I sale de un script, no de la agenda del referente.
- **Línea base incluida en la mezcla:** el mismo modelo del Track B, sin retrieval, respondiendo a pelo. Se especifica cuál es en la rúbrica, y se declara su límite: como el modelo de Copilot no es accesible desnudo, la línea base dice si el corpus pagó **para el Track B**, no para ambos. Aun así es casi gratis y sin ella dos tracks en 85% no se pueden interpretar.

### 4.4 Chequeo de respondibilidad, antes de congelar

Una pregunta cuya respuesta no está en el corpus congelado no mide plataformas: mide el corpus. Si entra al denominador de exactitud, ambos tracks pierden puntos por una razón que no tiene nada que ver con la decisión build/buy.

Antes de congelar, un humano verifica pregunta por pregunta si la respuesta **existe** en el corpus de la Fase 3. Las que no, salen del denominador y entran a un balde aparte.

**Ese balde no es descarte, es hallazgo.** El porcentaje de solicitudes reales que ningún documento institucional puede responder hoy es un número de negocio que esta PoC produce casi gratis, y que hasta esta revisión el plan iba a tirar a la basura como ruido de medición. Va en la caracterización y probablemente sea de las cosas más accionables que salgan de todo el ejercicio.

### 4.5 Presupuesto real del referente

La revisión 2 comprometía ~4 horas en la Fase 0 y después le pedía a la misma persona calificar a ciegas. Las cuentas no daban:

> 70 preguntas × 3 sistemas (Copilot, propio, línea base) × 3 corridas = **630 respuestas**. A un minuto cada una son 10 horas y media — sobre un compromiso de 4.

El presupuesto se corrige y el diseño se ajusta para caber en él:

| Actividad | Costo |
|---|---|
| Verificar las 30 respuestas oro | ~4 h |
| Calificación ciega de **una sola corrida**: 70 × 3 = 210 ítems | ~3,5 h |
| Muestreo cronometrado de ~20 tickets (Fase 2.2) | ~0,5 h |
| **Total comprometido en Fase 0** | **~8 h** |

Las corridas 2 y 3 se conservan —la varianza sigue siendo un hallazgo— pero se explotan por comparación automática, no por lectura humana.

**Entregable:** `banco_evaluacion.jsonl` + `rubrica.md` + protocolo de calificación ciega + registro de preguntas excluidas por no respondibilidad. **Congelado antes de la Fase 5.**

---

## Fase 5 — Dos tracks en paralelo

Misma tarea, mismo corpus (Fase 3), mismo banco (Fase 4), mismo contrato de comportamiento.

### Contrato común — obligatorio en ambos

Sin esto la comparación no es válida:
- Toda respuesta cita la fuente.
- Existe una condición explícita de abstención, con la misma definición de "fuera de alcance" en los dos.
- Mismo alcance: solo tipo A.
- **Mismo corpus verificado**, no asumido: hashes cotejados e indexación confirmada en ambos lados antes de correr (3.1).
- **Se registra qué modelo corre cada track.** No van a ser el mismo y eso no se puede evitar, pero sí declarar: es el confusor de 1.4 y va escrito en la matriz, no descubierto en la sustentación.

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
- Aplicación de los pesos **y de la regla de agregación** aprobados en la Fase 1 — **sin renegociar ninguno de los dos.**
- Verificación de la compuerta de 1.3 antes de cualquier suma: si un track cae por debajo de 3 en un criterio *Crítico*, queda descalificado y el ponderado ya no se discute.

### 6.1 Sobre la hipótesis de trabajo

La revisión 2 anunciaba aquí, bajo el rótulo *"resultado esperado"*, que el desenlace más probable era un híbrido. Escribir el resultado antes de la evidencia, en un documento cuya venta entera es la disciplina anti-sesgo, es exactamente el párrafo que un revisor escéptico usa para desacreditar todo lo demás. Se reclasifica:

> **Hipótesis de trabajo, no predicción y no resultado esperado:** que la respuesta sea un híbrido — Copilot Studio para consultas informativas internas donde la licencia ya está pagada y el dato no sale del tenant, solución propia para lo que toca datos de estudiantes e integración con HubSpot.

Se declara aquí precisamente para que quede registrada como sesgo del autor y sea auditable contra el resultado, que es el único uso legítimo de una corazonada en este documento. **Si la evidencia apunta a otra parte, se reporta lo que dice la evidencia** — incluida la posibilidad, contemplada en 1.3, de que ningún track pase la compuerta.

**Entregable:** matriz diligenciada + recomendación de una página. **Este es el artefacto que autoriza —o no— la construcción.**

---

## Fase 7 — Prototipo asistido, embebido en HubSpot

Primer despliegue: **el agente le responde al asesor, no al estudiante.**

### 7.1 Superficie de entrega: dentro del ticket

Si el asesor tiene que salir de HubSpot para consultar el agente, la adopción es cero y el log —que es el punto entero de esta fase— queda vacío.

- **Opción principal:** UI extension de HubSpot (tarjeta en el registro de ticket / conversación). El asesor ve la respuesta sugerida y sus fuentes sin cambiar de pestaña. Se construye como proyecto de HubSpot — el CLI `hs` y su MCP son exactamente la herramienta para esto.
- **Respaldo:** aplicación web interna mínima, si la extensión no se alcanza.

La superficie se decide **antes** de esta fase, no dentro de ella — y la *factibilidad* se verifica todavía antes, en la Fase 0. La UI extension no es configuración: requiere cuenta de desarrollador y portal con proyectos habilitados. Descubrir que el portal no lo soporta en la semana 10 cuesta una fase; descubrirlo en la semana 1 cuesta veinte minutos y solo cambia una decisión de diseño.

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

Cada meta dice explícitamente **sobre quién** aplica. Una meta sin sujeto se interpreta después, y se interpreta a conveniencia.

| Métrica | Meta | Sujeto |
|---|---|---|
| Exactitud sobre banco oro (tipo A) | ≥ 80% | **Al menos un track.** Que ninguno llegue es el go/no-go de la tecnología, y es independiente de cuál gane |
| Respuestas con fuente citada que no la sustenta | **0** | Compuerta, por track, sobre las 30 oro (ver 4.2) |
| Abstención correcta ante fuera de alcance | ≥ 90% | Por track |
| Minutos de atención direccionables | Cuantificado como **rango**, por triangulación (2.2), y contrastado contra el piso de viabilidad de 1.5 | La PoC |
| Matriz | Diligenciada con pesos **y regla de agregación** aprobados *antes* de los números | La PoC |
| Decisión build/buy | Sustentada en la matriz, no en preferencia técnica. "Ninguno de los dos, todavía" es un resultado válido | La PoC |

---

## Orden y dependencias

Las fechas son secundarias; el orden no. Lo que gatilla cada fase:

El grafo de la revisión 2 dibujaba las fases 2, 3 y 4 como hermanas paralelas. **Es falso y el propio texto lo contradecía:** las preguntas plata salen de las resoluciones históricas que extrae la Fase 2, y el chequeo de respondibilidad de 4.4 exige el corpus congelado de la Fase 3. La Fase 4 es hija de las otras dos, no su hermana. Corregido:

```
0 Verificación ──> 1 Matriz: pesos + regla de agregación + piso de viabilidad (firmados)
                        │
                        ├──> 2 Caracterización HubSpot ──┬──> 4 Banco + rúbrica ──[CONGELADO]──┐
                        │                                │                                      │
                        └──> 3 Corpus auditado ──────────┤                                      ├──> 6 Corrida + matriz ──> 7 Prototipo
                                                         │                                      │
                                                         └──> 5 Tracks A/B ─────────────────────┘
```

La Fase 2 alimenta además, en la 6, las filas de volumen y TCO de la matriz.

**Cortes duros:**
- La Fase 1 va antes que todo. Los pesos **y la aritmética que los combina** se firman sin números sobre la mesa. Firmar unos sin la otra no cierra nada.
- La Fase 3 va antes que la 5. No se indexa un corpus sin auditar.
- La Fase 4 no se puede congelar sin la 2 (preguntas plata) ni sin la 3 (respondibilidad).
- La Fase 4 se **congela** antes de que arranque la 5. Es la única defensa contra el sesgo.
- La Fase 7 no arranca sin la recomendación de la 6.

### Presupuesto de tiempo — pendiente de declarar

El §2.1 justifica sacar LangGraph y MCP porque "consumen la mayor parte del tiempo disponible", pero ese tiempo **nunca se declara en ninguna parte del plan**. Un argumento de alcance apoyado en un presupuesto invisible no es verificable.

Estimación honesta para una persona: **8–12 semanas** para las fases 0 a 7, con la 3, la 4 y la 5 llevándose la mayor parte.

> **Presupuesto real disponible: _______ semanas.** Se declara antes de arrancar la Fase 2.

Si el presupuesto es menor, el recorte se decide ahora y no sobre la marcha. En orden de sacrificio:

1. **Fase 7** — sale completa. La decisión build/buy no la necesita; el artefacto que autoriza la inversión es la matriz de la Fase 6.
2. **Banco reducido a 30 oro** — se pierden las plata y con ellas robustez estadística, pero el Bloque I sigue siendo interpretable y se ahorra la dependencia del scope de conversaciones.
3. **Una sola corrida** — se pierde la fila de consistencia. Es la de peso *Medio*, así que es la más barata de perder.

Lo que **no** se recorta bajo ninguna presión de cronograma: la auditoría del corpus (Fase 3), el congelamiento del banco antes de construir, y la calificación ciega. Recortar cualquiera de esas tres convierte la PoC en una opinión con tablas.

---

## Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| El referente de atención no aparece | **Alto** | **8 horas** comprometidas por escrito en Fase 0, con el desglose de 4.5 a la vista. Banco en dos niveles: las 40 *plata* no dependen de su agenda. |
| **El aprobador de pesos no firma a tiempo** | **Alto** | Bloquea las ocho fases y no estaba en esta tabla. Default explícito: si no hay firma en 5 días hábiles, se procede con los pesos y la regla de agregación marcados como *propuestos, no firmados*, y la matriz final lo declara en su encabezado. |
| **Se usa `time_to_close` como tiempo de atención** | **Alto** | Infla el número principal uno o dos órdenes de magnitud. Prohibido por 2.2: triangulación de tres fuentes y reporte por rango. |
| Tickets de HubSpot sin tipología poblada | Alto | Se detecta en Fase 0, con umbral numérico fijado *antes* de ver los datos (0.1). Plan B: derivar taxonomía por clustering de asuntos. |
| **El banco termina midiendo el corpus, no las plataformas** | Alto | Chequeo de respondibilidad antes de congelar (4.4). Las no respondibles salen del denominador y se reportan como hallazgo aparte. |
| **Los dos tracks no indexan lo mismo** | Alto | Manifiesto de hashes, verificación de texto extraíble —el caso a cazar es el PDF escaneado sin OCR— y confirmación de indexación completa antes de correr (3.1). |
| **La cuota de mensajes de Copilot se agota a mitad de evaluación** | Medio | Se dimensiona en Fase 0 contra las ~200–600 respuestas que consume la Fase 6. |
| **El scope de conversaciones no está disponible** | Medio | Se verifica en Fase 0 leyendo un hilo real. Si falla, el banco se reduce a 30 oro y se declara en la matriz — no se descubre en la Fase 4. |
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
6. Los confusores y supuestos que la fase introdujo quedaron declarados en la matriz, no en la cabeza del autor.

---

## Preguntas abiertas

1. **¿Cómo se desagregan los ~20.000 registros entre aspirantes, estudiantes vigentes y egresados?** Cada grupo consulta cosas distintas y solo uno es la población objetivo. Define el denominador del volumen y de la fila de costo. Se resuelve en Fase 2.
2. **¿Qué plan de Copilot Studio hay disponible y bajo qué modelo de consumo?** Determina si el Track A es comparación justa y alimenta el TCO.
3. **¿Hay restricción institucional para que consultas de estudiantes salgan del tenant de la UTB?** Determina si el Track B necesita modelo local o si un proveedor externo es aceptable.
4. **¿Hay iniciativa previa de chatbot en la UTB?** Sus resultados son evidencia gratis, y su fracaso —si lo hubo— es un riesgo político a nombrar antes, no después.
5. **¿Quién es el dueño del contenido documental y con qué frecuencia se actualiza?** Es un costo permanente del *build* que va en la fila de TCO.

Y dos que **no son preguntas abiertas sino decisiones pendientes de firma**, con fecha límite propia porque bloquean el arranque:

6. **¿Cuál es el piso de viabilidad en horas/mes?** Se firma en la Fase 1, antes de la primera consulta de la Fase 2. Sin él, cualquier cifra que salga se declarará suficiente a posteriori. Ver 1.5.
7. **¿Cuántas semanas hay realmente?** Determina si el plan corre completo o entra el recorte de la sección de presupuesto. Se declara antes de la Fase 2.
