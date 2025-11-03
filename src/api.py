from fastapi import FastAPI
from pydantic import BaseModel
from src.main import handle_query

app = FastAPI(title="Text-to-SQL Agent API")

class QueryRequest(BaseModel):
    """Modelo de request para procesar queries """
    use_default_db: bool
    db_path: str
    context: str
    model_name: str
    question: str


@app.post("/query")
def process_query_endpoint(request: QueryRequest):
    """
    Endpoint para procesar queries del usuario.
    Returns: Respuesta del agente
    """
    db_path = "data/demo.db" if request.use_default_db else request.db_path
    response = handle_query(request.model_name, db_path, request.context, request.question)
    return {"response": response}
