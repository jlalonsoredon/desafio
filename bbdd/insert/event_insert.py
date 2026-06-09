import pandas as pd
import os
import psycopg2
import pandas as pd
from datetime import datetime


df = pd.read_csv('data/eventos.csv')

df['precio_eur'] = df['price_eur'].fillna(0).astype(str).str[:2].astype(float)

df['municipalityEs'] = df['municipalityEs'].str.replace(' / ', '-')
df['municipalityEs'] = df['municipalityEs'].str.replace('/', '-')

def smart_truncate(text, max_len=100):
    if pd.isna(text) or len(str(text)) <= max_len:
        return text
    
    s = str(text)[:max_len]
    # Busca el último espacio dentro de los 100 primeros caracteres
    last_space = s.rfind(' ')
    
    # Si hay un espacio, corta ahí. Si no (palabra muy larga), corta a lo bestia a 100.
    return s[:last_space] if last_space != -1 else s

df['openingHoursEs'] = df['openingHoursEs'].apply(smart_truncate)

conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="1234")

df_munis = pd.read_sql("SELECT id, nombre FROM shared.municipalities", conn)
conn.close()

df_munis['nombre_norm'] = df_munis['nombre'].str.lower().str.strip()
df['municipio_norm'] = df['municipalityEs'].str.lower().str.strip()

# 1. Cruzamos por el nombre normalizado y guardamos el resultado en df
df = pd.merge(
    df, 
    df_munis[['id', 'nombre_norm']], 
    left_on='municipio_norm', 
    right_on='nombre_norm', 
    how='left'
)

# 2. Renombramos la columna 'id' de la BD a 'municipality_id'
df.rename(columns={'id': 'municipality_id'}, inplace=True)

# 3. Eliminamos las columnas temporales de normalización
df.drop(columns=['nombre_norm', 'municipio_norm'], inplace=True)

os.environ['PYTHONUTF8'] = '1'

column_mapping = {
    'id_Kulturklik': 'external_id',
    'typeEs': 'type',
    'subtipo': 'subtipo',
    'startDate': 'start_date',
    'endDate': 'end_date',
    'publicationDate': 'publication_date',
    'language': 'language',
    'openingHoursEs': 'opening_hours',
    'price_eur': 'price_eur',
    'is_free': 'is_free',
    'purchaseUrlEs': 'purchase_url',
    'urlEventEs': 'url_event',
    'urlOnlineEs': 'url_online',
    'images': 'images',
    'online': 'online',
    'establishmentEs': 'establishment',
    'placeEs': 'place',
    'companyEs': 'company',
    'municipality_id': 'municipality_id'
}

# Seleccionar y renombrar columnas
df_db = df[list(column_mapping.keys())].rename(columns=column_mapping)

# 3. Limpieza y conversión de tipos
# Convertir fechas a datetime
date_cols = ['start_date', 'end_date', 'publication_date']
for col in date_cols:
    df_db[col] = pd.to_datetime(df_db[col], errors='coerce')
    
    # Asegurar que los booleanos sean correctos (si vienen como 0/1 o True/False)
bool_cols = ['is_free', 'online']
for col in bool_cols:
    if col in df_db.columns:
        df_db[col] = df_db[col].fillna(False).astype(bool)
        
        # Manejar nulls en campos numéricos
if 'price_eur' in df_db.columns:
    df_db['price_eur'] = pd.to_numeric(df_db['price_eur'], errors='coerce')
    
    import psycopg2
from psycopg2.extras import Json

# 0. VERIFICAR Y LIMPIAR NULL EN municipality_id ANTES DE INSERTAR
print(f"Registros con municipality_id NULL: {df_db['municipality_id'].isna().sum()}")

# Opción A: Eliminar registros sin municipio
df_db = df_db.dropna(subset=['municipality_id'])
print(f"Registros después de eliminar sin municipio: {len(df_db)}")

# Asegurar que municipality_id es integer
df_db['municipality_id'] = df_db['municipality_id'].astype('int64')

# 1. Asegúrate de que la columna 'images' tenga objetos Python (listas/dicts), NO strings.
import ast
def to_obj(val):
    if pd.isna(val): return None
    if isinstance(val, str):
        try: return ast.literal_eval(val)
        except: return None
    return val

df_db['images'] = df_db['images'].apply(to_obj)

# 2. Preparar los registros
records = df_db.where(pd.notnull(df_db), None).values.tolist()

try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="1234",
        options="-c client_encoding=UTF8"
    )
    cur = conn.cursor()
    
    cols = ", ".join(df_db.columns)
    placeholders = ", ".join(["%s"] * len(df_db.columns))
    
    query_insert = f"""
        INSERT INTO market_data.events ({cols})
        VALUES ({placeholders})
        ON CONFLICT (external_id) DO NOTHING;
    """
    
    # Convertir la columna images a objeto Json explícito
    df_db['images'] = df_db['images'].apply(lambda x: Json(x) if x is not None else None)
    records = df_db.where(pd.notnull(df_db), None).values.tolist()
    
    cur.executemany(query_insert, records)
    conn.commit()
    print(f"✅ {cur.rowcount} registros insertados/actualizados.")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals():
        cur.close()
        conn.close()