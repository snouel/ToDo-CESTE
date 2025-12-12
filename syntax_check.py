import py_compile
import os
import sys

def check_syntax():
    """Busca y compila todos los archivos .py para verificar la sintaxis."""
    base_dir = '.'
    success = True
    
    print("--- Running Native Python Syntax Check ---")

    for root, dirs, files in os.walk(base_dir):
        # Ignorar directorios comunes que no son código fuente (como el entorno virtual)
        dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '.git']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    # Intenta compilar el archivo. Si hay un error de sintaxis, falla aquí.
                    py_compile.compile(filepath, doraise=True)
                    # print(f" {filepath}: OK")
                except py_compile.PyCompileError as e:
                    print(f"\n FATAL SYNTAX ERROR in {filepath}")
                    print(e)
                    success = False
                except Exception as e:
                    print(f" Unhandled Error in {filepath}: {e}")
                    success = False

    if not success:
        print("\n SYNTAX CHECK FAILED: One or more files have fatal syntax errors.")
        sys.exit(1)
    
    print(" All Python source files passed native syntax check.")

if __name__ == "__main__":
    check_syntax()