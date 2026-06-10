import math
import psycopg2
import pandas as pd

# ── 1. Leer CSV ──────────────────────────────────────────────────────────────
df = pd.read_csv('../data/patrimonio.csv')
print(f"Registros leídos: {len(df)}")

# ── 2. Normalizar municipios ─────────────────────────────────────────────────
conn = psycopg2.connect(host="localhost", database="sustraiapp",
                        user="postgres", password="postgres")
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

# ── 3. Función de limpieza de valores ────────────────────────────────────────
def clean(v):
    """Convierte cualquier valor problemático a un tipo que psycopg2 entienda."""
    # NaN / NaT / NA → None
    if v is None:
        return None
    if v is pd.NA or v is pd.NaT:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    # numpy int → int nativo
    if hasattr(v, 'item'):
        return v.item()
    # strings "nan", "None", "<NA>" que quedaron como texto
    if isinstance(v, str) and v.strip().lower() in ('nan', 'none', '<na>', ''):
        return None
    return v

# ── 4. Mapear columnas ───────────────────────────────────────────────────────
def safe_str(series, max_len):
    """Convierte a string, limpia nulos y trunca."""
    return series.astype(str).str.strip().str[:max_len].replace(
        {'nan': None, 'None': None, '<NA>': None, '': None}
    )

df_db = pd.DataFrame({
    'fuente':               'Manual',
    'nombre':               df['Nombre'],
    'tipo_lugar':           df['Tipo de lugar'],
    'tipo_cultura':         df['Tipo de Cultura'],
    'descripcion':          df['Descripción'],
    'telefono':             safe_str(df['Teléfono'], 50),
    'email':                safe_str(df['Email'], 100),
    'web':                  safe_str(df['WEB'], 255),
    'web_amigable':         safe_str(df['URL amigable'], 255),
    'imagen_url':           df['url_imagen'],
    'municipality_id':      df['municipality_id'].astype(int),
    'direccion':            safe_str(df['Dirección'], 255),
    'codigo_postal':        safe_str(df['Postal Code'].astype(str), 10),
    'visita_guiada':        df['Visita Guiada'].fillna(0).astype(bool),
    'capacidad':            pd.to_numeric(df['Capacidad'], errors='coerce'),
    'tienda':               df['Tienda'].fillna(0).astype(bool),
    'lat':                  pd.to_numeric(df['lat'], errors='coerce'),
    'lng':                  pd.to_numeric(df['lon'], errors='coerce'),
    'valoracion':           pd.to_numeric(df['valoracion'], errors='coerce'),
    'numero_valoraciones':  pd.to_numeric(df['num_resenas'], errors='coerce'),
    'is_sponsored':         df['Patrocinado'].fillna(0).astype(bool),
    'active':               df['Active'].fillna(1).astype(bool),
})

print(f"Registros a insertar: {len(df_db)}")

# ── 5. Convertir a lista limpia ──────────────────────────────────────────────
records = [
    [clean(v) for v in row]
    for row in df_db.itertuples(index=False, name=None)
]

# ── 6. Insertar ──────────────────────────────────────────────────────────────
cols         = ", ".join(df_db.columns)
placeholders = ", ".join(["%s"] * len(df_db.columns))

query_insert = f"""
    INSERT INTO market_data.culture ({cols})
    VALUES ({placeholders})
    ON CONFLICT DO NOTHING;
"""

try:
    conn = psycopg2.connect(
        host="localhost", database="sustraiapp",
        user="postgres", password="postgres",
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