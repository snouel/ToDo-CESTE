# Simulación de una base de datos en memoria para las tareas
tasks_db = {}
next_id = 1

def create_task(title: str, description: str):
    """Crea una nueva tarea y la añade a la base de datos."""
    global next_id
    
    # Validación simple de datos
    if not title or not description:
        return None

    new_task = {
        "id": next_id,
        "title": title,
        "description": description,
        "completed": False
    }
    tasks_db[next_id] = new_task
    next_id += 1
    return new_task

def get_all_tasks():
    """Devuelve todas las tareas."""
    return list(tasks_db.values())

def get_task(task_id: int):
    """Devuelve una tarea por su ID."""
    return tasks_db.get(task_id)

def complete_task(task_id: int):
    """Marca una tarea como completada."""
    task = tasks_db.get(task_id)
    if task:
        task["completed"] = True
        return task
    return None

def reset_db():
    """Función de utilidad para tests: reinicia la base de datos."""
    global tasks_db, next_id
    tasks_db = {}
    next_id = 1