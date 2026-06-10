#!/usr/bin/env python3
"""
contexto_db.py - Extrae el esquema y filas de ejemplo de una base de datos
PostgreSQL en formato Markdown, listo para compartir.

Pensado para preparar el refactor CSV -> DB de SustraiApp: vuelca catalogos,
interacciones y taxonomia sin exponer PII (emails, hashes, telefonos...).

Es de SOLO LECTURA: no crea, modifica ni borra nada.

Uso (PowerShell):
    python contexto_db.py
    python contexto_db.py --tables "catalogo*,interacciones,intereses"
    python contexto_db.py --rows 5 --output contexto_db.md
    python contexto_db.py --url "postgresql+psycopg2://user:pass@host:5432/db"
    python contexto_db.py --no-redact          # desactiva la redaccion de PII
    python contexto_db.py --no-counts          # no calcula count(*) por tabla

Conexion:
    1. --url tiene prioridad si se pasa.
    2. Si no, lee la variable de entorno DATABASE_URL (admite fichero .env).
    3. Si no, intenta construirla con DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD.

Requisitos:
    pip install sqlalchemy psycopg2-binary
    (opcional) pip install python-dotenv   # para leer .env automaticamente
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import os
import sys
from decimal import Decimal

try:
    from dotenv import load_dotenv  # opcional
    load_dotenv()
except ImportError:
    pass

try:
    from sqlalchemy import create_engine, inspect, text
    from sqlalchemy.engine import Engine
except ImportError:
    sys.exit(
        "Falta SQLAlchemy. Instala con:\n"
        "    pip install sqlalchemy psycopg2-binary"
    )


# --- Columnas que se redactan por defecto (coincidencia por subcadena) ---------
PATRONES_PII = (
    "email", "mail", "correo",
    "password", "passwd", "pass", "pwd",
    "hash", "salt", "token", "secret", "api_key", "apikey",
    "phone", "telefono", "tel", "movil",
    "dni", "nif", "nie", "iban", "tarjeta", "card", "cvv",
    "direccion", "address",
)

MAX_LEN_VALOR = 50  # trunca valores largos en las filas de ejemplo
ESQUEMAS_SISTEMA = {"information_schema", "pg_catalog", "pg_toast"}
DB_HOST="localhost"

def construir_url(args: argparse.Namespace) -> str:
    """Resuelve la cadena de conexion segun prioridad: --url > env > partes."""
    if args.url:
        return args.url

    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    host = os.getenv("DB_HOST")
    if host:
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "sustraiapp")
        user = os.getenv("DB_USER", "postgres")
        pwd = os.getenv("DB_PASSWORD", "postgres")
        cred = f"{user}:{pwd}@" if user else ""
        return f"postgresql+psycopg2://{cred}{host}:{port}/{name}"

    sys.exit(
        "No encuentro la conexion. Pasa --url o define DATABASE_URL "
        "(o DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD)."
    )


def es_columna_pii(nombre: str) -> bool:
    n = nombre.lower()
    return any(p in n for p in PATRONES_PII)


def formatear_valor(valor, redactar: bool, columna: str) -> str:
    if valor is None:
        return "NULL"
    if redactar and es_columna_pii(columna):
        return "‹oculto›"
    if isinstance(valor, (bytes, bytearray, memoryview)):
        return f"‹binario {len(bytes(valor))} bytes›"
    if isinstance(valor, Decimal):
        valor = str(valor)
    texto = str(valor).replace("\n", " ").replace("\r", " ")
    if len(texto) > MAX_LEN_VALOR:
        texto = texto[: MAX_LEN_VALOR - 1] + "…"
    return texto


def seleccionar_tablas(todas: list[str], filtro: str | None) -> list[str]:
    """Filtra tablas por patrones separados por comas (admite * y %)."""
    if not filtro:
        return todas
    patrones = [p.strip().replace("%", "*") for p in filtro.split(",") if p.strip()]
    seleccion = []
    for t in todas:
        if any(fnmatch.fnmatch(t, p) for p in patrones):
            seleccion.append(t)
    return seleccion


def describir_tabla(
    engine: Engine,
    insp,
    tabla: str,
    schema: str | None,
    n_filas: int,
    redactar: bool,
    contar: bool,
) -> str:
    titulo = f"{schema}.{tabla}" if schema else tabla
    out: list[str] = [f"### Tabla `{titulo}`\n"]

    # --- recuento de filas ---
    table_ref = f'"{tabla}"' if not schema else f'"{schema}"."{tabla}"'
    if contar:
        try:
            with engine.connect() as conn:
                total = conn.execute(
                    text(f"SELECT count(*) FROM {table_ref}")
                ).scalar()
            out.append(f"_Filas totales: {total}_\n")
        except Exception as e:  # noqa: BLE001
            out.append(f"_Filas totales: no disponible ({e.__class__.__name__})_\n")

    # --- claves para anotar columnas ---
    try:
        pk_cols = set(insp.get_pk_constraint(tabla, schema=schema).get("constrained_columns") or [])
    except Exception:  # noqa: BLE001
        pk_cols = set()

    fk_map: dict[str, str] = {}
    try:
        for fk in insp.get_foreign_keys(tabla, schema=schema):
            destino = fk.get("referred_table")
            destino_schema = fk.get("referred_schema")
            ref_cols = fk.get("referred_columns") or []
            for i, col in enumerate(fk.get("constrained_columns") or []):
                ref = ref_cols[i] if i < len(ref_cols) else "?"
                target = f"{destino_schema}.{destino}" if destino_schema else destino
                fk_map[col] = f"{target}.{ref}"
    except Exception:  # noqa: BLE001
        pass

    # --- columnas ---
    out.append("\n**Columnas:**\n")
    out.append("| Columna | Tipo | Nulo | Notas |")
    out.append("|---|---|---|---|")
    columnas = insp.get_columns(tabla, schema=schema)
    for col in columnas:
        nombre = col["name"]
        tipo = str(col["type"])
        nulo = "sí" if col.get("nullable", True) else "NO"
        notas = []
        if nombre in pk_cols:
            notas.append("PK")
        if nombre in fk_map:
            notas.append(f"FK → {fk_map[nombre]}")
        if es_columna_pii(nombre):
            notas.append("PII (redactada)")
        out.append(f"| `{nombre}` | {tipo} | {nulo} | {', '.join(notas)} |")

    # --- filas de ejemplo ---
    if n_filas > 0:
        nombres = [c["name"] for c in columnas]
        try:
            with engine.connect() as conn:
                filas = conn.execute(
                    text(f"SELECT * FROM {table_ref} LIMIT :n"), {"n": n_filas}
                ).fetchall()
        except Exception as e:  # noqa: BLE001
            out.append(f"\n_Filas de ejemplo: error ({e})_\n")
            return "\n".join(out) + "\n"

        if filas:
            out.append(f"\n**Filas de ejemplo (máx. {n_filas}):**\n")
            out.append("| " + " | ".join(nombres) + " |")
            out.append("|" + "|".join("---" for _ in nombres) + "|")
            for fila in filas:
                celdas = [
                    formatear_valor(v, redactar, nombres[i])
                    for i, v in enumerate(fila)
                ]
                out.append("| " + " | ".join(celdas) + " |")
        else:
            out.append("\n_Sin filas._\n")

    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vuelca esquema + filas de ejemplo de PostgreSQL a Markdown."
    )
    parser.add_argument("--url", help="Cadena de conexion SQLAlchemy.")
    parser.add_argument(
        "--tables",
        help='Patrones separados por comas, p.ej. "catalogo*,interacciones".',
    )
    parser.add_argument(
        "--rows", type=int, default=3, help="Filas de ejemplo por tabla (def. 3, 0 = ninguna)."
    )
    parser.add_argument(
        "--output", default="contexto_db.md", help="Fichero de salida (def. contexto_db.md)."
    )
    parser.add_argument(
        "--schema", default=None, help="Esquema de PostgreSQL (def. el de por defecto)."
    )
    parser.add_argument(
        "--no-redact", action="store_true", help="No redactar columnas con pinta de PII."
    )
    parser.add_argument(
        "--no-counts", action="store_true", help="No calcular count(*) por tabla."
    )
    args = parser.parse_args()

    redactar = not args.no_redact
    contar = not args.no_counts

    url = construir_url(args)
    try:
        engine = create_engine(url)
        insp = inspect(engine)
        # toca la conexion para fallar pronto y con mensaje claro
        with engine.connect():
            pass
    except Exception as e:  # noqa: BLE001
        sys.exit(f"No pude conectar a la DB: {e}")

    entradas: list[tuple[str | None, str]] = []
    if args.schema:
        entradas = [(args.schema, t) for t in sorted(insp.get_table_names(schema=args.schema))]
    else:
        # 1) intenta search_path por defecto
        default_tables = sorted(insp.get_table_names(schema=None))
        entradas.extend((None, t) for t in default_tables)

        # 2) si no hay nada visible por defecto, recorre esquemas no del sistema
        if not entradas:
            esquemas = [
                s for s in insp.get_schema_names()
                if s not in ESQUEMAS_SISTEMA and not s.startswith("pg_")
            ]
            for esquema in sorted(esquemas):
                for tabla in sorted(insp.get_table_names(schema=esquema)):
                    entradas.append((esquema, tabla))

    if not entradas:
        sys.exit("No hay tablas visibles con esa conexion/esquema.")

    etiquetas = [f"{s}.{t}" if s else t for s, t in entradas]
    if args.tables:
        patrones = [p.strip().replace("%", "*") for p in args.tables.split(",") if p.strip()]
        seleccionadas: list[tuple[str | None, str]] = []
        for schema_name, tabla in entradas:
            etiqueta = f"{schema_name}.{tabla}" if schema_name else tabla
            if any(fnmatch.fnmatch(etiqueta, p) or fnmatch.fnmatch(tabla, p) for p in patrones):
                seleccionadas.append((schema_name, tabla))
    else:
        seleccionadas = entradas

    if not seleccionadas:
        sys.exit(
            f"Ningun nombre de tabla coincide con --tables. "
            f"Disponibles: {', '.join(etiquetas)}"
        )

    # --- cabecera del documento ---
    db_name = engine.url.database or "?"
    ahora = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    doc: list[str] = [
        f"# Contexto de base de datos — `{db_name}`",
        f"_Generado: {ahora} · {len(seleccionadas)} de {len(entradas)} tablas · "
        f"PII {'redactada' if redactar else 'SIN redactar'}_\n",
    ]
    if not redactar:
        doc.append(
            "> ⚠️ Has desactivado la redaccion de PII. Revisa el fichero antes "
            "de compartirlo.\n"
        )

    for schema_name, tabla in seleccionadas:
        etiqueta = f"{schema_name}.{tabla}" if schema_name else tabla
        print(f"Procesando {etiqueta}...", file=sys.stderr)
        doc.append(describir_tabla(engine, insp, tabla, schema_name, args.rows, redactar, contar))

    contenido = "\n".join(doc)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(contenido)

    print(
        f"\nListo: {args.output} ({len(seleccionadas)} tablas, "
        f"{len(contenido)} caracteres).",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
