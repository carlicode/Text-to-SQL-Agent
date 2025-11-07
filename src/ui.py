import os

import gradio as gr
from src.agent import process_query_with_mcp

DEFAULT_CONTEXT = (
    "TechNova LATAM es una empresa B2B con sede en Latinoamérica que vende hardware (notebooks, monitores, "
    "periféricos) y licencias SaaS. Opera también la compañía hermana NextGen Retail (SMB en Norteamérica). "
    "Departamentos clave: Ventas Enterprise (Laura Méndez), Operaciones (Camila Rojas), Ventas SMB (Emily Johnson) "
    "y Logística (Daniel Smith). Almacenes principales: Centro Distribución Santiago (Chile) y Hub Monterrey (México). "
    "Órdenes tienen estados Closed Won, Negotiation y Closed Lost; pagos pueden ser parciales. Inventario registra stock "
    "y safety stock. Tickets de soporte manejan severidad (low/medium/high/urgent) y estado. Responde en español con enfoque "
    "ejecutivo, explicando primero conclusiones y luego detalles."
)


def process_query(db_mode, upload_db_file, context_prompt, model_choice, question, selected_db_path):
    """Process the query and return a response."""
    try:
        if db_mode == "Usar base de datos de prueba":
            db_path = "data/test_database.db"
        elif db_mode == "Usar base enterprise (demo avanzada)":
            if selected_db_path and os.path.exists(selected_db_path):
                db_path = selected_db_path
            else:
                return "", "Por favor haz clic en 'Cargar base enterprise' antes de enviar la pregunta."
        elif db_mode == "Cargar base de datos nueva" and upload_db_file:
            db_path = upload_db_file.name
        else:
            db_path = "data/test_database.db"

        result = process_query_with_mcp(question, model_choice, db_path, context_prompt)
        if isinstance(result, dict):
            return result.get("sql_query", ""), result.get("response", "")
        return "", str(result)
    except Exception as e:
        return f"Error procesando la consulta: {str(e)}", ""


def create_ui():
    def on_db_mode_change(mode: str):
        if mode == "Cargar base de datos nueva":
            return (
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(value="", visible=False)
            )
        if mode == "Usar base enterprise (demo avanzada)":
            return (
                gr.update(visible=False, value=None),
                gr.update(visible=True),
                gr.update(value="Haz clic en el botón para cargar la base enterprise_demo.", visible=True)
            )
        return (
            gr.update(visible=False, value=None),
            gr.update(visible=False),
            gr.update(value="", visible=False)
        )

    def load_enterprise_database():
        db_path = "data/enterprise_demo.db"
        if not os.path.exists(db_path):
            return "", gr.update(value="La base enterprise_demo.db no existe en este servidor.", visible=True)
        return db_path, gr.update(value="Base enterprise_demo cargada ✅", visible=True)

    with gr.Blocks(title="Text-to-SQL Agent") as interface:
        gr.Markdown("## Text-to-SQL Agent")
        gr.Markdown(
            "1. Selecciona la fuente de datos. 2. Ajusta (opcional) el contexto. 3. Haz tu pregunta." \
            " Recibirás el resultado y la consulta SQL generada."
        )

        selected_db_path = gr.State("data/test_database.db")

        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                gr.Markdown("#### Fuente de datos")
                db_mode = gr.Radio(
                    choices=[
                        "Usar base de datos de prueba",
                        "Usar base enterprise (demo avanzada)",
                        "Cargar base de datos nueva"
                    ],
                    value="Usar base de datos de prueba",
                    show_label=False
                )
                upload_db_file = gr.File(
                    label="Archivo SQLite (.db/.sqlite/.sqlite3)",
                    visible=False,
                    file_types=[".db", ".sqlite", ".sqlite3"]
                )
                load_demo_btn = gr.Button("Cargar base enterprise", visible=False)
                load_status = gr.Markdown("", visible=False)

                db_mode.change(
                    fn=on_db_mode_change,
                    inputs=[db_mode],
                    outputs=[upload_db_file, load_demo_btn, load_status]
                )

                load_demo_btn.click(
                    fn=load_enterprise_database,
                    inputs=None,
                    outputs=[selected_db_path, load_status]
                )

                gr.Markdown("#### Modelo")
                model_choice = gr.Dropdown(
                    choices=["Claude 3 Sonnet", "Claude 3 Haiku", "Llama 3 70B"],
                    value="Claude 3 Haiku",
                    show_label=False
                )

                with gr.Accordion("Contexto (opcional)", open=False):
                    context_prompt = gr.Textbox(value=DEFAULT_CONTEXT, lines=8, label="")

            with gr.Column(scale=2):
                gr.Markdown("#### Pregunta")
                question = gr.Textbox(
                    placeholder="Ejemplo: ¿Cuál es el monto pendiente de las órdenes de TechNova LATAM?",
                    lines=4,
                    label=""
                )
                submit_btn = gr.Button("Enviar", variant="primary")

                gr.Markdown("#### Respuesta")
                response = gr.Textbox(lines=8, interactive=False, label="")

                gr.Markdown("#### Información Técnica")
                sql_query = gr.Textbox(
                    lines=5,
                    interactive=False,
                    label="",
                    placeholder="Aquí verás la consulta SQL generada."
                )

        submit_btn.click(
            fn=process_query,
            inputs=[db_mode, upload_db_file, context_prompt, model_choice, question, selected_db_path],
            outputs=[sql_query, response]
        )

    return interface


if __name__ == "__main__":
    ui = create_ui()
    ui.launch()
