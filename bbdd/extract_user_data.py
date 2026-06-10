import os
import psycopg2
import pandas as pd

# Forzar UTF8 en Windows antes de cualquier conexión
os.environ['PYTHONUTF8'] = '1'

query = """
SELECT 
    c.column_name AS feature,
    t.table_name AS tabla,
    c.column_name AS registro,
    c.data_type AS formato_origen,
    CASE 
        WHEN c.data_type IN ('integer', 'bigint', 'smallint') THEN 'int'
        WHEN c.data_type LIKE '%char%' OR c.data_type = 'text' THEN 'str'
        WHEN c.data_type = 'boolean' THEN 'bool'
        ELSE c.data_type
    END AS cambio_de_formato
FROM information_schema.columns c
JOIN information_schema.tables t 
    ON c.table_name = t.table_name 
    AND c.table_schema = t.table_schema
WHERE t.table_schema = 'public'
  AND t.table_type = 'BASE TABLE'
ORDER BY t.table_name, c.ordinal_position;
"""

try:
    # Conexión directa con psycopg2 (sin SQLAlchemy)
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="1234",
        options="-c client_encoding=UTF8"
    )
    
    # pandas acepta conexiones psycopg2 nativas directamente
    df_map = pd.read_sql(query, conn)
    print("✅ Extracción exitosa:")
    print(df_map.head())
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()