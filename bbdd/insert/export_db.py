import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from collections.abc import Mapping

import psycopg2
from psycopg2.extras import Json
from psycopg2.extensions import adapt


HOST = os.getenv("PGHOST", "localhost")
PORT = os.getenv("PGPORT", "5432")
DATABASE = os.getenv("PGDATABASE", "sustraiapp")
USER = os.getenv("PGUSER", "postgres")
PASSWORD = os.getenv("PGPASSWORD", "postgres")
OUTPUT_DIR = Path(__file__).resolve().parent / "exports"
SYSTEM_SCHEMAS = {"information_schema", "pg_catalog", "pg_toast"}


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def render_sql_value(value, cursor) -> str:
    if value is None:
        return "NULL"
    try:
        return cursor.mogrify("%s", (value,)).decode("utf-8")
    except Exception:
        if isinstance(value, Mapping):
            return cursor.mogrify("%s", (Json(dict(value)),)).decode("utf-8")
        return cursor.mogrify("%s", (Json(value),)).decode("utf-8")


def build_dump_command(output_file: Path) -> list[str]:
    return [
        "pg_dump",
        "--host",
        HOST,
        "--port",
        PORT,
        "--username",
        USER,
        "--format",
        "plain",
        "--no-owner",
        "--no-privileges",
        "--file",
        str(output_file),
        DATABASE,
    ]


def export_database() -> Path:
    pg_dump_path = shutil.which("pg_dump")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"{DATABASE}_{timestamp}.sql"

    if pg_dump_path:
        env = os.environ.copy()
        env["PGPASSWORD"] = PASSWORD

        command = build_dump_command(output_file)
        subprocess.run(command, check=True, env=env)
        return output_file

    dump_database_logical(output_file)
    return output_file


def dump_database_logical(output_file: Path) -> None:
    connection = psycopg2.connect(
        host=HOST,
        port=PORT,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        options="-c client_encoding=UTF8",
    )

    try:
        with connection, connection.cursor() as cursor, output_file.open("w", encoding="utf-8", newline="\n") as output:
            output.write("-- Backup lógico generado por export_db.py\n")
            output.write(f"-- Base de datos: {DATABASE}\n\n")
            output.write("SET client_encoding = 'UTF8';\n")
            output.write("SET standard_conforming_strings = on;\n\n")

            cursor.execute(
                """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT IN (%s, %s, %s)
                ORDER BY schema_name
                """,
                tuple(SYSTEM_SCHEMAS),
            )
            schemas = [row[0] for row in cursor.fetchall()]

            for schema_name in schemas:
                output.write(f"CREATE SCHEMA IF NOT EXISTS {quote_ident(schema_name)};\n")
            output.write("\n")

            cursor.execute(
                """
                SELECT sequence_schema, sequence_name, data_type, start_value, minimum_value, maximum_value, increment, cycle_option
                FROM information_schema.sequences
                WHERE sequence_schema NOT IN (%s, %s, %s)
                ORDER BY sequence_schema, sequence_name
                """,
                tuple(SYSTEM_SCHEMAS),
            )
            sequences = cursor.fetchall()

            for sequence_schema, sequence_name, data_type, start_value, minimum_value, maximum_value, increment, cycle_option in sequences:
                sequence_ref = f"{quote_ident(sequence_schema)}.{quote_ident(sequence_name)}"
                cycle_sql = "CYCLE" if cycle_option == "YES" else "NO CYCLE"
                output.write(
                    f"CREATE SEQUENCE IF NOT EXISTS {sequence_ref} AS {data_type} "
                    f"START WITH {start_value} INCREMENT BY {increment} "
                    f"MINVALUE {minimum_value} MAXVALUE {maximum_value} {cycle_sql};\n"
                )
            if sequences:
                output.write("\n")

            cursor.execute(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                  AND table_schema NOT IN (%s, %s, %s)
                ORDER BY table_schema, table_name
                """,
                tuple(SYSTEM_SCHEMAS),
            )
            tables = cursor.fetchall()

            for schema_name, table_name in tables:
                table_ref = f"{quote_ident(schema_name)}.{quote_ident(table_name)}"

                cursor.execute(
                    """
                    SELECT
                        a.attname,
                        pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
                        a.attnotnull,
                        pg_get_expr(ad.adbin, ad.adrelid) AS default_value
                    FROM pg_catalog.pg_attribute a
                    JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
                    JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
                    LEFT JOIN pg_catalog.pg_attrdef ad ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
                    WHERE n.nspname = %s
                      AND c.relname = %s
                      AND a.attnum > 0
                      AND NOT a.attisdropped
                    ORDER BY a.attnum
                    """,
                    (schema_name, table_name),
                )
                columns = cursor.fetchall()

                column_sql_parts = []
                for column_name, data_type, not_null, default_value in columns:
                    column_sql = f"{quote_ident(column_name)} {data_type}"
                    if default_value is not None:
                        column_sql += f" DEFAULT {default_value}"
                    if not_null:
                        column_sql += " NOT NULL"
                    column_sql_parts.append(column_sql)

                output.write(f"CREATE TABLE {table_ref} (\n    ")
                output.write(",\n    ".join(column_sql_parts))
                output.write("\n);\n\n")

                if columns:
                    column_names = [quote_ident(column_name) for column_name, *_ in columns]
                    select_sql = f"SELECT {', '.join(column_names)} FROM {table_ref}"
                    data_cursor = connection.cursor(name=f"dump_{schema_name}_{table_name}".replace('.', '_'))
                    data_cursor.itersize = 1000
                    data_cursor.execute(select_sql)

                    while True:
                        rows = data_cursor.fetchmany(1000)
                        if not rows:
                            break

                        values_sql = []
                        for row in rows:
                            values_sql.append(
                                "(" + ", ".join(render_sql_value(value, data_cursor) for value in row) + ")"
                            )

                        output.write(
                            f"INSERT INTO {table_ref} ({', '.join(column_names)}) VALUES\n"
                        )
                        output.write(",\n".join(values_sql))
                        output.write(";\n\n")

                    data_cursor.close()

            cursor.execute(
                """
                SELECT
                    ns.nspname AS sequence_schema,
                    seq.relname AS sequence_name,
                    tn.nspname AS table_schema,
                    tbl.relname AS table_name,
                    att.attname AS column_name
                FROM pg_class seq
                JOIN pg_namespace ns ON ns.oid = seq.relnamespace
                JOIN pg_depend dep ON dep.objid = seq.oid AND dep.deptype = 'a'
                JOIN pg_class tbl ON tbl.oid = dep.refobjid
                JOIN pg_namespace tn ON tn.oid = tbl.relnamespace
                JOIN pg_attribute att ON att.attrelid = tbl.oid AND att.attnum = dep.refobjsubid
                WHERE seq.relkind = 'S'
                  AND ns.nspname NOT IN (%s, %s, %s)
                ORDER BY ns.nspname, seq.relname
                """,
                tuple(SYSTEM_SCHEMAS),
            )
            owned_sequences = cursor.fetchall()

            if owned_sequences:
                output.write("\n")
                for sequence_schema, sequence_name, table_schema, table_name, column_name in owned_sequences:
                    sequence_ref = f"{sequence_schema}.{sequence_name}"
                    table_ref = f"{quote_ident(table_schema)}.{quote_ident(table_name)}"
                    column_ref = quote_ident(column_name)
                    output.write(
                        f"SELECT setval({quote_literal(sequence_ref)}, COALESCE((SELECT MAX({column_ref}) FROM {table_ref}), 1), true);\n"
                    )

            output.write("-- Fin del backup lógico\n")

    finally:
        connection.close()

if __name__ == "__main__":
    backup_file = export_database()
    print(f"✅ Exportación completa generada en: {backup_file}")