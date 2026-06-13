# Errores

1. **Ausencia de restricciones de nulidad (`NOT NULL`):**
   Casi todas las columnas de las tablas permiten valores nulos (`NULL`) por defecto. Por ejemplo, `data_listings.host_id`, `data_listings.price` e `hist_calendar.date` pueden ser nulos. Esto permite registros inconsistentes, como tener un precio de alojamiento vacío o disponibilidad en el calendario sin una fecha asignada.
2. **Tipos de datos numéricos imprecisos (`numeric` sin escala/precisión):**
   Las coordenadas geográficas (`latitude`, `longitude`) y los precios (`price` tanto en `data_listings` como en `hist_calendar`) están declarados simplemente como `numeric`. Sin especificar precisión y escala (ej. `numeric(10, 2)`), PostgreSQL asume precisión arbitraria. Esto genera inconsistencias de redondeo y uso ineficiente de almacenamiento en cálculos financieros y de agregación.

3. **Falta de restricciones de dominio (constraints lógicas):**
   No hay validaciones físicas a nivel de base de datos. Se pueden insertar precios negativos, números de camas o recámaras menores a cero, o coordenadas geográficas fuera de los rangos reales.

# Malas practicas

1. **Falta de Índices en Claves Foráneas (`FOREIGN KEY`):**
   En PostgreSQL, las claves foráneas no se indexan automáticamente. Esto genera un grave problema en tablas con volumen histórico/transaccional como `hist_reviews` y `hist_calendar`. Al no tener índices sobre `listing_id` o `reviewer_id`, cualquier `JOIN` o consulta que filtre por alojamiento obligará a PostgreSQL a hacer un escaneo secuencial completo (`Seq Scan`) de millones de registros, degradando drásticamente el rendimiento.

2. **Uso indiscriminado de `text` para cadenas cortas:**
   Se utiliza el tipo de dato `text` para atributos cortos como `host_name`, `host_url`, `reviewer_name` y `neighbourhood`. Aunque en PostgreSQL el almacenamiento físico es similar a `varchar`, el estándar de integridad de datos dicta limitar su longitud (ej. `varchar(255)`) para evitar la inserción accidental de cadenas excesivamente largas.

3. **Tabla residual `test_listings`:**
   El volcado de la base de datos incluye la tabla `test_listings`, la cual comparte la misma estructura de `data_listings` pero carece de datos y llaves foráneas. Esto introduce redundancia innecesaria y ensucia el esquema de producción.

# Mejoras

1. **Creación de Índices:**
   Añadir índices explícitos sobre las llaves foráneas para optimizar búsquedas y consultas cruzadas:
   - `CREATE INDEX idx_hist_calendar_listing ON hist_calendar(listing_id);`
   - `CREATE INDEX idx_hist_reviews_listing ON hist_reviews(listing_id);`
   - `CREATE INDEX idx_data_listings_host ON data_listings(host_id);`
   - Crear un índice compuesto en la tabla de calendario para búsquedas rápidas por rango de fechas: `CREATE INDEX idx_hist_calendar_listing_date ON hist_calendar(listing_id, date);`

2. **Definición de restricciones `NOT NULL`:**
   Asegurar la obligatoriedad de campos críticos:
   - `ALTER TABLE data_listings ALTER COLUMN host_id SET NOT NULL;`
   - `ALTER TABLE data_listings ALTER COLUMN price SET NOT NULL;`
   - `ALTER TABLE hist_calendar ALTER COLUMN listing_id SET NOT NULL;`
   - `ALTER TABLE hist_calendar ALTER COLUMN date SET NOT NULL;`

3. **Agregar Constraints de validación (`CHECK`):**
   Garantizar la veracidad de la información a nivel lógico:
   - Para precios: `ALTER TABLE data_listings ADD CONSTRAINT chk_listings_price CHECK (price >= 0);`
   - Para coordenadas:
   - `ALTER TABLE data_listings ADD CONSTRAINT chk_latitude CHECK (latitude BETWEEN -90 AND 90);`
   - `ALTER TABLE data_listings ADD CONSTRAINT chk_longitude CHECK (longitude BETWEEN -180 AND 180);`
   - Para cupos y noches:
   - `ALTER TABLE data_listings ADD CONSTRAINT chk_accommodates CHECK (accommodates > 0);`
   - `ALTER TABLE data_listings ADD CONSTRAINT chk_min_nights CHECK (minimum_nights > 0);`

4. **Optimización de tipos de datos:**
   Ajustar los tipos de columnas para un almacenamiento óptimo:
   - Cambiar coordenadas a `numeric(9, 6)` o `decimal(9, 6)`.
   - Cambiar precios a `numeric(10, 2)` o `decimal(10, 2)`.
   - Redefinir campos de nombres y URLs como `varchar(255)`.

# Script corrector de DB

Puedes ejecutar el siguiente bloque de comandos SQL en tu gestor de base de datos o consola de PostgreSQL para corregir los problemas de tipos, limpiar la redundancia, agregar índices y forzar la integridad de los datos:

```sql
-- =========================================================================
-- 1. LIMPIEZA DE TABLAS RESIDUALES
-- =========================================================================
DROP TABLE IF EXISTS test_listings;

-- =========================================================================
-- 2. OPTIMIZACIÓN DE TIPOS DE DATOS (MIGRACIÓN DE TIPOS)
-- =========================================================================
-- Ajustar precisión y escala en coordenadas
ALTER TABLE data_listings 
  ALTER COLUMN latitude TYPE decimal(9, 6),
  ALTER COLUMN longitude TYPE decimal(9, 6);

-- Ajustar precisión en precios
ALTER TABLE data_listings 
  ALTER COLUMN price TYPE decimal(10, 2);

ALTER TABLE hist_calendar 
  ALTER COLUMN price TYPE decimal(10, 2);

-- Redefinir campos de texto genéricos de TEXT a VARCHAR con límites estándar
ALTER TABLE cat_neighbourhoods 
  ALTER COLUMN neighbourhood_group TYPE varchar(255),
  ALTER COLUMN neighbourhood TYPE varchar(255);

ALTER TABLE cat_property_types 
  ALTER COLUMN property_type TYPE varchar(255);

ALTER TABLE cat_room_types 
  ALTER COLUMN room_type TYPE varchar(255);

ALTER TABLE data_hosts 
  ALTER COLUMN host_name TYPE varchar(255),
  ALTER COLUMN host_url TYPE varchar(255),
  ALTER COLUMN host_location TYPE varchar(255);

ALTER TABLE data_reviewers 
  ALTER COLUMN reviewer_name TYPE varchar(255);

-- =========================================================================
-- 3. INTEGRIDAD DE DATOS (NOT NULL CON RESOLUCIÓN DE HUÉRFANOS)
-- =========================================================================
-- Limpiar nulos antes de establecer NOT NULL en el precio
UPDATE data_listings SET price = 0 WHERE price IS NULL;
ALTER TABLE data_listings ALTER COLUMN price SET NOT NULL;

-- Limpiar nulos e imponer NOT NULL en calendario
DELETE FROM hist_calendar WHERE listing_id IS NULL OR date IS NULL;
ALTER TABLE hist_calendar 
  ALTER COLUMN listing_id SET NOT NULL,
  ALTER COLUMN date SET NOT NULL;

-- =========================================================================
-- 4. CONSTRAINTS DE VALIDACIÓN (CHECK CONSTRAINTS)
-- =========================================================================
-- Validaciones lógicas en data_listings
ALTER TABLE data_listings 
  ADD CONSTRAINT chk_listings_price CHECK (price >= 0),
  ADD CONSTRAINT chk_latitude CHECK (latitude BETWEEN -90 AND 90),
  ADD CONSTRAINT chk_longitude CHECK (longitude BETWEEN -180 AND 180),
  ADD CONSTRAINT chk_accommodates CHECK (accommodates > 0),
  ADD CONSTRAINT chk_min_nights CHECK (minimum_nights > 0);

-- Validaciones en hist_calendar
ALTER TABLE hist_calendar 
  ADD CONSTRAINT chk_calendar_price CHECK (price >= 0);

-- =========================================================================
-- 5. CREACIÓN DE ÍNDICES (MEJORA DE RENDIMIENTO EN JOINS Y FILTROS)
-- =========================================================================
-- Índices para optimizar JOINS y búsquedas por clave foránea
CREATE INDEX IF NOT EXISTS idx_hist_calendar_listing ON hist_calendar(listing_id);
CREATE INDEX IF NOT EXISTS idx_hist_reviews_listing ON hist_reviews(listing_id);
CREATE INDEX IF NOT EXISTS idx_data_listings_host ON data_listings(host_id);

-- Índice compuesto para optimizar búsquedas por alojamiento y rangos de fechas (Calendario)
CREATE INDEX IF NOT EXISTS idx_hist_calendar_listing_date ON hist_calendar(listing_id, date);
```

# Migración de Datos y Limpieza de Nulos

Para poblar la base de datos optimizada (`empty_airbnb_db`) con la información de la base de datos original (`v1_airbnb_db`), se desarrolló un script en Python (`migrate_db.py`) que implementa las siguientes reglas de negocio e integridad:

1. **Eliminación de Columnas 100% Nulas**:
   Se identificó que las siguientes columnas en la base de datos de origen eran completamente nulas y no aportaban información útil al negocio:
   - `data_listings.price` (453/453 nulos)
   - `hist_calendar.price` (165,345/165,345 nulos)
   - `cat_neighbourhoods.neighbourhood_group` (16/16 nulos)
   
   Por esta razón, al inicio de la migración el script ejecuta comandos `ALTER TABLE ... DROP COLUMN ... CASCADE` para eliminar estas columnas del esquema de destino, optimizando el espacio y evitando campos innecesarios.

2. **Reconfiguración para Eliminación en Cascada (`ON DELETE CASCADE`)**:
   Antes de migrar la información, el script redefine las restricciones de claves foráneas de todas las tablas en el destino para habilitar la eliminación en cascada. Esto garantiza que cualquier borrado de registros maestros (como anfitriones o alojamientos) limpie automáticamente sus registros hijos (reseñas, calendarios, etc.) sin causar errores de integridad referencial.

3. **Imputación de Nulos (Valores por Defecto)**:
   Para evitar la pérdida masiva de datos (más del 50% de alojamientos, reseñas y calendarios), el script implementa una estrategia de imputación de valores lógicos por defecto para columnas descriptivas no críticas. Si un campo de texto o número está vacío (`NULL`) en el origen, se rellena según la siguiente tabla al migrar al destino:

   | Tabla | Columna | Valor por Defecto |
   | :--- | :--- | :--- |
   | `cat_neighbourhoods` | `neighbourhood` | `'Desconocido'` |
   | `data_hosts` | `host_location` | `'Sin ubicación'` |
   | `data_hosts` | `host_about` | `'Sin descripción'` |
   | `data_listings` | `description` | `'Sin descripción'` |
   | `data_listings` | `bathrooms` | `1.0` |
   | `data_listings` | `bedrooms` | `1` |
   | `data_listings` | `beds` | `1` |
   | `hist_reviews` | `comments` | `'Sin comentarios'` |

4. **Preservación de Integridad Referencial en la Migración**:
   El script valida la coherencia relacional al migrar. Si por alguna razón un registro de una tabla hija no tiene una clave foránea válida que apunte a un registro maestro migrado, la fila se descarta para garantizar que la base de datos sea 100% íntegra y consistente. Debido a la imputación de nulos, se logró migrar el **100% de los registros** de origen con éxito.

## Script de Migración (`migrate_db.py`)

El script se puede ejecutar en la terminal del sistema mediante el siguiente comando:

```bash
python3 new_db/migrate_db.py
```

El código completo del script de migración se encuentra guardado en [migrate_db.py](file:///home/mario_lira/Documents/Universidad/Cuatrimestre_8/Data%20Base%20administration/mock-ecommerce-db/new_db/migrate_db.py).

