# Text-to-SQL Agent

¡Hola! 👋 

Este proyecto contiene un agente conversacional que convierte preguntas en lenguaje natural en consultas SQL y las ejecuta usando modelos de IA de AWS Bedrock.

## 🚀 Inicio rápido

Este repositorio tiene **dos ramas** con diferentes implementaciones. Elige la que mejor se ajuste a tus necesidades:

### 📦 Rama 1: `1-simple_text_to_SQL` (Recomendada para empezar)

**¿Qué tiene?**
- Implementación simple y directa con **LangChain**
- Conecta directamente con AWS Bedrock
- Menor latencia y configuración rápida
- Perfecta para prototipos y pruebas

**¿Cómo la uso?**
```bash
git checkout 1-simple_text_to_SQL
```

Luego sigue las instrucciones del README en esa rama.

### 🔧 Rama 2: `2-mcp_text_to_SQL` (Implementación con MCP)

**¿Qué tiene?**
- Implementación con **MCP (Model Context Protocol)**
- Usa **Bedrock Converse API** directamente con `boto3`
- Arquitectura más modular y escalable
- Implementación estándar siguiendo el protocolo MCP

**¿Cómo la uso?**
```bash
git checkout 2-mcp_text_to_SQL
```

Luego sigue las instrucciones del README en esa rama.

## 📋 Comparación rápida

| Característica | Rama 1 (`1-simple_text_to_SQL`) | Rama 2 (`2-mcp_text_to_SQL`) |
|---------------|----------------------------------|------------------------------|
| **Complejidad** | Simple | Avanzada |
| **Framework** | LangChain | MCP + boto3 |
| **Arquitectura** | Directa | Modular con servidores MCP |
| **Ideal para** | Prototipos rápidos | Proyectos escalables |
| **Dependencias** | LangChain, Gradio, boto3 | mcp, boto3, Gradio |

## 🎯 ¿Cuál elegir?

- **Elige la Rama 1** si quieres algo rápido de entender y probar
- **Elige la Rama 2** si quieres una implementación más avanzada siguiendo estándares (MCP)

## 📚 Requisitos previos

Ambas ramas requieren:
- Python 3.10 o superior
- Credenciales AWS (Access Key y Secret Key)
- Acceso a modelos de Bedrock (Claude 3 Sonnet, Claude 3 Haiku, o Llama 3 70B)

## 💡 Siguiente paso

1. Clona este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd Text-to-SQL-Agent
   ```

2. Cambia a la rama que prefieras:
   ```bash
   git checkout 1-simple_text_to_SQL
   # o
   git checkout 2-mcp_text_to_SQL
   ```

3. Lee el README específico de esa rama para instrucciones detalladas de instalación y uso.
