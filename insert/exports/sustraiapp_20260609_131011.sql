-- Backup lógico generado por export_db.py
-- Base de datos: sustraiapp

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

CREATE SCHEMA IF NOT EXISTS "market_data";
CREATE SCHEMA IF NOT EXISTS "public";
CREATE SCHEMA IF NOT EXISTS "shared";
CREATE SCHEMA IF NOT EXISTS "user_data";

CREATE SEQUENCE IF NOT EXISTS "market_data"."culture_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "market_data"."events_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "market_data"."gastronomy_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "market_data"."gastronomy_qualifications_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "market_data"."qualifications_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "shared"."municipalities_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "user_data"."culture_reviews_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "user_data"."event_reviews_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "user_data"."favorites_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "user_data"."gastronomy_reviews_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "user_data"."interests_id_interes_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "user_data"."preferences_id_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE IF NOT EXISTS "user_data"."users_id_user_seq" AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;

CREATE TABLE "market_data"."culture" (
    "id" integer DEFAULT nextval('market_data.culture_id_seq'::regclass) NOT NULL,
    "external_id" character varying(100),
    "fuente" character varying(50) DEFAULT 'Manual'::character varying NOT NULL,
    "nombre" character varying(255) NOT NULL,
    "tipo_lugar" character varying(100) NOT NULL,
    "tipo_cultura" character varying(100),
    "descripcion" text,
    "precio" character varying(100),
    "horario" jsonb,
    "telefono" character varying(50),
    "email" character varying(100),
    "web" character varying(255),
    "web_amigable" character varying(255),
    "imagen_url" text,
    "municipality_id" integer NOT NULL,
    "direccion" character varying(255),
    "codigo_postal" character varying(10),
    "visita_guiada" boolean DEFAULT false,
    "capacidad" integer,
    "tienda" boolean DEFAULT false,
    "lat" double precision NOT NULL,
    "lng" double precision NOT NULL,
    "valoracion" double precision,
    "numero_valoraciones" integer,
    "is_sponsored" boolean DEFAULT false,
    "active" boolean DEFAULT true,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

