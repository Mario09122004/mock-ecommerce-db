import psycopg2
from psycopg2.extras import execute_values

# 1. CONFIGURACIÓN DE LAS BASES DE DATOS (Objetos de Procedencia y Destino)
ORIGIN_DB = {
    "host": "localhost",
    "port": 5432,
    "database": "v1_airbnb_db",
    "user": "admin",
    "password": "admin"
}

DEST_DB = {
    "host": "localhost",
    "port": 5432,
    "database": "empty_airbnb_db",
    "user": "admin",
    "password": "admin"
}

# 2. MAPA DE VALORES POR DEFECTO PARA IMPUTACIÓN DE NULOS
TABLE_DEFAULTS = {
    "cat_neighbourhoods": {
        "neighbourhood": "Desconocido"
    },
    "data_hosts": {
        "host_location": "Sin ubicación",
        "host_about": "Sin descripción"
    },
    "data_listings": {
        "description": "Sin descripción",
        "bathrooms": 1.0,
        "bedrooms": 1,
        "beds": 1
    },
    "hist_reviews": {
        "comments": "Sin comentarios"
    }
}

def migrate():
    print("Iniciando migración de datos con imputación (relleno) de nulos...")
    
    # Establecer conexiones
    try:
        conn_origin = psycopg2.connect(**ORIGIN_DB)
        conn_dest = psycopg2.connect(**DEST_DB)
        print("Conexión a ambas bases de datos establecida con éxito.")
    except Exception as e:
        print(f"Error al conectar a las bases de datos: {e}")
        return

    cur_origin = conn_origin.cursor()
    cur_dest = conn_dest.cursor()

    try:
        # --- 3. CONFIGURACIÓN DE ESQUEMA Y ELIMINACIÓN POR CASCADA ---
        print("\n[Fase 1] Reconfigurando restricciones de cascada y eliminando columnas nulas de origen...")
        
        setup_schema_sql = """
        -- Eliminar columna 'price' en data_listings e hist_calendar
        ALTER TABLE public.data_listings DROP COLUMN IF EXISTS price CASCADE;
        ALTER TABLE public.hist_calendar DROP COLUMN IF EXISTS price CASCADE;

        -- Eliminar columna 'neighbourhood_group' en cat_neighbourhoods (al ser 100% nula)
        ALTER TABLE public.cat_neighbourhoods DROP COLUMN IF EXISTS neighbourhood_group CASCADE;

        -- Reconfigurar claves foráneas en data_listings para eliminación en cascada
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

        -- Reconfigurar clave foránea en hist_calendar
        ALTER TABLE ONLY public.hist_calendar 
            DROP CONSTRAINT IF EXISTS fk_listing_cal,
            ADD CONSTRAINT fk_listing_cal FOREIGN KEY (listing_id) REFERENCES public.data_listings(id) ON DELETE CASCADE;

        -- Reconfigurar claves foráneas en hist_reviews
        ALTER TABLE ONLY public.hist_reviews 
            DROP CONSTRAINT IF EXISTS fk_listing_rev,
            ADD CONSTRAINT fk_listing_rev FOREIGN KEY (listing_id) REFERENCES public.data_listings(id) ON DELETE CASCADE;

        ALTER TABLE ONLY public.hist_reviews 
            DROP CONSTRAINT IF EXISTS fk_reviewer_rev,
            ADD CONSTRAINT fk_reviewer_rev FOREIGN KEY (reviewer_id) REFERENCES public.data_reviewers(id) ON DELETE CASCADE;
        """
        cur_dest.execute(setup_schema_sql)
        conn_dest.commit()
        print("Esquema de destino ajustado y claves foráneas en ON DELETE CASCADE configuradas.")

        # --- 4. LIMPIEZA INICIAL DEL DESTINO ---
        print("\n[Fase 2] Limpiando tablas destino...")
        cur_dest.execute("""
            TRUNCATE TABLE 
                cat_neighbourhoods, 
                cat_property_types, 
                cat_room_types, 
                data_hosts, 
                data_reviewers, 
                data_listings, 
                hist_reviews, 
                hist_calendar 
            CASCADE;
        """)
        conn_dest.commit()
        print("Tablas destino truncadas exitosamente.")

        # Sets para mantener las llaves primarias válidas ya migradas (evitar violaciones FK)
        valid_neighbourhoods = set()
        valid_property_types = set()
        valid_room_types = set()
        valid_hosts = set()
        valid_listings = set()
        valid_reviewers = set()

        # --- 5. FUNCIÓN AUXILIAR DE MIGRACIÓN CON IMPUTACIÓN DE NULOS ---
        def migrate_table(table_name, columns, validator_fn=None, post_insert_fn=None):
            cols_str = ", ".join(columns)
            print(f"\nProcesando tabla: {table_name}...")
            
            # Obtener datos de la base de origen
            cur_origin.execute(f"SELECT {cols_str} FROM {table_name}")
            rows = cur_origin.fetchall()
            
            clean_rows = []
            defaults = TABLE_DEFAULTS.get(table_name, {})
            
            for row in rows:
                row_dict = dict(zip(columns, row))
                
                # A. Reemplazar valores nulos (None) con valores por defecto si existen
                for col, val in row_dict.items():
                    if val is None and col in defaults:
                        row_dict[col] = defaults[col]
                
                # B. Descartar la fila si contiene algún valor NULL crítico restante
                # (columnas sin valor por defecto asignado, como IDs de relación)
                if any(val is None for val in row_dict.values()):
                    continue
                
                # C. Comprobar validador de claves foráneas
                if validator_fn and not validator_fn(row_dict):
                    continue
                
                # Reconvertir el diccionario de vuelta a tupla ordenada para la consulta
                ordered_row = tuple(row_dict[col] for col in columns)
                clean_rows.append(ordered_row)
            
            if not clean_rows:
                print(f"Sin registros para insertar en {table_name}.")
                return

            # Insertar en base de datos de destino
            insert_query = f"INSERT INTO {table_name} ({cols_str}) VALUES %s ON CONFLICT DO NOTHING"
            execute_values(cur_dest, insert_query, clean_rows)
            
            # Ejecutar gancho para actualizar conjuntos de IDs válidos
            if post_insert_fn:
                post_insert_fn(clean_rows)
                
            print(f"Migrados exitosamente {len(clean_rows)} / {len(rows)} registros en {table_name}. (Descartados: {len(rows) - len(clean_rows)})")

        # --- 6. MIGRACIÓN EN ORDEN DE DEPENDENCIA DE LLAVES FORÁNEAS ---

        # 6.1 cat_neighbourhoods (Se excluye 'neighbourhood_group')
        def post_neighbourhoods(rows):
            for r in rows:
                valid_neighbourhoods.add(r[0])
        migrate_table("cat_neighbourhoods", ["id", "neighbourhood"], post_insert_fn=post_neighbourhoods)

        # 6.2 cat_property_types
        def post_property_types(rows):
            for r in rows:
                valid_property_types.add(r[0])
        migrate_table("cat_property_types", ["id", "property_type"], post_insert_fn=post_property_types)

        # 6.3 cat_room_types
        def post_room_types(rows):
            for r in rows:
                valid_room_types.add(r[0])
        migrate_table("cat_room_types", ["id", "room_type"], post_insert_fn=post_room_types)

        # 6.4 data_hosts
        def post_hosts(rows):
            for r in rows:
                valid_hosts.add(r[0])
        migrate_table("data_hosts", ["id", "host_name", "host_url", "host_location", "host_about", "host_is_superhost"], post_insert_fn=post_hosts)

        # 6.5 data_reviewers
        def post_reviewers(rows):
            for r in rows:
                valid_reviewers.add(r[0])
        migrate_table("data_reviewers", ["id", "reviewer_name"], post_insert_fn=post_reviewers)

        # 6.6 data_listings (Se excluye por completo la columna 'price')
        listings_cols = [
            "id", "name", "description", "host_id", "neighbourhood_id", 
            "property_type_id", "room_type_id", "latitude", "longitude", 
            "accommodates", "bathrooms", "bedrooms", "beds", 
            "minimum_nights", "maximum_nights"
        ]
        def validate_listing(row_dict):
            # Comprobar que todas sus llaves foráneas existan en las tablas ya migradas
            return (
                row_dict["host_id"] in valid_hosts and
                row_dict["neighbourhood_id"] in valid_neighbourhoods and
                row_dict["property_type_id"] in valid_property_types and
                row_dict["room_type_id"] in valid_room_types
            )
        def post_listings(rows):
            for r in rows:
                valid_listings.add(r[0])
        migrate_table("data_listings", listings_cols, validator_fn=validate_listing, post_insert_fn=post_listings)

        # 6.7 hist_reviews
        reviews_cols = ["id", "listing_id", "reviewer_id", "date", "comments"]
        def validate_review(row_dict):
            return (
                row_dict["listing_id"] in valid_listings and
                row_dict["reviewer_id"] in valid_reviewers
            )
        migrate_table("hist_reviews", reviews_cols, validator_fn=validate_review)

        # 6.8 hist_calendar (Se excluye por completo la columna 'price')
        calendar_cols = ["id", "listing_id", "date", "available", "minimum_nights", "maximum_nights"]
        def validate_calendar(row_dict):
            return row_dict["listing_id"] in valid_listings
        migrate_table("hist_calendar", calendar_cols, validator_fn=validate_calendar)

        # --- 7. ACTUALIZACIÓN DE LAS SECUENCIAS DE ID EN POSTGRESQL ---
        print("\n[Fase 4] Sincronizando secuencias de IDs...")
        cur_dest.execute("SELECT pg_catalog.setval('cat_neighbourhoods_id_seq', COALESCE(MAX(id), 1), true) FROM cat_neighbourhoods;")
        cur_dest.execute("SELECT pg_catalog.setval('hist_calendar_id_seq', COALESCE(MAX(id), 1), true) FROM hist_calendar;")
        
        conn_dest.commit()
        print("Sincronización de secuencias finalizada con éxito.")
        print("\n¡MIGRACIÓN COMPLETADA Y DATOS LIMPIOS EXITOSAMENTE!")

    except Exception as e:
        print(f"\n[ERROR] Ocurrió un fallo en la migración. Revirtiendo cambios... Detalle: {e}")
        conn_dest.rollback()
    finally:
        cur_origin.close()
        cur_dest.close()
        conn_origin.close()
        conn_dest.close()

if __name__ == "__main__":
    migrate()
