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
        cur.execute("CREATE TABLE categorias (id SERIAL PRIMARY KEY, nombre TEXT, descripcion TEXT, activa BOOLEAN);")
        cur.execute("CREATE TABLE usuarios (id SERIAL PRIMARY KEY, nombre TEXT, email TEXT, telefono TEXT, direccion TEXT, ciudad TEXT, pais TEXT, fecha_registro DATE, activo BOOLEAN);")
        cur.execute("CREATE TABLE proveedores (id SERIAL PRIMARY KEY, empresa TEXT, contacto TEXT, email TEXT, telefono TEXT, direccion TEXT, pais TEXT, calificacion DECIMAL);")
        cur.execute("CREATE TABLE productos (id SERIAL PRIMARY KEY, nombre TEXT, descripcion TEXT, sku TEXT, precio DECIMAL, categoria_id INT, talla TEXT, color TEXT, peso DECIMAL, proveedor_id INT, activo BOOLEAN);")
        cur.execute("CREATE TABLE almacenes (id SERIAL PRIMARY KEY, nombre TEXT, ubicacion TEXT, capacidad INT, encargado TEXT, telefono TEXT, operativo BOOLEAN);")
        cur.execute("CREATE TABLE inventario (id SERIAL PRIMARY KEY, producto_id INT, almacen_id INT, stock INT, nivel_minimo INT, fecha_ultima_actualizacion DATE);")
        cur.execute("CREATE TABLE pedidos (id SERIAL PRIMARY KEY, usuario_id INT, fecha_pedido TIMESTAMP, estado TEXT, direccion_envio TEXT, costo_envio DECIMAL, total DECIMAL);")
        cur.execute("CREATE TABLE detalle_pedidos (id SERIAL PRIMARY KEY, pedido_id INT, producto_id INT, cantidad INT, precio_unitario DECIMAL, descuento DECIMAL, subtotal DECIMAL);")
        cur.execute("CREATE TABLE metodos_pago (id SERIAL PRIMARY KEY, usuario_id INT, tipo TEXT, proveedor_tarjeta TEXT, ultimos_cuatro_digitos TEXT, fecha_expiracion DATE, por_defecto BOOLEAN);")
        cur.execute("CREATE TABLE reseñas (id SERIAL PRIMARY KEY, producto_id INT, usuario_id INT, calificacion INT, comentario TEXT, fecha_reseña DATE, utilidad INT, recomendado BOOLEAN);")

        # --- 2. GENERACIÓN E INSERCIÓN DE DATOS ---
        
        print("Insertando categorías...")
        base_cats = ['Electrónica', 'Ropa', 'Hogar', 'Deportes', 'Juguetes', 'Libros', 'Belleza', 'Mascotas', 'Automotriz', 'Jardín']
        cat_data = []
        for i, nombre in enumerate(base_cats, 1):
            descripcion = f"Todo lo relacionado con {nombre.lower()}"
            activa = random.choices([True, False], weights=[0.9, 0.1])[0]
            cat_data.append((i, nombre, descripcion, activa))
        execute_values(cur, "INSERT INTO categorias (id, nombre, descripcion, activa) VALUES %s", cat_data)
        NUM_CATEGORIAS = len(base_cats)

        print("Insertando usuarios...")
        user_data = []
        for i in range(1, NUM_RECORDS + 1):
            nombre = fake.name().replace("'", "")
            email = fake.unique.email()
            telefono = fake.phone_number()
            direccion = fake.street_address().replace("'", "")
            ciudad = fake.city().replace("'", "")
            pais = fake.country().replace("'", "")
            fecha = fake.date_between(start_date='-2y')
            activo = random.choices([True, False], weights=[0.85, 0.15])[0]
            user_data.append((i, nombre, email, telefono, direccion, ciudad, pais, fecha, activo))
        execute_values(cur, "INSERT INTO usuarios (id, nombre, email, telefono, direccion, ciudad, pais, fecha_registro, activo) VALUES %s", user_data)

        print("Insertando proveedores...")
        prov_data = []
        for i in range(1, NUM_RECORDS + 1):
            empresa = fake.company().replace("'", "")
            contacto = fake.name().replace("'", "")
            email = fake.company_email()
            telefono = fake.phone_number()
            direccion = fake.address().replace("'", "").replace('\n', ', ')
            pais = fake.country().replace("'", "")
            calificacion = round(random.uniform(1.0, 5.0), 2)
            prov_data.append((i, empresa, contacto, email, telefono, direccion, pais, calificacion))
        execute_values(cur, "INSERT INTO proveedores (id, empresa, contacto, email, telefono, direccion, pais, calificacion) VALUES %s", prov_data)

        print("Insertando productos...")
        tallas = ['XS', 'S', 'M', 'L', 'XL', 'N/A']
        colores = ['Rojo', 'Azul', 'Verde', 'Negro', 'Blanco', 'Gris', 'Dorado', 'Plateado', 'Multicolor']
        prod_data = []
        productos_precios = {}
        for i in range(1, NUM_RECORDS + 1):
            nombre = fake.catch_phrase().replace("'", "")
            descripcion = fake.text(max_nb_chars=100).replace("'", "").replace('\n', ' ')
            sku = f"{fake.bothify(text='???-#####').upper()}"
            precio = round(random.uniform(10, 500), 2)
            productos_precios[i] = precio
            categoria_id = random.randint(1, NUM_CATEGORIAS)
            talla = random.choice(tallas)
            color = random.choice(colores)
            peso = round(random.uniform(0.1, 50.0), 2)
            proveedor_id = random.randint(1, NUM_RECORDS)
            activo = random.choices([True, False], weights=[0.9, 0.1])[0]
            prod_data.append((i, nombre, descripcion, sku, precio, categoria_id, talla, color, peso, proveedor_id, activo))
        execute_values(cur, "INSERT INTO productos (id, nombre, descripcion, sku, precio, categoria_id, talla, color, peso, proveedor_id, activo) VALUES %s", prod_data)

        print("Insertando almacenes...")
        alm_data = []
        for i in range(1, NUM_RECORDS + 1):
            nombre = f"Almacén {fake.city()}".replace("'", "")
            ubicacion = fake.address().replace("'", "").replace('\n', ', ')
            capacidad = random.randint(1000, 50000)
            encargado = fake.name().replace("'", "")
            telefono = fake.phone_number()
            operativo = random.choices([True, False], weights=[0.95, 0.05])[0]
            alm_data.append((i, nombre, ubicacion, capacidad, encargado, telefono, operativo))
        execute_values(cur, "INSERT INTO almacenes (id, nombre, ubicacion, capacidad, encargado, telefono, operativo) VALUES %s", alm_data)

        print("Insertando inventario...")
        inv_data = []
        for i in range(1, NUM_RECORDS + 1):
            producto_id = random.randint(1, NUM_RECORDS)
            almacen_id = random.randint(1, NUM_RECORDS)
            stock = random.randint(0, 500)
            nivel_minimo = random.randint(5, 50)
            fecha_ultima_actualizacion = fake.date_between(start_date='-6m')
            inv_data.append((i, producto_id, almacen_id, stock, nivel_minimo, fecha_ultima_actualizacion))
        execute_values(cur, "INSERT INTO inventario (id, producto_id, almacen_id, stock, nivel_minimo, fecha_ultima_actualizacion) VALUES %s", inv_data)

        print("Generando datos de pedidos y detalles...")
        estados_pedido = ['Pendiente', 'Procesando', 'Enviado', 'Entregado', 'Cancelado']
        pedidos_dict = {}
        for i in range(1, NUM_RECORDS + 1):
            usuario_id = random.randint(1, NUM_RECORDS)
            fecha_pedido = fake.date_time_between(start_date='-1y')
            estado = random.choices(estados_pedido, weights=[0.1, 0.1, 0.2, 0.5, 0.1])[0]
            direccion_envio = fake.address().replace("'", "").replace('\n', ', ')
            costo_envio = round(random.uniform(0, 50), 2) if estado != 'Cancelado' else 0.0
            pedidos_dict[i] = {
                'usuario_id': usuario_id,
                'fecha_pedido': fecha_pedido,
                'estado': estado,
                'direccion_envio': direccion_envio,
                'costo_envio': costo_envio,
                'total_detalles': 0.0
            }

        det_data = []
        for i in range(1, NUM_RECORDS + 1):
            pedido_id = random.randint(1, NUM_RECORDS)
            producto_id = random.randint(1, NUM_RECORDS)
            cantidad = random.randint(1, 5)
            precio_unitario = productos_precios[producto_id]
            descuento = round(random.uniform(0, precio_unitario * 0.2), 2)
            subtotal = round((cantidad * precio_unitario) - descuento, 2)
            if subtotal < 0: subtotal = 0.0
            
            pedidos_dict[pedido_id]['total_detalles'] += subtotal
            det_data.append((i, pedido_id, producto_id, cantidad, precio_unitario, descuento, subtotal))

        ped_data = []
        for i in range(1, NUM_RECORDS + 1):
            p = pedidos_dict[i]
            total_final = round(p['total_detalles'] + p['costo_envio'], 2)
            ped_data.append((i, p['usuario_id'], p['fecha_pedido'], p['estado'], p['direccion_envio'], p['costo_envio'], total_final))

        print("Insertando pedidos...")
        execute_values(cur, "INSERT INTO pedidos (id, usuario_id, fecha_pedido, estado, direccion_envio, costo_envio, total) VALUES %s", ped_data)
        
        print("Insertando detalles de pedidos...")
        execute_values(cur, "INSERT INTO detalle_pedidos (id, pedido_id, producto_id, cantidad, precio_unitario, descuento, subtotal) VALUES %s", det_data)

        print("Insertando métodos de pago...")
        tipos_pago = ['Crédito', 'Débito', 'PayPal', 'Transferencia']
        marcas = ['Visa', 'Mastercard', 'Amex', 'N/A']
        pago_data = []
        for i in range(1, NUM_RECORDS + 1):
            usuario_id = random.randint(1, NUM_RECORDS)
            tipo = random.choice(tipos_pago)
            proveedor_tarjeta = random.choice(marcas) if tipo in ['Crédito', 'Débito'] else 'N/A'
            ultimos_cuatro = str(random.randint(1000, 9999)) if tipo in ['Crédito', 'Débito'] else 'N/A'
            fecha_expiracion = fake.date_between(start_date='today', end_date='+5y') if tipo in ['Crédito', 'Débito'] else None
            por_defecto = random.choices([True, False], weights=[0.3, 0.7])[0]
            pago_data.append((i, usuario_id, tipo, proveedor_tarjeta, ultimos_cuatro, fecha_expiracion, por_defecto))
        execute_values(cur, "INSERT INTO metodos_pago (id, usuario_id, tipo, proveedor_tarjeta, ultimos_cuatro_digitos, fecha_expiracion, por_defecto) VALUES %s", pago_data)

        print("Insertando reseñas...")
        rev_data = []
        for i in range(1, NUM_RECORDS + 1):
            producto_id = random.randint(1, NUM_RECORDS)
            usuario_id = random.randint(1, NUM_RECORDS)
            calificacion = random.randint(1, 5)
            comentario = fake.sentence().replace("'", "")
            fecha_reseña = fake.date_between(start_date='-6m', end_date='today')
            utilidad = random.randint(0, 50)
            recomendado = calificacion >= 4
            rev_data.append((i, producto_id, usuario_id, calificacion, comentario, fecha_reseña, utilidad, recomendado))
        execute_values(cur, "INSERT INTO reseñas (id, producto_id, usuario_id, calificacion, comentario, fecha_reseña, utilidad, recomendado) VALUES %s", rev_data)

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