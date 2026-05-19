import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
import numpy as np

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ecommerce_db",
    "user": "admin",
    "password": "admin"
}

def clean_df(df):
    return df.astype(object).where(pd.notnull(df), None)

def run_seed():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Conectado a PostgreSQL exitosamente.")

        # --- 0. LIMPIEZA TOTAL ---
        print("Limpiando tablas anteriores...")
        cur.execute("""
            DROP TABLE IF EXISTS hist_calendar, hist_reviews, data_reviewers, data_listings, data_hosts, 
            cat_property_types, cat_room_types, cat_neighbourhoods,
            calendar, reviews, reviewers, listings, hosts, neighbourhoods, 
            reseñas, metodos_pago, detalle_pedidos, pedidos, inventario, productos, almacenes, usuarios, categorias, proveedores CASCADE;
        """)

        # --- 1. CREACIÓN DE TABLAS ---
        print("Creando estructura de tablas estandarizada (Airbnb)...")
        
        # 1.1 Tablas Categóricas
        cur.execute("""
            CREATE TABLE cat_neighbourhoods (
                id SERIAL PRIMARY KEY,
                neighbourhood_group TEXT,
                neighbourhood TEXT UNIQUE
            );
        """)
        
        cur.execute("""
            CREATE TABLE cat_property_types (
                id INT PRIMARY KEY,
                property_type TEXT UNIQUE
            );
        """)
        
        cur.execute("""
            CREATE TABLE cat_room_types (
                id INT PRIMARY KEY,
                room_type TEXT UNIQUE
            );
        """)

        # 1.2 Tablas de Datos Maestros
        cur.execute("""
            CREATE TABLE data_hosts (
                id BIGINT PRIMARY KEY,
                host_name TEXT,
                host_url TEXT,
                host_location TEXT,
                host_about TEXT,
                host_is_superhost BOOLEAN
            );
        """)

        cur.execute("""
            CREATE TABLE data_reviewers (
                id BIGINT PRIMARY KEY,
                reviewer_name TEXT
            );
        """)

        cur.execute("""
            CREATE TABLE data_listings (
                id BIGINT PRIMARY KEY,
                name TEXT,
                description TEXT,
                host_id BIGINT,
                neighbourhood_id INT,
                property_type_id INT,
                room_type_id INT,
                latitude DECIMAL,
                longitude DECIMAL,
                accommodates INT,
                bathrooms DECIMAL,
                bedrooms INT,
                beds INT,
                price DECIMAL,
                minimum_nights INT,
                maximum_nights INT
            );
        """)

        # 1.3 Tablas Históricas / Transaccionales
        cur.execute("""
            CREATE TABLE hist_reviews (
                id BIGINT PRIMARY KEY,
                listing_id BIGINT,
                reviewer_id BIGINT,
                date DATE,
                comments TEXT
            );
        """)

        cur.execute("""
            CREATE TABLE hist_calendar (
                id SERIAL PRIMARY KEY,
                listing_id BIGINT,
                date DATE,
                available BOOLEAN,
                price DECIMAL,
                minimum_nights INT,
                maximum_nights INT
            );
        """)

        # --- 2. CARGA Y PROCESAMIENTO DE DATOS ---
        print("Leyendo y procesando CSVs...")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # Categórica: Neighbourhoods
        print("Procesando cat_neighbourhoods...")
        nh_df = pd.read_csv(os.path.join(BASE_DIR, 'neighbourhoods.csv'))
        nh_df = clean_df(nh_df)
        nh_data = nh_df[['neighbourhood_group', 'neighbourhood']].values.tolist()
        execute_values(cur, "INSERT INTO cat_neighbourhoods (neighbourhood_group, neighbourhood) VALUES %s ON CONFLICT (neighbourhood) DO NOTHING", nh_data)
        
        cur.execute("SELECT neighbourhood, id FROM cat_neighbourhoods;")
        nh_map = dict(cur.fetchall())

        # Leer listings
        print("Procesando listings y extrayendo catálogos...")
        list_df = pd.read_csv(os.path.join(BASE_DIR, 'listings.csv'), low_memory=False)
        
        # Categórica: Property Types
        prop_types = list_df[['property_type']].dropna().drop_duplicates().reset_index(drop=True)
        prop_types['id'] = range(1, len(prop_types) + 1)
        prop_map = prop_types.set_index('property_type')['id'].to_dict()
        execute_values(cur, "INSERT INTO cat_property_types (id, property_type) VALUES %s", prop_types[['id', 'property_type']].values.tolist())

        # Categórica: Room Types
        room_types = list_df[['room_type']].dropna().drop_duplicates().reset_index(drop=True)
        room_types['id'] = range(1, len(room_types) + 1)
        room_map = room_types.set_index('room_type')['id'].to_dict()
        execute_values(cur, "INSERT INTO cat_room_types (id, room_type) VALUES %s", room_types[['id', 'room_type']].values.tolist())

        # Datos: Hosts
        print("Procesando data_hosts...")
        hosts_df = list_df[['host_id', 'host_name', 'host_url', 'host_location', 'host_about', 'host_is_superhost']].drop_duplicates(subset=['host_id'])
        hosts_df['host_is_superhost'] = hosts_df['host_is_superhost'].map({'t': True, 'f': False})
        hosts_df = clean_df(hosts_df)
        execute_values(cur, "INSERT INTO data_hosts (id, host_name, host_url, host_location, host_about, host_is_superhost) VALUES %s", hosts_df.values.tolist())

        # Datos: Listings
        print("Procesando data_listings...")
        list_df['neighbourhood_id'] = list_df['neighbourhood_cleansed'].map(nh_map)
        list_df['property_type_id'] = list_df['property_type'].map(prop_map)
        list_df['room_type_id'] = list_df['room_type'].map(room_map)
        
        if list_df['price'].dtype == object:
            list_df['price'] = list_df['price'].replace(r'[\$,]', '', regex=True).astype(float)
        
        cols_listing = ['id', 'name', 'description', 'host_id', 'neighbourhood_id', 'property_type_id', 'room_type_id', 
                        'latitude', 'longitude', 'accommodates', 'bathrooms', 'bedrooms', 'beds', 
                        'price', 'minimum_nights', 'maximum_nights']
        
        if 'bathrooms_text' in list_df.columns:
            list_df['bathrooms'] = list_df['bathrooms_text'].astype(str).str.extract(r'([\d\.]+)').astype(float)
            
        list_insert_df = list_df[cols_listing]
        list_insert_df = clean_df(list_insert_df)
        execute_values(cur, "INSERT INTO data_listings (id, name, description, host_id, neighbourhood_id, property_type_id, room_type_id, latitude, longitude, accommodates, bathrooms, bedrooms, beds, price, minimum_nights, maximum_nights) VALUES %s", list_insert_df.values.tolist())

        valid_listings = set(list_insert_df['id'])

        # Histórica & Datos: Reviews y Reviewers
        print("Procesando hist_reviews y data_reviewers...")
        rev_df = pd.read_csv(os.path.join(BASE_DIR, 'reviews.csv'))
        rev_df = rev_df[rev_df['listing_id'].isin(valid_listings)]
        
        reviewers_df = rev_df[['reviewer_id', 'reviewer_name']].drop_duplicates(subset=['reviewer_id'])
        reviewers_df = clean_df(reviewers_df)
        execute_values(cur, "INSERT INTO data_reviewers (id, reviewer_name) VALUES %s", reviewers_df.values.tolist())

        cols_reviews = ['id', 'listing_id', 'reviewer_id', 'date', 'comments']
        rev_insert_df = rev_df[cols_reviews]
        rev_insert_df = clean_df(rev_insert_df)
        execute_values(cur, "INSERT INTO hist_reviews (id, listing_id, reviewer_id, date, comments) VALUES %s", rev_insert_df.values.tolist())

        # Histórica: Calendar
        print("Procesando hist_calendar...")
        cal_df = pd.read_csv(os.path.join(BASE_DIR, 'calendar.csv'))
        cal_df = cal_df[cal_df['listing_id'].isin(valid_listings)]
        cal_df['available'] = cal_df['available'].map({'t': True, 'f': False})
        if cal_df['price'].dtype == object:
            cal_df['price'] = cal_df['price'].replace(r'[\$,]', '', regex=True).astype(float)
        
        cols_cal = ['listing_id', 'date', 'available', 'price', 'minimum_nights', 'maximum_nights']
        cal_insert_df = cal_df[cols_cal]
        cal_insert_df = clean_df(cal_insert_df)
        execute_values(cur, "INSERT INTO hist_calendar (listing_id, date, available, price, minimum_nights, maximum_nights) VALUES %s", cal_insert_df.values.tolist())

        print("Estableciendo relaciones de llaves foráneas...")
        cur.execute("""
            ALTER TABLE data_listings ADD CONSTRAINT fk_host FOREIGN KEY (host_id) REFERENCES data_hosts(id);
            ALTER TABLE data_listings ADD CONSTRAINT fk_neighbourhood FOREIGN KEY (neighbourhood_id) REFERENCES cat_neighbourhoods(id);
            ALTER TABLE data_listings ADD CONSTRAINT fk_property_type FOREIGN KEY (property_type_id) REFERENCES cat_property_types(id);
            ALTER TABLE data_listings ADD CONSTRAINT fk_room_type FOREIGN KEY (room_type_id) REFERENCES cat_room_types(id);
            
            ALTER TABLE hist_reviews ADD CONSTRAINT fk_listing_rev FOREIGN KEY (listing_id) REFERENCES data_listings(id);
            ALTER TABLE hist_reviews ADD CONSTRAINT fk_reviewer_rev FOREIGN KEY (reviewer_id) REFERENCES data_reviewers(id);
            
            ALTER TABLE hist_calendar ADD CONSTRAINT fk_listing_cal FOREIGN KEY (listing_id) REFERENCES data_listings(id);
        """)

        conn.commit()
        print("\n¡Éxito! Base de datos estandarizada poblada exitosamente.")

    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals(): conn.rollback()
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    run_seed()