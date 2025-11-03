# Text-to-SQL Agent

¡Hola! 👋 

Esta es la solución para la prueba técnica. Te voy a explicar qué hace, cómo lo construí y cómo puedes correrlo tú mismo.

## ¿Qué hace este proyecto?

Es un agente conversacional que convierte preguntas en lenguaje natural (como "¿Cuál fue el precio promedio de venta en Chile?") en consultas SQL y las ejecuta. Lo interesante es que puede responder de dos formas:

1. **Usando contexto**: Si la pregunta puede responderse con la información general que proporcionas sobre tu empresa, lo hace directamente sin tocar la base de datos.
2. **Consultando la base de datos**: Si necesita datos específicos, genera una consulta SQL automáticamente, la ejecuta e interpreta los resultados para darte una respuesta en lenguaje natural.

Todo esto usando modelos de IA de AWS Bedrock: Claude y Llama a través de LangChain.

## ¿Cómo lo hice? (Arquitectura)

Decidí usar un **modelo directo y simplificado**. La razón es que quería algo que funcionara rápido sin complicaciones, simplemente LangChain conectándose directamente a AWS Bedrock y mostrando el resultado en gradio.

**¿Por qué esta arquitectura?**
- Es más simple de entender y mantener
- Menos latencia (comunicación directa con Bedrock)
- Configuración rápida sin necesidad de servidores adicionales
- Perfecta para prototipos y pruebas

Si quieres más detalles técnicos, los dejo más abajo en la sección de Arquitectura.

## Estructura del proyecto
Si quieres entender cómo está organizado el código, aquí te explico:

### Archivos:

- **`src/main.py`**: El cerebro del agente. Aquí está:
  - La carga de los modelos LLM desde Bedrock
  - La lógica que decide si usar contexto o SQL
  - La generación de SQL desde lenguaje natural
  - La interpretación de resultados
  - El orquestador que coordina todo el flujo

- **`src/database.py`**: Todo lo relacionado con bases de datos:
  - Conectarse a SQLite
  - Extraer el esquema de las tablas
  - Formatear el esquema para los prompts
  - Ejecutar queries

- **`src/api.py`**: La API REST con FastAPI. Incluye endpoints para hacer queries.

- **`src/ui.py`**: La interfaz web de Gradio. Aquí está toda la UI de la aplicación.

### Directorio `data/`

- **`seed_data.sql`**: El script SQL con el esquema y datos de ejemplo
- **`demo.db`**: La base de datos que se creada.

## Lo que necesitas antes de empezar

- Python 3.10 o superior (puedes verificar tu versión con `python --version`)
- Las credenciales de AWS que te envié por correo (Access Key y Secret Access Key)

> **Nota rápida sobre las credenciales**: Sé que pasar credenciales por correo no es la práctica más segura del mundo, pero para esta prueba lo hice así para que puedas empezar a probar inmediatamente sin tener que configurar IAM roles o perfiles de AWS. En producción usaría variables de entorno o IAM roles. ¡Pero para probar esto funciona perfecto :D !

## Cómo correr el proyecto

Te explico cómo lo pongo en marcha. Es bastante simple:

### 1. Navega a la carpeta del proyecto  luego de clonar el repositorio

```bash
cd Text-to-SQL-Agent
```

### 2. Crea un entorno virtual

```bash
# En macOS/Linux
python3 -m venv venv

# En Windows
python -m venv venv
```

### 3. Activa el entorno virtual

```bash
# En macOS/Linux
source venv/bin/activate

# En Windows
venv\Scripts\activate
```

Verás `(venv)` aparecer en tu terminal - eso significa que está activo ✅

### 4. Instala las dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Esto instalará todas las librerías que necesita el proyecto (LangChain, Gradio, FastAPI, boto3, etc.)

### 5. ¡Ejecuta la aplicación!

```bash
python main.py
```

Se abrirá automáticamente en tu navegador en `http://localhost:7860`. Si no se abre solo, copia esa URL y pégalo en tu navegador.

### 7. Ingresa las credenciales AWS

Cuando la aplicación esté corriendo, verás campos para ingresar las credenciales que te envié por correo. Simplemente cópialas y pégalas ahí.

> 💡 **Tip**: Las credenciales solo se usan durante la sesión y no se guardan permanentemente. Si cierras la aplicación, tendrás que ingresarlas de nuevo y solo tienen una duración de 48 horas.

---

**Cuando termines de probar:**

Para desactivar el entorno virtual simplemente escribe:

```bash
deactivate
```

## Cómo usar la interfaz

Una vez que la aplicación esté corriendo, la interfaz es súper intuitiva. Te explico qué hace cada cosa:

1. **Base de datos**: Por defecto usa la demo que creamos (`data/demo.db`), pero puedes cargar tu propia base SQLite si quieres.

2. **Contexto de la empresa**: Este es el "conocimiento general" que le das al agente. Por ejemplo, si escribes "Mi empresa vende productos electrónicos y tiene 5000 ventas mensuales", el agente puede responder preguntas sobre esto sin tocar la base de datos.

3. **Modelo LLM**: Puedes elegir entre Claude 3 Sonnet, Claude 3 Haiku o Llama 3 70B. Recomiendo empezar con "Claude 3 Haiku" porque es rápido y eficiente.

4. **Credenciales AWS**: Aquí pegas las credenciales que te envié por correo.

5. **Haz tu pregunta**: Escribe lo que quieras saber en lenguaje natural, como si le hablaras a un compañero.

6. **Click en "Enviar"** y espera la magia ✨

### Ejemplos de preguntas que puedes hacer

**Pregunta que usa contexto:**
- Tú: "¿Cuántos productos principales vende TechNova?"
- El agente: Detecta que puede responder con el contexto y te dice directamente: "TechNova se enfoca en tres categorías principales: smartphones, notebooks y accesorios."

**Pregunta que consulta la base de datos:**
- Tú: "¿Cuál fue el precio promedio de venta en Chile?"
- El agente: 
  - Genera este SQL: `SELECT AVG(precio) FROM ventas WHERE pais = 'Chile';`
  - Lo ejecuta en la base de datos
  - Te responde: "El precio promedio de venta en Chile fue de 1800 USD."

**Más ideas para probar:**
- "¿Cuántas ventas de smartphones hubo en mayo?"
- "¿Qué países tienen ventas registradas?"
- "¿Cuál es el producto más caro vendido?"
- "Muéstrame las ventas de notebooks en Argentina"

### También hay una API REST (opcional)

Si prefieres consumir el agente como API en lugar de usar la interfaz web, también incluí una API REST con FastAPI. Para correrla:

```bash
uvicorn src.api:app --reload --port 8000
```

Estará disponible en `http://localhost:8000`.

**Endpoints que puedes usar:**

- `POST /query`: Para hacer preguntas
  ```json
  {
    "use_default_db": true,
    "db_path": "data/demo.db",
    "context": "La empresa TechNova vende productos electrónicos...",
    "model_name": "Claude 3 Haiku",
    "question": "¿Cuál es el promedio de ventas?"
  }
  ```

- `GET /health`: Para verificar que el servicio esté funcionando

## Modelos Disponibles

- **Claude 3 Sonnet**: Modelo balanceado de Anthropic
- **Claude 3 Haiku**: Modelo rápido y eficiente de Anthropic
- **Llama 3 70B**: Modelo de Meta, optimizado para instrucciones

## Detalles técnicos (si te interesa cómo lo construí)

### Arquitectura: Modelo Directo y Simplificado

Como te comenté arriba, elegí una arquitectura directa sin complicaciones. Aquí te explico los detalles:

**Componentes principales:**
- **Conexión directa**: LangChain habla directamente con AWS Bedrock, sin servidores intermedios ni MCP
- **Chain Pattern**: Uso las "cadenas" de LangChain para orquestar el flujo
- **Separación de responsabilidades**: Cada módulo hace una cosa bien (UI, API, lógica, base de datos)

### ¿Cómo funciona internamente?

El agente toma decisiones en dos pasos:

**Paso 1: ¿Puedo responder con contexto?**
- Analiza tu pregunta y el contexto que proporcionaste
- Si encuentra la respuesta ahí, te responde directamente (rápido y eficiente)

**Paso 2: Necesito consultar la base de datos**
Si no puede responder con contexto:
1. Extrae el esquema de tu base de datos
2. Le pide al LLM que genere una consulta SQL válida basándose en tu pregunta
3. Ejecuta esa consulta en la base de datos
4. Interpreta los resultados y te da una respuesta en lenguaje natural

### ¿Por qué esta arquitectura?

- ✅ **Simple**: No necesitas entender MCP ni configurar servidores extra
- ✅ **Rápida**: Menos latencia = respuestas más inmediatas
- ✅ **Fácil de mantener**: El código es claro y directo
- ✅ **Perfecta para prototipos**: Funciona rápido sin mucha configuración

## Base de Datos

La base de datos demo incluye una tabla `ventas` con los siguientes campos:
- `id`: Identificador único
- `producto`: Nombre del producto
- `categoria`: Categoría del producto (smartphones, notebooks, accesorios)
- `precio`: Precio de venta
- `pais`: País donde se realizó la venta
- `fecha_venta`: Fecha de la venta

Puedes extender o modificar `data/seed_data.sql` para agregar más datos de prueba.

## Si algo sale mal (troubleshooting)

**"Modelo no soportado"**
- Asegúrate de que el nombre del modelo coincida exactamente con las opciones del dropdown (Claude 3 Sonnet, Claude 3 Haiku, etc.)

**Error de credenciales AWS**
- Revisa que hayas copiado bien las credenciales (a veces hay espacios extras)
- Verifica que las credenciales que te envié sigan siendo válidas

**AccessDeniedException**
- Esto significa que las credenciales no tienen permisos para usar Bedrock. Si pasa esto, avísame y reviso los permisos en AWS.

**Base de datos no encontrada**
- Ejecuta de nuevo: `python create_demo_db.py`

**Error de conexión a la base de datos**
- Verifica que el archivo `data/demo.db` exista
- Si cargaste tu propia base de datos, asegúrate de que sea un archivo SQLite válido

## Stack tecnológico que usé

Para que sepas qué tecnologías elegí y por qué:

- **Python 3.10+**: Base del proyecto
- **LangChain**: Framework que hace súper fácil trabajar con LLMs y crear cadenas de procesamiento
- **AWS Bedrock**: Servicio de AWS para acceder a modelos como Claude y Llama
- **Gradio**: Para crear la interfaz web rápidamente (muy fácil de usar)
- **FastAPI**: Para la API REST (rápida y moderna)
- **SQLite**: Base de datos simple y perfecta para este tipo de demos
- **boto3**: SDK oficial de AWS para Python

---

## Últimas palabras

Este proyecto lo hice con mucho cariño para demostrar cómo puedo trabajar con LLMs, AWS y crear herramientas útiles. Si tienes preguntas o quieres que explique algo más a fondo, ¡no dudes en preguntar! 

¡Espero que te sea útil y puedas probarlo sin problemas! 🚀

