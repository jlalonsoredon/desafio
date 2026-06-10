# Contexto de base de datos — `sustraiapp`
_Generado: 2026-06-09 15:34 · 14 de 14 tablas · PII redactada_

### Tabla `market_data.culture`

_Filas totales: 577_


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

**Filas de ejemplo (máx. 3):**

| id | external_id | fuente | nombre | tipo_lugar | tipo_cultura | descripcion | precio | horario | telefono | email | web | web_amigable | imagen_url | municipality_id | direccion | codigo_postal | visita_guiada | capacidad | tienda | lat | lng | valoracion | numero_valoraciones | is_sponsored | active | created_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | NULL | Manual | Museo Bibat | Museo | Otros | Ubicado en el Casco Antiguo de Vitoria, consta de… | NULL | NULL | ‹oculto› | ‹oculto› | https://fourniermuseoabibat.eus/es/inicio | https://turismoa.euskadi.eus/es/museos/museo-biba… | https://places.googleapis.com/v1/places/ChIJd6FTz… | 1 | ‹oculto› | 10010 | True | 0 | True | 42.8493094 | -2.671176400000036 | 4.4 | 2420 | False | True | 2026-06-08 21:24:10.797309 |
| 1 | NULL | Manual | Museo de Faroles de la Cofradía de la Virgen Blan… | Museo | Otros | Este original museo alberga las 267 piezas de vid… | NULL | NULL | ‹oculto› | ‹oculto› | http://www.cofradiavirgenblanca.com/ | https://turismoa.euskadi.eus/es/museos/museo-de-f… | https://places.googleapis.com/v1/places/ChIJN4tn5… | 1 | ‹oculto› | 10010 | True | 1000 | False | 42.84809749 | -2.67413986 | 4.7 | 2500 | False | True | 2026-06-08 21:24:10.797309 |
| 2 | NULL | Manual | Museo de Ciencias Naturales de Álava | Museo | Ciencias Naturales | El Museo de Ciencias Naturales de Álava cuenta co… | NULL | NULL | ‹oculto› | ‹oculto› | NULL | https://turismoa.euskadi.eus/es/museos/museo-de-c… | https://places.googleapis.com/v1/places/ChIJHQzfO… | 1 | ‹oculto› | 10010 | True | 1000 | False | 42.8502903 | -2.67462519 | 4.6 | 7700 | False | True | 2026-06-08 21:24:10.797309 |

### Tabla `market_data.events`

_Filas totales: 2744_


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

**Filas de ejemplo (máx. 3):**

| id | external_id | municipality_id | type | subtipo | start_date | end_date | publication_date | language | opening_hours | price_eur | is_free | is_sponsored | purchase_url | url_event | url_online | images | online | establishment | place | company | active | created_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2025072111423614 | 1 | Concierto | Otros | 2026-05-25 00:00:00+00:00 | 2026-05-25 00:00:00+00:00 | 2026-05-25 08:05:01+00:00 | NULL | 19:30 | NULL | True | False | https://sarrerak.bilbaorkestra.eus/index.php?acti… | https://www.euskalduna.eus/ | NULL | [{'imageId': '1145543', 'imageUrl': 'https://open… | False | Palacio Euskalduna | NULL | NULL | True | 2026-06-08 21:44:38.705483 |
| 2 | 2025072213252895 | 1 | Concierto | Otros | 2026-05-25 00:00:00+00:00 | 2026-05-25 00:00:00+00:00 | 2026-05-15 14:35:48+00:00 | NULL | 19:30 | NULL | True | False | NULL | https://conservatoriovitoria.com/index.php/es/ | NULL | [{'imageId': '1143256', 'imageUrl': 'https://open… | False | Conservatorio de Música Jesús Guridi | NULL | NULL | True | 2026-06-08 21:44:38.705483 |
| 3 | 2025090511122854 | 1 | Conferencia | Otros | 2026-05-25 00:00:00+00:00 | 2026-05-25 00:00:00+00:00 | 2025-09-05 11:12:52+00:00 | EN | 19:00 | NULL | True | False | NULL | https://web.araba.eus/es/cultura/casa-cultura-ign… | NULL | [{'imageId': '1051276', 'imageUrl': 'https://open… | False | Casa de Cultura Ignacio Aldecoa | NULL | NULL | True | 2026-06-08 21:44:38.705483 |

### Tabla `market_data.gastronomy`

_Filas totales: 490_


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

**Filas de ejemplo (máx. 3):**

| id | external_id | nombre | descripcion | municipality_id | lat | lng | type | tipo_comida | entorno | email | web | web_euskadi | categoria | calidad | url_imagen | valoracion | num_resenas | nivel_precio | national_phone_number | is_sponsored | active | created_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | NULL | Agorregi | El restaurante Agorregi, ubicado en el barrio de … | 182 | 43.30240464 | -2.011846 | Restaurante | NULL | Costa Vasca,San Sebastián | ‹oculto› | https://agorregi.com/ | https://turismoa.euskadi.eus/es/restaurantes/rest… | NULL | False | https://places.googleapis.com/v1/places/ChIJFTHOi… | 4.6 | 571 | Moderado | ‹oculto› | False | True | 2026-06-08 21:07:08.754435 |
| 1 | NULL | Aizian | Este moderno y acogedor restaurante fue diseñado … | 52 | 43.26751936 | -2.94180662 | Restaurante | NULL | Bilbao | ‹oculto› | https://www.restaurante-aizian.com/ | https://turismoa.euskadi.eus/es/restaurantes/rest… | NULL | False | https://places.googleapis.com/v1/places/ChIJdeCXz… | 4.7 | 435 | Moderado | ‹oculto› | False | True | 2026-06-08 21:07:08.754435 |
| 2 | NULL | Akelarre | Pedro Subijana desarrolla desde 1970 una cocina p… | 172 | 43.3077501796958 | -2.043134673141481 | Restaurante | NULL | San Sebastián | ‹oculto› | https://www.akelarre.net | https://turismoa.euskadi.eus/es/restaurantes/rest… | NULL | True | https://places.googleapis.com/v1/places/ChIJXdMPl… | 4.5 | 1925 | Muy caro | ‹oculto› | False | True | 2026-06-08 21:07:08.754435 |

### Tabla `market_data.gastronomy_qualifications`

_Filas totales: 277_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `gastronomy_id` | INTEGER | NO | FK → market_data.gastronomy.id |
| `qualification_id` | INTEGER | NO | FK → market_data.qualifications.id |

**Filas de ejemplo (máx. 3):**

| id | gastronomy_id | qualification_id |
|---|---|---|
| 1 | 2 | 1 |
| 2 | 2 | 2 |
| 3 | 3 | 1 |

### Tabla `market_data.qualifications`

_Filas totales: 7_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `codigo` | VARCHAR(50) | sí |  |
| `nombre` | VARCHAR(100) | NO |  |

**Filas de ejemplo (máx. 3):**

| id | codigo | nombre |
|---|---|---|
| 1 | repsol_sol | Sol Repsol |
| 2 | michelin_estrella | Estrella Michelin |
| 3 | denominacion_origen | Denominación de Origen |

### Tabla `shared.municipalities`

_Filas totales: 252_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `nombre` | VARCHAR(100) | NO |  |
| `provincia` | VARCHAR(50) | NO |  |
| `nora_code` | VARCHAR(20) | sí |  |
| `province_code` | VARCHAR(5) | sí |  |
| `lat` | DOUBLE PRECISION | sí |  |
| `lng` | DOUBLE PRECISION | sí |  |

**Filas de ejemplo (máx. 3):**

| id | nombre | provincia | nora_code | province_code | lat | lng |
|---|---|---|---|---|---|---|
| 1 | Alegría-Dulantzi | Araba | 01001 | 1 | 42.839812 | -2.512437 |
| 2 | Amurrio | Araba | 01002 | 1 | 43.054278 | -3.000073 |
| 3 | Aramaio | Araba | 01003 | 1 | 43.051197 | -2.5654 |

### Tabla `user_data.culture_reviews`

_Filas totales: 6410_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `user_id` | INTEGER | NO | FK → user_data.users.id_user |
| `culture_id` | INTEGER | NO |  |
| `puntuacion` | INTEGER | NO |  |
| `texto` | TEXT | sí |  |
| `created_at` | TIMESTAMP | sí |  |

**Filas de ejemplo (máx. 3):**

| id | user_id | culture_id | puntuacion | texto | created_at |
|---|---|---|---|---|---|
| 1 | 1587 | 0 | 3 | Está bien para verlo una vez, pero le falta renov… | 2026-05-01 16:43:00 |
| 2 | 1326 | 0 | 4 | Sitio bonito con mucha historia local. Recomendad… | 2026-04-07 13:22:00 |
| 3 | 211 | 0 | 5 | Espectacular puesta en escena. Un orgullo cultura… | 2026-04-26 20:32:00 |

### Tabla `user_data.event_reviews`

_Filas totales: 83485_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `user_id` | INTEGER | NO | FK → user_data.users.id_user |
| `event_id` | INTEGER | NO |  |
| `puntuacion` | INTEGER | NO |  |
| `texto` | TEXT | sí |  |
| `created_at` | TIMESTAMP | sí |  |

**Filas de ejemplo (máx. 3):**

| id | user_id | event_id | puntuacion | texto | created_at |
|---|---|---|---|---|---|
| 1 | 1532 | 1 | 5 | Maravilloso de principio a fin. Muy dinámico, emo… | 2026-06-01 21:43:00 |
| 2 | 1326 | 1 | 5 | Superó todas mis expectativas. Una calidad artíst… | 2026-05-07 20:22:00 |
| 3 | 211 | 1 | 5 | Superó todas mis expectativas. Una calidad artíst… | 2026-05-26 23:32:00 |

### Tabla `user_data.favorites`

_Filas totales: 0_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `user_id` | INTEGER | NO | FK → user_data.users.id_user |
| `entidad_id` | INTEGER | NO |  |
| `entidad_tipo` | VARCHAR(20) | NO |  |
| `created_at` | TIMESTAMP | sí |  |

_Sin filas._


### Tabla `user_data.gastronomy_reviews`

_Filas totales: 15581_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `user_id` | INTEGER | NO | FK → user_data.users.id_user |
| `gastro_id` | INTEGER | NO |  |
| `puntuacion` | INTEGER | NO |  |
| `texto` | TEXT | sí |  |
| `created_at` | TIMESTAMP | sí |  |

**Filas de ejemplo (máx. 3):**

| id | user_id | gastro_id | puntuacion | texto | created_at |
|---|---|---|---|---|---|
| 1 | 1441 | 0 | 4 | Muy buena comida y ambiente agradable. Volveremos. | 2026-05-23 18:30:00 |
| 2 | 1326 | 0 | 4 | Muy buena comida y ambiente agradable. Volveremos. | 2026-03-16 13:40:00 |
| 3 | 211 | 0 | 5 | Comida espectacular, servicio impecable. De los m… | 2026-05-15 19:45:00 |

### Tabla `user_data.interests`

_Filas totales: 29_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id_interes` | INTEGER | NO | PK |
| `nombre` | VARCHAR(100) | NO |  |
| `father_id` | INTEGER | sí | FK → user_data.interests.id_interes |
| `level` | INTEGER | NO |  |

**Filas de ejemplo (máx. 3):**

| id_interes | nombre | father_id | level |
|---|---|---|---|
| 1 | Eventos | NULL | 0 |
| 2 | Gastronomía | NULL | 0 |
| 3 | Puntos de interés | NULL | 0 |

### Tabla `user_data.preferences`

_Filas totales: 0_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id` | INTEGER | NO | PK |
| `user_id` | INTEGER | NO | FK → user_data.users.id_user |
| `rango_precio` | VARCHAR(10) | sí |  |
| `movilidad_reducida` | BOOLEAN | sí | PII (redactada) |
| `municipios_interes` | ARRAY | sí |  |
| `updated_at` | TIMESTAMP | sí |  |

_Sin filas._


### Tabla `user_data.user_interests`

_Filas totales: 9172_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id_user` | INTEGER | NO | PK, FK → user_data.users.id_user |
| `id_interes` | INTEGER | NO | PK, FK → user_data.interests.id_interes |

**Filas de ejemplo (máx. 3):**

| id_user | id_interes |
|---|---|
| 1 | 14 |
| 1 | 17 |
| 1 | 20 |

### Tabla `user_data.users`

_Filas totales: 2000_


**Columnas:**

| Columna | Tipo | Nulo | Notas |
|---|---|---|---|
| `id_user` | INTEGER | NO | PK |
| `nombre` | VARCHAR(100) | NO |  |
| `apellido` | VARCHAR(100) | sí |  |
| `email` | VARCHAR(255) | NO | PII (redactada) |
| `password_hash` | VARCHAR(256) | NO | PII (redactada) |
| `tlf` | VARCHAR(20) | sí |  |
| `municipality_id` | INTEGER | NO | FK → shared.municipalities.id |
| `sexo` | VARCHAR(10) | NO |  |
| `age` | INTEGER | NO |  |
| `role` | VARCHAR(10) | NO |  |
| `created_at` | TIMESTAMP | sí |  |
| `updated_at` | TIMESTAMP | sí |  |

**Filas de ejemplo (máx. 3):**

| id_user | nombre | apellido | email | password_hash | tlf | municipality_id | sexo | age | role | created_at | updated_at |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Ander | Martin Alonso | ‹oculto› | ‹oculto› | +34 98266521 | 219 | hombre | 47 | user | 2026-03-16 10:22:00 | 2026-03-16 10:22:00 |
| 2 | Daniel | Agirre Ruiz | ‹oculto› | ‹oculto› | +34 97389339 | 66 | hombre | 58 | user | 2026-03-20 13:43:00 | 2026-03-20 13:43:00 |
| 3 | Joseba | Garate Moreno | ‹oculto› | ‹oculto› | +34 69278928 | 78 | hombre | 45 | user | 2026-03-18 06:39:00 | 2026-03-18 06:39:00 |
