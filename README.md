# Text-to-SQL Agent con MCP y Bedrock Converse API

¡Hola! 👋 

Esta es la solución de agente conversacional que convierte preguntas en lenguaje natural en consultas SQL. La solución usa **MCP (Model Context Protocol)** directamente con **AWS Bedrock Converse API** para que el agente decida automáticamente qué herramientas necesita para responder.

## ¿Qué hace esta solución?

Es un agente conversacional inteligente que convierte preguntas en lenguaje natural (como "¿Cuántos usuarios hay registrados?") en consultas SQL y las ejecuta. Puede responder de dos formas:

1. **Usando contexto**: Si la pregunta puede responderse con información general sobre la empresa, lo hace directamente sin consultar la base de datos.
2. **Consultando la base de datos**: Si necesita datos específicos, el agente genera automáticamente una consulta SQL, la ejecuta e interpreta los resultados para darte una respuesta en lenguaje natural.

Todo esto usando modelos LLM de AWS Bedrock a través de **Bedrock Converse API** directamente. Implementé **MCP (Model Context Protocol)** usando el paquete oficial `mcp` de Python, con un servidor MCP usando FastMCP que expone las herramientas, y un cliente MCP personalizado que se conecta al servidor y usa las herramientas con Bedrock Converse API.

## ¿Cómo funciona?

La arquitectura es simple pero potente. El LLM (en Bedrock) decide automáticamente qué herramienta usar según la pregunta:

- Si es sobre información general → usa `get_context()`
- Si necesita datos específicos → usa `get_database_schema_tool()` y luego `execute_sql()`

**Arquitectura MCP:**
- ✅ **Servidor MCP oficial**: Uso `FastMCP` de la biblioteca `mcp` (`src/mcp/server.py`) que expone las herramientas usando el protocolo MCP estándar
- ✅ **Cliente MCP personalizado**: Uso `ClientSession` y `stdio_client` del paquete `mcp` (`src/mcp/client.py`) para conectarse al servidor MCP
- ✅ **Herramientas a través de MCP**: Las herramientas se obtienen y ejecutan a través del protocolo MCP estándar usando transporte stdio
- ✅ **Bedrock Converse API**: Uso `boto3` directamente para llamar a Bedrock Converse API con las herramientas MCP
- ✅ **Ciclo conversacional**: Bedrock puede usar herramientas múltiples veces en un ciclo conversacional hasta obtener la respuesta

**¿Por qué este enfoque?**
- Más simple: sin SDKs adicionales innecesarios
- El agente decide automáticamente qué herramientas necesita
- Flexible y escalable: fácil agregar nuevas herramientas
- Separación clara de responsabilidades
- Usa bibliotecas oficiales (paquete `mcp` de Python)

## Estructura del proyecto

Aquí tienes cómo está organizado el código:

### Archivos principales:

- **`main.py`**: Punto de entrada simple que lanza la interfaz
- **`src/agent.py`**: El agente principal que orquesta todo usando MCP y Bedrock Converse API
- **`src/mcp/server.py`**: Servidor MCP usando FastMCP (biblioteca oficial `mcp`) que expone las herramientas a través del protocolo MCP estándar con transporte stdio
- **`src/mcp/client.py`**: Cliente MCP personalizado que usa `ClientSession` y `stdio_client` del paquete `mcp`
- **`src/mcp/factory.py`**: Factory para crear parámetros del servidor MCP
- **`src/database.py`**: Funciones para conectar y manejar SQLite
- **`src/ui.py`**: La interfaz web con Gradio

### Directorio `data/`

- **`test_database.db`**: Base de datos de prueba con datos de ejemplo
- **`test_database.sql`**: Script SQL para recrear la base de datos

## Configuración e instalación

### Requisitos previos

- Python 3.10 o superior
- Cuenta de AWS con acceso a Bedrock
- Credenciales AWS (Access Key y Secret Key)
- Acceso a modelos de Bedrock (Claude 3 Sonnet, Claude 3 Haiku, o Llama 3 70B)

### Instalación

1. **Clona este repositorio** (asegúrate de estar en la rama correcta):
```bash
git clone <repo-url>
cd Text-to-SQL-Agent
git checkout <rama-actual>  # Por ejemplo: git checkout 2-mcp_text_to_SQL
```

2. **Crea un entorno virtual** (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instala las dependencias**:
```bash
pip install -r requirements.txt
```

Esto instalará:
- `gradio`: Para la interfaz web
- `mcp`: Biblioteca oficial de Python para MCP (Model Context Protocol)
- `boto3`: SDK oficial de AWS para Python
- `python-dotenv`: Para variables de entorno (opcional)

4. **Prepara la base de datos de prueba** (opcional):
```bash
# Si necesitas recrear la base de datos
sqlite3 data/test_database.db < data/test_database.sql
```

### Configuración de AWS

Para facilitar la reproducción del experimento, las credenciales AWS (Access Key y Secret Key) se entregaron por correo. **⚠️ Nota importante**: Usar credenciales directamente en la interfaz no es una buena práctica de seguridad y solo se hace aquí para simplificar la reproducción del experimento. En un entorno de producción, deberías usar:

- Variables de entorno
- Roles IAM con permisos mínimos
- Secrets Manager de AWS
- Credenciales temporales con AWS STS

**Para este experimento, debes ingresar las credenciales manualmente en la interfaz de Gradio:**
- Las credenciales se ingresan directamente en los campos de la interfaz de Gradio
- **Las credenciales tienen una validez de 48 horas** desde el momento en que se entregaron
- Las credenciales no se guardan permanentemente en la aplicación (solo se usan durante la sesión)

> **💡 Por qué esta decisión**: Aunque no es la mejor práctica, ingresar credenciales en la UI permite reproducir el experimento de forma rápida sin configurar variables de entorno, lo cual es útil para demos y pruebas. Sin embargo, en producción siempre debes usar métodos más seguros.

## Uso

### Iniciar la aplicación

```bash
python main.py
```

Esto abrirá una interfaz web de Gradio en tu navegador (por defecto en `http://localhost:7860`).

### Usar la interfaz

1. **Configura la base de datos**:
   - Selecciona "Usar base de datos de prueba" para usar la base de datos de ejemplo
   - O "Cargar base de datos nueva" para usar tu propia base SQLite

2. **Configura el contexto** (opcional):
   - Modifica el prompt de contexto si quieres cambiar la información general sobre la empresa
   - Por defecto incluye información sobre la base de datos de e-commerce

3. **Selecciona el modelo**:
   - Elige entre Claude 3 Sonnet, Claude 3 Haiku, o Llama 3 70B
   - Recomendado: Claude 3 Sonnet para mejores resultados

4. **Ingresa tus credenciales AWS**:
   - Access Key y Secret Access Key (las recibiste por correo)
   - ⚠️ **Nota de seguridad**: Estas credenciales tienen una validez de 48 horas y solo se usan durante la sesión (no se guardan). En producción usarías métodos más seguros como variables de entorno o roles IAM.
   - Asegúrate de tener permisos para usar Bedrock

5. **Haz una pregunta**:
   - Escribe tu pregunta en lenguaje natural
   - El agente decidirá automáticamente si usar contexto o consultar la base de datos

### Ejemplos de preguntas

Aquí tienes algunas preguntas que puedes probar:

**Preguntas sobre información general:**
- "¿Qué tipo de empresa es esta?"
- "¿Qué hace esta empresa?"
- "¿Cuál es el negocio de esta empresa?"

**Preguntas sobre datos específicos:**
- "¿Cuántos usuarios hay registrados?"
- "¿Cuántos pedidos hay en total?"
- "¿Qué productos están en la categoría de Electrónicos?"
- "¿Cuál es el producto más caro?"
- "Muéstrame todos los pedidos completados"
- "¿Qué usuarios han hecho pedidos?"
- "¿Cuántos pedidos tiene el usuario con ID 1?"

## Detalles técnicos (si te interesa cómo funciona)

### Arquitectura: MCP con Bedrock Converse API

La solución implementa MCP usando el paquete oficial `mcp` de Python y Bedrock Converse API directamente con boto3. Aquí te explico la arquitectura completa:

**Componentes principales:**
- **Servidor MCP oficial** (`src/mcp/server.py`): Usa `FastMCP` de la biblioteca oficial `mcp` para exponer herramientas con transporte stdio
- **Cliente MCP personalizado** (`src/mcp/client.py`): Usa `ClientSession` y `stdio_client` del paquete `mcp` - se conecta al servidor MCP para obtener herramientas
- **Factory MCP** (`src/mcp/factory.py`): Crea parámetros del servidor MCP con PYTHONPATH configurado para que el subproceso pueda encontrar los módulos
- **Herramientas MCP**: Definidas con `@mcp.tool()` decorator y se obtienen a través del protocolo MCP estándar
- **Bedrock Converse API**: Llamado directamente con `boto3` - convierte herramientas MCP al formato Bedrock y maneja el ciclo conversacional
- **Conexión a Bedrock**: Directa a través de `boto3.client('bedrock-runtime')` - las herramientas pasan por MCP, y Bedrock Converse API gestiona la orquestación

**Nota**: Uso el paquete oficial `mcp` de Python. El servidor MCP usa FastMCP con transporte stdio (simple y local). El cliente usa `ClientSession` y `stdio_client` del mismo paquete. Bedrock Converse API se llama directamente con boto3 sin SDKs adicionales.

### ¿Cómo funciona internamente?

El agente funciona así:

1. **Recibe la pregunta** del usuario
2. **Servidor MCP**: Se inicia un servidor MCP usando FastMCP (biblioteca oficial `mcp`) con transporte stdio
3. **Cliente MCP**: El agente crea un `MCPClient` personalizado usando `ClientSession` y `stdio_client` del paquete `mcp`, conectado al servidor
4. **Obtiene herramientas MCP**: El cliente obtiene las herramientas del servidor a través del protocolo MCP
5. **Convierte herramientas a formato Bedrock**: Las herramientas MCP se convierten al formato que espera Bedrock Converse API
6. **Ciclo conversacional con Bedrock**: 
   - Se llama a Bedrock Converse API con la pregunta y herramientas
   - Bedrock decide qué herramienta usar
   - Si quiere usar una herramienta → se ejecuta a través del cliente MCP
   - Los resultados vuelven a Bedrock
   - Bedrock puede usar otra herramienta o dar la respuesta final
   - Este ciclo se repite hasta obtener la respuesta final
7. **Interpreta resultados** y da una respuesta en lenguaje natural

### ¿Por qué esta arquitectura?

- ✅ **Simple**: MCP básico sin SDKs adicionales innecesarios
- ✅ **Flexible**: Fácil agregar nuevas herramientas MCP
- ✅ **Estándar**: Usa bibliotecas oficiales (paquete `mcp` de Python)
- ✅ **Modular**: Servidor MCP separado, fácil de mantener
- ✅ **Escalable**: Puedes agregar múltiples servidores MCP si lo necesitas
- ✅ **Directo**: Bedrock Converse API directamente con boto3, sin capas intermedias

## Solución de problemas

### Error de credenciales AWS
- Revisa que hayas copiado bien las credenciales (a veces hay espacios extras)
- Verifica que las credenciales sigan siendo válidas
- Asegúrate de haber ingresado ambas: Access Key y Secret Key

### AccessDeniedException
- Esto significa que las credenciales no tienen permisos para usar Bedrock. Verifica los permisos en AWS.

### Base de datos no encontrada
- Verifica que el archivo `data/test_database.db` exista
- Si necesitas recrearlo: `sqlite3 data/test_database.db < data/test_database.sql`

### Error de conexión a la base de datos
- Verifica que el archivo `data/test_database.db` exista
- Si cargaste tu propia base de datos, asegúrate de que sea un archivo SQLite válido

### El agente no responde correctamente
- Verifica que las credenciales AWS estén correctas
- Prueba con diferentes modelos (a veces Claude 3 Sonnet funciona mejor que Haiku)
- Revisa los logs en la terminal para ver qué está pasando

### Error "ModuleNotFoundError: No module named 'src'"
- Este error ocurre cuando el servidor MCP se ejecuta como subproceso y no encuentra los módulos
- **Solución**: El código ya está configurado para agregar PYTHONPATH automáticamente, pero si persiste:
  - Asegúrate de ejecutar la aplicación desde el directorio raíz del proyecto
  - Verifica que el archivo `src/mcp/factory.py` esté configurando PYTHONPATH correctamente

### Error "Connection closed" o "McpError"
- Esto puede ocurrir si el servidor MCP se cierra prematuramente
- **Solución**: 
  - Asegúrate de tener todas las dependencias instaladas: `pip install -r requirements.txt`
  - Verifica que el servidor MCP pueda ejecutarse independientemente: `python src/mcp/server.py`
  - Si el error persiste, revisa los logs en la terminal para más detalles

### Error con el paquete mcp
- Asegúrate de tener instalado: `pip install mcp>=1.0.0`
- Verifica que tengas la versión correcta: `pip show mcp`
- Si hay problemas, reinstala: `pip install --upgrade mcp`

## Stack tecnológico

Para que sepas qué tecnologías elegí y por qué:

- **Python 3.10+**: Base del proyecto
- **AWS Bedrock Converse API**: API directa de AWS para conversaciones con herramientas, llamada directamente con boto3
- **AWS Bedrock**: Servicio de AWS para acceder a modelos como Claude y Llama
- **Gradio**: Para crear la interfaz web rápidamente (muy fácil de usar)
- **SQLite**: Base de datos simple y perfecta para este tipo de demos
- **boto3**: SDK oficial de AWS para Python
- **MCP (Model Context Protocol)**: Protocolo estándar para conectar herramientas a LLMs
  - **`mcp`**: Biblioteca oficial de Python para crear servidores y clientes MCP (usamos FastMCP para servidor y ClientSession/stdio_client para cliente)

## Notas sobre la solución

Esta solución implementa MCP (Model Context Protocol) directamente con Bedrock Converse API usando boto3. Las decisiones que tomé:

1. **Implementé MCP usando el paquete oficial `mcp`**: Uso `FastMCP` para el servidor y `ClientSession`/`stdio_client` para el cliente. Esto es la forma estándar y recomendada de usar MCP en Python.

2. **Arquitectura MCP oficial**: Servidor FastMCP (transporte stdio) → Cliente MCP personalizado (ClientSession) → Bedrock Converse API con herramientas MCP. Las herramientas se obtienen y ejecutan a través del protocolo MCP estándar usando las bibliotecas oficiales.

3. **Bedrock Converse API directamente**: No uso SDKs adicionales, llamo directamente a Bedrock Converse API con boto3. Esto simplifica la dependencia y da más control sobre el ciclo conversacional.

4. **Mantuve la estructura clara**: Cada archivo tiene una responsabilidad específica (agente, servidor MCP, cliente MCP, base de datos, UI).

5. **Separación MCP**: Los componentes MCP están en su propia carpeta (`src/mcp/`) para mantener el código organizado.

6. **Ciclo conversacional completo**: Implementé un ciclo donde Bedrock puede usar herramientas múltiples veces hasta obtener la respuesta final.
