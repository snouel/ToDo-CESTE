
import pytest
from business_logic import create_task, get_all_tasks, get_task, complete_task, reset_db

# Fixture de pytest para asegurar que la DB esté limpia antes de cada test
@pytest.fixture(autouse=True)
def setup_teardown():
    # Se ejecuta antes de cada test
    reset_db()
    yield

def test_create_task_success():
    """Verifica la creación exitosa de una tarea y su estado inicial."""
    task = create_task("Estudiar DevOps", "Revisar Jenkinsfile.")
    assert task is not None
    assert task["id"] == 1
    assert task["completed"] == False

def test_create_task_invalid_data():
    """Verifica que no se pueda crear una tarea con título vacío."""
    task = create_task("", "Descripción válida.")
    assert task is None
    assert len(get_all_tasks()) == 0

def test_get_all_tasks_multiple():
    """Verifica que se devuelvan todas las tareas creadas."""
    create_task("Tarea 1", "D1")
    create_task("Tarea 2", "D2")
    tasks = get_all_tasks()
    assert len(tasks) == 2

def test_complete_task_found():
    """Verifica que una tarea existente pueda ser marcada como completada."""
    created_task = create_task("Finalizar Proyecto", "Subir informe final.")
    task_id = created_task["id"]
    completed_task = complete_task(task_id)
    
    assert completed_task is not None
    assert completed_task["completed"] == True