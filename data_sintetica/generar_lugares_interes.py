"""
Generador de base de datos sintética - LUGARES DE INTERÉS
Basado en buyer personas del proyecto y distribución poblacional de Euskadi:
  - Bizkaia: 50% | Gipuzkoa: 35% | Araba: 15%
Perfil principal: 45-65 años (con ~10% fuera del rango)

Categorías según tabla:
  Museos (global), Historia, Ciencias Naturales, Arte, Etnografía,
  Patrimonio cultural
"""

import pandas as pd
import numpy as np
import random

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
SEED = 42
N_USERS = 2000
OUTPUT_FILE = "datos_lugares_interes.csv"

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
# CATEGORÍAS Y PERFILES
# ─────────────────────────────────────────────
CATEGORIAS_LUGARES = [
    "Museos",
    "Museos_Historia",
    "Museos_Ciencias_Naturales",
    "Museos_Arte",
    "Museos_Etnografia",
    "Patrimonio_cultural",
]

# María (HighCulture, 58): museos de arte, patrimonio, exposiciones
# Ignacio (SocialFun, 52): historia local, patrimonio puntual
# Amaia (Explorer, 46, profesora): etnografía, historia, ciencias naturales, patrimonio

perfiles_lugares = {
    "HighCulture": {
        "Museos": 0.90,
        "Museos_Historia": 0.70,
        "Museos_Ciencias_Naturales": 0.45,
        "Museos_Arte": 0.90,
        "Museos_Etnografia": 0.55,
        "Patrimonio_cultural": 0.80,
    },
    "SocialFun": {
        "Museos": 0.55,
        "Museos_Historia": 0.65,
        "Museos_Ciencias_Naturales": 0.30,
        "Museos_Arte": 0.35,
        "Museos_Etnografia": 0.40,
        "Patrimonio_cultural": 0.60,
    },
    "Explorer": {
        "Museos": 0.85,
        "Museos_Historia": 0.80,
        "Museos_Ciencias_Naturales": 0.70,
        "Museos_Arte": 0.65,
        "Museos_Etnografia": 0.88,
        "Patrimonio_cultural": 0.90,
    },
}

def asignar_perfil(sexo, edad, municipio):
    if sexo == "F" and edad >= 50:
        return np.random.choice(["HighCulture", "Explorer", "SocialFun"], p=[0.50, 0.35, 0.15])
    elif sexo == "M" and 45 <= edad <= 60:
        return np.random.choice(["SocialFun", "HighCulture", "Explorer"], p=[0.45, 0.30, 0.25])
    else:
        return np.random.choice(["HighCulture", "SocialFun", "Explorer"], p=[0.35, 0.35, 0.30])

def generar_preferencias_lugares(perfil):
    """Genera preferencias binarias con coherencia interna bidireccional:
    - Si padre = 0 → todas las hijas = 0 (no puede interesar lo específico si no interesa lo general).
    - Si alguna hija = 1 → padre = 1 (consistencia ascendente, por si el padre salió 0 por azar).
    """
    probs = perfiles_lugares[perfil]
    prefs = {}
    for cat in CATEGORIAS_LUGARES:
        p = probs[cat]
        p_noisy = np.clip(p + np.random.normal(0, 0.07), 0.05, 0.95)
        prefs[cat] = int(np.random.rand() < p_noisy)

    sub_museos = ["Museos_Historia", "Museos_Ciencias_Naturales", "Museos_Arte", "Museos_Etnografia"]

    # Si padre = 0 → hijas = 0
    if prefs["Museos"] == 0:
        for k in sub_museos:
            prefs[k] = 0

    # Si alguna hija = 1 → padre = 1 (coherencia ascendente)
    if any(prefs[k] for k in sub_museos):
        prefs["Museos"] = 1

    return prefs

def generar_review(prefs):
    """
    Target 1-5. Ponderamos patrimonio cultural y arte con mayor peso
    (suelen ser las visitas más memorables y determinantes del NPS).
    """
    pesos = {
        "Museos": 0.5,
        "Museos_Historia": 1.0,
        "Museos_Ciencias_Naturales": 0.9,
        "Museos_Arte": 1.2,
        "Museos_Etnografia": 1.1,
        "Patrimonio_cultural": 1.3,
    }
    score = sum(prefs[k] * pesos[k] for k in CATEGORIAS_LUGARES)
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

    prefs = generar_preferencias_lugares(perfil)
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
    + CATEGORIAS_LUGARES
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
print(df[CATEGORIAS_LUGARES].mean().sort_values(ascending=False).map("{:.2f}".format))
print(f"\n--- Distribución Target_Review ---")
print(df["Target_Review"].value_counts().sort_index())
