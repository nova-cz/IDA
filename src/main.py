import argparse
import os
import time
from board_manager import Board
from ida_star import ida_star
from heuristics import combined_heuristic, get_goal_positions
from utils import read_instance, save_performance_metrics, write_solution

def solve_single_file(filepath):
    """
    Modo 1: Recibe archivo .txt y manda la solución a la consola estándar.
    """
    if not os.path.exists(filepath):
        print(f"Error: El archivo {filepath} no existe.")
        return

    n, initial_matrix, goal_matrix = read_instance(filepath)
    initial_board = Board(initial_matrix)
    goal_board = Board(goal_matrix)
    goal_pos = get_goal_positions(goal_matrix)
    
    if not initial_board.is_solvable():
        print("El tablero proporcionado no tiene solución (falla de paridad).")
        return
        
    start_time = time.perf_counter()
    moves_str, nodes, _ = ida_star(initial_board, goal_board, combined_heuristic, goal_pos)
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    if moves_str is not None:
        print(f"Solución: {moves_str}")
        print(f"Tiempo: {duration:.4f}s | Nodos Expandidos: {nodes} | Longitud: {len(moves_str.replace(',', ''))}")
    else:
        print("No se encontró solución dentro del límite iterativo.")

def run_empirical_analysis(base_instances_dir, base_results_dir):
    """
    Modo 2: Análisis empírico sobre las 1,800 instancias (3x3 a 8x8).
    Exporta CSV global para gráficas de desempeño.
    """
    print(f"Iniciando Análisis Empírico sobre {base_instances_dir}...")
    
    metrics_csv_path = os.path.join(base_results_dir, "performance_metrics.csv")
    solutions_txt_path = os.path.join(base_results_dir, "solutions.txt")
    
    sizes = range(3, 9)
    difficulties = ['faciles', 'medios', 'dificiles']
    
    total_processed = 0
    total_solved = 0
    
    for n in sizes:
        for diff in difficulties:
            folder_path = os.path.join(base_instances_dir, f"{n}x{n}", diff)
            if not os.path.isdir(folder_path):
                continue
                
            print(f"\n=> Evaluando tableros de {n}x{n} - Dificultad: {diff}")
            
            for i in range(1, 101):
                filepath = os.path.join(folder_path, f"{i}.txt")
                if not os.path.exists(filepath):
                    continue
                    
                total_processed += 1
                
                n_size, init_m, goal_m = read_instance(filepath)
                initial_board, goal_board = Board(init_m), Board(goal_m)
                goal_pos = get_goal_positions(goal_m)
                
                start_time = time.perf_counter()
                
                if not initial_board.is_solvable():
                    duration = time.perf_counter() - start_time
                    metrics = {
                        'file': f"{n}x{n}/{diff}/{i}.txt",
                        'n_size': n,
                        'difficulty': diff,
                        'solved': False,
                        'nodes_expanded': 0,
                        'time_seconds': round(duration, 4),
                        'solution_length': 0,
                        'reason': 'parity_fail'
                    }
                    save_performance_metrics(metrics_csv_path, metrics)
                    continue
                
                # Ejecutar IDA*
                moves_str, nodes, _ = ida_star(initial_board, goal_board, combined_heuristic, goal_pos)
                end_time = time.perf_counter()
                duration = end_time - start_time
                
                solved = moves_str is not None
                if solved:
                    total_solved += 1
                    sol_len = len(moves_str.split(',')) if moves_str else 0
                    write_solution(solutions_txt_path, f"{n}x{n}/{diff}/{i}.txt => [{duration:.3f}s] {moves_str}")
                else:
                    sol_len = 0
                    
                # Guardar CSV
                metrics = {
                    'file': f"{n}x{n}/{diff}/{i}.txt",
                    'n_size': n,
                    'difficulty': diff,
                    'solved': solved,
                    'nodes_expanded': nodes,
                    'time_seconds': round(duration, 4),
                    'solution_length': sol_len,
                    'reason': 'OK' if solved else 'timeout_or_limit'
                }
                save_performance_metrics(metrics_csv_path, metrics)
                
                if i % 10 == 0:
                    print(f"  Progreso {diff}: {i}/100 completados.")

    print(f"\n======== ANÁLISIS FINALIZADO ========")
    print(f"Total procesadas: {total_processed}")
    print(f"Total resueltas (éxito): {total_solved}")
    print(f"Resultados métricos guardados en: {metrics_csv_path}")

def main():
    parser = argparse.ArgumentParser(description="Solucionador del N-Puzzle mediante IDA*")
    parser.add_argument("--file", type=str, help="Ruta de un archivo .txt para resolver individualmente y mostrar solución en consola.")
    parser.add_argument("--analysis", action="store_true", help="Ejecuta el benchmark de Análisis Empírico sobre el lote de 1,800 instancias.")
    
    args = parser.parse_args()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if args.file:
        solve_single_file(args.file)
    elif args.analysis:
        instances_dir = os.path.join(base_dir, "..", "instances")
        results_dir = os.path.join(base_dir, "..", "results")
        os.makedirs(results_dir, exist_ok=True)
        run_empirical_analysis(instances_dir, results_dir)
    else:
        print("Uso incorrecto. Ejecuta con --help para ver opciones.")
        print("Ejemplo 1 (Individual): python src/main.py --file instances/3x3/faciles/1.txt")
        print("Ejemplo 2 (Masivo CSV): python src/main.py --analysis")

if __name__ == "__main__":
    main()
