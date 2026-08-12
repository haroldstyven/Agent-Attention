#!/usr/bin/env python3
"""
Fase 0 — Verificacion de arranque de la PoC de agente de atencion.

Corre las verificaciones que el plan (plan.md, Fase 0 y 0.1) exige antes de
cualquier otra cosa, y emite un informe en markdown:

  1. Acceso de lectura a tickets  (scope de tickets)
  2. Acceso de lectura a hilos de conversacion  (scope aparte; sin el, las
     40 preguntas plata del banco de la Fase 4 no existen)
  3. Estado de la tipologia: % poblado, distribucion, cajon de sastre y
     variantes duplicadas, contra el umbral fijado en 0.1
  4. Contraste time_to_close vs. primera respuesta, que sustenta 2.2
  5. Volumen por mes, insumo de estacionalidad para la Fase 2

Solo biblioteca estandar. No escribe nada en HubSpot: todas las llamadas
son GET.

Uso:
    set HUBSPOT_TOKEN=pat-na1-...          (PowerShell: $env:HUBSPOT_TOKEN=...)
    python fase0_verificacion.py
    python fase0_verificacion.py --props categoria_ticket,motivo --max-pages 50
"""

import argparse
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone

BASE = "https://api.hubapi.com"

# --- Umbral de 0.1, fijado antes de ver los datos. No se toca aqui. ---
MIN_POBLADO = 0.70          # >=70% de tickets con la propiedad llena
MAX_VALOR_DOMINANTE = 0.35  # el valor mas frecuente no supera el 35%
MAX_CAJON = 0.25            # el cajon de sastre, sumadas sus grafias, no pasa del 25%

CAJON_DE_SASTRE = re.compile(
    r"^(otro|otros|general|generales|varios|misc|n/?a|ninguno|no\s+aplica|"
    r"sin\s+(categor|clasific|especific)|por\s+clasificar|pendiente)",
    re.IGNORECASE,
)

# Nombres que sugieren que una propiedad es la tipologia del ticket.
PISTAS_TIPOLOGIA = (
    "categor", "tipo", "motivo", "clasific", "asunto", "area", "solicitud",
    "tema", "servicio", "subtipo",
)

PROPS_BASE = [
    "subject", "createdate", "hs_pipeline", "hs_pipeline_stage",
    "time_to_close", "hs_first_response_time", "source_type",
]


# --------------------------------------------------------------------------
# Cliente HTTP
# --------------------------------------------------------------------------

class HubSpotError(Exception):
    def __init__(self, status, cuerpo):
        self.status = status
        self.cuerpo = cuerpo
        super().__init__(f"HTTP {status}: {cuerpo[:300]}")


def api_get(token, path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise HubSpotError(e.code, e.read().decode("utf-8", "replace")) from None


def paginar(token, path, params, max_pages):
    """Recorre un endpoint paginado del CRM. Devuelve (resultados, paginas, truncado)."""
    params = dict(params)
    salida, pagina = [], 0
    while True:
        data = api_get(token, path, params)
        salida.extend(data.get("results", []))
        pagina += 1
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            return salida, pagina, False
        if pagina >= max_pages:
            return salida, pagina, True
        params["after"] = after
        time.sleep(0.12)   # margen frente al limite de 100 req/10s


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def normalizar(valor):
    """Minusculas, sin tildes, sin puntuacion, espacios colapsados."""
    s = unicodedata.normalize("NFKD", valor.strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def clave(valor):
    """Clave de concepto: normaliza y ademas colapsa el plural castellano.

    'Otro' / 'Otros' / 'OTRO ' son el mismo concepto escrito de tres formas
    — el caso que 0.1 advierte — y sin colapsarlos el cajon de sastre se ve
    la mitad de grande de lo que es.

    Se quita una 's' final y despues una 'e' final. Suena tosco, pero es lo
    que hace coincidir los dos patrones de plural del castellano sobre la
    misma raiz: clase/clases -> 'clas', general/generales -> 'general'.
    Nunca se muestra al lector: para eso esta la etiqueta de la seccion 2.
    """
    partes = []
    for p in normalizar(valor).split():
        if len(p) >= 5:
            p = re.sub(r"s$", "", p)
            p = re.sub(r"e$", "", p)
        partes.append(p)
    return " ".join(partes)


def ms_a_horas(valor):
    try:
        return int(valor) / 3_600_000.0
    except (TypeError, ValueError):
        return None


def percentil(datos, p):
    if not datos:
        return None
    orden = sorted(datos)
    i = min(int(round((p / 100.0) * (len(orden) - 1))), len(orden) - 1)
    return orden[i]


def parse_fecha(valor):
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None


# --------------------------------------------------------------------------
# Verificaciones
# --------------------------------------------------------------------------

def verificar_conversaciones(token):
    """Scope aparte del de tickets. Sin el, el banco colapsa a 30 preguntas."""
    try:
        data = api_get(token, "/conversations/v3/conversations/threads", {"limit": 1})
    except HubSpotError as e:
        if e.status in (401, 403):
            return False, f"Sin acceso (HTTP {e.status}). Falta el scope de conversaciones."
        return False, f"Error inesperado: {e}"

    hilos = data.get("results", [])
    if not hilos:
        return True, "Scope concedido, pero el inbox no devolvio hilos. Confirmar que hay conversaciones."

    # Leer los mensajes de un hilo: es lo que realmente alimenta las plata.
    tid = hilos[0].get("id")
    try:
        msgs = api_get(token, f"/conversations/v3/conversations/threads/{tid}/messages", {"limit": 1})
    except HubSpotError as e:
        return False, f"Lista hilos pero no lee mensajes (HTTP {e.status}). Las plata quedan en riesgo."
    n = len(msgs.get("results", []))
    return True, f"Lectura de hilos y mensajes confirmada (hilo {tid}, {n} mensaje/s leidos)."


def elegir_candidatas(propiedades, forzadas):
    """Propiedades de tipo enumeracion que podrian ser la tipologia."""
    if forzadas:
        elegidas = [p for p in propiedades if p["name"] in forzadas]
        faltantes = set(forzadas) - {p["name"] for p in elegidas}
        return elegidas, sorted(faltantes)

    puntuadas = []
    for p in propiedades:
        if p.get("type") != "enumeration" or p.get("hidden"):
            continue
        etiqueta = f"{p.get('name','')} {p.get('label','')}".lower()
        puntaje = sum(2 for pista in PISTAS_TIPOLOGIA if pista in etiqueta)
        if not p.get("hubspotDefined"):
            puntaje += 1          # una propiedad creada por la UTB pesa mas
        if puntaje:
            puntuadas.append((puntaje, p))

    puntuadas.sort(key=lambda x: -x[0])
    return [p for _, p in puntuadas[:8]], []


def analizar_tipologia(tickets, prop):
    total = len(tickets)
    valores = [(t.get("properties") or {}).get(prop) for t in tickets]
    llenos = [v for v in valores if v not in (None, "")]

    conteo = Counter(llenos)          # por cadena cruda, como esta en el CRM
    n_llenos = len(llenos)
    pct_poblado = n_llenos / total if total else 0.0

    # Distribucion por concepto, no por cadena: 'Otro' y 'Otros' son uno solo.
    conteo_concepto = Counter()
    variantes = defaultdict(Counter)
    for valor, n in conteo.items():
        k = clave(valor)
        conteo_concepto[k] += n
        variantes[k][valor] += n

    # Se muestra la grafia mas usada de cada concepto, no la clave interna.
    def etiqueta(k):
        return variantes[k].most_common(1)[0][0]

    dominante_pct = 0.0
    if conteo_concepto:
        dominante_pct = conteo_concepto.most_common(1)[0][1] / n_llenos

    # El cajon se detecta sobre el valor crudo normalizado, donde el patron
    # sigue siendo legible; sumando todas las grafias del mismo concepto.
    cajon = sum(n for valor, n in conteo.items()
                if CAJON_DE_SASTRE.match(normalizar(valor)))
    cajon_pct = (cajon / n_llenos) if n_llenos else 0.0

    duplicadas = {etiqueta(k): sorted(v) for k, v in variantes.items() if len(v) > 1}

    # Cuando empezo a poblarse de verdad: detecta la propiedad que alguien
    # volvio obligatoria hace unos meses y que solo parece sana.
    fechas = [parse_fecha((t.get("properties") or {}).get("createdate"))
              for t in tickets if (t.get("properties") or {}).get(prop)]
    fechas = [f for f in fechas if f]
    primer_lleno = min(fechas) if fechas else None

    fallos = []
    if pct_poblado < MIN_POBLADO:
        fallos.append(f"poblado {pct_poblado:.1%} < {MIN_POBLADO:.0%}")
    if dominante_pct > MAX_VALOR_DOMINANTE:
        fallos.append(f"valor dominante {dominante_pct:.1%} > {MAX_VALOR_DOMINANTE:.0%}")
    if cajon_pct > MAX_CAJON:
        fallos.append(f"cajon de sastre {cajon_pct:.1%} > {MAX_CAJON:.0%}")
    if duplicadas:
        fallos.append(f"{len(duplicadas)} concepto/s con variantes duplicadas")

    return {
        "prop": prop,
        "total": total,
        "n_llenos": n_llenos,
        "pct_poblado": pct_poblado,
        "n_valores": len(conteo_concepto),
        "dominante": (etiqueta(conteo_concepto.most_common(1)[0][0])
                      if conteo_concepto else None),
        "dominante_pct": dominante_pct,
        "cajon_pct": cajon_pct,
        "duplicadas": duplicadas,
        "top": [(etiqueta(k), n) for k, n in conteo_concepto.most_common(15)],
        "primer_lleno": primer_lleno,
        "fallos": fallos,
        "limpia": not fallos,
    }


def analizar_tiempos(tickets):
    """Contrasta las dos columnas de tiempo. Sustenta el argumento de 2.2."""
    cierre, respuesta = [], []
    for t in tickets:
        p = t.get("properties") or {}
        h = ms_a_horas(p.get("time_to_close"))
        if h is not None:
            cierre.append(h)
        h = ms_a_horas(p.get("hs_first_response_time"))
        if h is not None:
            respuesta.append(h)
    return {
        "n_cierre": len(cierre),
        "cierre_p50": percentil(cierre, 50),
        "cierre_p90": percentil(cierre, 90),
        "n_respuesta": len(respuesta),
        "respuesta_p50": percentil(respuesta, 50),
        "respuesta_p90": percentil(respuesta, 90),
    }


def volumen_mensual(tickets):
    meses = Counter()
    for t in tickets:
        f = parse_fecha((t.get("properties") or {}).get("createdate"))
        if f:
            meses[f.strftime("%Y-%m")] += 1
    return sorted(meses.items())


# --------------------------------------------------------------------------
# Informe
# --------------------------------------------------------------------------

def redactar(res, ruta):
    L = []
    w = L.append
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    w("# Fase 0 — Resultado de la verificacion de arranque\n")
    w(f"**Generado:** {ahora} · `fase0_verificacion.py`")
    w(f"**Umbral de 0.1 (fijado antes de ver los datos):** poblado >= {MIN_POBLADO:.0%}, "
      f"valor dominante <= {MAX_VALOR_DOMINANTE:.0%}, cajon de sastre <= {MAX_CAJON:.0%}, "
      "sin variantes duplicadas\n")
    w("---\n")

    w("## 1. Accesos\n")
    w("| Verificacion | Resultado |")
    w("|---|---|")
    w(f"| Lectura de tickets | {res['tickets_estado']} |")
    w(f"| Lectura de hilos de conversacion | {res['conv_estado']} |")
    w("")
    if not res["conv_ok"]:
        w("> **Consecuencia:** sin lectura de conversaciones no existen las 40 preguntas "
          "plata de la Fase 4. El banco se reduce a 30 oro y hay que declararlo en la "
          "matriz antes de empezar, no descubrirlo en la Fase 4.\n")

    w("## 2. Estado de la tipologia\n")
    if not res["analisis"]:
        w("No se encontro ninguna propiedad de enumeracion candidata a tipologia.")
        w("**Consecuencia: ruta de clustering** sobre `subject` (plan.md, Fase 0.1).\n")
    else:
        w("| Propiedad | Poblado | Valores | Valor dominante | Cajon de sastre | Variantes dup. | Veredicto |")
        w("|---|---|---|---|---|---|---|")
        for a in res["analisis"]:
            dom = f"{a['dominante']} ({a['dominante_pct']:.0%})" if a["dominante"] else "—"
            w(f"| `{a['prop']}` | {a['pct_poblado']:.0%} | {a['n_valores']} | {dom} | "
              f"{a['cajon_pct']:.0%} | {len(a['duplicadas'])} | "
              f"{'**LIMPIA**' if a['limpia'] else 'SUCIA'} |")
        w("")

        mejor = res["analisis"][0]
        if mejor["limpia"]:
            w(f"### Veredicto: ruta aritmetica sobre `{mejor['prop']}`\n")
            w("La Fase 2 agrupa y suma. ~1 dia.\n")
        else:
            w("### Veredicto: ruta de clustering\n")
            w(f"Ninguna candidata pasa el umbral. La mejor, `{mejor['prop']}`, falla por: "
              f"{'; '.join(mejor['fallos'])}.\n")
            w("La Fase 2 deriva la taxonomia agrupando `subject` por similitud semantica. "
              "Cuesta 1-2 dias mas y produce una taxonomia que refleja lo que los "
              "estudiantes preguntan, no las categorias que alguien eligio hace dos anos.\n")

        for a in res["analisis"][:3]:
            w(f"#### `{a['prop']}` — detalle\n")
            if a["primer_lleno"]:
                w(f"Primer ticket con esta propiedad poblada: **{a['primer_lleno'].date()}**. "
                  "Si es muy posterior al inicio del historial, la propiedad se volvio "
                  "obligatoria en algun momento y el historial previo no es comparable.\n")
            w("| Valor | Tickets | % |")
            w("|---|---|---|")
            for valor, n in a["top"]:
                w(f"| {valor} | {n} | {n / a['n_llenos']:.1%} |" if a["n_llenos"] else f"| {valor} | {n} | — |")
            w("")
            if a["duplicadas"]:
                w("**El mismo concepto escrito de varias formas** — cada grupo se conto "
                  "una sola vez arriba, pero en HubSpot son valores distintos:\n")
                for etiq, variantes in sorted(a["duplicadas"].items()):
                    w(f"- **{etiq}** agrupa: {', '.join(repr(x) for x in variantes)}")
                w("")

    w("## 3. Las dos columnas de tiempo\n")
    t = res["tiempos"]
    w("| Metrica | n | p50 (h) | p90 (h) |")
    w("|---|---|---|---|")
    w(f"| `time_to_close` | {t['n_cierre']} | "
      f"{t['cierre_p50']:.1f} | {t['cierre_p90']:.1f} |" if t["n_cierre"] else
      "| `time_to_close` | 0 | — | — |")
    w(f"| `hs_first_response_time` | {t['n_respuesta']} | "
      f"{t['respuesta_p50']:.1f} | {t['respuesta_p90']:.1f} |" if t["n_respuesta"] else
      "| `hs_first_response_time` | 0 | — | — |")
    w("")
    if t["n_cierre"] and t["cierre_p50"]:
        w(f"> La mediana de cierre es de **{t['cierre_p50']:.1f} horas**. Ese numero incluye "
          "colas, fines de semana y espera del estudiante: **no es tiempo de atencion** y "
          "usarlo como tal infla los minutos direccionables uno o dos ordenes de magnitud "
          "(plan.md, 2.2). Se usa como techo, nunca como estimador.\n")

    w("## 4. Volumen por mes\n")
    w("| Mes | Tickets |")
    w("|---|---|")
    for mes, n in res["meses"]:
        w(f"| {mes} | {n} |")
    w("")
    if res["truncado"]:
        w(f"> **Muestra parcial:** se leyeron {res['n_tickets']} tickets en "
          f"{res['paginas']} paginas y quedaron mas. Subir `--max-pages` antes de citar "
          "cualquier cifra de volumen en la Fase 2.\n")
    else:
        w(f"Historial completo: **{res['n_tickets']} tickets**.\n")

    w("---\n")
    w("## Siguiente paso\n")
    w("Este informe llena la fila de tipologia de la Fase 0 y decide si la Fase 2 es "
      "aritmetica o clustering. No calcula minutos direccionables: esa cifra no se "
      "produce hasta que los pesos de `matriz_decision.md` esten firmados.\n")

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Verificacion de arranque de la Fase 0")
    ap.add_argument("--props", default="",
                    help="Propiedades de tipologia a analizar, separadas por coma "
                         "(si se omite, se detectan solas)")
    ap.add_argument("--max-pages", type=int, default=200,
                    help="Tope de paginas de 100 tickets (por defecto 200 = 20.000)")
    ap.add_argument("--out", default="fase0_resultado.md")
    args = ap.parse_args()

    token = os.environ.get("HUBSPOT_TOKEN", "").strip()
    if not token:
        sys.exit("Falta HUBSPOT_TOKEN en el entorno.\n"
                 "  PowerShell: $env:HUBSPOT_TOKEN = 'pat-na1-...'\n"
                 "  Bash:       export HUBSPOT_TOKEN=pat-na1-...")

    print("1/5 Propiedades de ticket...", flush=True)
    try:
        propiedades = api_get(token, "/crm/v3/properties/tickets").get("results", [])
    except HubSpotError as e:
        if e.status in (401, 403):
            sys.exit(f"Sin acceso a tickets (HTTP {e.status}). Revisar el scope del token.")
        raise
    tickets_estado = f"OK — {len(propiedades)} propiedades visibles"

    forzadas = [p.strip() for p in args.props.split(",") if p.strip()]
    candidatas, faltantes = elegir_candidatas(propiedades, forzadas)
    if faltantes:
        print(f"    aviso: no existen estas propiedades: {', '.join(faltantes)}")
    nombres = [p["name"] for p in candidatas]
    print(f"    candidatas a tipologia: {', '.join(nombres) or '(ninguna)'}")

    print("2/5 Hilos de conversacion...", flush=True)
    conv_ok, conv_estado = verificar_conversaciones(token)
    print(f"    {conv_estado}")

    print(f"3/5 Tickets (hasta {args.max_pages} paginas)...", flush=True)
    tickets, paginas, truncado = paginar(
        token, "/crm/v3/objects/tickets",
        {"limit": 100, "properties": ",".join(PROPS_BASE + nombres), "archived": "false"},
        args.max_pages,
    )
    print(f"    {len(tickets)} tickets en {paginas} pagina/s"
          f"{' (truncado)' if truncado else ''}")

    print("4/5 Analisis...", flush=True)
    analisis = [analizar_tipologia(tickets, n) for n in nombres]
    # Primero las limpias; entre iguales, la mas poblada.
    analisis.sort(key=lambda a: (not a["limpia"], -a["pct_poblado"]))

    print("5/5 Informe...", flush=True)
    redactar({
        "tickets_estado": tickets_estado,
        "conv_ok": conv_ok,
        "conv_estado": conv_estado,
        "analisis": analisis,
        "tiempos": analizar_tiempos(tickets),
        "meses": volumen_mensual(tickets),
        "n_tickets": len(tickets),
        "paginas": paginas,
        "truncado": truncado,
    }, args.out)

    print(f"\nListo: {args.out}")
    if analisis:
        mejor = analisis[0]
        print(f"Veredicto: {'ARITMETICA' if mejor['limpia'] else 'CLUSTERING'}"
              f" (mejor candidata: {mejor['prop']})")
    else:
        print("Veredicto: CLUSTERING (sin candidatas)")


if __name__ == "__main__":
    main()
