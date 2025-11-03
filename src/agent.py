"""Agente usando MCP con Bedrock Converse API directamente."""
from mcp import StdioServerParameters
from src.mcp.client import MCPClient
from src.mcp.factory import MCPServerFactory
from typing import Optional
import os
import asyncio
import boto3
import json


def get_bedrock_model_id(model_name: str) -> str:
    """Convierte el nombre del modelo a formato Bedrock."""
    model_mapping = {
        "Claude 3 Sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
        "Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "Llama 3 70B": "meta.llama3-70b-instruct-v1:0"
    }
    return model_mapping.get(model_name, "anthropic.claude-3-haiku-20240307-v1:0")


def create_bedrock_client(aws_access_key: Optional[str] = None,
                         aws_secret_key: Optional[str] = None):
    """Crea cliente de Bedrock con credenciales explícitas."""
    # Siempre requerir credenciales explícitas
    if not aws_access_key or not aws_secret_key:
        raise ValueError(
            "Las credenciales AWS son requeridas. "
            "Por favor ingresa Access Key y Secret Key en la interfaz."
        )
    
    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name='us-east-1'
    )
    return session.client('bedrock-runtime')


def convert_mcp_tool_to_bedrock(tool):
    """
    Convierte una herramienta MCP al formato que espera Bedrock Converse.
    
    Args:
        tool: Herramienta MCP
        
    Returns:
        dict: Especificación de herramienta para Bedrock
    """
    # Obtener inputSchema de la herramienta MCP
    input_schema = {}
    
    # Intentar obtener el schema de diferentes formas
    if hasattr(tool, 'inputSchema'):
        schema_attr = tool.inputSchema
        if isinstance(schema_attr, dict):
            input_schema = schema_attr
        elif hasattr(schema_attr, 'json'):
            input_schema = schema_attr.json
    elif hasattr(tool, 'input_schema_json'):
        input_schema = tool.input_schema_json
    
    # Si no tiene schema, crear uno básico según el nombre de la herramienta
    if not input_schema:
        tool_name_lower = tool.name.lower()
        if "sql" in tool_name_lower or "execute" in tool_name_lower:
            input_schema = {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Consulta SQL a ejecutar"
                    }
                },
                "required": ["query"]
            }
        elif "schema" in tool_name_lower or "context" in tool_name_lower:
            input_schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
        else:
            input_schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
    
    return {
        "toolSpec": {
            "name": tool.name,
            "description": tool.description or f"Tool: {tool.name}",
            "inputSchema": {
                "json": input_schema
            }
        }
    }


async def execute_tool_with_mcp(mcp_client: MCPClient, tool_name: str, arguments: dict):
    """
    Ejecuta una herramienta usando el cliente MCP.
    
    Args:
        mcp_client: Cliente MCP conectado
        tool_name: Nombre de la herramienta a ejecutar
        arguments: Argumentos para la herramienta
        
    Returns:
        str: Resultado de la ejecución de la herramienta
    """
    try:
        result = await mcp_client.call_tool(tool_name, arguments)
        
        # Extraer texto del resultado MCP
        if hasattr(result, 'content') and result.content:
            if isinstance(result.content, list) and len(result.content) > 0:
                content_item = result.content[0]
                if hasattr(content_item, 'text'):
                    return content_item.text
                elif isinstance(content_item, dict) and 'text' in content_item:
                    return content_item['text']
                elif isinstance(content_item, str):
                    return content_item
        
        # Si no tiene formato esperado, convertir a string
        return str(result)
    except Exception as e:
        return f"Error ejecutando herramienta {tool_name}: {str(e)}"


async def process_with_bedrock_converse(bedrock_client, model_id: str, question: str, 
                                        mcp_client: MCPClient, tools: list):
    """
    Procesa una consulta usando Bedrock Converse API con herramientas MCP.
    
    Implementa un ciclo conversacional donde Bedrock puede usar herramientas múltiples veces.
    """
    # Convertir herramientas MCP al formato Bedrock
    bedrock_tools = [convert_mcp_tool_to_bedrock(tool) for tool in tools]
    
    messages = [
        {
            "role": "user",
            "content": [{"text": question}]
        }
    ]
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        try:
            # Llamar a Bedrock Converse API
            response = bedrock_client.converse(
                modelId=model_id,
                messages=messages,
                toolConfig={
                    "tools": bedrock_tools
                } if bedrock_tools else None,
                inferenceConfig={
                    "maxTokens": 4096,
                    "temperature": 0.7
                }
            )
            
            # Procesar respuesta
            output = response.get('output', {})
            message = output.get('message', {})
            content_list = message.get('content', [])
            
            if not content_list:
                break
            
            # Revisar si el modelo quiere usar herramientas o tiene texto
            tool_uses = []
            text_parts = []
            
            for content_item in content_list:
                if 'toolUse' in content_item:
                    tool_uses.append(content_item['toolUse'])
                elif 'text' in content_item:
                    text_parts.append(content_item['text'])
            
            # Si hay texto y no hay tool uses, es la respuesta final
            if text_parts and not tool_uses:
                return ''.join(text_parts)
            
            # Si hay tool uses, ejecutarlas y continuar el ciclo
            if tool_uses:
                tool_results = []
                
                for tool_use in tool_uses:
                    tool_id = tool_use.get('toolUseId')
                    tool_name = tool_use.get('name')
                    tool_input = tool_use.get('input', {})
                    
                    # Ejecutar herramienta con MCP
                    tool_result_text = await execute_tool_with_mcp(
                        mcp_client, tool_name, tool_input
                    )
                    
                    tool_results.append({
                        "toolUseId": tool_id,
                        "content": [{"text": str(tool_result_text)}]
                    })
                
                # Agregar mensaje del asistente con tool uses a la conversación
                messages.append({
                    "role": "assistant",
                    "content": content_list
                })
                
                # Agregar resultados de herramientas como mensaje del usuario
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "toolResult": result
                        } for result in tool_results
                    ]
                })
            else:
                # Respuesta final sin herramientas
                if text_parts:
                    return ''.join(text_parts)
                break
                
        except Exception as e:
            return f"Error en conversación con Bedrock: {str(e)}"
    
    # Si llegamos aquí, se alcanzó el máximo de iteraciones
    return "Se alcanzó el máximo de iteraciones. Intenta reformular tu pregunta."


def process_query_with_mcp(question: str, model_name: str, db_path: str, 
                           context: str, aws_access_key: Optional[str] = None,
                           aws_secret_key: Optional[str] = None):
    """
    Procesa una consulta usando MCP con Bedrock Converse API.
    
    Usa:
    - FastMCP server (src/mcp/server.py) con transporte stdio
    - Cliente MCP personalizado usando el paquete mcp de Python
    - Bedrock Converse API directamente con boto3
    """
    async def process_async():
        """Procesa la consulta de forma asíncrona."""
        try:
            # Validar credenciales antes de continuar
            if not aws_access_key or not aws_secret_key:
                return {
                    "sql_query": "",
                    "response": "Error: Las credenciales AWS son requeridas. Por favor ingresa Access Key y Secret Key en la interfaz."
                }
            
            # Crear servidor MCP usando la factory
            server_params = MCPServerFactory.create_server(db_path, context)
            
            # Crear cliente MCP y conectar
            mcp_client = MCPClient(server_params)
            
            async with mcp_client:
                # Obtener herramientas disponibles del servidor MCP
                tools = await mcp_client.get_available_tools()
                
                # Crear cliente de Bedrock con credenciales explícitas
                bedrock_client = create_bedrock_client(aws_access_key, aws_secret_key)
                model_id = get_bedrock_model_id(model_name)
                
                # Procesar con Bedrock Converse API y herramientas MCP
                response = await process_with_bedrock_converse(
                    bedrock_client, model_id, question, mcp_client, tools
                )
                
                return {
                    "sql_query": "MCP Tools via Bedrock Converse",
                    "response": response
                }
                
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {
                "sql_query": "",
                "response": f"Error procesando consulta: {str(e)}\n\nDetalles técnicos:\n{type(e).__name__}\n\nTraceback:\n{error_trace}"
            }
    
    # Ejecutar de forma síncrona
    try:
        return asyncio.run(process_async())
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return {
            "sql_query": "",
            "response": f"Error ejecutando agente: {str(e)}\n\nAsegúrate de:\n1. Tener instalado el paquete mcp (pip install mcp)\n2. Tener configuradas las credenciales AWS correctamente\n3. Tener acceso al modelo Bedrock seleccionado\n\nTraceback:\n{error_trace}"
        }
