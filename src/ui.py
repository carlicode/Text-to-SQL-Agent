import gradio as gr
from src.agent import process_query_with_mcp

def process_query(db_mode, upload_db_file, context_prompt, model_choice, question):
    """Process the query and return a response."""
    try:
        # Determina la ruta de la base de datos según el modo seleccionado
        if db_mode == "Usar base de datos de prueba":
            db_path = "data/test_database.db"
        elif db_mode == "Cargar base de datos nueva" and upload_db_file:
            db_path = upload_db_file.name
        else:
            # Fallback a test_database si no hay archivo subido o modo no reconocido
            db_path = "data/test_database.db"

        result = process_query_with_mcp(question, model_choice, db_path, context_prompt)
        if isinstance(result, dict):
            return result.get("sql_query", ""), result.get("response", "")
        else:
            return "", str(result)
    except Exception as e:
        return f"Error procesando la consulta: {str(e)}", ""

def create_ui():
    with gr.Blocks(title="Text-to-SQL Agent") as interface:
        gr.Markdown("# Text-to-SQL Agent")
        gr.Markdown("Agente conversacional que convierte preguntas en lenguaje natural en consultas SQL usando AWS Bedrock.")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Configuración de la Base de Datos")
                db_mode = gr.Radio(
                    label="Selecciona el modo de base de datos",
                    choices=["Usar base de datos de prueba", "Cargar base de datos nueva"],
                    value="Usar base de datos de prueba",
                    info="Selecciona si quieres usar la base de datos de ejemplo o cargar tu propia base SQLite"
                )
                upload_db_file = gr.File(
                    label="Cargar archivo SQLite (.db, .sqlite, .sqlite3)",
                    file_types=[".db", ".sqlite", ".sqlite3"],
                    visible=False  
                )
                
                # Función callback: mostrar/ocultar el campo de upload según la selección
                def on_db_mode_change(mode):
                    """Muestra u oculta el campo de upload según el modo seleccionado"""
                    if mode == "Cargar base de datos nueva":
                        return gr.update(visible=True) 
                    else:
                        return gr.update(visible=False, value=None)  
                
                # Conectar el cambio de selección con la función callback
                db_mode.change(
                    fn=on_db_mode_change,
                    inputs=[db_mode],
                    outputs=[upload_db_file]
                )
                
                gr.Markdown("### Prompt de Contexto")
                context_prompt = gr.Textbox(
                    label="Contexto de la empresa por defecto. Puedes modificar este Prompts",
                    value='TechNova es una empresa que vende productos electrónicos. Tiene un promedio de 5,000 ventas mensuales en Latinoamérica. Sus tres categorías principales son: smartphones, notebooks y accesorios.',
                    lines=3
                )
                
                gr.Markdown("### Selección de Modelo LLM")
                model_choice = gr.Dropdown(
                    label="Modelo",
                    choices=["Claude 3 Sonnet", "Claude 3 Haiku", "Llama 3 70B"],
                    value="Claude 3 Haiku"
                )
                
                gr.Markdown("### Pregunta")
                question = gr.Textbox(
                    label="Haz una pregunta en lenguaje natural",
                    placeholder="Ejemplo: ¿Cuál fue el precio promedio de venta en Chile?",
                    lines=3
                )
                
                submit_btn = gr.Button("Enviar", variant="primary")
                
                gr.Markdown("### Información Técnica")
                sql_query = gr.Textbox(
                    label="Herramientas MCP utilizadas",
                    lines=3,
                    interactive=False,
                    placeholder="El agente MCP utiliza herramientas automáticamente para acceder a la base de datos..."
                )
                
                gr.Markdown("### Respuesta")
                response = gr.Textbox(
                    label="Resultado",
                    lines=10,
                    interactive=False
                )
        
        submit_btn.click(
            fn=process_query,
            inputs=[db_mode, upload_db_file, context_prompt, model_choice, question],
            outputs=[sql_query, response]
        )
    
    return interface

if __name__ == "__main__":
    interface = create_ui()
    interface.launch()
