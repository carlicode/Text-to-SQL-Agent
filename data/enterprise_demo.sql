-- Enterprise demo database with multiple related tables
PRAGMA foreign_keys = ON;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS shipment_items;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS support_tickets;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS warehouses;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS companies;

CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    founded_year INTEGER
);

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(company_id),
    name TEXT NOT NULL,
    cost_center TEXT UNIQUE NOT NULL
);

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(department_id),
    full_name TEXT NOT NULL,
    title TEXT NOT NULL,
    manager_id INTEGER REFERENCES employees(employee_id),
    salary REAL NOT NULL,
    hire_date TEXT NOT NULL
);

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_category_id INTEGER REFERENCES categories(category_id)
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(category_id),
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    price REAL NOT NULL,
    lifecycle_stage TEXT CHECK (lifecycle_stage IN ('draft','active','discontinued'))
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    company_name TEXT,
    contact_name TEXT NOT NULL,
    country TEXT NOT NULL,
    segment TEXT NOT NULL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    account_owner_id INTEGER NOT NULL REFERENCES employees(employee_id),
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    total_amount REAL NOT NULL
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount REAL DEFAULT 0
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    payment_date TEXT NOT NULL,
    method TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE warehouses (
    warehouse_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    manager_id INTEGER REFERENCES employees(employee_id)
);

CREATE TABLE inventory (
    inventory_id INTEGER PRIMARY KEY,
    warehouse_id INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    on_hand INTEGER NOT NULL,
    safety_stock INTEGER NOT NULL,
    UNIQUE (warehouse_id, product_id)
);

CREATE TABLE shipments (
    shipment_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    warehouse_id INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
    ship_date TEXT NOT NULL,
    carrier TEXT NOT NULL,
    tracking_number TEXT UNIQUE
);

CREATE TABLE shipment_items (
    shipment_item_id INTEGER PRIMARY KEY,
    shipment_id INTEGER NOT NULL REFERENCES shipments(shipment_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL
);

CREATE TABLE support_tickets (
    ticket_id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    assigned_employee_id INTEGER REFERENCES employees(employee_id),
    opened_at TEXT NOT NULL,
    severity TEXT CHECK (severity IN ('low','medium','high','urgent')),
    status TEXT NOT NULL,
    subject TEXT NOT NULL
);

INSERT INTO companies (company_id, name, region, founded_year) VALUES
(1, 'TechNova LATAM', 'Latinoamérica', 2012),
(2, 'NextGen Retail', 'Norteamérica', 2016);

INSERT INTO departments (department_id, company_id, name, cost_center) VALUES
(10, 1, 'Ventas Enterprise', 'LAT-ENT-001'),
(11, 1, 'Operaciones', 'LAT-OPS-002'),
(12, 2, 'Ventas SMB', 'NA-SMB-010'),
(13, 2, 'Logística', 'NA-LOG-011');

INSERT INTO employees (employee_id, department_id, full_name, title, manager_id, salary, hire_date) VALUES
(100, 10, 'Laura Méndez', 'Directora Comercial', NULL, 120000, '2018-03-15'),
(101, 10, 'Jorge Paredes', 'Ejecutivo Senior', 100, 85000, '2019-07-01'),
(102, 11, 'Camila Rojas', 'Gerente de Operaciones', NULL, 95000, '2020-01-10'),
(103, 13, 'Daniel Smith', 'Supervisor Logístico', NULL, 68000, '2021-05-18'),
(104, 12, 'Emily Johnson', 'Account Manager', NULL, 72000, '2019-09-09'),
(105, 10, 'Marcos Díaz', 'Especialista de Renovaciones', 100, 65000, '2022-02-14');

INSERT INTO categories (category_id, name, parent_category_id) VALUES
(1, 'Electrónicos', NULL),
(2, 'Computadoras', 1),
(3, 'Periféricos', 1),
(4, 'Servicios', NULL),
(5, 'Suscripciones', 4);

INSERT INTO products (product_id, category_id, name, sku, price, lifecycle_stage) VALUES
(200, 2, 'Notebook Pro 15"', 'NBPRO-15-2024', 1899, 'active'),
(201, 2, 'Ultrabook Air 13"', 'ULAIR-13-2024', 1399, 'active'),
(202, 3, 'Monitor 4K 27"', 'MON-4K27-2024', 499, 'active'),
(203, 3, 'Docking Station USB-C', 'DOC-USBC-2024', 189, 'active'),
(204, 5, 'Licencia Analytics Cloud', 'LIC-AN-12M', 299, 'active'),
(205, 5, 'Licencia Customer Insights', 'LIC-CI-12M', 259, 'draft');

INSERT INTO customers (customer_id, company_name, contact_name, country, segment) VALUES
(300, 'Grupo Andina', 'Valentina Ortiz', 'Chile', 'Enterprise'),
(301, 'Finanzas Unidas', 'Carlos Pérez', 'México', 'Enterprise'),
(302, 'Retail Norte', 'Susan Clark', 'Estados Unidos', 'SMB'),
(303, 'Logística Sur', 'Martín Gómez', 'Argentina', 'SMB');

INSERT INTO orders (order_id, customer_id, account_owner_id, order_date, status, total_amount) VALUES
(400, 300, 101, '2025-06-02', 'Closed Won', 5124),
(401, 301, 100, '2025-06-18', 'Closed Won', 3788),
(402, 302, 104, '2025-07-05', 'Negotiation', 1899),
(403, 303, 105, '2025-07-12', 'Closed Lost', 0);

INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price, discount) VALUES
(500, 400, 200, 2, 1899, 0.05),
(501, 400, 202, 4, 499, 0),
(502, 401, 201, 2, 1399, 0),
(503, 401, 204, 5, 299, 0.10),
(504, 402, 200, 1, 1899, 0);

INSERT INTO payments (payment_id, order_id, payment_date, method, amount, status) VALUES
(600, 400, '2025-06-10', 'Transferencia', 3000, 'Parcial'),
(601, 400, '2025-07-01', 'Transferencia', 2124, 'Pagado'),
(602, 401, '2025-06-25', 'Tarjeta de Crédito', 3788, 'Pagado');

INSERT INTO warehouses (warehouse_id, name, region, manager_id) VALUES
(700, 'Centro Distribución Santiago', 'Chile', 102),
(701, 'Hub Monterrey', 'México', 103);

INSERT INTO inventory (inventory_id, warehouse_id, product_id, on_hand, safety_stock) VALUES
(800, 700, 200, 35, 10),
(801, 700, 202, 60, 15),
(802, 700, 204, 200, 50),
(803, 701, 201, 25, 8),
(804, 701, 203, 75, 20);

INSERT INTO shipments (shipment_id, order_id, warehouse_id, ship_date, carrier, tracking_number) VALUES
(900, 400, 700, '2025-06-06', 'LATAM Cargo', 'LT-7765-CL'),
(901, 401, 701, '2025-06-20', 'DHL Express', 'DHL-9981-MX');

INSERT INTO shipment_items (shipment_item_id, shipment_id, product_id, quantity) VALUES
(950, 900, 200, 2),
(951, 900, 202, 4),
(952, 901, 201, 2),
(953, 901, 204, 5);

INSERT INTO support_tickets (ticket_id, order_id, customer_id, assigned_employee_id, opened_at, severity, status, subject) VALUES
(1000, 400, 300, 105, '2025-07-03 09:15', 'medium', 'Open', 'Duda sobre licenciamientos en renovación'),
(1001, 401, 301, 101, '2025-07-08 14:22', 'high', 'In Progress', 'Incidencia en activación de Analytics Cloud'),
(1002, NULL, 302, 104, '2025-07-10 10:05', 'low', 'Closed', 'Consulta general sobre roadmap de productos');

