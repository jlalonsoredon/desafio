"""
API de recomendaciones SustraiApp
=================================
Replica la lógica de los notebooks svd_gastro-db, svd-cultura-db y svd_eventos-db.

Endpoints (GET):
    /health
    /recomendaciones/gastro   ?user_id=123 [&tipo_lugar=Bodega] [&provincia=Bizkaia] [&precio=Moderado] [&top_n=10]
    /recomendaciones/cultura  ?user_id=123 [&tipo_lugar=Museo]  [&provincia=Gipuzkoa] [&top_n=10]
    /recomendaciones/eventos  ?user_id=123 [&tipo=Concierto]    [&provincia=48] [&gratis=true] [&finde=true] [&top_n=10]

Respuesta: listado ORDENADO de ids (mejor primero). En gastro y cultura las dos
primeras posiciones son lugares patrocinados (is_sponsored=TRUE), si existen
tras aplicar los filtros.

    {
      "user_id": 123,
      "categoria": "gastro",
      "metodo": "SVD personalizado",
      "ids": [23, 150, 43, ...],
      "resultados": [
          {"id": 23, "puntuacion_estimada": 4.91, "patrocinado": true},
          ...
      ]
    }

Si los filtros no devuelven nada (o la provincia no se reconoce):
    {"user_id": 123, "categoria": "gastro", "ids": [],
     "mensaje": "No hay resultados para esta busqueda"}

Provincia: acepta castellano, euskera o código —
    Vizcaya/Bizkaia/48 · Guipúzcoa/Gipuzkoa/20 · Álava/Araba/01

Arranque local:   python app.py        (puerto 5000)
Producción:       gunicorn app:app     (Render)
Requiere: flask, psycopg2-binary, pandas, numpy, scikit-surprise
"""

import os
import pickle
import unicodedata

import numpy as np
import pandas as pd
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────────────────────────────────────
PG = dict(
    host=os.getenv("PGHOST", "localhost"),
    port=os.getenv("PGPORT", "5432"),
    dbname=os.getenv("PGDATABASE", "sustraiapp"),
    user=os.getenv("PGUSER", "postgres"),
    password=os.getenv("PGPASSWORD", "postgres"),
)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

N_PATROCINADOS = 2          # nº de patrocinados a incluir al inicio de cada respuesta
SIN_RESULTADOS = "No hay resultados para esta busqueda"

# ──────────────────────────────────────────────────────────────────────────────
# Normalización de provincia y texto (idéntica a los notebooks)
# Vizcaya/Bizkaia → 48 · Guipúzcoa/Gipuzkoa → 20 · Álava/Araba → 01
# ──────────────────────────────────────────────────────────────────────────────
PROVINCIA_ALIAS = {
    "alava": "01", "araba": "01", "araba/alava": "01", "01": "01", "1": "01",
    "guipuzcoa": "20", "gipuzkoa": "20", "20": "20",
    "vizcaya": "48", "bizkaia": "48", "48": "48",
}


def _norm_txt(valor):
    """minúsculas + sin tildes + sin espacios sobrantes ('Álava ' → 'alava')"""
    s = str(valor).strip().lower()
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c))


def _cod_provincia(valor):
    """Código de provincia ('01','20','48') o None si no se reconoce."""
    if valor is None:
        return None
    return PROVINCIA_ALIAS.get(_norm_txt(valor))


# ──────────────────────────────────────────────────────────────────────────────
# Carga de modelos y datos (una vez, al arrancar)
# ──────────────────────────────────────────────────────────────────────────────
def _cargar_modelo(nombre):
    with open(os.path.join(MODELS_DIR, nombre), "rb") as f:
        return pickle.load(f)


model_gastro  = _cargar_modelo("svd_gastro.pkl")
model_cultura = _cargar_modelo("svd_patrimonio.pkl")
model_eventos = _cargar_modelo("svd_eventos.pkl")

conn = psycopg2.connect(**PG, options="-c client_encoding=UTF8")
try:
    # ── Gastronomía ──────────────────────────────────────────────────────────
    reviews_gastro = pd.read_sql(
        "SELECT user_id, gastro_id, puntuacion FROM user_data.gastronomy_reviews", conn)
    gastro = pd.read_sql("""
        SELECT g.id           AS gastro_id,
               g.type         AS "Tipo de lugar",
               m.provincia    AS "Provincia",
               g.nivel_precio AS "Nivel precio",
               g.is_sponsored AS is_sponsored,
               g.valoracion   AS valoracion
        FROM market_data.gastronomy g
        JOIN shared.municipalities m ON m.id = g.municipality_id
    """, conn)

    # ── Patrimonio cultural ──────────────────────────────────────────────────
    reviews_cultura = pd.read_sql(
        "SELECT user_id, culture_id, puntuacion FROM user_data.culture_reviews", conn)
    patrimonio = pd.read_sql("""
        SELECT c.id           AS culture_id,
               c.tipo_lugar   AS "Tipo de lugar",
               m.provincia    AS "Provincia",
               c.is_sponsored AS is_sponsored,
               c.valoracion   AS valoracion
        FROM market_data.culture c
        JOIN shared.municipalities m ON m.id = c.municipality_id
    """, conn)

    # ── Eventos ──────────────────────────────────────────────────────────────
    reviews_eventos = pd.read_sql(
        "SELECT user_id, event_id, puntuacion FROM user_data.event_reviews", conn)
    eventos = pd.read_sql("""
        SELECT e.id            AS event_id,
               e.type          AS "typeEs",
               e.is_free       AS is_free,
               e.start_date    AS "startDate",
               m.province_code AS "provinceNoraCode"
        FROM market_data.events e
        JOIN shared.municipalities m ON m.id = e.municipality_id
    """, conn)
finally:
    conn.close()

# Tipos y columnas derivadas (igual que en los notebooks)
gastro["is_sponsored"]     = gastro["is_sponsored"].fillna(False).astype(bool)
patrimonio["is_sponsored"] = patrimonio["is_sponsored"].fillna(False).astype(bool)

eventos["startDate"]        = pd.to_datetime(eventos["startDate"], utc=True, errors="coerce")
eventos["is_weekend"]       = eventos["startDate"].dt.weekday >= 5
eventos["provinceNoraCode"] = pd.to_numeric(eventos["provinceNoraCode"], errors="coerce")


# ──────────────────────────────────────────────────────────────────────────────
# Lógica de recomendación (compartida por las 3 categorías)
# ──────────────────────────────────────────────────────────────────────────────
def _rankear(user_id, modelo, df_reviews, catalogo, id_col, top_n, con_patrocinados):
    """
    Núcleo común: SVD para usuarios con historial, media de reseñas para cold
    start, y (opcionalmente) 2 patrocinados priorizados al inicio del listado.
    Devuelve lista [(id, score, patrocinado), ...] o el string SIN_RESULTADOS.
    """
    if catalogo.empty:
        return SIN_RESULTADOS

    tiene_historial = user_id in df_reviews["user_id"].values
    visitados = set(df_reviews[df_reviews["user_id"] == user_id][id_col])

    no_visitados = [i for i in catalogo[id_col] if i not in visitados]
    if not no_visitados:
        return SIN_RESULTADOS

    if tiene_historial:
        preds  = [(i, modelo.predict(user_id, i).est) for i in no_visitados]
        metodo = "SVD personalizado"
    else:
        media = df_reviews.groupby(id_col)["puntuacion"].mean()
        if "valoracion" in catalogo.columns:
            val = catalogo.set_index(id_col)["valoracion"]
            preds = [(i, float(media.get(i, val.get(i, 4.0)
                                if pd.notna(val.get(i, np.nan)) else 4.0)))
                     for i in no_visitados]
        else:
            preds = [(i, float(media.get(i, 3.5))) for i in no_visitados]
        metodo = "Cold start (media de reseñas)"

    preds.sort(key=lambda x: x[1], reverse=True)

    # ── Priorizar N_PATROCINADOS al inicio del listado ───────────────────────
    ids_sponsor = set()
    if con_patrocinados and "is_sponsored" in catalogo.columns:
        sponsor_all   = set(catalogo.loc[catalogo["is_sponsored"], id_col])
        preds_sponsor = [p for p in preds if p[0] in sponsor_all][:N_PATROCINADOS]
        ids_sponsor   = {p[0] for p in preds_sponsor}
        organico      = [p for p in preds if p[0] not in ids_sponsor]
        preds         = preds_sponsor + organico

    top = preds[:top_n]
    if not top:
        return SIN_RESULTADOS

    return [(int(i), round(float(s), 2), i in ids_sponsor) for i, s in top], metodo


def _respuesta(user_id, categoria, resultado):
    """Convierte el resultado de _rankear en la respuesta JSON de la API."""
    if isinstance(resultado, str):  # SIN_RESULTADOS
        return jsonify({"user_id": user_id, "categoria": categoria,
                        "ids": [], "mensaje": resultado})
    top, metodo = resultado
    return jsonify({
        "user_id":    user_id,
        "categoria":  categoria,
        "metodo":     metodo,
        "ids":        [i for i, _, _ in top],
        "resultados": [{"id": i, "puntuacion_estimada": s, "patrocinado": p}
                       for i, s, p in top],
    })


def _params_comunes():
    """user_id (obligatorio) y top_n (opcional, por defecto 10)."""
    user_id = request.args.get("user_id", type=int)
    top_n   = request.args.get("top_n", default=10, type=int)
    return user_id, top_n


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok",
                    "gastro": len(gastro), "cultura": len(patrimonio),
                    "eventos": len(eventos)})


@app.route("/recomendaciones/gastro")
def recomendaciones_gastro():
    user_id, top_n = _params_comunes()
    if user_id is None:
        return jsonify({"error": "user_id es obligatorio"}), 400

    tipo_lugar = request.args.get("tipo_lugar")
    provincia  = request.args.get("provincia")
    precio     = request.args.get("precio")

    catalogo = gastro
    if tipo_lugar:
        catalogo = catalogo[catalogo["Tipo de lugar"].map(_norm_txt) == _norm_txt(tipo_lugar)]
    if provincia:
        cod = _cod_provincia(provincia)
        if cod is None:
            return _respuesta(user_id, "gastro", SIN_RESULTADOS)
        catalogo = catalogo[catalogo["Provincia"].map(_cod_provincia) == cod]
    if precio:
        catalogo = catalogo[catalogo["Nivel precio"].map(_norm_txt) == _norm_txt(precio)]

    resultado = _rankear(user_id, model_gastro, reviews_gastro, catalogo,
                         "gastro_id", top_n, con_patrocinados=True)
    return _respuesta(user_id, "gastro", resultado)


@app.route("/recomendaciones/cultura")
def recomendaciones_cultura():
    user_id, top_n = _params_comunes()
    if user_id is None:
        return jsonify({"error": "user_id es obligatorio"}), 400

    tipo_lugar = request.args.get("tipo_lugar")
    provincia  = request.args.get("provincia")

    catalogo = patrimonio
    if tipo_lugar:
        catalogo = catalogo[catalogo["Tipo de lugar"].map(_norm_txt) == _norm_txt(tipo_lugar)]
    if provincia:
        cod = _cod_provincia(provincia)
        if cod is None:
            return _respuesta(user_id, "cultura", SIN_RESULTADOS)
        catalogo = catalogo[catalogo["Provincia"].map(_cod_provincia) == cod]

    resultado = _rankear(user_id, model_cultura, reviews_cultura, catalogo,
                         "culture_id", top_n, con_patrocinados=True)
    return _respuesta(user_id, "cultura", resultado)


@app.route("/recomendaciones/eventos")
def recomendaciones_eventos():
    user_id, top_n = _params_comunes()
    if user_id is None:
        return jsonify({"error": "user_id es obligatorio"}), 400

    tipo            = request.args.get("tipo")
    provincia       = request.args.get("provincia")
    solo_gratis     = request.args.get("gratis", "false").lower() == "true"
    solo_fin_semana = request.args.get("finde",  "false").lower() == "true"

    catalogo = eventos
    if tipo:
        catalogo = catalogo[catalogo["typeEs"].map(_norm_txt) == _norm_txt(tipo)]
    if provincia:
        cod = _cod_provincia(provincia)
        if cod is None:
            return _respuesta(user_id, "eventos", SIN_RESULTADOS)
        catalogo = catalogo[catalogo["provinceNoraCode"] == int(cod)]
    if solo_gratis:
        catalogo = catalogo[catalogo["is_free"] == True]
    if solo_fin_semana:
        catalogo = catalogo[catalogo["is_weekend"] == True]

    resultado = _rankear(user_id, model_eventos, reviews_eventos, catalogo,
                         "event_id", top_n, con_patrocinados=False)
    return _respuesta(user_id, "eventos", resultado)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
