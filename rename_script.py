import os
import subprocess

def rename_and_update():
    replacements = {
        'board_manager': 'gestor_tablero',
        'ida_star': 'ida_estrella',
        'instance_generator': 'generador_instancias',
        'utils': 'utilidades',
        'visualizer': 'visualizador',
        'heuristics': 'heuristicas'
    }
    
    # Update contents
    src_dir = '/Users/nglmike/Downloads/IA/n_puzzle_solver/src'
    for file in os.listdir(src_dir):
        if file.endswith('.py'):
            path = os.path.join(src_dir, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            for old, new in replacements.items():
                content = content.replace(old, new)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
    # Git rename
    for old, new in replacements.items():
        old_path = os.path.join(src_dir, f"{old}.py")
        new_path = os.path.join(src_dir, f"{new}.py")
        if os.path.exists(old_path):
            subprocess.run(['git', 'mv', old_path, new_path])
            
    # Also rename main.py -> principal.py
    main_old = os.path.join(src_dir, 'main.py')
    main_new = os.path.join(src_dir, 'principal.py')
    if os.path.exists(main_old):
        subprocess.run(['git', 'mv', main_old, main_new])
        
if __name__ == "__main__":
    rename_and_update()
    print("Files successfully translated and updated.")
