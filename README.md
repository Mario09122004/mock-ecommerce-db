<img width="1093" height="703" alt="DB diagram" src="https://github.com/user-attachments/assets/db4e271d-0b14-42f2-82c5-0423654326fd" />

---

# E-commerce Test Database with PostgreSQL

## Description
This repository contains the files needed to deploy and populate a relational test database (PostgreSQL) designed for an e-commerce system. It was developed to provide a testing environment with a more robust database containing more data, enabling more complex queries and performance testing.

## Contents

- `compose.yaml`: Docker Compose file to quickly spin up a PostgreSQL container (version 14.22-bookworm) with the initial configuration of the `ecommerce_db` database.
- `db_create.py`: Python script that uses the `psycopg2` and `Faker` libraries to create a structure of 10 interrelated tables and automatically populate each with 10,000 test records.
- `backup.sql`: A backup file containing the structure and the data already generated, ideal for quickly restoring the database without needing to run the Python script.

## Database Structure

The database simulates an e-commerce environment and consists of the following 10 relational tables:

1. **categories**: Product categories.

2. **users**: Customers registered in the system.

3. **suppliers**: Companies that supply the items.

4. **products**: General product catalog.

5. **warehouses**: Physical storage locations.

6. **inventory**: Product stock control for each warehouse.

7. **orders**: Purchase orders placed by users.

8. **order_details**: List of specific products and quantities within each order.

9. **payment_methods**: Payment methods registered by users (credit cards, PayPal, etc.).

10. **reviews**: User ratings and comments on products.

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose installed.
- [Python 3.x](https://www.python.org/) (Optional, only if you want to run the `db_create.py` script to generate new data).
  - Python dependencies: `psycopg2`, `Faker`.


## Instructions for Use

### 1. Start the database with Docker
Run the following command in the project root directory to start the PostgreSQL container in the background:
```bash
docker compose up -d
```
This will create the `ecommerce_db` database, exposed on local port `5432`, with the username and password `admin`.

### 2. Populate the Database (Option A: Restore from Backup)
If you prefer to use the pre-generated data directly, you can restore the `backup.sql` file.
Assuming the service name in Docker Compose is `postgres`, you can restore it like this:
```bash
cat backup.sql | docker exec -i $(docker compose ps -q postgres) psql -U admin -d ecommerce_db
```

### 3. Populate the database (Option B: Generate new data with Python)
If you prefer to generate the data from scratch (note that this will delete any existing tables):
1. Create a virtual environment and install the necessary dependencies:
   ```bash
   pip install psycopg2-binary faker
   ```
2. Run the script:
   ```bash
   python db_create.py
   ```

## Security and Performance Notes
- **Warning:** The credentials configured in the `compose.yaml` file (username: `admin`, password: `admin`) are strictly for **local development and testing environments**. Under no circumstances should they be used in a production environment.
- The `db_create.py` script inserts a total of 100,000 records (10,000 per table) and then establishes the foreign key relationships. The execution time will depend on the resources of your local machine.

---

# DB de pruebas de E-commerce con PostgreSQL

## Descripción
Este repositorio contiene los archivos necesarios para desplegar y poblar una base de datos relacional de prueba (PostgreSQL) orientada a un sistema de comercio electrónico (E-commerce). Fue desarrollado para tener un entorno de pruebas con una base de datos más robusta y con más datos para poder realizar consultas más complejas y pruebas de rendimiento.

## Contenido

- `compose.yaml`: Archivo de Docker Compose para levantar rápidamente un contenedor de PostgreSQL (versión 14.22-bookworm) con la configuración inicial de la base de datos `ecommerce_db`.
- `db_create.py`: Script en Python que utiliza las librerías `psycopg2` y `Faker` para crear la estructura de 10 tablas interrelacionadas y poblarlas automáticamente con 10,000 registros de prueba cada una.
- `backup.sql`: Archivo de respaldo (backup) que contiene la estructura y los datos ya generados, ideal para restaurar la base de datos rápidamente sin necesidad de ejecutar el script de Python.

## Estructura de la Base de Datos

La base de datos simula un entorno de E-commerce y consta de las siguientes 10 tablas relacionales:

1. **categorias**: Categorías de los productos.

2. **usuarios**: Clientes registrados en el sistema.

3. **proveedores**: Empresas proveedoras de los artículos.

4. **productos**: Catálogo general de productos.

5. **almacenes**: Ubicaciones físicas de almacenamiento.

6. **inventario**: Control de stock de los productos por cada almacén.

7. **pedidos**: Órdenes de compra realizadas por los usuarios.

8. **detalle_pedidos**: Relación de productos específicos y cantidades dentro de cada pedido.

9. **metodos_pago**: Formas de pago registradas por los usuarios (Tarjetas, PayPal, etc.).

10. **reseñas**: Calificaciones y comentarios de los usuarios sobre los productos.

## Requisitos Previos

- [Docker](https://www.docker.com/) y Docker Compose instalados.
- [Python 3.x](https://www.python.org/) (Opcional, solo si deseas ejecutar el script `db_create.py` para generar datos nuevos).
  - Dependencias de Python: `psycopg2`, `Faker`.

## Instrucciones de Uso

### 1. Levantar la base de datos con Docker
Ejecuta el siguiente comando en la raíz del proyecto para iniciar el contenedor de PostgreSQL en segundo plano:
```bash
docker compose up -d
```
Esto creará la base de datos `ecommerce_db` expuesta en el puerto local `5432` con el usuario y contraseña `admin`.

### 2. Poblar la base de datos (Opción A: Restaurar desde el backup)
Si prefieres utilizar los datos pre-generados directamente, puedes restaurar el archivo `backup.sql`.
Asumiendo que el nombre del servicio en Docker Compose es `postgres`, puedes restaurarlo así:
```bash
cat backup.sql | docker exec -i $(docker compose ps -q postgres) psql -U admin -d ecommerce_db
```

### 3. Poblar la base de datos (Opción B: Generar datos nuevos con Python)
Si prefieres generar los datos desde cero (ten en cuenta que esto borrará cualquier tabla existente):
1. Crea un entorno virtual e instala las dependencias necesarias:
   ```bash
   pip install psycopg2-binary faker
   ```
2. Ejecuta el script:
   ```bash
   python db_create.py
   ```

## Notas de Seguridad y Rendimiento
- **Advertencia:** Las credenciales configuradas en el archivo `compose.yaml` (usuario: `admin`, password: `admin`) son estrictamente para **entornos de desarrollo local y pruebas**. Bajo ninguna circunstancia deben utilizarse en un entorno de producción.
- El script `db_create.py` realiza la inserción de 100,000 registros en total (10,000 por tabla) y posteriormente establece las relaciones de llaves foráneas. El tiempo de ejecución dependerá de los recursos de tu máquina local.
