import time
import random
import copy
import json
import sys
import tracemalloc

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

def generate_random_graph_matrix(n, density=0.25):
    matrix = [['0'] * n for _ in range(n)]
    terminals = ['a', 'c', 'd'] 
    for i in range(n):
        for j in range(n):
            if i != j and random.random() < density:
                matrix[i][j] = random.choice(terminals)
    return matrix

def run_benchmarks():
    sizes = [i for i in range(2, 71, 2)] 
    
    results = {
        "sizes": sizes,
        
        "old_times": [], 
        "new_times": [],
        
        "old_mems": [], 
        "new_mems": [],
        
        "density": [],
    }

    new_grammar_obj = new_impl.Grammar(G_RULES)
    new_solver = new_impl.CYKGraph(new_grammar_obj)

    print(f"{'Size':<5} | {'Old T (s)':<12} | {'New T (s)':<12} | {'Old Mem (KB)':<12} | {'New Mem (KB)':<12} | {'Density':<12}")
    print("-" * 70)

    ITERATIONS = 5
    DENSITY = 0.3

    for n in sizes:
        sum_t_old, sum_m_old = 0.0, 0.0
        sum_t_new, sum_m_new = 0.0, 0.0

        for _ in range(ITERATIONS):
            graph = generate_random_graph_matrix(n, density=DENSITY)
            
            graph_for_old = copy.deepcopy(graph)
                
            tracemalloc.start()
            t0 = time.perf_counter()
                
            old_impl.CYK_graph(graph_for_old, old_impl.G, log=False)
                
            t1 = time.perf_counter()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
                
            sum_t_old += (t1 - t0)
            sum_m_old += peak
            
            graph_for_new = copy.deepcopy(graph)
            
            tracemalloc.start()
            t0 = time.perf_counter()
            
            new_solver.solve(graph_for_new)
            
            t1 = time.perf_counter()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            sum_t_new += (t1 - t0)
            sum_m_new += peak
        
        avg_t_new = sum_t_new / ITERATIONS
        avg_m_new = (sum_m_new / ITERATIONS) / 1024 
        
        results["new_times"].append(avg_t_new)
        results["new_mems"].append(avg_m_new)
        
        avg_t_old = sum_t_old / ITERATIONS
        avg_m_old = (sum_m_old / ITERATIONS) / 1024
        results["old_times"].append(avg_t_old)
        results["old_mems"].append(avg_m_old)
            
        print(f"{n:<5} | {avg_t_old:<12.5f} | {avg_t_new:<12.5f} | {avg_m_old:<12.2f} | {avg_m_new:<12.2f}")

    with open(f'benchmark_full_results_{DENSITY}.json', 'w') as f:
        json.dump(results, f)
    
if __name__ == '__main__':
    run_benchmarks()