from src.ui import create_ui
import os

if __name__ == "__main__":
    interface = create_ui()
    # Obtener host y puerto de variables de entorno (para Docker)
    host = os.getenv("GRADIO_HOST", "0.0.0.0")
    port = int(os.getenv("GRADIO_PORT", "7860"))
    interface.launch(server_name=host, server_port=port, share=False)

