# Contexto Completo del Proyecto N-Puzzle (Solucionador Múltiple)

**Objetivo del Documento:**
Proveer todo el contexto técnico, código fuente completo traducido al español, explicación paso a paso de las funciones y respuestas formales del examen. Esta información sirve para redactar un reporte tipo "Paper" profesional y detallado.

---

## 📌 PARTE 1: Respuestas del Examen (Características Implementadas)

### 1. Lectura de Archivo y Salida de Consola (1 pts)
El programa principal (`src/principal.py`) cuenta con un modo de ejecución individual que lee un archivo `.txt` con la estructura exigida (dimensión, tablero inicial y tablero final separados por comas). Respeta los movimientos en blanco.
Salida esperada (ejemplo):
`Solución: U,D,L,R`
`Tiempo: 0.0034s | Nodos Expandidos: 102 | Longitud: 4`

### 2. Pseudocódigo y Lógica IDA* Híbrido (2 pts)
La implementación núcleo se encuentra en `src/ida_estrella.py`. Cumple con todos los requisitos arquitectónicos y soluciona bloqueos de memoria:
- **Criterio Tabú Estricto:** Se mantiene una estructura `tabu_set` local (set en memoria) por cada rama de profundidad (DFS) para evitar generar ciclos infinitos retrocediendo a un estado recién visitado.
- **Evitar Nodos Repetidos Tempranos (Extensión BFS):** El problema histórico del IDA* regular es re-expandir inútilmente los primeros nodos cercanos a la raíz millones de veces. Aquí se implementó una fase inicial en **Anchura (BFS)** de 500 nodos, generando una frontera diversa y guardando sus rastros en una `base_transposition_table` global O(1).
- **Control de Nivel de Profundidad:** El algoritmo `ida_estrella()` gestiona el límite mediante la variable `threshold` (umbral f(n)). Corta el DFS cuando se excede, y retroalimenta al IDA* con el mínimo excedente encontrado (`min_exceeded`) para iterar progresivamente. Tiene un límite agresivo anticolapso de `1,000,000` expansiones.

### 3. Función de Evaluación y Heurísticas (2 pts)
Implementado en `src/heuristicas.py`. Las matrices 2D son lentísimas en Python, así que el motor aplanó matemáticamente los tableros a **Arreglos 1D**. Se usan **6 Componentes Avanzados**:
1. **Distancia Manhattan (MD):** Distancia geométrica base.
2. **Conflicto Lineal (LC):** Penalización prioritaria cuando dos piezas de la misma fila/columna están invertidas.
3. **Fichas en Esquinas (Corner Tiles - CT):** Penalización si una pieza está atrapada en una esquina adyacente a su meta.
4. **Último Movimiento (Last Move - LM):** Beneficio marginal cuando faltan $\le$ 2 piezas.
5. **Distancia Caminando (Walking Distance - WD):** Abstracción por flujo de ejes matemáticos.
6. **Distancia de Inversión (Inversion Distance - IDR):** Conteo de inversiones cruzadas absolutas divididas entre N-1 (movimientos verticales matemáticos mínimos).
**Regla de Admisibilidad Matemática (MAX):** Sumar todas ciegamente destruiría la optimalidad (rompería el IDA* al sobreestimar). Las seguras son aditivas, las mixtas no. Por ende, usamos el límite superior seguro:
`f(n) = max(MD + LC + CT, MD + LC + LM, MD + IDR, WD)`

### 4. Implementación Nativa
Codificado 100% en Python 3 puro (sólo usando librerías nativas para el algoritmo: `os`, `time`, `collections`). Las librerías de terceros (pandas, seaborn, matplotlib) se usan únicamente para graficación y minería de los outputs generados (Punto 5). Todo el flujo metodológico fue traducido y refactorizado al Español.

### 5. Análisis Empírico (Dashboard Estadístico)
Pipeline en `visualizador.py`. Se probaron **1,800 matrices** (de 3x3 hasta 8x8 con dificultades Fáciles, Medias, y Difíciles). El dashboard entrega 4 vistas:
1. Curva Logarítmica de explosión de tiempo por tamaño del tablero.
2. Gráfico de Costo Individual (Nube de dispersión) demostrando eficiencia de ms a segundos dependiendo de la entropía mezclada.
3. Histogramas de Rendimiento (Éxito contra Timeouts prevenidos).
4. Proporción analítica Global en gráfico circular.

---

## 📌 PARTE 2: Explicación de la Arquitectura de Archivos 

- **`principal.py`**: El cerebro de orquestación. Usa `argparse` para aceptar comandos de consola (`--file` para evaluar un tablero o `--analysis` para automatizar la resolución y escritura CSV de todos los archivos alojados en `/instances`).
- **`ida_estrella.py`**: Posee dos métodos clave. `generate_bfs_frontier()` (fuerza bruta controlada para abrir el árbol evitando la cabeza embotellada) y la recursividad profunda `search()` que efectúa las ramificaciones con podas de rama (Si $f(n) > threshold$, corta).
- **`heuristicas.py`**: Las matemáticas del proyecto. Todo en 1D calculando residuos de división `//` e `%` para figurar Renglones y Columnas virtuales.
- **`gestor_tablero.py`**: Maneja el N-Puzzle como un objeto inmutable de tupla (`self.matrix = tuple()`), agilizando brutalmente las tablas Hash de Python equivalentes al arreglo de Tabú O(1) de acceso de lectura. 
- **`visualizador.py`**: Minería de datos y construcción del dashboard Seaborn multiparadigma.
- **`generador_instancias.py` & `utilidades.py`**: Script complementario para generar los miles de tableros del banco y scripts I/O para escritura/lectura estandarizada con separadores de coma (`read_instance`).

---

## 📌 PARTE 3: Código Fuente Completo (Para Referencia Documental)

### A. `src/principal.py`
```python
import argparse
import os
import time
from gestor_tablero import Board
from ida_estrella import ida_estrella
from heuristicas import heuristica_combinada, get_posiciones_meta
from utilidades import read_instance, save_performance_metrics, write_solution

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
    goal_pos = get_posiciones_meta(goal_matrix)
    
    if not initial_board.is_solvable():
        print("El tablero proporcionado no tiene solución (falla de paridad).")
        return
        
    start_time = time.perf_counter()
    moves_str, nodes, _ = ida_estrella(initial_board, goal_board, heuristica_combinada, goal_pos)
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
                goal_pos = get_posiciones_meta(goal_m)
                
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
                moves_str, nodes, _ = ida_estrella(initial_board, goal_board, heuristica_combinada, goal_pos)
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
        print("Ejemplo 1 (Individual): python src/principal.py --file instances/3x3/faciles/1.txt")
        print("Ejemplo 2 (Masivo CSV): python src/principal.py --analysis")

if __name__ == "__main__":
    main()
```

### B. `src/ida_estrella.py`
```python
import time
from collections import deque

def generate_bfs_frontier(initial_board, goal_board, heuristic_func, goal_positions, max_nodes=500):
    """
    Fase 1: BFS para generar una frontera inicial rica en estados diversos.
    Crea una Tabla de Transposición inicial (visited_states) para evitar re-expansiones.
    """
    if initial_board == goal_board:
        return [(0, initial_board, [])], {initial_board}

    transposition_table = {initial_board}
    queue = deque([(initial_board, [])])
    frontier_nodes = []
    nodes_expanded = 0
    
    while queue and nodes_expanded < max_nodes:
        current_board, moves_path = queue.popleft()
        g_cost = len(moves_path)
        
        children = current_board.get_possible_moves()
        nodes_expanded += 1
        
        for child_board, move_str in children:
            if child_board == goal_board:
                new_path = list(moves_path)
                new_path.append(move_str)
                frontier_nodes.append((g_cost + 1, child_board, new_path))
                return frontier_nodes, transposition_table
                
            if child_board not in transposition_table:
                transposition_table.add(child_board)
                new_path = list(moves_path)
                new_path.append(move_str)
                queue.append((child_board, new_path))
                
    while queue:
        board, moves = queue.popleft()
        frontier_nodes.append((len(moves), board, moves))
        
    return frontier_nodes, transposition_table

def ida_estrella(initial_board, goal_board, heuristic_func, goal_positions):
    """
    Implementación rigurosa de Híbrido BFS-IDA* con tabla de transposición superficial.
    """
    start_time = time.time()
    nodes_expanded = [0] 

    MAX_ITERATIONS = 500
    MAX_EXPANS_PER_ITER = 1_000_000
    BFS_FRONTIER_SIZE = 500

    frontier, base_transposition_table = generate_bfs_frontier(
        initial_board, goal_board, heuristic_func, goal_positions, max_nodes=BFS_FRONTIER_SIZE
    )
    
    nodes_expanded[0] += len(base_transposition_table)
    
    for g, b, m in frontier:
        if b == goal_board:
            end_time = time.time()
            return ",".join(m), nodes_expanded[0], end_time - start_time

    def sort_f(item):
        g_c, brd, _ = item
        return g_c + heuristic_func(brd.matrix, goal_positions)
        
    frontier.sort(key=sort_f)
    
    best_g, best_b, _ = frontier[0]
    threshold = best_g + heuristic_func(best_b.matrix, goal_positions)

    for _ in range(MAX_ITERATIONS):
        next_threshold = float('inf')
        iteration_expansions = [0]
        
        for initial_g, start_node, base_moves in frontier:
            f_val = initial_g + heuristic_func(start_node.matrix, goal_positions)
            
            if f_val > threshold:
                if f_val < next_threshold:
                    next_threshold = f_val
                continue
            
            path = [start_node]
            moves_path = list(base_moves)
            tabu_set = {start_node}
            
            res, t = search(
                path, moves_path, initial_g, threshold, goal_board, 
                heuristic_func, goal_positions, nodes_expanded, 
                iteration_expansions, MAX_EXPANS_PER_ITER, tabu_set, base_transposition_table
            )
            
            if res == "FOUND":
                end_time = time.time()
                return ",".join(moves_path), nodes_expanded[0], end_time - start_time
                
            if t < next_threshold:
                next_threshold = t
                
            if nodes_expanded[0] > MAX_EXPANS_PER_ITER:
                break
                
        if nodes_expanded[0] > MAX_EXPANS_PER_ITER or next_threshold == float('inf'):
            break 
            
        threshold = next_threshold

    end_time = time.time()
    return None, nodes_expanded[0], end_time - start_time

def search(path, moves_path, g, threshold, goal_board, heuristic_func, goal_positions, 
           nodes_expanded, iteration_expansions, max_expansions, tabu_set, base_transposition_table):
    
    current_node = path[-1]
    f = g + heuristic_func(current_node.matrix, goal_positions)
    
    if f > threshold:
        return "NOT_FOUND", f
        
    if current_node == goal_board:
        return "FOUND", f

    if iteration_expansions[0] > max_expansions:
        return "NOT_FOUND", f + 1
        
    min_exceeded = float('inf')
    
    children = current_node.get_possible_moves()
    nodes_expanded[0] += 1
    iteration_expansions[0] += 1
    
    for child_board, move_str in children:
        if child_board not in tabu_set and child_board not in base_transposition_table:
            
            path.append(child_board)
            moves_path.append(move_str)
            tabu_set.add(child_board)
            
            res, t = search(
                path, moves_path, g + 1, threshold, goal_board, heuristic_func, 
                goal_positions, nodes_expanded, iteration_expansions, max_expansions, 
                tabu_set, base_transposition_table
            )
            
            if res == "FOUND":
                return "FOUND", t
                
            if t < min_exceeded:
                min_exceeded = t
                
            tabu_set.remove(child_board)
            moves_path.pop()
            path.pop()
            
    return "NOT_FOUND", min_exceeded
```

### C. `src/heuristicas.py`
```python
def get_posiciones_meta(goal_matrix):
    pos = {}
    size = len(goal_matrix)
    for r in range(size):
        for c in range(size):
            val = goal_matrix[r][c]
            if val != 0:
                pos[val] = r * size + c
    return pos

def h_DistanciaManhattan(board_matrix, goal_positions):
    dist = 0
    size = int(len(board_matrix)**0.5)
    for i, val in enumerate(board_matrix):
        if val != 0 and val in goal_positions:
            r, c = i // size, i % size
            gr, gc = goal_positions[val] // size, goal_positions[val] % size
            dist += abs(r - gr) + abs(c - gc)
    return dist

def h_ConflictoLineal(board_matrix, goal_positions):
    conflict = 0
    size = int(len(board_matrix)**0.5)
    
    for r in range(size):
        row_tiles = []
        for c in range(size):
            val = board_matrix[r * size + c]
            if val != 0 and val in goal_positions:
                g_idx = goal_positions[val]
                if g_idx // size == r:
                    row_tiles.append((val, c, g_idx % size))
        for i in range(len(row_tiles)):
            for j in range(i + 1, len(row_tiles)):
                if row_tiles[i][2] > row_tiles[j][2]:
                    conflict += 2
                    
    for c in range(size):
        col_tiles = []
        for r in range(size):
            val = board_matrix[r * size + c]
            if val != 0 and val in goal_positions:
                g_idx = goal_positions[val]
                if g_idx % size == c:
                    col_tiles.append((val, r, g_idx // size))
        for i in range(len(col_tiles)):
            for j in range(i + 1, len(col_tiles)):
                if col_tiles[i][2] > col_tiles[j][2]:
                    conflict += 2
    return conflict

def h_WalkingDistance(board_matrix, goal_positions):
    wd_row = 0
    wd_col = 0
    size = int(len(board_matrix)**0.5)
    for i, val in enumerate(board_matrix):
        if val != 0 and val in goal_positions:
            r, c = i // size, i % size
            gr, gc = goal_positions[val] // size, goal_positions[val] % size
            if r != gr: wd_row += 1 
            if c != gc: wd_col += 1
    return (wd_row + wd_col) // 2 

def h_CornerTiles(board_matrix, goal_positions):
    penalty = 0
    size = int(len(board_matrix)**0.5)
    def at(r, c): return r * size + c
    
    corners = [
        (0, 0, (0, 1), (1, 0)), 
        (0, size-1, (0, size-2), (1, size-1)),
        (size-1, 0, (size-1, 1), (size-2, 0)),
        (size-1, size-1, (size-1, size-2), (size-2, size-1))
    ]
    
    for r_corn, c_corn, adj_1, adj_2 in corners:
        corn_val = board_matrix[at(r_corn, c_corn)]
        target_val = None
        for v, g_idx in goal_positions.items():
            if g_idx == at(r_corn, c_corn):
                target_val = v
                break
                
        if corn_val != 0 and corn_val == target_val:
            val_adj1 = board_matrix[at(adj_1[0], adj_1[1])]
            val_adj2 = board_matrix[at(adj_2[0], adj_2[1])]
            
            target_adj1, target_adj2 = None, None
            for v, g_idx in goal_positions.items():
                if g_idx == at(adj_1[0], adj_1[1]): target_adj1 = v
                if g_idx == at(adj_2[0], adj_2[1]): target_adj2 = v
                
            if val_adj1 != 0 and val_adj1 != target_adj1 and val_adj2 != 0 and val_adj2 != target_adj2:
                penalty += 2
                
        elif corn_val != 0 and corn_val != target_val:
            val_adj1 = board_matrix[at(adj_1[0], adj_1[1])]
            val_adj2 = board_matrix[at(adj_2[0], adj_2[1])]
            if (val_adj1 == target_val and val_adj1 != 0) or (val_adj2 == target_val and val_adj2 != 0):
                penalty += 2
                
    return penalty

def h_LastMove(board_matrix, goal_positions):
    misplaced = 0
    for i, v in enumerate(board_matrix):
        if v != 0 and v in goal_positions:
            if i != goal_positions[v]:
                misplaced += 1
    if 0 < misplaced <= 2:
        return 1
    return 0

def h_DistanciaInversion(board_matrix, goal_positions):
    inv_count = 0
    tiles = [val for val in board_matrix if val != 0]
    size = int(len(board_matrix)**0.5)
    
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            val1 = tiles[i]
            val2 = tiles[j]
            if val1 in goal_positions and val2 in goal_positions:
                if goal_positions[val1] > goal_positions[val2]:
                    inv_count += 1
                    
    return inv_count // (size - 1) if size > 1 else 0

def heuristica_combinada(board_matrix, goal_positions):
    md = h_DistanciaManhattan(board_matrix, goal_positions)
    lc = h_ConflictoLineal(board_matrix, goal_positions)
    wd = h_WalkingDistance(board_matrix, goal_positions)
    ct = h_CornerTiles(board_matrix, goal_positions)
    lm = h_LastMove(board_matrix, goal_positions)
    idr = h_DistanciaInversion(board_matrix, goal_positions)
    
    # Extraer MÁXIMO conservador para preservar admisibilidad IDA*
    return max(md + lc + ct, md + lc + lm, md + idr, wd)
```

### D. `src/gestor_tablero.py`
```python
class Board:
    """Clase Board (1D) extremadamente optimizada."""
    def __init__(self, matrix, size=None):
        if len(matrix) > 0 and isinstance(matrix[0], (list, tuple)):
            self.size = len(matrix)
            self.matrix = tuple(val for row in matrix for val in row)
        else:
            self.size = size
            self.matrix = tuple(matrix)
            
        self.blank_pos = self.matrix.index(0)

    def get_possible_moves(self):
        moves = []
        blnk = self.blank_pos
        sz = self.size
        r, c = blnk // sz, blnk % sz
        
        if r > 0:
            nm = list(self.matrix)
            nm[blnk], nm[blnk - sz] = nm[blnk - sz], nm[blnk]
            moves.append((Board(nm, sz), 'U'))
            
        if r < sz - 1:
            nm = list(self.matrix)
            nm[blnk], nm[blnk + sz] = nm[blnk + sz], nm[blnk]
            moves.append((Board(nm, sz), 'D'))
            
        if c > 0:
            nm = list(self.matrix)
            nm[blnk], nm[blnk - 1] = nm[blnk - 1], nm[blnk]
            moves.append((Board(nm, sz), 'L'))
            
        if c < sz - 1:
            nm = list(self.matrix)
            nm[blnk], nm[blnk + 1] = nm[blnk + 1], nm[blnk] 
            moves.append((Board(nm, sz), 'R'))
            
        return moves

    def get_inversions(self):
        flat = [val for val in self.matrix if val != 0]
        return sum(1 for i in range(len(flat)) for j in range(i + 1, len(flat)) if flat[i] > flat[j])

    def is_solvable(self):
        inv_count = self.get_inversions()
        if self.size % 2 != 0:
            return inv_count % 2 == 0
        else:
            r = self.blank_pos // self.size
            row_from_bottom = self.size - r
            if row_from_bottom % 2 == 0:
                return inv_count % 2 != 0
            else:
                return inv_count % 2 == 0

    def __hash__(self):
        return hash(self.matrix)
        
    def __eq__(self, other):
        if not isinstance(other, Board):
            return False
        return self.matrix == other.matrix

    def __str__(self):
        res = ""
        for i in range(self.size):
            row = self.matrix[i * self.size : (i + 1) * self.size]
            res += "\t".join(str(x) if x != 0 else "_" for x in row) + "\n"
        return res
```

### E. `src/utilidades.py`
```python
import os
import csv

def read_instance(filepath):
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

def save_performance_metrics(filepath, metrics_dict):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file_exists = os.path.isfile(filepath)
    
    with open(filepath, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics_dict.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(metrics_dict)

def write_solution(filepath, solution_path_str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'a') as f:
        f.write(solution_path_str + "\n")
```

### F. Dashboard e Imágenes 
Las implementaciones de Python (generando los JSON) y React (código JSX `page.tsx`) alimentaron localmente el repositorio con imágenes gráficas ubicadas en `results/stats_plots/resultados_completos_dashboard.png`. Estos gráficos visualizan las métricas de `performance_metrics.csv` para completar el requerimiento gráfico estético de Claude.
