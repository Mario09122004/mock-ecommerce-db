import psycopg2
from psycopg2.extras import execute_values
import random
from faker import Faker

fake = Faker()

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ecommerce_db",
    "user": "admin",
    "password": "admin"
}

NUM_RECORDS = 10000

def run_seed():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Conectado a PostgreSQL exitosamente.")

        # --- 0. LIMPIEZA TOTAL ---
        print("Limpiando tablas anteriores...")
        cur.execute("""
            DROP TABLE IF EXISTS reseñas, metodos_pago, detalle_pedidos, pedidos, 
            inventario, productos, almacenes, usuarios, categorias, proveedores CASCADE;
        """)

        # --- 1. CREACIÓN DE TABLAS ---
        print("Creando estructura de tablas...")
        cur.execute("CREATE TABLE categorias (id SERIAL PRIMARY KEY, nombre TEXT);")
        cur.execute("CREATE TABLE usuarios (id SERIAL PRIMARY KEY, nombre TEXT, email TEXT, fecha_registro DATE);")
        cur.execute("CREATE TABLE proveedores (id SERIAL PRIMARY KEY, empresa TEXT, contacto TEXT);")
        cur.execute("CREATE TABLE productos (id SERIAL PRIMARY KEY, nombre TEXT, precio DECIMAL, categoria_id INT, talla TEXT, color TEXT, proveedor_id INT);")
        cur.execute("CREATE TABLE almacenes (id SERIAL PRIMARY KEY, ubicacion TEXT, capacidad INT);")
        cur.execute("CREATE TABLE inventario (id SERIAL PRIMARY KEY, producto_id INT, almacen_id INT, stock INT);")
        cur.execute("CREATE TABLE pedidos (id SERIAL PRIMARY KEY, usuario_id INT, fecha_pedido TIMESTAMP, total DECIMAL);")
        cur.execute("CREATE TABLE detalle_pedidos (id SERIAL PRIMARY KEY, pedido_id INT, producto_id INT, cantidad INT);")
        cur.execute("CREATE TABLE metodos_pago (id SERIAL PRIMARY KEY, usuario_id INT, tipo TEXT, proveedor_tarjeta TEXT);")
        cur.execute("CREATE TABLE reseñas (id SERIAL PRIMARY KEY, producto_id INT, usuario_id INT, calificacion INT, comentario TEXT);")

        # --- 2. GENERACIÓN E INSERCIÓN DE DATOS ---
        
        print("Insertando categorías...")
        base_cats = ['Electrónica', 'Ropa', 'Hogar', 'Deportes', 'Juguetes', 'Libros', 'Belleza', 'Mascotas', 'Automotriz', 'Jardín']
        cat_data = []
        for i in range(1, NUM_RECORDS + 1):
            if i <= len(base_cats):
                nombre = base_cats[i-1]
            else:
                nombre = f"{fake.word().capitalize()} {fake.word()}"
            cat_data.append((i, nombre))
        execute_values(cur, "INSERT INTO categorias (id, nombre) VALUES %s", cat_data)

        print("Insertando usuarios...")
        user_data = []
        for i in range(1, NUM_RECORDS + 1):
            nombre = fake.name().replace("'", "")
            email = fake.unique.email()
            fecha = fake.date_between(start_date='-2y')
            user_data.append((i, nombre, email, fecha))
        execute_values(cur, "INSERT INTO usuarios (id, nombre, email, fecha_registro) VALUES %s", user_data)

        print("Insertando proveedores...")
        prov_data = []
        for i in range(1, NUM_RECORDS + 1):
            empresa = fake.company().replace("'", "")
            contacto = fake.phone_number()
            prov_data.append((i, empresa, contacto))
        execute_values(cur, "INSERT INTO proveedores (id, empresa, contacto) VALUES %s", prov_data)

        print("Insertando productos...")
        tallas = ['XS', 'S', 'M', 'L', 'XL', 'N/A']
        colores = ['Rojo', 'Azul', 'Verde', 'Negro', 'Blanco', 'Gris', 'Dorado']
        prod_data = []
        for i in range(1, NUM_RECORDS + 1):
            nombre = fake.catch_phrase().replace("'", "")
            precio = round(random.uniform(10, 500), 2)
            categoria_id = random.randint(1, NUM_RECORDS)
            talla = random.choice(tallas)
            color = random.choice(colores)
            proveedor_id = random.randint(1, NUM_RECORDS)
            prod_data.append((i, nombre, precio, categoria_id, talla, color, proveedor_id))
        execute_values(cur, "INSERT INTO productos (id, nombre, precio, categoria_id, talla, color, proveedor_id) VALUES %s", prod_data)

        print("Insertando almacenes...")
        alm_data = []
        for i in range(1, NUM_RECORDS + 1):
            ubicacion = fake.city().replace("'", "")
            capacidad = random.randint(1000, 5000)
            alm_data.append((i, ubicacion, capacidad))
        execute_values(cur, "INSERT INTO almacenes (id, ubicacion, capacidad) VALUES %s", alm_data)

        print("Insertando inventario...")
        inv_data = []
        for i in range(1, NUM_RECORDS + 1):
            producto_id = random.randint(1, NUM_RECORDS)
            almacen_id = random.randint(1, NUM_RECORDS)
            stock = random.randint(0, 100)
            inv_data.append((i, producto_id, almacen_id, stock))
        execute_values(cur, "INSERT INTO inventario (id, producto_id, almacen_id, stock) VALUES %s", inv_data)

        print("Insertando pedidos...")
        ped_data = []
        for i in range(1, NUM_RECORDS + 1):
            usuario_id = random.randint(1, NUM_RECORDS)
            fecha_pedido = fake.date_time_between(start_date='-1y')
            total = round(random.uniform(20, 2000), 2)
            ped_data.append((i, usuario_id, fecha_pedido, total))
        execute_values(cur, "INSERT INTO pedidos (id, usuario_id, fecha_pedido, total) VALUES %s", ped_data)

        print("Insertando detalles de pedidos...")
        det_data = []
        for i in range(1, NUM_RECORDS + 1):
            pedido_id = random.randint(1, NUM_RECORDS)
            producto_id = random.randint(1, NUM_RECORDS)
            cantidad = random.randint(1, 5)
            det_data.append((i, pedido_id, producto_id, cantidad))
        execute_values(cur, "INSERT INTO detalle_pedidos (id, pedido_id, producto_id, cantidad) VALUES %s", det_data)

        print("Insertando métodos de pago...")
        tipos_pago = ['Crédito', 'Débito', 'PayPal', 'Transferencia']
        marcas = ['Visa', 'Mastercard', 'Amex', 'N/A']
        pago_data = []
        for i in range(1, NUM_RECORDS + 1):
            usuario_id = random.randint(1, NUM_RECORDS)
            tipo = random.choice(tipos_pago)
            proveedor_tarjeta = random.choice(marcas)
            pago_data.append((i, usuario_id, tipo, proveedor_tarjeta))
        execute_values(cur, "INSERT INTO metodos_pago (id, usuario_id, tipo, proveedor_tarjeta) VALUES %s", pago_data)

        print("Insertando reseñas...")
        rev_data = []
        for i in range(1, NUM_RECORDS + 1):
            producto_id = random.randint(1, NUM_RECORDS)
            usuario_id = random.randint(1, NUM_RECORDS)
            calificacion = random.randint(1, 5)
            comentario = fake.sentence().replace("'", "")
            rev_data.append((i, producto_id, usuario_id, calificacion, comentario))
        execute_values(cur, "INSERT INTO reseñas (id, producto_id, usuario_id, calificacion, comentario) VALUES %s", rev_data)

        print("Estableciendo relaciones de llaves foráneas...")
        cur.execute("""
            ALTER TABLE productos ADD CONSTRAINT fk_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id);
            ALTER TABLE productos ADD CONSTRAINT fk_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores(id);
            ALTER TABLE inventario ADD CONSTRAINT fk_producto_inv FOREIGN KEY (producto_id) REFERENCES productos(id);
            ALTER TABLE inventario ADD CONSTRAINT fk_almacen_inv FOREIGN KEY (almacen_id) REFERENCES almacenes(id);
            ALTER TABLE pedidos ADD CONSTRAINT fk_usuario_ped FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
            ALTER TABLE detalle_pedidos ADD CONSTRAINT fk_pedido_det FOREIGN KEY (pedido_id) REFERENCES pedidos(id);
            ALTER TABLE detalle_pedidos ADD CONSTRAINT fk_producto_det FOREIGN KEY (producto_id) REFERENCES productos(id);
            ALTER TABLE metodos_pago ADD CONSTRAINT fk_usuario_pago FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
            ALTER TABLE reseñas ADD CONSTRAINT fk_producto_res FOREIGN KEY (producto_id) REFERENCES productos(id);
            ALTER TABLE reseñas ADD CONSTRAINT fk_usuario_res FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
        """)
        
        conn.commit()
        print(f"\n¡Éxito! Base de datos poblada con 10 tablas y {NUM_RECORDS} registros cada una.")

    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals(): conn.rollback()
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    run_seed()