"""
Generador de base de datos sintética - EVENTOS
Basado en buyer personas del proyecto y distribución poblacional de Euskadi:
  - Bizkaia: 50% | Gipuzkoa: 35% | Araba: 15%
Perfil principal: 45-65 años (con ~10% fuera del rango)
"""

import pandas as pd
import numpy as np
import random

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
SEED = 42
N_USERS = 2000
OUTPUT_FILE = "datos_eventos.csv"

np.random.seed(SEED)
random.seed(SEED)

# ─────────────────────────────────────────────
# MUNICIPIOS POR TERRITORIO (distribución realista)
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

# Pesos territoriales
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
# ~90% en rango 45-65, ~10% fuera (coherente con buyer personas)
def edad_aleatoria():
    if np.random.rand() < 0.90:
        return np.random.randint(45, 66)
    else:
        grupo = np.random.choice(["joven", "mayor"], p=[0.6, 0.4])
        if grupo == "joven":
            return np.random.randint(25, 45)
        else:
            return np.random.randint(66, 76)

# Sexo ligeramente más femenino (refleja los buyer personas)
def sexo_aleatorio():
    return np.random.choice(["F", "M"], p=[0.55, 0.45])

# ─────────────────────────────────────────────
# PREFERENCIAS POR BUYER PERSONA
# ─────────────────────────────────────────────
# Categorías de eventos disponibles
CATEGORIAS_EVENTO = [
    "Concierto_Festival",
    "Fiestas_Feria",
    "Teatro",
    "Danza",
    "Conferencia_Jornadas_Presentacion",
    "Cine_Audiovisuales",
    "Bertsolarismo",
    "Exposicion",
    "Formacion",
    "Concurso",
]

# Perfil de preferencias por categoría según buyer persona
# María (58, funcionaria, cultura, exposiciones) → HighCulture
# Ignacio (52, técnico, conciertos, fiestas)     → SocialFun
# Amaia (46, profesora, formación, museos, autenticidad) → Explorer

perfiles_evento = {
    "HighCulture": {
        "Concierto_Festival": 0.60,
        "Fiestas_Feria": 0.35,
        "Teatro": 0.80,
        "Danza": 0.65,
        "Conferencia_Jornadas_Presentacion": 0.55,
        "Cine_Audiovisuales": 0.70,
        "Bertsolarismo": 0.45,
        "Exposicion": 0.85,
        "Formacion": 0.50,
        "Concurso": 0.25,
    },
    "SocialFun": {
        "Concierto_Festival": 0.85,
        "Fiestas_Feria": 0.80,
        "Teatro": 0.40,
        "Danza": 0.30,
        "Conferencia_Jornadas_Presentacion": 0.20,
        "Cine_Audiovisuales": 0.65,
        "Bertsolarismo": 0.55,
        "Exposicion": 0.30,
        "Formacion": 0.20,
        "Concurso": 0.60,
    },
    "Explorer": {
        "Concierto_Festival": 0.50,
        "Fiestas_Feria": 0.65,
        "Teatro": 0.55,
        "Danza": 0.50,
        "Conferencia_Jornadas_Presentacion": 0.70,
        "Cine_Audiovisuales": 0.60,
        "Bertsolarismo": 0.75,
        "Exposicion": 0.70,
        "Formacion": 0.80,
        "Concurso": 0.35,
    },
}

def asignar_perfil(sexo, edad, municipio):
    """Asigna un perfil con probabilidades basadas en sexo, edad y municipio."""
    if sexo == "F" and edad >= 50:
        return np.random.choice(["HighCulture", "Explorer", "SocialFun"], p=[0.50, 0.35, 0.15])
    elif sexo == "M" and 45 <= edad <= 60:
        return np.random.choice(["SocialFun", "HighCulture", "Explorer"], p=[0.45, 0.30, 0.25])
    else:
        return np.random.choice(["HighCulture", "SocialFun", "Explorer"], p=[0.35, 0.35, 0.30])

def generar_preferencias_evento(perfil):
    """Genera valores binarios de preferencia (1 = interesa, 0 = no) con algo de ruido."""
    probs = perfiles_evento[perfil]
    prefs = {}
    for cat in CATEGORIAS_EVENTO:
        p = probs[cat]
        # Añadir pequeño ruido gaussiano para naturalidad
        p_noisy = np.clip(p + np.random.normal(0, 0.08), 0.05, 0.95)
        prefs[cat] = int(np.random.rand() < p_noisy)
    return prefs

def generar_review(prefs):
    """
    Target: puntuación de satisfacción (1-5) correlacionada con el nº de intereses.
    Simula que a más afinidad temática, mayor satisfacción.
    """
    n_intereses = sum(prefs.values())
    base = 2.5 + (n_intereses / len(CATEGORIAS_EVENTO)) * 2.0
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

    prefs = generar_preferencias_evento(perfil)
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

# Reordenar columnas según tabla original
cols = (
    ["Id_user", "Sexo", "Edad", "Municipio"]
    + CATEGORIAS_EVENTO
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
print(df[CATEGORIAS_EVENTO].mean().sort_values(ascending=False).map("{:.2f}".format))
print(f"\n--- Distribución Target_Review ---")
print(df["Target_Review"].value_counts().sort_index())
