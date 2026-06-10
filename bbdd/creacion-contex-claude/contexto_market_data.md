# Contexto de base de datos — `sustraiapp`
_Generado: 2026-06-09 15:33 · 5 de 5 tablas · PII redactada_

### Tabla `culture`


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `external_id` | VARCHAR(100) | sí |  |
| `fuente` | VARCHAR(50) | NO |  |
| `nombre` | VARCHAR(255) | NO |  |
| `tipo_lugar` | VARCHAR(100) | NO |  |
| `tipo_cultura` | VARCHAR(100) | sí |  |
| `descripcion` | TEXT | sí |  |
| `precio` | VARCHAR(100) | sí |  |
| `horario` | JSONB | sí |  |
| `telefono` | VARCHAR(50) | sí | PII (redactada) |
| `email` | VARCHAR(100) | sí | PII (redactada) |
| `web` | VARCHAR(255) | sí |  |
| `web_amigable` | VARCHAR(255) | sí |  |
| `imagen_url` | TEXT | sí |  |
| `municipality_id` | INTEGER | NO | FK → shared.municipalities.id |
| `direccion` | VARCHAR(255) | sí | PII (redactada) |
| `codigo_postal` | VARCHAR(10) | sí |  |
| `visita_guiada` | BOOLEAN | sí |  |
| `capacidad` | INTEGER | sí |  |
| `tienda` | BOOLEAN | sí |  |
| `lat` | DOUBLE PRECISION | NO |  |
| `lng` | DOUBLE PRECISION | NO |  |
| `valoracion` | DOUBLE PRECISION | sí |  |
| `numero_valoraciones` | INTEGER | sí |  |
| `is_sponsored` | BOOLEAN | sí |  |
| `active` | BOOLEAN | sí |  |
| `created_at` | TIMESTAMP | sí |  |

### Tabla `events`


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `external_id` | VARCHAR(100) | sí |  |
| `municipality_id` | INTEGER | NO | FK → shared.municipalities.id |
| `type` | VARCHAR(50) | sí |  |
| `subtipo` | VARCHAR(255) | sí |  |
| `start_date` | TIMESTAMP | NO |  |
| `end_date` | TIMESTAMP | NO |  |
| `publication_date` | TIMESTAMP | sí |  |
| `language` | VARCHAR(10) | sí |  |
| `opening_hours` | TEXT | sí |  |
| `price_eur` | DOUBLE PRECISION | sí |  |
| `is_free` | BOOLEAN | sí |  |
| `is_sponsored` | BOOLEAN | sí |  |
| `purchase_url` | TEXT | sí |  |
| `url_event` | TEXT | sí |  |
| `url_online` | TEXT | sí |  |
| `images` | JSONB | sí |  |
| `online` | BOOLEAN | sí |  |
| `establishment` | VARCHAR(255) | sí |  |
| `place` | VARCHAR(255) | sí |  |
| `company` | VARCHAR(255) | sí |  |
| `active` | BOOLEAN | sí |  |
| `created_at` | TIMESTAMP | sí |  |

### Tabla `gastronomy`


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `external_id` | VARCHAR(100) | sí |  |
| `nombre` | VARCHAR(255) | NO |  |
| `descripcion` | TEXT | sí |  |
| `municipality_id` | INTEGER | NO |  |
| `lat` | DOUBLE PRECISION | sí |  |
| `lng` | DOUBLE PRECISION | sí |  |
| `type` | VARCHAR(50) | sí |  |
| `tipo_comida` | VARCHAR(100) | sí |  |
| `entorno` | VARCHAR(100) | sí |  |
| `email` | VARCHAR(100) | sí | PII (redactada) |
| `web` | TEXT | sí |  |
| `web_euskadi` | TEXT | sí |  |
| `categoria` | VARCHAR(50) | sí |  |
| `calidad` | BOOLEAN | sí |  |
| `url_imagen` | TEXT | sí |  |
| `valoracion` | DOUBLE PRECISION | sí |  |
| `num_resenas` | INTEGER | sí |  |
| `nivel_precio` | VARCHAR(50) | sí |  |
| `national_phone_number` | VARCHAR(20) | sí | PII (redactada) |
| `is_sponsored` | BOOLEAN | sí |  |
| `active` | BOOLEAN | sí |  |
| `created_at` | TIMESTAMP | sí |  |

### Tabla `gastronomy_qualifications`


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `gastronomy_id` | INTEGER | NO | FK → market_data.gastronomy.id |
| `qualification_id` | INTEGER | NO | FK → market_data.qualifications.id |

### Tabla `qualifications`


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `codigo` | VARCHAR(50) | sí |  |
| `nombre` | VARCHAR(100) | NO |  |
