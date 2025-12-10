from fastapi import FastAPI, HTTPException
from business_logic import create_task, get_all_tasks, get_task, complete_task, reset_db

# Inicialización de la API
app = FastAPI()

# 1. Endpoint para crear una tarea (POST)
@app.post("/tasks/")
def add_task(title: str, description: str):
    """Crea una nueva tarea."""
    task = create_task(title, description)
    if task is None:
        raise HTTPException(status_code=400, detail="El título y la descripción no pueden estar vacíos.")
    return task

# 2. Endpoint para obtener todas las tareas (GET)
@app.get("/tasks/")
def list_tasks():
    """Lista todas las tareas."""
    return get_all_tasks()

# 3. Endpoint para obtener una tarea específica (GET)
@app.get("/tasks/{task_id}")
def retrieve_task(task_id: int):
    """Obtiene una tarea por su ID."""
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

# 4. Endpoint para marcar como completada (PUT/PATCH)
@app.put("/tasks/{task_id}/complete")
def update_task_complete(task_id: int):
    """Marca una tarea como completada."""
    task = complete_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada para completar")
    return task

# Endpoint de utilidad para verificar que la app está viva (Health Check)
@app.get("/health")
def health_check():
    """Verificación de estado del servicio."""
    return {"status": "ok"}

# Nota: No incluimos el uvicorn.run(...) aquí, ya que será ejecutado por el CMD del Dockerfile