import sqlite3
from typing import Dict, List, Tuple, Any, Optional

def get_database_connection(db_path: str):
    """Obtiene la conexión con la base de datos SQLite."""
    return sqlite3.connect(db_path)

def get_database_schema(connection) -> Dict[str, Dict]:
    """Obtiene el esquema completo de la base de datos incluyendo constraints, foreign keys e índices."""
    cursor = connection.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    schema = {}
    
    for (table_name,) in tables:
        table_info = {
            "columns": [],
            "primary_keys": [],
            "foreign_keys": [],
            "indexes": [],
            "sample_data": None
        }
        
        # Información de columnas con PRAGMA table_info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        # Formato: (cid, name, type, notnull, dflt_value, pk)
        
        for col in columns:
            col_info = {
                "name": col[1],
                "type": col[2],
                "not_null": bool(col[3]),
                "default_value": col[4],
                "primary_key": bool(col[5])
            }
            table_info["columns"].append(col_info)
            
            if col_info["primary_key"]:
                table_info["primary_keys"].append(col_info["name"])
        
        # Foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()
        # Formato: (id, seq, table, from, to, on_update, on_delete, match)
        for fk in fks:
            table_info["foreign_keys"].append({
                "from_column": fk[3],
                "to_table": fk[2],
                "to_column": fk[4]
            })
        
        # Índices
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}' AND name NOT LIKE 'sqlite_%'")
        indexes = cursor.fetchall()
        for (index_name,) in indexes:
            cursor.execute(f"PRAGMA index_info({index_name})")
            index_cols = cursor.fetchall()
            # Formato: (seqno, cid, name)
            table_info["indexes"].append({
                "name": index_name,
                "columns": [col[2] for col in index_cols]
            })
        
        # Muestra de datos (primeras 2 filas para ayudar al LLM a entender los datos)
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
            sample = cursor.fetchall()
            if sample:
                column_names = [col[1] for col in columns]
                table_info["sample_data"] = [
                    dict(zip(column_names, row)) for row in sample
                ]
        except:
            pass  # Si hay error obteniendo muestra, continuar sin ella
        
        schema[table_name] = table_info
    
    return schema

def format_schema(schema: Dict[str, Dict]) -> str:
    """Formatea el esquema completo de la base de datos como string legible y estructurado."""
    if not schema:
        return "No hay tablas en la base de datos."
    
    schema_str = f"BASE DE DATOS: SQLite\nTotal de tablas: {len(schema)}\n\n"
    schema_str += "=" * 60 + "\n\n"
    
    for table_name, table_info in schema.items():
        schema_str += f"TABLA: {table_name}\n"
        schema_str += "-" * 40 + "\n\n"
        
        # Columnas
        schema_str += "COLUMNAS:\n"
        for col in table_info["columns"]:
            constraints = []
            if col["primary_key"]:
                constraints.append("PRIMARY KEY")
            if col["not_null"]:
                constraints.append("NOT NULL")
            if col["default_value"]:
                constraints.append(f"DEFAULT {col['default_value']}")
            
            constraint_str = f" ({', '.join(constraints)})" if constraints else ""
            schema_str += f"  • {col['name']} ({col['type']}){constraint_str}\n"
        
        # Primary Keys
        if table_info["primary_keys"]:
            schema_str += f"\nPRIMARY KEY: {', '.join(table_info['primary_keys'])}\n"
        
        # Foreign Keys
        if table_info["foreign_keys"]:
            schema_str += "\nRELACIONES (FOREIGN KEYS):\n"
            for fk in table_info["foreign_keys"]:
                schema_str += f"  • {table_name}.{fk['from_column']} → {fk['to_table']}.{fk['to_column']}\n"
        
        # Índices
        if table_info["indexes"]:
            schema_str += "\nÍNDICES:\n"
            for idx in table_info["indexes"]:
                cols_str = ", ".join(idx["columns"])
                schema_str += f"  • {idx['name']} ON ({cols_str})\n"
        
        # Muestra de datos
        if table_info["sample_data"]:
            schema_str += "\nMUESTRA DE DATOS (ejemplos):\n"
            for i, sample_row in enumerate(table_info["sample_data"], 1):
                schema_str += f"  Fila {i}: {sample_row}\n"
        
        schema_str += "\n" + "=" * 60 + "\n\n"
    
    return schema_str

def execute_query(connection, query: str) -> List[Tuple[Any, ...]]:
    """Ejecuta una consulta SQL y retorna los resultados."""
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    return results
