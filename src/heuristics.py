"""
Módulo avanzado de heurísticas (Optimizado a índices 1D)
Multiplica el rendimiento al obviar las matrices 2D.
"""

def get_posiciones_meta(goal_matrix):
    """Retorna posiciones como un único índice plano."""
    pos = {}
    size = len(goal_matrix)
    for r in range(size):
        for c in range(size):
            val = goal_matrix[r][c]
            if val != 0:
                pos[val] = r * size + c
    return pos

def h_DistanciaManhattan(board_matrix, goal_positions):
    """Distancia Manhattan 1D"""
    dist = 0
    size = int(len(board_matrix)**0.5)
    for i, val in enumerate(board_matrix):
        if val != 0 and val in goal_positions:
            r, c = i // size, i % size
            gr, gc = goal_positions[val] // size, goal_positions[val] % size
            dist += abs(r - gr) + abs(c - gc)
    return dist

def h_ConflictoLineal(board_matrix, goal_positions):
    """Conflicto Lineal 1D"""
    conflict = 0
    size = int(len(board_matrix)**0.5)
    
    # Filas
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
                    
    # Columnas
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
    """Distancia Caminando (Walking Distance) 1D"""
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
    """Fichas en Esquina 1D"""
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
    """Último Movimiento 1D"""
    misplaced = 0
    for i, v in enumerate(board_matrix):
        if v != 0 and v in goal_positions:
            if i != goal_positions[v]:
                misplaced += 1
    if 0 < misplaced <= 2:
        return 1
    return 0

def heuristica_combinada(board_matrix, goal_positions):
    md = h_DistanciaManhattan(board_matrix, goal_positions)
    lc = h_ConflictoLineal(board_matrix, goal_positions)
    wd = h_WalkingDistance(board_matrix, goal_positions)
    ct = h_CornerTiles(board_matrix, goal_positions)
    lm = h_LastMove(board_matrix, goal_positions)
    
    # MD y LC son matemática y estructuralmente aditivas (seguras).
    # CT y LM no se pueden sumar libremente sin riesgo de sobreestimar el costo (romper la admisibilidad del IDA*).
    # WD es un modelo totalmente distinto.
    # Por lo tanto, extraemos el MÁXIMO de estas tres combinaciones plausibles:
    return max(md + lc + ct, md + lc + lm, wd)
