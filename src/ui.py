import gradio as gr
from src.main import handle_query

def process_query(use_default_db, upload_db_file, context_prompt, model_choice, access_key, secret_key, question):
    """Process the query and return a response."""
    try:
        # Determina la ruta de la base de datos
        db_path = "data/demo.db" if use_default_db else upload_db_file.name if upload_db_file else "data/demo.db"
        # Procesa la query usando el agente
        result = handle_query(model_choice, db_path, context_prompt, question, access_key, secret_key)
        # Si recibimos un diccionario con sql_query y response
        if isinstance(result, dict):
            return result.get("sql_query", ""), result.get("response", "")
        else:
            return "", str(result)
    except Exception as e:
        return f"Error procesando la consulta: {str(e)}", ""

def create_ui():
    with gr.Blocks(title="Text-to-SQL Agent") as interface:
        gr.Markdown("# Text-to-SQL Agent")
        gr.Markdown("Ingresa las credenciales compartidas por correo.")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Configuración de la Base de Datos")
                use_default_db = gr.Checkbox(
                    label="Usar base de datos por defecto con la tabla 'ventas' (en /data/demo.db)",
                    value=True
                )
                upload_db_file = gr.File(
                    label="Cargar archivo SQLite (.db)",
                    file_types=[".db", ".sqlite", ".sqlite3"]
                )
                
                gr.Markdown("### Prompt de Contexto")
                context_prompt = gr.Textbox(
                    label="Contexto de la empresa por defecto. Puedes modificar este Prompts",
                    value='La empresa "TechNova" vende productos electrónicos. Tiene un promedio de 5.000 ventas mensuales en Latinoamérica. Sus categorías principales son smartphones, notebooks y accesorios.',
                    lines=3
                )
                
                gr.Markdown("### Selección de Modelo LLM")
                model_choice = gr.Dropdown(
                    label="Modelo",
                    choices=["Claude 3 Sonnet", "Claude 3 Haiku", "Llama 3 70B"],
                    value="Claude 3 Haiku"
                )
                
                gr.Markdown("### Credenciales")
                access_key = gr.Textbox(
                    label="Access Key",
                    placeholder="Ingresa la AWS Access Key"
                )
                secret_key = gr.Textbox(
                    label="Secret Access Key",
                    placeholder="Ingresa la AWS Secret Access Key",
                    type="password"
                )
                
                gr.Markdown("### Pregunta")
                question = gr.Textbox(
                    label="Haz una pregunta en lenguaje natural",
                    placeholder="Ejemplo: ¿Cuál fue el precio promedio de venta en Chile?",
                    lines=3
                )
                
                submit_btn = gr.Button("Enviar", variant="primary")
                
                gr.Markdown("### Consulta SQL Generada por el modelo:")
                sql_query = gr.Textbox(
                    label="SQL Query",
                    lines=3,
                    interactive=False
                )
                
                gr.Markdown("### Respuesta")
                response = gr.Textbox(
                    label="Resultado",
                    lines=10,
                    interactive=False
                )
        
        submit_btn.click(
            fn=process_query,
            inputs=[use_default_db, upload_db_file, context_prompt, model_choice, access_key, secret_key, question],
            outputs=[sql_query, response]
        )
    
    return interface

if __name__ == "__main__":
    interface = create_ui()
    interface.launch()
