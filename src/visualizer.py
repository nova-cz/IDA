import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def generate_plots():
    """
    Genera un dashboard integrado de rendimiento a partir de performance_metrics.csv.
    Utiliza estilos ultramodernos de Seaborn y combina todo en una sola imagen HD.
    """
    # Establecer un estilo moderno, "darkgrid" para resaltar colores vibrantes
    sns.set_theme(style="darkgrid", palette="pastel")
    plt.rcParams.update({
        'font.size': 12, 
        'font.family': 'sans-serif',
        'font.weight': 'medium',
        'axes.labelweight': 'bold',
        'axes.titleweight': 'bold'
    })
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, "..", "results")
    csv_path = os.path.join(results_dir, "performance_metrics.csv")
    plots_dir = os.path.join(results_dir, "stats_plots")
    
    os.makedirs(plots_dir, exist_ok=True)
    
    if not os.path.exists(csv_path):
        print(f"Error: No se encontró el archivo {csv_path}.")
        return
        
    df = pd.read_csv(csv_path)
    if df.empty:
        print("El archivo CSV está vacío.")
        return

    # Preparar Datos
    df['Estado'] = df['solved'].apply(lambda x: 'Encontrada' if x else 'Timeout (Memoria Límite)')
    df_solved = df[df['solved'] == True].copy()
    time_df = df_solved.groupby(['n_size', 'difficulty'])['time_seconds'].mean().reset_index()
    count_df = df.groupby(['n_size', 'Estado']).size().reset_index(name='Cantidad')

    # Crear Figura principal (Dashboard 2x2)
    fig = plt.figure(figsize=(18, 14), facecolor='#f7f9fc')
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.25)
    
    # Titulo General
    fig.suptitle("Análisis Empírico de Rendimiento: IDA* Híbrido (N-Puzzle)", 
                 fontsize=24, fontweight='bold', color='#2c3e50', y=0.96)

    # ----- 1. Gráfica de Líneas: Tamaño vs Tiempo (Arriba, abarca ambas columnas) -----
    ax1 = fig.add_subplot(gs[0, :])
    if not time_df.empty:
        sns.lineplot(
            data=time_df, x='n_size', y='time_seconds', hue='difficulty',
            marker='o', linewidth=4, markersize=12, palette=['#3498db', '#f1c40f', '#e74c3c'], ax=ax1
        )
        
        max_t = time_df['time_seconds'].max()
        min_t = time_df['time_seconds'].replace(0, np.nan).min()
        if pd.notna(min_t) and (max_t / min_t) > 10:
            ax1.set_yscale("log")
            ax1.set_ylabel("Tiempo Promedio (seg.) [LOG]", fontsize=13)
        else:
            ax1.set_ylabel("Tiempo Promedio (segundos)", fontsize=13)

        ax1.set_title("Explosión Combinatoria: Crecimiento de Tiempo por Dimensión", fontsize=16, pad=15)
        ax1.set_xlabel("Dimensión del Tablero (N x N)", fontsize=13)
        ax1.legend(title='Dificultad Inicial', title_fontsize='14', fontsize='12', shadow=True, fancybox=True)
        ax1.grid(True, linestyle='--', alpha=0.7)

    # ----- 2. Gráfica de Barras Apiladas (Abajo Izquierda) -----
    ax2 = fig.add_subplot(gs[1, 0])
    if not count_df.empty:
        sns.barplot(
            data=count_df, x='n_size', y='Cantidad', hue='Estado',
            palette={'Encontrada': '#2ecc71', 'Timeout (Memoria Límite)': '#e74c3c'}, ax=ax2, alpha=0.9
        )
        ax2.set_title("Rotura de Rendimiento: Éxito vs Timeout", fontsize=16, pad=15)
        ax2.set_xlabel("Dimensión (N)", fontsize=13)
        ax2.set_ylabel("Cantidad de Instancias", fontsize=13)
        
        for container in ax2.containers:
            ax2.bar_label(container, padding=5, fontsize=12, fontweight='bold', color='#34495e')
            
        ax2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=2, shadow=True, fancybox=True)

    # ----- 3. Gráfica de Pastel (Abajo Derecha) -----
    ax3 = fig.add_subplot(gs[1, 1])
    global_counts = df['Estado'].value_counts()
    
    if not global_counts.empty:
        colors = ['#2ecc71' if state == 'Encontrada' else '#e74c3c' for state in global_counts.index]
        explode = tuple(0.05 for _ in range(len(global_counts))) # Separar rebanadas ligeramente
        
        ax3.pie(
            global_counts, 
            labels=global_counts.index, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=colors,
            explode=explode,
            shadow=True,
            textprops={'fontsize': 14, 'fontweight': 'bold', 'color': 'black'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
        )
        ax3.set_title("Proporción Global de Resolución del IDA*", fontsize=16, pad=15)

    # Guardar Dashboard Integrado
    dashboard_path = os.path.join(plots_dir, "resultados_completos_dashboard.png")
    fig.savefig(dashboard_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"\n¡Dashboard moderno de gráficos guardado en: {dashboard_path}!")
    plt.close(fig)

if __name__ == "__main__":
    generate_plots()
