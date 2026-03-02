class Board:
    """
    Clase Board (1D) extremadamente optimizada.
    Aprende la matriz como una tupla plana unidimensional (1D)
    evitando la pesada memoria y saltos de caché de estructuras 2D.
    """
    def __init__(self, matrix, size=None):
        # Si entra una matriz 2D (desde lectura de archivo) la aplanamos
        if len(matrix) > 0 and isinstance(matrix[0], (list, tuple)):
            self.size = len(matrix)
            self.matrix = tuple(val for row in matrix for val in row)
        else:
            # Si entramos recursivamente copiando el 1D
            self.size = size
            self.matrix = tuple(matrix)
            
        self.blank_pos = self.matrix.index(0)

    def get_possible_moves(self):
        """Genera movimientos U, D, L, R con intercambios 1D en caché O(1)"""
        moves = []
        blnk = self.blank_pos
        sz = self.size
        r, c = blnk // sz, blnk % sz
        
        # UP: r > 0 implica que podemos restar una fila de longitud `size`
        if r > 0:
            nm = list(self.matrix)
            nm[blnk], nm[blnk - sz] = nm[blnk - sz], nm[blnk]
            moves.append((Board(nm, sz), 'U'))
            
        # DOWN
        if r < sz - 1:
            nm = list(self.matrix)
            nm[blnk], nm[blnk + sz] = nm[blnk + sz], nm[blnk]
            moves.append((Board(nm, sz), 'D'))
            
        # LEFT
        if c > 0:
            nm = list(self.matrix)
            nm[blnk], nm[blnk - 1] = nm[blnk - 1], nm[blnk]
            moves.append((Board(nm, sz), 'L'))
            
        # RIGHT
        if c < sz - 1:
            nm = list(self.matrix)
            nm[blnk], nm[blnk + 1] = nm[blnk + 1], nm[blnk]
            moves.append((Board(nm, sz), 'R'))
            
        return moves

    def get_inversions(self):
        flat = [val for val in self.matrix if val != 0]
        # Sum generator in C is extremely fast
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
