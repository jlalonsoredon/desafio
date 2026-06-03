"""
Generador de base de datos sintética - GASTRONOMÍA
Basado en buyer personas del proyecto y distribución poblacional de Euskadi:
  - Bizkaia: 50% | Gipuzkoa: 35% | Araba: 15%
Perfil principal: 45-65 años (con ~10% fuera del rango)

Categorías según tabla:
  Restaurantes (global), Restaurante, Asador, Sidrería,
  Bodegas, Queserías,
  Gourmet (global), Agricultura ecológica, Denominación de Origen,
  Eusko Label, Euskal Baserri
"""

import pandas as pd
import numpy as np
import random

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
SEED = 42
N_USERS = 2000
OUTPUT_FILE = "datos_gastronomia.csv"

np.random.seed(SEED)
random.seed(SEED)

# ─────────────────────────────────────────────
# MUNICIPIOS POR TERRITORIO
# ─────────────────────────────────────────────
municipios = {
    "Bizkaia": {
        "Bilbao": 0.40,
        "Getxo": 0.10,
        "Barakaldo": 0.12,
        "Basauri": 0.07,
        "Leioa": 0.07,
        "Portugalete": 0.07,
        "Santurtzi": 0.06,
        "Durango": 0.06,
        "Bermeo": 0.03,
        "Mungia": 0.02,
    },
    "Gipuzkoa": {
        "Donostia-San Sebastián": 0.38,
        "Irun": 0.14,
        "Errenteria": 0.10,
        "Zarautz": 0.08,
        "Eibar": 0.08,
        "Tolosa": 0.08,
        "Hernani": 0.07,
        "Azpeitia": 0.04,
        "Beasain": 0.03,
    },
    "Araba": {
        "Vitoria-Gasteiz": 0.75,
        "Llodio": 0.12,
        "Amurrio": 0.08,
        "Salvatierra": 0.05,
    },
}

territorio_pesos = {"Bizkaia": 0.50, "Gipuzkoa": 0.35, "Araba": 0.15}

def municipio_aleatorio():
    territorio = np.random.choice(
        list(territorio_pesos.keys()),
        p=list(territorio_pesos.values())
    )
    munis = municipios[territorio]
    return np.random.choice(list(munis.keys()), p=list(munis.values()))

# ─────────────────────────────────────────────
# EDAD Y SEXO
# ─────────────────────────────────────────────
def edad_aleatoria():
    if np.random.rand() < 0.90:
        return np.random.randint(45, 66)
    else:
        grupo = np.random.choice(["joven", "mayor"], p=[0.6, 0.4])
        return np.random.randint(25, 45) if grupo == "joven" else np.random.randint(66, 76)

def sexo_aleatorio():
    return np.random.choice(["F", "M"], p=[0.55, 0.45])

# ─────────────────────────────────────────────
# CATEGORÍAS Y PERFILES GASTRONÓMICOS
# ─────────────────────────────────────────────
# Columnas tal como aparecen en la tabla (nombres limpios para CSV)
CATEGORIAS_GASTRO = [
    "Restaurantes",
    "Restaurantes_Restaurante",
    "Restaurantes_Asador",
    "Restaurantes_Sidreria",
    "Bodegas",
    "Queserias",
    "Gourmet",
    "Gourmet_Agricultura_ecologica",
    "Gourmet_Denominacion_de_Origen",
    "Gourmet_Eusko_Label",
    "Gourmet_Euskal_Baserri",
]

# María (HighCulture): buena mesa, ambientes cuidados, servicio, producto
# Ignacio (SocialFun): asador, sidrerías, honestidad, sin humos
# Amaia (Explorer): producto local, ecológico, Eusko Label, Baserri, mercados

perfiles_gastro = {
    "HighCulture": {
        "Restaurantes": 0.90,
        "Restaurantes_Restaurante": 0.85,
        "Restaurantes_Asador": 0.65,
        "Restaurantes_Sidreria": 0.55,
        "Bodegas": 0.70,
        "Queserias": 0.60,
        "Gourmet": 0.80,
        "Gourmet_Agricultura_ecologica": 0.55,
        "Gourmet_Denominacion_de_Origen": 0.75,
        "Gourmet_Eusko_Label": 0.65,
        "Gourmet_Euskal_Baserri": 0.60,
    },
    "SocialFun": {
        "Restaurantes": 0.88,
        "Restaurantes_Restaurante": 0.70,
        "Restaurantes_Asador": 0.90,
        "Restaurantes_Sidreria": 0.85,
        "Bodegas": 0.60,
        "Queserias": 0.35,
        "Gourmet": 0.45,
        "Gourmet_Agricultura_ecologica": 0.25,
        "Gourmet_Denominacion_de_Origen": 0.50,
        "Gourmet_Eusko_Label": 0.55,
        "Gourmet_Euskal_Baserri": 0.60,
    },
    "Explorer": {
        "Restaurantes": 0.85,
        "Restaurantes_Restaurante": 0.70,
        "Restaurantes_Asador": 0.60,
        "Restaurantes_Sidreria": 0.65,
        "Bodegas": 0.55,
        "Queserias": 0.70,
        "Gourmet": 0.80,
        "Gourmet_Agricultura_ecologica": 0.85,
        "Gourmet_Denominacion_de_Origen": 0.70,
        "Gourmet_Eusko_Label": 0.88,
        "Gourmet_Euskal_Baserri": 0.90,
    },
}

def asignar_perfil(sexo, edad, municipio):
    if sexo == "F" and edad >= 50:
        return np.random.choice(["HighCulture", "Explorer", "SocialFun"], p=[0.50, 0.35, 0.15])
    elif sexo == "M" and 45 <= edad <= 60:
        return np.random.choice(["SocialFun", "HighCulture", "Explorer"], p=[0.45, 0.30, 0.25])
    else:
        return np.random.choice(["HighCulture", "SocialFun", "Explorer"], p=[0.35, 0.35, 0.30])

def generar_preferencias_gastro(perfil):
    """Genera preferencias binarias con coherencia interna bidireccional:
    - Si padre = 0 → todas las hijas = 0 (no puede interesar lo específico si no interesa lo general).
    - Si alguna hija = 1 → padre = 1 (consistencia ascendente, por si el padre salió 0 por azar).
    """
    probs = perfiles_gastro[perfil]
    prefs = {}
    for cat in CATEGORIAS_GASTRO:
        p = probs[cat]
        p_noisy = np.clip(p + np.random.normal(0, 0.07), 0.05, 0.95)
        prefs[cat] = int(np.random.rand() < p_noisy)

    rest_subs = ["Restaurantes_Restaurante", "Restaurantes_Asador", "Restaurantes_Sidreria"]
    gourmet_subs = ["Gourmet_Agricultura_ecologica", "Gourmet_Denominacion_de_Origen",
                    "Gourmet_Eusko_Label", "Gourmet_Euskal_Baserri"]

    # Si padre = 0 → hijas = 0
    if prefs["Restaurantes"] == 0:
        for k in rest_subs:
            prefs[k] = 0
    if prefs["Gourmet"] == 0:
        for k in gourmet_subs:
            prefs[k] = 0

    # Si alguna hija = 1 → padre = 1 (coherencia ascendente)
    if any(prefs[k] for k in rest_subs):
        prefs["Restaurantes"] = 1
    if any(prefs[k] for k in gourmet_subs):
        prefs["Gourmet"] = 1

    return prefs

def generar_review(prefs):
    """
    Target: puntuación 1-5.
    Ponderamos más los campos gourmet (mayor discriminación de calidad).
    """
    pesos = {
        "Restaurantes": 0.5,
        "Restaurantes_Restaurante": 1.0,
        "Restaurantes_Asador": 1.0,
        "Restaurantes_Sidreria": 1.0,
        "Bodegas": 0.8,
        "Queserias": 0.8,
        "Gourmet": 0.5,
        "Gourmet_Agricultura_ecologica": 1.2,
        "Gourmet_Denominacion_de_Origen": 1.2,
        "Gourmet_Eusko_Label": 1.2,
        "Gourmet_Euskal_Baserri": 1.2,
    }
    score = sum(prefs[k] * pesos[k] for k in CATEGORIAS_GASTRO)
    max_score = sum(pesos.values())
    base = 2.5 + (score / max_score) * 2.0
    ruido = np.random.normal(0, 0.4)
    return int(np.clip(round(base + ruido), 1, 5))

# ─────────────────────────────────────────────
# GENERACIÓN
# ─────────────────────────────────────────────
registros = []
for i in range(1, N_USERS + 1):
    sexo = sexo_aleatorio()
    edad = edad_aleatoria()
    municipio = municipio_aleatorio()
    perfil = asignar_perfil(sexo, edad, municipio)

    prefs = generar_preferencias_gastro(perfil)
    review = generar_review(prefs)

    fila = {
        "Id_user": f"U{i:05d}",
        "Sexo": sexo,
        "Edad": edad,
        "Municipio": municipio,
        **prefs,
        "Target_Review": review,
    }
    registros.append(fila)

df = pd.DataFrame(registros)

cols = (
    ["Id_user", "Sexo", "Edad", "Municipio"]
    + CATEGORIAS_GASTRO
    + ["Target_Review"]
)
df = df[cols]

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

# ─────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────
print(f"✅  Archivo generado: {OUTPUT_FILE}")
print(f"    Registros: {len(df)}")
print(f"\n--- Distribución de sexo ---")
print(df["Sexo"].value_counts(normalize=True).map("{:.1%}".format))
print(f"\n--- Distribución de edad ---")
bins = [0, 24, 44, 65, 100]
labels = ["<25", "25-44", "45-65", "65+"]
print(pd.cut(df["Edad"], bins=bins, labels=labels).value_counts(normalize=True).sort_index().map("{:.1%}".format))
print(f"\n--- Top municipios ---")
print(df["Municipio"].value_counts().head(6))
print(f"\n--- Media de preferencias por categoría ---")
print(df[CATEGORIAS_GASTRO].mean().sort_values(ascending=False).map("{:.2f}".format))
print(f"\n--- Distribución Target_Review ---")
print(df["Target_Review"].value_counts().sort_index())
