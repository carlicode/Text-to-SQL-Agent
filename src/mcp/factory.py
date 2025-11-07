from mcp import StdioServerParameters
from typing import Optional
import os
import pathlib
import sys


class MCPServerFactory:
    """Factory para crear servidores MCP según el tipo de base de datos."""
    
    @staticmethod
    def create_server(db_path: str, context: str) -> StdioServerParameters:
        """
        Crea parámetros de servidor MCP para SQLite.
        
        Args:
            db_path: Ruta absoluta a la base de datos SQLite
            context: Contexto de la empresa/información general
            
        Returns:
            StdioServerParameters: Parámetros para conectar al servidor MCP
        """
        # Obtener ruta absoluta del servidor MCP
        current_dir = pathlib.Path(__file__).parent
        mcp_server_path = str(current_dir / "server.py")
        
        # Obtener el directorio raíz del proyecto (dos niveles arriba desde src/mcp/)
        project_root = current_dir.parent.parent
        project_root_str = str(project_root)
        
        # Obtener PYTHONPATH actual y agregar el directorio raíz
        current_pythonpath = os.environ.get("PYTHONPATH", "")
        if current_pythonpath:
            new_pythonpath = f"{project_root_str}:{current_pythonpath}"
        else:
            new_pythonpath = project_root_str
        
        db_path_abs = os.path.abspath(db_path)
        
        python_executable = sys.executable or "python"

        return StdioServerParameters(
            command=python_executable,
            args=[mcp_server_path],
            env={
                "MCP_DB_PATH": db_path_abs,
                "MCP_CONTEXT": context,
                "PYTHONPATH": new_pythonpath,
            }
        )

