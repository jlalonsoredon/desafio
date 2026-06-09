-- =============================================================
-- MIGRACIÓN COMPLETA: Eliminar shared.municipalities y reemplazar
-- municipality_id por municipality VARCHAR en todas las tablas
-- =============================================================

-- -------------------------------------------------------------
-- 1. VISTAS dependientes
-- -------------------------------------------------------------

DROP VIEW IF EXISTS market_data.gastronomy_with_qualifications;


-- -------------------------------------------------------------
-- 2. market_data.gastronomy
-- -------------------------------------------------------------

ALTER TABLE market_data.gastronomy
    DROP CONSTRAINT IF EXISTS gastronomy_municipality_id_fkey,
    DROP COLUMN IF EXISTS municipality_id,
    ADD COLUMN IF NOT EXISTS municipality VARCHAR(100);

DROP INDEX IF EXISTS market_data.idx_gastro_municipality_active;
CREATE INDEX IF NOT EXISTS idx_gastro_municipality_active
    ON market_data.gastronomy (municipality, active);


-- -------------------------------------------------------------
-- 3. market_data.events
-- -------------------------------------------------------------

ALTER TABLE market_data.events
    DROP CONSTRAINT IF EXISTS events_municipality_id_fkey,
    DROP COLUMN IF EXISTS municipality_id,
    ADD COLUMN IF NOT EXISTS municipality VARCHAR(100);

DROP INDEX IF EXISTS market_data.idx_events_municipality;
CREATE INDEX IF NOT EXISTS idx_events_municipality
    ON market_data.events (municipality);


-- -------------------------------------------------------------
-- 4. market_data.culture
-- -------------------------------------------------------------

ALTER TABLE market_data.culture
    DROP CONSTRAINT IF EXISTS culture_municipality_id_fkey,
    DROP COLUMN IF EXISTS municipality_id,
    ADD COLUMN IF NOT EXISTS municipality VARCHAR(100);

DROP INDEX IF EXISTS market_data.idx_culture_municipality;
CREATE INDEX IF NOT EXISTS idx_culture_municipality
    ON market_data.culture (municipality);


-- -------------------------------------------------------------
-- 5. user_data.users
-- -------------------------------------------------------------

ALTER TABLE user_data.users
    DROP CONSTRAINT IF EXISTS users_municipality_id_fkey,
    DROP COLUMN IF EXISTS municipality_id,
    ADD COLUMN IF NOT EXISTS municipality VARCHAR(100);


-- -------------------------------------------------------------
-- 6. user_data.preferences
-- -------------------------------------------------------------

ALTER TABLE user_data.preferences
    DROP COLUMN IF EXISTS municipios_interes;

ALTER TABLE user_data.preferences
    ADD COLUMN IF NOT EXISTS municipios_interes VARCHAR(100)[] DEFAULT '{}';


-- -------------------------------------------------------------
-- 7. Eliminar tabla y esquema shared
-- -------------------------------------------------------------

DROP TABLE IF EXISTS shared.municipalities CASCADE;
DROP SCHEMA  IF EXISTS shared CASCADE;


-- -------------------------------------------------------------
-- 8. Recrear vista gastronomy_with_qualifications
-- -------------------------------------------------------------

CREATE OR REPLACE VIEW market_data.gastronomy_with_qualifications AS
SELECT
    g.id,
    g.nombre,
    g.municipality,
    g.valoracion,
    g.active,
    COALESCE(
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'id',     q.id,
                'nombre', q.nombre
            )
        ) FILTER (WHERE q.id IS NOT NULL),
        '[]'
    ) AS cualificaciones
FROM market_data.gastronomy g
LEFT JOIN market_data.gastronomy_qualifications gq ON gq.gastronomy_id = g.id
LEFT JOIN market_data.qualifications            q  ON q.id = gq.qualification_id
GROUP BY g.id;