import pandas as pd
import json
import os

df = pd.read_csv('/Users/nglmike/Downloads/IA/n_puzzle_solver/results/performance_metrics.csv')

# timeData: avg time per n_size and difficulty
time_data = df[df['solved'] == True].groupby(['n_size', 'difficulty'])['time_seconds'].mean().reset_index()
time_data_list = time_data.to_dict(orient='records')

# countData: 
df['Estado'] = df['reason'].apply(lambda x: 'Encontrada' if x == 'OK' else 'Timeout (Memoria Límite)')
count_data = df.groupby(['n_size', 'Estado']).size().reset_index(name='Cantidad')
count_data_list = count_data.to_dict(orient='records')

# globalCounts:
global_counts = df['Estado'].value_counts().to_dict()

# missing data for the new charts: nodes expanded, solution length
nodes_data = df[df['solved'] == True].groupby(['n_size', 'difficulty'])['nodes_expanded'].mean().reset_index()
nodes_data_list = nodes_data.to_dict(orient='records')

length_data = df[df['solved'] == True].groupby(['n_size', 'difficulty'])['solution_length'].mean().reset_index()
length_data_list = length_data.to_dict(orient='records')

# scatter data: individual instances sorted by time
scatter_df = df[df['solved'] == True].copy()
scatter_df = scatter_df.sort_values(by='time_seconds').reset_index(drop=True)
scatter_data_list = []
for i, row in scatter_df.iterrows():
    scatter_data_list.append({
        'index': i,
        'difficulty': row['difficulty'],
        'time_seconds': row['time_seconds'],
        'n_size': row['n_size']
    })

output = {
    "timeData": time_data_list,
    "countData": count_data_list,
    "globalCounts": global_counts,
    "nodesData": nodes_data_list,
    "lengthData": length_data_list,
    "scatterData": scatter_data_list
}

with open('/Users/nglmike/Downloads/IA/n_puzzle_solver/dashboard/src/data.json', 'w') as f:
    json.dump(output, f, indent=4)
print("JSON generated at dashboard/src/data.json")
