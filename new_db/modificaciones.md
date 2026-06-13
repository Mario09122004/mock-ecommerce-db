# Registro de Modificaciones de Base de Datos (Airbnb)

Este documento detalla los cambios realizados sobre el esquema de la base de datos de Airbnb para corregir errores de diseño, garantizar la integridad referencial y mejorar el rendimiento de las consultas.

---

## 1. Modificaciones Realizadas

### A. Integridad Referencial (`ON DELETE CASCADE`)
Se reconfiguraron todas las claves foráneas del esquema para habilitar eliminaciones en cascada. Esto garantiza que al eliminar un registro maestro (por ejemplo, un anfitrión o un alojamiento), toda su información relacionada (como calendarios y reseñas) se elimine automáticamente, evitando inconsistencias de datos huérfanos.

Las claves foráneas reconfiguradas son:
*   **En `data_listings`:**
    *   `fk_host` (hacia `data_hosts`)
    *   `fk_neighbourhood` (hacia `cat_neighbourhoods`)
    *   `fk_property_type` (hacia `cat_property_types`)
    *   `fk_room_type` (hacia `cat_room_types`)
*   **En `hist_calendar`:**
    *   `fk_listing_cal` (hacia `data_listings`)
*   **En `hist_reviews`:**
    *   `fk_listing_rev` (hacia `data_listings`)
    *   `fk_reviewer_rev` (hacia `data_reviewers`)

### B. Depuración de Nulos y Restricciones `NOT NULL`
Se eliminaron los registros con valores nulos en campos esenciales para el negocio e integridad del esquema. Posteriormente, se impuso la restricción física `NOT NULL` en estas columnas para evitar la inserción de futuros registros incompletos.

*   **`data_listings`:** Limpieza y restricción en `host_id` y `price`.
*   **`hist_calendar`:** Limpieza y restricción en `listing_id` y `date`.
*   **`hist_reviews`:** Limpieza y restricción en `listing_id`, `reviewer_id` y `date`.

### C. Creación de Índices para Rendimiento
Se crearon índices sobre las claves foráneas más consultadas y sobre combinaciones clave para evitar escaneos secuenciales completos (`Seq Scan`) en tablas con alta densidad de registros (como el historial de calendario y reseñas).

*   `idx_hist_calendar_listing` en `hist_calendar(listing_id)`
*   `idx_hist_reviews_listing` en `hist_reviews(listing_id)`
*   `idx_data_listings_host` on `data_listings(host_id)`
*   `idx_hist_calendar_listing_date` (índice compuesto) en `hist_calendar(listing_id, date)`

---

## 2. Script SQL Completo de las Modificaciones

A continuación se muestra el script de comandos SQL ejecutado para aplicar estos cambios:

```sql
-- =========================================================================
-- 1. ELIMINACIÓN EN CASCADA (ON DELETE CASCADE)
-- =========================================================================

-- Alojamientos (data_listings)
ALTER TABLE ONLY public.data_listings 
    DROP CONSTRAINT IF EXISTS fk_host,
    ADD CONSTRAINT fk_host FOREIGN KEY (host_id) REFERENCES public.data_hosts(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.data_listings 
    DROP CONSTRAINT IF EXISTS fk_neighbourhood,
    ADD CONSTRAINT fk_neighbourhood FOREIGN KEY (neighbourhood_id) REFERENCES public.cat_neighbourhoods(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.data_listings 
    DROP CONSTRAINT IF EXISTS fk_property_type,
    ADD CONSTRAINT fk_property_type FOREIGN KEY (property_type_id) REFERENCES public.cat_property_types(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.data_listings 
    DROP CONSTRAINT IF EXISTS fk_room_type,
    ADD CONSTRAINT fk_room_type FOREIGN KEY (room_type_id) REFERENCES public.cat_room_types(id) ON DELETE CASCADE;

-- Calendario (hist_calendar)
ALTER TABLE ONLY public.hist_calendar 
    DROP CONSTRAINT IF EXISTS fk_listing_cal,
    ADD CONSTRAINT fk_listing_cal FOREIGN KEY (listing_id) REFERENCES public.data_listings(id) ON DELETE CASCADE;

-- Reseñas (hist_reviews)
ALTER TABLE ONLY public.hist_reviews 
    DROP CONSTRAINT IF EXISTS fk_listing_rev,
    ADD CONSTRAINT fk_listing_rev FOREIGN KEY (listing_id) REFERENCES public.data_listings(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.hist_reviews 
    DROP CONSTRAINT IF EXISTS fk_reviewer_rev,
    ADD CONSTRAINT fk_reviewer_rev FOREIGN KEY (reviewer_id) REFERENCES public.data_reviewers(id) ON DELETE CASCADE;


-- =========================================================================
-- 2. INTEGRIDAD DE DATOS (NOT NULL)
-- =========================================================================

-- Tabla: data_listings
DELETE FROM public.data_listings WHERE host_id IS NULL OR price IS NULL;
ALTER TABLE public.data_listings 
    ALTER COLUMN host_id SET NOT NULL,
    ALTER COLUMN price SET NOT NULL;

-- Tabla: hist_calendar
DELETE FROM public.hist_calendar WHERE listing_id IS NULL OR date IS NULL;
ALTER TABLE public.hist_calendar 
    ALTER COLUMN listing_id SET NOT NULL,
    ALTER COLUMN date SET NOT NULL;

-- Tabla: hist_reviews
DELETE FROM public.hist_reviews WHERE listing_id IS NULL OR reviewer_id IS NULL OR date IS NULL;
ALTER TABLE public.hist_reviews 
    ALTER COLUMN listing_id SET NOT NULL,
    ALTER COLUMN reviewer_id SET NOT NULL,
    ALTER COLUMN date SET NOT NULL;


-- =========================================================================
-- 3. OPTIMIZACIÓN Y CREACIÓN DE ÍNDICES
-- =========================================================================
CREATE INDEX IF NOT EXISTS idx_hist_calendar_listing ON hist_calendar(listing_id);
CREATE INDEX IF NOT EXISTS idx_hist_reviews_listing ON hist_reviews(listing_id);
CREATE INDEX IF NOT EXISTS idx_data_listings_host ON data_listings(host_id);
CREATE INDEX IF NOT EXISTS idx_hist_calendar_listing_date ON hist_calendar(listing_id, date);
```
