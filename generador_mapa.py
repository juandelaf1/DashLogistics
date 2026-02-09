import os

root_dir = '.'  # raíz del proyecto
summary_file = 'project_summary.txt'

with open(summary_file, 'w', encoding='utf-8') as f:
    for dirpath, dirnames, filenames in os.walk(root_dir):
        f.write(f"\nCARPETA: {dirpath}\n")
        for file in filenames:
            if file.endswith('.py'):
                filepath = os.path.join(dirpath, file)
                f.write(f"  - {file}\n")
                try:
                    with open(filepath, 'r', encoding='utf-8') as code:
                        # escribimos las primeras 5 líneas del script para dar contexto
                        for i in range(5):
                            line = code.readline().strip()
                            if line:
                                f.write(f"      {line}\n")
                except Exception as e:
                    f.write(f"      ERROR leyendo archivo: {e}\n")

print(f"Resumen generado en {summary_file}")
