import os
import ast
import psycopg2
import pandas as pd

# ── 1. Leer CSV ──────────────────────────────────────────────────────────────
df = pd.read_csv('../data/gastronomia.csv')
print(f"Registros leídos: {len(df)}")

# ── 2. Normalizar municipios ─────────────────────────────────────────────────
conn = psycopg2.connect(host="localhost", database="postgres",
                        user="postgres", password="1234")
df_munis = pd.read_sql("SELECT id, nombre FROM shared.municipalities", conn)
conn.close()

df_munis['nombre_norm'] = df_munis['nombre'].str.lower().str.strip()
df['municipio_norm']    = df['Municipio'].str.lower().str.strip()

df = pd.merge(
    df,
    df_munis[['id', 'nombre_norm']],
    left_on='municipio_norm',
    right_on='nombre_norm',
    how='left'
)
df.rename(columns={'id': 'municipality_id'}, inplace=True)
df.drop(columns=['nombre_norm', 'municipio_norm'], inplace=True)

null_munis = df['municipality_id'].isna().sum()
print(f"Registros sin municipio (se descartarán): {null_munis}")
df = df.dropna(subset=['municipality_id'])
df['municipality_id'] = df['municipality_id'].astype('int64')

# ── 3. Mapear columnas ───────────────────────────────────────────────────────
# El CSV no tiene external_id propio → lo dejamos NULL (UNIQUE permite múltiples NULLs en Postgres)
df_db = pd.DataFrame({
    'nombre':                df['Nombre'],
    'descripcion':           df['Descripcion'],
    'municipality_id':       df['municipality_id'],
    'lat':                   df['lat'],
    'lng':                   df['lon'],
    'type':                  df['Tipo de lugar'],    # Restaurante, Asador, Sidreria…
    'entorno':               df['Entorno'],
    'email':                 df['Email'],
    'web':                   df['WEB'],
    'web_euskadi':           df['URL amigable'],
    'calidad':               df['Calidad'].fillna(0).astype(bool),
    'url_imagen':            df['url_imagen'],
    'valoracion':            pd.to_numeric(df['valoracion'], errors='coerce'),
    'num_resenas':           pd.to_numeric(df['num_resenas'], errors='coerce').astype('Int64'),
    'nivel_precio':          df['Nivel precio'],
    'national_phone_number': df['Teléfono'],
    'is_sponsored':          df['Patrocinado'].fillna(0).astype(bool),
    'active':                df['Active'].fillna(1).astype(bool),
})

# Truncar campos que tienen límite en el schema
df_db['email']                 = df_db['email'].str[:100]
df_db['national_phone_number'] = df_db['national_phone_number'].str[:20]
df_db['nivel_precio']          = df_db['nivel_precio'].str[:50]
df_db['entorno']               = df_db['entorno'].str[:100]
df_db['type']                  = df_db['type'].str[:50]

print(f"Registros a insertar: {len(df_db)}")

# ── 4. Insertar ──────────────────────────────────────────────────────────────
cols         = ", ".join(df_db.columns)
placeholders = ", ".join(["%s"] * len(df_db.columns))

query_insert = f"""
    INSERT INTO market_data.gastronomy ({cols})
    VALUES ({placeholders})
    ON CONFLICT DO NOTHING;
"""

records = df_db.where(pd.notnull(df_db), None).values.tolist()
# Int64 → int nativo para psycopg2
records = [
    [int(v) if isinstance(v, (pd.NA.__class__,)) else v for v in row]
    for row in records
]

try:
    conn = psycopg2.connect(
        host="localhost", database="postgres",
        user="postgres", password="1234",
        options="-c client_encoding=UTF8"
    )
    cur = conn.cursor()
    cur.executemany(query_insert, records)
    conn.commit()
    print(f"✅ {cur.rowcount} registros insertados.")
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals():
        cur.close()
        conn.close()