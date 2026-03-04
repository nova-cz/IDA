import os
import csv

def read_instance(filepath):
    """
    Funciones de lectura de archivos siguiendo el formato de examen.
    [Línea 1] Dimensión n
    [Líneas siguientes] Matriz del tablero inicial
    [Líneas siguientes] Matriz del tablero meta
    
    Retorna: (n, initial_board_matrix, goal_board_matrix)
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    n = int(lines[0].strip())
    
    initial_matrix = []
    for i in range(1, n + 1):
        row = list(map(int, lines[i].strip().split(',')))
        initial_matrix.append(row)
        
    goal_matrix = []
    for i in range(n + 1, 2 * n + 1):
        row = list(map(int, lines[i].strip().split(',')))
        goal_matrix.append(row)
        
    return n, initial_matrix, goal_matrix

def write_instance(filepath, n, initial_matrix, goal_matrix):
    """Guarda un caso generado en el formato especificado."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(f"{n}\n")
        
        for row in initial_matrix:
            f.write(",".join(map(str, row)) + "\n")
            
        for row in goal_matrix:
            f.write(",".join(map(str, row)) + "\n")

def save_performance_metrics(filepath, metrics_dict):
    """
    Anexa a un CSV metrics_dict con estadísticas del IDA*
    como nudos expandidos, tiempo de ejecución, longitud de la solución.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file_exists = os.path.isfile(filepath)
    
    with open(filepath, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics_dict.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(metrics_dict)

def write_solution(filepath, solution_path_str):
    """
    Guarda la ruta de las fichas en solutions.txt
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'a') as f:
        f.write(solution_path_str + "\n")
