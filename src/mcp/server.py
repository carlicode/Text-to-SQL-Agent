from mcp.server.fastmcp import FastMCP
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path when launched as a standalone script
PROJECT_ROOT = Path(__file__).resolve().parents[2]
project_root_str = str(PROJECT_ROOT)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

from src.database import get_database_connection, get_database_schema, format_schema

# Estado del servidor (db_path y context se pasan como variables de entorno o argumentos)
mcp = FastMCP("Text-to-SQL-Agent")

@mcp.tool()
def get_database_schema_tool() -> str:
    """Obtiene el esquema completo de la base de datos SQLite.
    Usa esta herramienta cuando necesites entender la estructura de las tablas,
    columnas, relaciones y tipos de datos disponibles en la base de datos.
    Returns:
        str: Esquema formateado de la base de datos
    """
    db_path = os.getenv("MCP_DB_PATH", "data/test_database.db")
    
    try:
        connection = get_database_connection(db_path)
        schema = get_database_schema(connection)
        schema_str = format_schema(schema)
        connection.close()
        return schema_str
    except Exception as e:
        return f"Error obteniendo esquema: {str(e)}"


@mcp.tool()
def execute_sql(query: str) -> str:
    """Ejecuta una consulta SQL en la base de datos y retorna los resultados.
    Usa esta herramienta cuando necesites obtener datos específicos de la base de datos.
    Asegúrate de que la consulta SQL sea válida para SQLite.
    Args:
        query: Consulta SQL a ejecutar (debe ser válida para SQLite)
    Returns:
        str: Resultados de la consulta en formato legible, o mensaje de error
    """
    db_path = os.getenv("MCP_DB_PATH", "data/test_database.db")
    
    try:
        connection = get_database_connection(db_path)
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Obtener nombres de columnas
        try:
            column_names = [description[0] for description in cursor.description]
            formatted_results = []
            for row in results:
                formatted_results.append(dict(zip(column_names, row)))
            results_str = str(formatted_results)
        except:
            results_str = str(results)
        
        connection.close()
        return results_str if results_str else "No se encontraron resultados."
    except Exception as e:
        return f"Error ejecutando SQL: {str(e)}"


@mcp.tool()
def get_context() -> str:
    """Obtiene el contexto general de la empresa/información disponible.
    Usa esta herramienta cuando la pregunta sea sobre información general
    de la empresa o negocio que no requiere consultar datos específicos de la base de datos.
    Returns:
        str: Contexto de la empresa
    """
    context = os.getenv("MCP_CONTEXT", "No hay contexto disponible.")
    return context


if __name__ == "__main__":
    mcp.run(transport="stdio")

