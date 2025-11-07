-- Base de datos de prueba para TechNova
-- Tabla de ventas con productos electrónicos

-- Crear tabla de ventas
CREATE TABLE ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL,
    pais TEXT NOT NULL,
    fecha_venta TEXT NOT NULL
);

-- Insertar datos de ejemplo de TechNova (solo los 2 productos de la imagen)
INSERT INTO ventas (producto, categoria, precio, pais, fecha_venta) VALUES
('iPhone 14', 'smartphones', 1300, 'Argentina', '2024-05-10'),
('MacBook Air', 'notebooks', 1800, 'Chile', '2024-05-12');
