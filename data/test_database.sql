-- Base de datos de prueba para carga manual
-- Estructura más compleja con múltiples tablas y relaciones

-- Crear tabla de categorías
CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

-- Crear tabla de usuarios
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    edad INTEGER,
    ciudad TEXT,
    fecha_registro TEXT
);

-- Crear tabla de productos (con foreign key a categorias)
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    stock INTEGER DEFAULT 0,
    categoria_id INTEGER,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- Crear tabla de pedidos (con foreign keys a usuarios y productos)
CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_pedido TEXT NOT NULL,
    estado TEXT DEFAULT 'pendiente',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Insertar datos de ejemplo

-- Categorías
INSERT INTO categorias (nombre, descripcion) VALUES
('Electrónicos', 'Dispositivos electrónicos y tecnología'),
('Ropa', 'Ropa y accesorios de moda'),
('Hogar', 'Artículos para el hogar');

-- Usuarios
INSERT INTO usuarios (nombre, email, edad, ciudad, fecha_registro) VALUES
('Juan Pérez', 'juan@example.com', 28, 'Madrid', '2024-01-15'),
('María García', 'maria@example.com', 35, 'Barcelona', '2024-02-20'),
('Carlos López', 'carlos@example.com', 42, 'Valencia', '2024-03-10');

-- Productos
INSERT INTO productos (nombre, precio, stock, categoria_id) VALUES
('Laptop HP', 899.99, 15, 1),
('iPhone 15', 999.99, 8, 1),
('Camiseta Nike', 29.99, 50, 2),
('Sofá Moderno', 599.99, 5, 3),
('Auriculares Sony', 149.99, 20, 1);

-- Pedidos
INSERT INTO pedidos (usuario_id, producto_id, cantidad, fecha_pedido, estado) VALUES
(1, 1, 1, '2024-04-01', 'completado'),
(2, 2, 2, '2024-04-05', 'pendiente'),
(3, 4, 1, '2024-04-10', 'enviado'),
(1, 5, 1, '2024-04-12', 'completado');

