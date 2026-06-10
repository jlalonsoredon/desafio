import os
import ast
import pandas as pd
import psycopg2
from psycopg2.extras import Json

df = pd.read_csv('data/gastronomia.csv')

# -------------------------------------------------------------
# Limpieza y normalización
# -------------------------------------------------------------

def smart_truncate(text, max_len=255):
    if pd.isna(text) or len(str(text)) <= max_len:
        return text
    s = str(text)[:max_len]
    last_space = s.rfind(' ')
    return s[:last_space] if last_space != -1 else s

df['Nombre']      = df['Nombre'].apply(lambda x: smart_truncate(x, 255))
df['Dirección']   = df['Dirección'].apply(lambda x: smart_truncate(x, 255))
df['Tipo de lugar'] = df['Tipo de lugar'].apply(lambda x: smart_truncate(x, 50))
df['Entorno']     = df['Entorno'].apply(lambda x: smart_truncate(x, 100))
df['Nivel precio'] = df['Nivel precio'].apply(lambda x: smart_truncate(x, 50))

# Booleanos
bool_cols = ['Calidad', 'Active', 'Patrocinado']
for col in bool_cols:
    df[col] = df[col].fillna(0).astype(int).astype(bool)

# Numéricos
df['valoracion']  = pd.to_numeric(df['valoracion'],  errors='coerce')
df['num_resenas'] = pd.to_numeric(df['num_resenas'],  errors='coerce').astype('Int64')
df['lat']         = pd.to_numeric(df['lat'], errors='coerce')
df['lon']         = pd.to_numeric(df['lon'], errors='coerce')

# -------------------------------------------------------------
# Mapeo de columnas CSV → BD
# -------------------------------------------------------------

column_mapping = {
    'Nombre':       'nombre',
    'Descripcion':  'descripcion',
    'Municipio':    'municipality',
    'Entorno':      'entorno',
    'Email':        'email',
    'Teléfono':     'national_phone_number',
    'WEB':          'web',
    'URL amigable': 'web_euskadi',
    'Calidad':      'calidad',
    'Tipo de lugar':'type',
    'Nivel precio': 'nivel_precio',
    'lat':          'lat',
    'lon':          'lng',
    'valoracion':   'valoracion',
    'num_resenas':  'num_resenas',
    'url_imagen':   'url_imagen',
    'Active':       'active',
    'Patrocinado':  'is_sponsored',
}

df_db = df[list(column_mapping.keys())].rename(columns=column_mapping)

# Eliminar filas sin nombre (campo obligatorio)
df_db = df_db.dropna(subset=['nombre'])
print(f"Registros a insertar: {len(df_db)}")

# -------------------------------------------------------------
# Inserción
# -------------------------------------------------------------

os.environ['PYTHONUTF8'] = '1'

try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="1234",
        options="-c client_encoding=UTF8"
    )
    cur = conn.cursor()

    cols         = ", ".join(df_db.columns)
    placeholders = ", ".join(["%s"] * len(df_db.columns))

    query_insert = f"""
        INSERT INTO market_data.gastronomy ({cols})
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING;
    """

    records = df_db.where(pd.notnull(df_db), None).values.tolist()

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