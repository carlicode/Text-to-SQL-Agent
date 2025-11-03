from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate
from src.database import get_database_connection, get_database_schema, format_schema
import re

def get_llm_model(model_name: str, aws_access_key: str = None, aws_secret_key: str = None):
    """Carga e inicializa el modelo LLM a través de Bedrock."""
    bedrock_model_ids = {
        "Claude 3 Sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
        "Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "Llama 3 70B": "meta.llama3-70b-instruct-v1:0"
    }
    model_id = bedrock_model_ids.get(model_name)
    if not model_id:
        raise ValueError(f"Modelo {model_name} no soportado")
    
    # Si se proporcionan credenciales, crea un cliente Bedrock con alguno de los modelos disponibles
    if aws_access_key and aws_secret_key:
        import boto3
        
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name='us-east-1' #La región que configuré por defecto
        )
        client = session.client('bedrock-runtime')
        return ChatBedrock(model_id=model_id, client=client)
    else:
        #Perfil por defecto
        return ChatBedrock(model_id=model_id, credentials_profile_name="default")


def create_sql_chain(llm, db_schema: str):
    """Crea una chain para generar SQL desde lenguaje natural específica para SQLite."""
    prompt = PromptTemplate.from_template(
        """Eres un experto en SQL especializado en SQLite. Tu tarea es generar consultas SQL válidas basándote en preguntas en lenguaje natural.
        DIALECTO: SQLite 3
        SINTAXIS SQLite IMPORTANTE:
        - Fechas: Usa strftime('%Y-%m-%d', fecha_venta) para formatear fechas
        Ejemplo: strftime('%Y-%m', fecha) para obtener año-mes
        - Texto: Usa LIKE para búsquedas (no ILIKE), LIKE es case-insensitive si usas LOWER()
        Ejemplo: LOWER(nombre) LIKE '%texto%'
        - Funciones comunes: COUNT(), SUM(), AVG(), MAX(), MIN(), GROUP BY, HAVING
        - JOINs: INNER JOIN, LEFT JOIN, RIGHT JOIN están disponibles
        - Subconsultas: Puedes usar subconsultas en WHERE, SELECT, FROM
        - Limitar resultados: LIMIT n para limitar filas

        ESQUEMA DE LA BASE DE DATOS:
        {schema}

        INSTRUCCIONES:
        1. Analiza la pregunta del usuario y el esquema proporcionado
        2. Identifica qué tablas y columnas necesitas usar
        3. Si hay relaciones (FOREIGN KEYS), úsalas para hacer JOINs cuando sea necesario
        4. Genera SOLO la consulta SQL válida para SQLite, sin explicaciones
        5. Usa nombres de tablas y columnas exactamente como aparecen en el esquema
        6. Si la pregunta requiere múltiples tablas, usa JOINs apropiados
        7. Si la pregunta es ambigua, usa tu mejor criterio basado en el esquema

        EJEMPLOS:

        Pregunta: "¿Cuántas ventas hubo en mayo?"
        SQL: SELECT COUNT(*) FROM ventas WHERE strftime('%Y-%m', fecha_venta) = '2024-05';

        Pregunta: "¿Cuál es el precio promedio por categoría?"
        SQL: SELECT categoria, AVG(precio) as precio_promedio FROM ventas GROUP BY categoria;

        Pregunta: "Muéstrame los productos más caros vendidos en Argentina"
        SQL: SELECT producto, precio FROM ventas WHERE pais = 'Argentina' ORDER BY precio DESC LIMIT 10;

        Pregunta del usuario: {question}

        CRÍTICO: 
        - Responde ÚNICAMENTE con la consulta SQL válida
        - NO incluyas explicaciones, comentarios, ni texto adicional
        - NO escribas "No puedo...", "No hay...", o cualquier frase
        - NO uses markdown (no ```sql ```)
        - Empieza directamente con SELECT, INSERT, UPDATE o DELETE
        - Termina con punto y coma (;)

        Ejemplo de respuesta CORRECTA:
        SELECT COUNT(*) FROM usuarios WHERE nombre = 'Juan';

        Ejemplo de respuesta INCORRECTA (NO hagas esto):
        No puedo generar SQL sin más información.
        ```sql
        SELECT COUNT(*) FROM usuarios;
        ```

        Genera SOLO la consulta SQL:
        SQL:""")
    return prompt | llm

def clean_sql_response(sql_response: str) -> str:
    """Limpia la respuesta del LLM para extraer solo el SQL válido."""
    if not sql_response:
        return ""
    
    # Eliminar markdown code blocks si existen
    sql_response = re.sub(r'```sql\s*\n?', '', sql_response)
    sql_response = re.sub(r'```\s*\n?', '', sql_response)
    
    # Buscar la primera sentencia SQL (SELECT, INSERT, UPDATE, DELETE)
    sql_match = re.search(r'(SELECT|INSERT|UPDATE|DELETE|WITH)\s+.*?;', sql_response, re.IGNORECASE | re.DOTALL)
    if sql_match:
        return sql_match.group(0).strip()
    
    # Si no encuentra con punto y coma, buscar sin punto y coma
    sql_match = re.search(r'(SELECT|INSERT|UPDATE|DELETE|WITH)\s+.*', sql_response, re.IGNORECASE | re.DOTALL)
    if sql_match:
        sql = sql_match.group(0).strip()
        # Agregar punto y coma si no tiene
        if not sql.endswith(';'):
            sql += ';'
        return sql
    
    # Si no encuentra ninguna sentencia SQL, intentar usar toda la respuesta pero limpiarla
    lines = sql_response.strip().split('\n')
    # Tomar solo líneas que parecen SQL (contienen palabras clave SQL)
    sql_lines = []
    for line in lines:
        line = line.strip()
        if any(keyword in line.upper() for keyword in ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INSERT', 'UPDATE', 'DELETE', 'COUNT', 'AVG', 'SUM', 'GROUP', 'ORDER', 'HAVING']):
            sql_lines.append(line)
    
    if sql_lines:
        sql = ' '.join(sql_lines)
        if not sql.endswith(';'):
            sql += ';'
        return sql
    
    return sql_response.strip()

def create_decision_chain(llm, context_prompt: str):
    """Crea una cadena para decidir si responder desde contexto o generar SQL."""
    prompt = PromptTemplate.from_template(
        """Eres un asistente experto que decide si una pregunta puede responderse con información general (contexto) o requiere consultar datos específicos en una base de datos.
        CONTEXTO DE LA EMPRESA (información general):
        {context}

        PREGUNTA DEL USUARIO:
        {question}

        CRITERIOS PARA TU DECISIÓN:

        REGLA DE ORO: Si la pregunta solicita LISTAR, CONTAR, FILTRAR, ORDENAR o consultar datos específicos de registros individuales en la base de datos, SIEMPRE responde 'sql', incluso si el contexto tiene información relacionada.

        Responde 'contexto' ÚNICAMENTE si:
        - La pregunta es SOBRE información general de la empresa (qué tipo de productos vende, descripción del negocio)
        - La respuesta está explícitamente y completamente en el contexto
        - La pregunta NO requiere consultar registros, filtrar, contar, o listar datos específicos

        Ejemplos que usan 'contexto':
        - "¿Qué tipo de productos vende la empresa?" → Si el contexto lista los tipos completamente
        - "¿Cuál es el negocio de la empresa?" → Descripción general

        Responde 'sql' SIEMPRE si la pregunta:
        - Solicita LISTAR datos: "¿Qué países...", "¿Qué productos...", "¿En qué países...", "¿Dónde se vende...", "¿En qué país se vende..."
        - Solicita CONTAR: "¿Cuántos...", "¿Cantidad de..."
        - Solicita CALCULAR: "¿Cuál es el promedio...", "¿Suma de...", "¿Precio promedio..."
        - Solicita FILTRAR: "¿Qué productos en...", "¿Ventas de...", "¿Pedidos con..."
        - Solicita ORDENAR o comparar: "¿El más caro...", "¿Los top 3...", "¿El más vendido..."
        - Menciona países, ciudades, fechas, productos específicos, o cualquier dato que podría estar en una tabla

        Ejemplos que DEBEN usar 'sql':
        - "¿En qué país se vende?" → LISTA países, usa 'sql'
        - "¿Qué países tienen ventas?" → LISTA países, usa 'sql'
        - "¿Cuántos productos hay?" → CUENTA registros, usa 'sql'
        - "¿Cuál es el precio promedio?" → CALCULA, usa 'sql'
        - "¿Qué productos se vendieron en Argentina?" → FILTRA y LISTA, usa 'sql'
        - "¿Dónde se vende?" → LISTA ubicaciones, usa 'sql'

        IMPORTANTE: Responde ÚNICAMENTE con 'contexto' o 'sql' (en minúsculas), sin explicaciones adicionales.

        Respuesta:""")
    return prompt | llm

def process_query_logic(question: str, context: str, db_schema: str, llm, db_connection):
    """Orquestador principal que procesa la pregunta del usuario."""
    decision_chain = create_decision_chain(llm, context)
    decision_response = decision_chain.invoke({"question": question, "context": context})
    decision = decision_response.content.strip().lower()

    # Si dice 'sql' o cualquier otra cosa, usa SQL
    if decision == 'contexto' or decision.startswith('contexto'):
        prompt_template = PromptTemplate.from_template(
            """Eres un asistente experto en análisis de datos empresariales. 
            Tu tarea es responder preguntas usando únicamente la información 
            proporcionada en el contexto.
            CONTEXTO DE LA EMPRESA:
            {context}

            PREGUNTA DEL USUARIO:
            {question}

            INSTRUCCIONES:
            1. Responde la pregunta usando SOLO la información disponible en el contexto proporcionado
            2. Si la información no está en el contexto, di claramente que no tienes esa información
            3. Sé claro, conciso y profesional en tu respuesta
            4. No inventes o asumas información que no está en el contexto
            5. Si la pregunta requiere datos específicos que no están en el contexto, indica que se necesitaría consultar la base de datos

            Respuesta:""")
        context_chain = prompt_template | llm
        response = context_chain.invoke({"question": question, "context": context})
        return {"sql_query": "", "response": response.content}
    
    sql_chain = create_sql_chain(llm, db_schema)
    sql_response = sql_chain.invoke({"question": question, "schema": db_schema})
    sql_query_raw = sql_response.content
    
    # Limpiar y extraer SQL de la respuesta del LLM
    sql_query = clean_sql_response(sql_query_raw)
    
    if db_connection:
        cursor = db_connection.cursor()
        try:
            cursor.execute(sql_query)
            results = cursor.fetchall()
        except Exception as e:
            # Si hay error SQL, retornar con el SQL generado y el error para debugging
            error_msg = str(e)
            return {
                "sql_query": sql_query,
                "response": f"Error SQL: {error_msg}\n\nSQL generado: {sql_query}\n\nNota: El modelo generó SQL inválido. Por favor, verifica la consulta o intenta reformular tu pregunta."
            }
        
        # Obtener nombres de columnas para dar contexto a los resultados
        try:
            column_names = [description[0] for description in cursor.description]
            # Formatear resultados con contexto de columnas
            formatted_results = []
            for row in results:
                formatted_results.append(dict(zip(column_names, row)))
            results_str = str(formatted_results)
        except:
            results_str = str(results)
        
        interpretation_prompt = PromptTemplate.from_template(
            """Eres un analista de datos experto. Tu tarea es interpretar resultados de una consulta SQL y presentarlos en lenguaje natural de manera clara y comprensible.
            PREGUNTA ORIGINAL DEL USUARIO:
            {question}

            RESULTADOS DE LA CONSULTA SQL:
            {results}

            INSTRUCCIONES:
            1. Analiza los resultados de la consulta SQL en relación con la pregunta original
            2. Interpreta los datos y presenta una respuesta clara en lenguaje natural
            3. Si hay múltiples resultados, explica los patrones o tendencias principales
            4. Si no hay resultados, indica claramente que no se encontraron datos que coincidan con la pregunta
            5. Incluye números, valores o información específica cuando sea relevante
            6. Sé conciso pero completo en tu explicación
            7. Si los resultados son numéricos o estadísticos, contextualízalos apropiadamente

            Ejemplos de buenas respuestas:

            Pregunta: "¿Cuántas ventas hubo en mayo?"
            Resultados: [(5,)]
            Respuesta: "Hubo 5 ventas en mayo de 2024."

            Pregunta: "¿Cuál es el precio promedio por categoría?"
            Resultados: [{{'categoria': 'smartphones', 'precio_promedio': 1300.0}}, {{'categoria': 'notebooks', 'precio_promedio': 1800.0}}]
            Respuesta: "El precio promedio varía por categoría: smartphones tiene un precio promedio de 1300, mientras que notebooks tiene un precio promedio de 1800."

            Pregunta: "¿Qué países tienen ventas registradas?"
            Resultados: [('Argentina',), ('Chile',), ('Colombia',)]
            Respuesta: "Se registraron ventas en tres países: Argentina, Chile y Colombia."

            Genera una respuesta clara y natural basada en los resultados:

            Respuesta:""")
        interpret_chain = interpretation_prompt | llm
        response = interpret_chain.invoke({"question": question, "results": results_str})
        return {"sql_query": sql_query, "response": response.content}
    
    return {"sql_query": sql_query, "response": ""}


def handle_query(model_name: str, db_path: str, context: str, question: str, 
                aws_access_key: str = None, aws_secret_key: str = None):
    """Procesa la consulta del usuario."""
    llm = get_llm_model(model_name, aws_access_key, aws_secret_key)
    connection = get_database_connection(db_path)
    schema = get_database_schema(connection)
    schema_str = format_schema(schema)
    
    response = process_query_logic(question, context, schema_str, llm, connection)
    connection.close()
    
    return response

if __name__ == "__main__":
    from src.ui import create_ui
    interface = create_ui()
    interface.launch(share=False)