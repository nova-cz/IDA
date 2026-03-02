import os
import random
import copy

def get_goal_board(n):
    """Generates the goal board for size n x n."""
    board = list(range(1, n * n))
    board.append(0)
    return [board[i * n:(i + 1) * n] for i in range(n)]

def get_blank_pos(board, n):
    for r in range(n):
        for c in range(n):
            if board[r][c] == 0:
                return r, c
    return -1, -1

def get_valid_moves(r, c, n):
    moves = []
    if r > 0: moves.append((r - 1, c)) # Up (empty space moves up)
    if r < n - 1: moves.append((r + 1, c)) # Down
    if c > 0: moves.append((r, c - 1)) # Left
    if c < n - 1: moves.append((r, c + 1)) # Right
    return moves

def reverse_shuffle(goal_board, n, num_moves):
    """
    Shuffles the board backwards from the goal state by num_moves.
    Avoids trivial cycles (undoing the immediate previous move).
    """
    current_board = copy.deepcopy(goal_board)
    r, c = get_blank_pos(current_board, n)
    prev_r, prev_c = -1, -1
    
    for _ in range(num_moves):
        moves = get_valid_moves(r, c, n)
        # Avoid going back to the exact previous blank position
        valid_moves = [m for m in moves if m != (prev_r, prev_c)]
        
        if not valid_moves: # Should not happen unless 1x1, but prevents errors
            valid_moves = moves
            
        next_r, next_c = random.choice(valid_moves)
        
        # Swap blank with chosen valid adjacent tile
        current_board[r][c], current_board[next_r][next_c] = current_board[next_r][next_c], current_board[r][c]
        
        # Update trackers
        prev_r, prev_c = r, c
        r, c = next_r, next_c
        
    return current_board

def save_instance(filepath, n, initial_board, goal_board):
    """
    Guarda la instancia con el formato estricto:
    - Línea 1: n
    - n líneas: inicial en comas
    - n líneas: meta en comas
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(f"{n}\n")
        
        for row in initial_board:
            f.write(",".join(map(str, row)) + "\n")
            
        for row in goal_board:
            f.write(",".join(map(str, row)) + "\n")

def generate_instances():
    """
    Script para crear 1,800 casos (300 por tamaño de tablero de 3x3 a 8x8) 
    siguiendo el método de barajado inverso (partiendo desde la meta y aplicando movimientos válidos aleatorios).
    """
    sizes = range(3, 9) # 3x3 to 8x8
    difficulties = {
        'faciles': 10,
        'medios': 20,
        'dificiles': 50
    }
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instances"))
    
    total = 0
    for n in sizes:
        goal_board = get_goal_board(n)
        for diff_name, num_moves in difficulties.items():
            for i in range(1, 101):
                initial_board = reverse_shuffle(goal_board, n, num_moves)
                file_path = os.path.join(base_dir, f"{n}x{n}", diff_name, f"{i}.txt")
                save_instance(file_path, n, initial_board, goal_board)
                total += 1
                
    print(f"Generated {total} instances successfully in: {base_dir}")

if __name__ == "__main__":
    generate_instances()
