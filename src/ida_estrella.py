import time
from collections import deque

def generate_bfs_frontier(initial_board, goal_board, heuristic_func, goal_positions, max_nodes=500):
    """
    Fase 1: BFS para generar una frontera inicial rica en estados diversos.
    Crea una Tabla de Transposición inicial (visited_states) para evitar re-expansiones 
    inútiles de las primeras pasadas.
    
    Retorna:
    - frontier_nodes: Lista de (g_cost, current_board, moves_path) listos para arrancar el IDA*.
    - transposition_table: set() global con todos los nodos de la fase superficial.
    """
    # Si la meta está ridículamente cerca
    if initial_board == goal_board:
        return [(0, initial_board, [])], {initial_board}

    transposition_table = {initial_board}
    # queue almacena: (current_board, moves_path)
    queue = deque([(initial_board, [])])
    frontier_nodes = []
    
    nodes_expanded = 0
    
    # Expandimos en BFS hasta alcanzar el conteo máximo de nodos permitidos en memoria tabla
    while queue and nodes_expanded < max_nodes:
        current_board, moves_path = queue.popleft()
        g_cost = len(moves_path)
        
        # Expandir
        children = current_board.get_possible_moves()
        nodes_expanded += 1
        
        for child_board, move_str in children:
            if child_board == goal_board:
                # Meta atrapada oportunamente en la capa BFS superficial
                new_path = list(moves_path)
                new_path.append(move_str)
                frontier_nodes.append((g_cost + 1, child_board, new_path))
                return frontier_nodes, transposition_table
                
            if child_board not in transposition_table:
                transposition_table.add(child_board)
                new_path = list(moves_path)
                new_path.append(move_str)
                queue.append((child_board, new_path))
                
    # Volcar la queue restante como las hojas de la frontera
    while queue:
        board, moves = queue.popleft()
        frontier_nodes.append((len(moves), board, moves))
        
    return frontier_nodes, transposition_table


def ida_estrella(initial_board, goal_board, heuristic_func, goal_positions):
    """
    Implementación rigurosa de Híbrido BFS-IDA* con tabla de transposición superficial.
    
    Características clave para el examen:
    1. Fase BFS: Expande la cabecera del árbol en anchura hasta ~500 nodos.
    2. Tabla de Transposición: O(1) set para bloquear re-evaluaciones iniciales.
    3. IDA* Híbrido: Ordena iterativamente las cabezas de frontera por su heurística f(n)
       y despacha DFS acotados individuales conservando la lista Tabú.
    4. Control de expansión máxima para evitar ciclos infinitos o estancamientos críticos (`MAX_EXPANS_PER_ITER`).
    """
    start_time = time.time()
    nodes_expanded = [0]  # Contador global por referencia

    # Límites dudos contra estancamientos absolutos en tableros muy grandes
    MAX_ITERATIONS = 500
    MAX_EXPANS_PER_ITER = 1_000_000
    BFS_FRONTIER_SIZE = 500

    # ==========================
    # FASE 1: Construir Frontera BFS
    # ==========================
    frontier, base_transposition_table = generate_bfs_frontier(
        initial_board, goal_board, heuristic_func, goal_positions, max_nodes=BFS_FRONTIER_SIZE
    )
    
    # Contabilizar la capa superficial
    nodes_expanded[0] += len(base_transposition_table)
    
    # Si de milagro el BFS encontró la meta inmediatamente
    for g, b, m in frontier:
        if b == goal_board:
            end_time = time.time()
            return ",".join(m), nodes_expanded[0], end_time - start_time

    # ==========================
    # FASE 2: Sort Heurístico de Frontera
    # ==========================
    # Ordenamos los nodos frontera con el menor f(n) = g + h(n) primero para despachar el IDA*
    def sort_f(item):
        g_c, brd, _ = item
        return g_c + heuristic_func(brd.matrix, goal_positions)
        
    frontier.sort(key=sort_f)
    
    # Calcular el umbral inicial basado en el mejor nodo de la frontera BFS
    best_g, best_b, _ = frontier[0]
    threshold = best_g + heuristic_func(best_b.matrix, goal_positions)

    # ==========================
    # FASE 3: Motor IDA* Iterativo
    # ==========================
    for _ in range(MAX_ITERATIONS):
        next_threshold = float('inf')
        iteration_expansions = [0]
        
        # Despachar una búsqueda DFS desde cada "cabeza" de la frontera ordenada
        for initial_g, start_node, base_moves in frontier:
            f_val = initial_g + heuristic_func(start_node.matrix, goal_positions)
            
            # Si el f_val de re-arranque excede el umbral, ni siquiera entramos (poda estricta de raíz)
            if f_val > threshold:
                if f_val < next_threshold:
                    next_threshold = f_val
                continue
            
            # Preparar estructuras per-DFS
            path = [start_node]
            moves_path = list(base_moves) # Copia de seguridad del prefijo BFS
            tabu_set = {start_node}
            
            res, t = search(
                path, 
                moves_path, 
                initial_g, 
                threshold, 
                goal_board, 
                heuristic_func, 
                goal_positions, 
                nodes_expanded, 
                iteration_expansions,
                MAX_EXPANS_PER_ITER,
                tabu_set,
                base_transposition_table
            )
            
            if res == "FOUND":
                end_time = time.time()
                return ",".join(moves_path), nodes_expanded[0], end_time - start_time
                
            if t < next_threshold:
                next_threshold = t
                
            # Salida forzosa global para limitar estancamientos académicos a 1,000,000 expansiones TOTALES
            if nodes_expanded[0] > MAX_EXPANS_PER_ITER:
                break
                
        if nodes_expanded[0] > MAX_EXPANS_PER_ITER or next_threshold == float('inf'):
            break # El árbol agotó la cuota empírica o ya no hay estados validos
            
            
        threshold = next_threshold

    end_time = time.time()
    return None, nodes_expanded[0], end_time - start_time


def search(path, moves_path, g, threshold, goal_board, heuristic_func, goal_positions, 
           nodes_expanded, iteration_expansions, max_expansions, tabu_set, base_transposition_table):
    """
    Búsqueda DFS recursiva del IDA* con tabla de transposición profunda combinada:
    Usa el tabu_set local sumado al base_transposition_table global para no repetir
    capas superficiales ya abarcadas por el BFS.
    """
    current_node = path[-1]
    f = g + heuristic_func(current_node.matrix, goal_positions)
    
    # Poda 1: Límite de rama
    if f > threshold:
        return "NOT_FOUND", f
        
    # Poda 2: Meta encontrada
    if current_node == goal_board:
        return "FOUND", f

    # Poda 3: Cota anti-estancamiento (Limitador interno solicitado)
    if iteration_expansions[0] > max_expansions:
        return "NOT_FOUND", f + 1
        
    min_exceeded = float('inf')
    
    children = current_node.get_possible_moves()
    nodes_expanded[0] += 1
    iteration_expansions[0] += 1
    
    # Estrategia de exploración
    for child_board, move_str in children:
        # Poda crítica: No visitar nodos que forman ciclo local (tabu_set) 
        # ni nodos que ya sabemos que son re-entradas a la fase superficial BFS (base_transposition_table)
        if child_board not in tabu_set and child_board not in base_transposition_table:
            
            path.append(child_board)
            moves_path.append(move_str)
            tabu_set.add(child_board)
            
            res, t = search(
                path, 
                moves_path, 
                g + 1, 
                threshold, 
                goal_board, 
                heuristic_func, 
                goal_positions, 
                nodes_expanded, 
                iteration_expansions,
                max_expansions,
                tabu_set,
                base_transposition_table
            )
            
            if res == "FOUND":
                return "FOUND", t
                
            if t < min_exceeded:
                min_exceeded = t
                
            # Libera el nodo de la rama actual para permitirlo en ramas alternas
            tabu_set.remove(child_board)
            moves_path.pop()
            path.pop()
            
    return "NOT_FOUND", min_exceeded
