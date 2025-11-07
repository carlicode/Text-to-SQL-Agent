import os

import gradio as gr
from src.agent import process_query_with_mcp

DEFAULT_CONTEXT = (
    "La empresa \"TechNova\" vende productos electrónicos. Tiene un promedio de 5.000 ventas mensuales en "
    "Latinoamérica. Sus categorías principales son smartphones, notebooks y accesorios."
)


def process_query(db_mode, upload_db_file, context_prompt, model_choice, question):
    """Process the query and return a response."""
    try:
        if db_mode == "Usar base de datos de prueba":
            db_path = "data/test_database.db"
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
            return gr.update(visible=True)
        return gr.update(visible=False, value=None)

    with gr.Blocks(title="Text-to-SQL Agent") as interface:
        gr.Markdown("## Text-to-SQL Agent")
        gr.Markdown(
            "Sigue tres pasos: 1) elige la fuente de datos, 2) ajusta modelo/contexto si lo necesitas, 3) formula tu pregunta."
        )

        gr.Markdown("### 1. Fuente de datos")
        with gr.Row():
            db_mode = gr.Radio(
                choices=[
                    "Usar base de datos de prueba",
                    "Cargar base de datos nueva"
                ],
                value="Usar base de datos de prueba",
                show_label=False,
                scale=2
            )
            upload_db_file = gr.File(
                label="Archivo SQLite (.db/.sqlite/.sqlite3)",
                visible=False,
                file_types=[".db", ".sqlite", ".sqlite3"],
                scale=1
            )

        db_mode.change(
            fn=on_db_mode_change,
            inputs=[db_mode],
            outputs=[upload_db_file]
        )

        gr.Markdown("### 2. Modelo y contexto")
        with gr.Row():
            model_choice = gr.Dropdown(
                choices=["Claude 3 Sonnet", "Claude 3 Haiku", "Llama 3 70B"],
                value="Claude 3 Haiku",
                label="Modelo",
                scale=1
            )
            context_prompt = gr.Textbox(
                value=DEFAULT_CONTEXT,
                lines=4,
                label="Contexto",
                scale=2
            )

        gr.Markdown("### 3. Haz tu pregunta")
        question = gr.Textbox(
            placeholder="Ejemplo: ¿Cuál es el monto pendiente de las órdenes de TechNova LATAM?",
            lines=4,
            label="Pregunta"
        )
        submit_btn = gr.Button("Enviar", variant="primary")

        gr.Markdown("### Resultados")
        with gr.Row():
            response = gr.Textbox(
                lines=8,
                interactive=False,
                label="Respuesta"
            )
            sql_query = gr.Textbox(
                lines=8,
                interactive=False,
                label="Consulta SQL generada",
                placeholder="Aquí verás la consulta SQL generada."
            )

        submit_btn.click(
            fn=process_query,
            inputs=[db_mode, upload_db_file, context_prompt, model_choice, question],
            outputs=[sql_query, response]
        )

    return interface


if __name__ == "__main__":
    ui = create_ui()
    ui.launch()
