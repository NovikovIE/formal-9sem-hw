import time
import random
import copy
import json
import sys

import CYK_graph_naive as old_impl
import CYK as new_impl

G_RULES = {
    'A': [['a']],
    'B': [['d']],
    'C': [['c']],
    'D': [['A', 'B']],
    'E': [['B', 'C']],
    'S': [['D', 'E']]
}

def generate_random_graph_matrix(n, density=0.3):
    matrix = [['0'] * n for _ in range(n)]
    terminals = ['a', 'c', 'd'] # Терминалы, которые есть в грамматике
    
    for i in range(n):
        for j in range(n):
            if i != j and random.random() < density:
                matrix[i][j] = random.choice(terminals)
    return matrix

def run_benchmarks():
    sizes = [i for i in range(1, 70 + 1)] 
    
    results = {
        "sizes": sizes,
        "old_times": [],
        "new_times": []
    }

    new_grammar_obj = new_impl.Grammar(G_RULES)
    new_solver = new_impl.CYKGraph(new_grammar_obj)

    print(f"{'Size (N)':<10} | {'Old Time (s)':<15} | {'New Time (s)':<15}")
    print("-" * 45)

    ITERATIONS = 5

    for n in sizes:
        for _ in range(ITERATIONS):
            graph = generate_random_graph_matrix(n, density=0.25)
            
            graph_for_old = copy.deepcopy(graph)
            
            start_time = time.perf_counter()
            old_impl.CYK_graph(graph_for_old, old_impl.G, log=False)
            end_time = time.perf_counter()
            old_time = end_time - start_time
            
            graph_for_new = copy.deepcopy(graph)
            
            start_time = time.perf_counter()
            new_solver.solve(graph_for_new)
            end_time = time.perf_counter()
            new_time = end_time - start_time
            
            results["old_times"].append(old_time)
            results["new_times"].append(new_time)

            print(f"{n:<10} | {old_time:<15.6f} | {new_time:<15.6f}")

    with open('benchmark_results.json', 'w') as f:
        json.dump(results, f)
    
    print("\nРезультаты сохранены в 'benchmark_results.json'")

if __name__ == '__main__':
    # old_impl.G = G_RULES 
    
    run_benchmarks()