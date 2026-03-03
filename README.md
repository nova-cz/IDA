# 🧠 IDA* N-Puzzle Solver

Este proyecto implementa una solución de alto rendimiento para el problema del **N-Puzzle (desde 3x3 hasta 8x8)**, utilizando una variante híbrida y optimizada del algoritmo **IDA* (Iterative Deepening A*) con inicialización estructurada BFS**.

Se desarrolló como parte del **Primer Examen Parcial** de la asignatura, cumpliendo rigurosamente con los 5 puntos requeridos en la especificación.

---

## 🚀 Características Principales (Respuestas al Examen)

### 1. Lectura de Archivo y Salida de Consola (1 pts)
El programa principal (`src/main.py`) cuenta con un modo de ejecución individual que lee un archivo `.txt` con la estructura exigida (dimensión, tablero inicial y tablero final separados por comas). 
Para resolver un archivo y ver la salida en consola (formato `U,D,L,R`), se utiliza:
```bash
python src/main.py --file instances/3x3/faciles/1.txt
```

### 2. Pseudocódigo y Lógica IDA* (2 pts)
La implementación núcleo se encuentra en `src/ida_star.py`. Cumple con todos los requisitos arquitectónicos:
- **Criterio Tabú:** Mantiene una estructura `tabu_set` local por cada rama de profundidad (DFS) para evitar generar ciclos.
- **Evitar Nodos Repetidos en Exploración Superficial:** Implementa una fase inicial en **Anchura (BFS)** de hasta 500 nodos para poblar una frontera diversa. Estos nodos fundacionales se guardan en una `base_transposition_table` global O(1) que previene re-expansiones inmediatas de la cabecera.
- **Control de Nivel de Profundidad:** El algoritmo `ida_star()` gestiona el límite mediante la variable `threshold`, la cual dicta hasta dónde puede profundizar el DFS interno, descartando y recordando el mínimo excedente (`min_exceeded`) para la próxima iteración. Asimismo, se integró una cota de seguridad contra estallidos de memoria (`MAX_EXPANS_PER_ITER = 1_000_000`).

### 3. Función de Evaluación y Heurísticas (2 pts)
El motor de evaluación heurística, implementado en `src/heuristics.py`, opera con arreglos planos (1D) para multiplicar el rendimiento en Python. La función combinada final $f(n) = g(n) + h(n)$ extrae su valor $h(n)$ empleando **más de 3 componentes avanzados (6 en total)**:
1. **Distancia Manhattan (MD):** Distancia geométrica base.
2. **Conflicto Lineal (LC):** Penalización prioritaria cuando dos piezas de la misma fila/columna están invertidas.
3. **Distancia Caminando (Walking Distance - WD):** Un modelo de abstracción basado en flujos de filas y columnas.
4. **Fichas en Esquinas (Corner Tiles - CT):** Penalización si una pieza está atrapada en una esquina adyacente a su lugar correcto, pero la esquina está ocupada por un rival.
5. **Último Movimiento (Last Move - LM):** Beneficio marginal de reconocimiento cuando solo faltan 2 piezas por acomodar.
6. **Distancia de Inversión (Inversion Distance - IDR):** Calcula el número de inversiones relativas entre fichas y deriva un estimado matemático de movimientos obligatorios.

> **Definición de Integración (Admisibilidad Matemática):** MD y LC son componentes que por definición pueden sumarse libremente ("additive"). Sin embargo, sumar directamente CT, LM e IDR al costo puede sobreestimar el valor real (rompiendo la garantía de encontrar el camino óptimo en el algoritmo IDA*).
> Para solucionar esto estrictamente, la heurística extrae la información más agresiva utilizando de forma segura el máximo entre las configuraciones probables: `max(md + lc + ct, md + lc + lm, md + idr, wd)`.

### 4. Implementación en Python (2 pts)
Todo el sistema está programado en Python 3.
**Ejecución General:**
- Instalar dependencias para la visualización (opcional para el modo consola):
  ```bash
  pip install pandas matplotlib seaborn
  ```
- **Modo 1:** Para probar un tablero individual (salida `U,L,R,D` a consola).
  ```bash
  python src/main.py --file PATH_AL_TXT
  ```
- **Modo 2:** Ejecutar benchmark maestro para todas las carpetas (análisis empírico).
  ```bash
  python src/main.py --analysis
  ```

### 5. Análisis Empírico Empaquetado (3 pts)
El aplicativo provee un pipeline propio para experimentar contra la carpeta `/instances` (1 a 100 tableros).
Al correr `python src/main.py --analysis`, se explora iterativamente cada carpeta (`3x3/faciles`, `3x3/medios`, `3x3/dificiles`, hasta `8x8`).

Para generar y visualizar los resultados exigidos:
```bash
python src/visualizer.py
```
Este script leerá métricas y guardará un archivo `resultados_completos_dashboard.png` provisto en estilos modernos Seaborn/Matplotlib en un formato Dashboard (4 Cuadrantes), donde se exponen abiertamente:
1. **Crecimiento de Tiempo por Dimensión:** Aumentos agudos de logaritmo temporal por complejidad de instancias.
2. **Costo por Instancia Individual:** Gráfica de dispersión mostrando el tiempo de cada tablero de menor a mayor (más barata a más cara).
3. **Distribución de Éxito vs Timeout:** Estadística explícita de éxito (0% a 100%) vs cortes de protección de iteraciones IDA* (evitando ciclos infinitos).
4. **Proporción Global:** Gráfica de pastel global indicando la tasa final de éxito del framework.

---

## 🛠️ Estructura del Proyecto

```text
n_puzzle_solver/
│
├── instances/               # Almacena los txt generados (3x3 al 8x8, faciles, medios, dificiles)
├── results/                 # Donde caen los tests empíricos (CSV)
│   ├── stats_plots/         # Directorio automático de gráficas y dashboards
│
├── src/
│   ├── main.py              # CLI principal de interacción
│   ├── ida_star.py          # Implementacion rigurosa IDA* + BFS
│   ├── heuristics.py        # 5 heurísticas avanzadas 1D
│   ├── board_manager.py     # Lógica matemática de transiciones y validación de paridad
│   ├── instance_generator.py# Generador de tableros
│   ├── visualizer.py        # Graficador Seaborn para el análisis estadístico del punto 5
│   └── utils.py             # Lectores I/O de txt
```
