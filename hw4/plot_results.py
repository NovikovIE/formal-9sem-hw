import json
import matplotlib.pyplot as plt
import os

# Список плотностей
DENSITIES = [0.1, 0.2, 0.3]

def load_data(densities):
    data_store = {}
    for d in densities:
        filename = f'benchmark_full_results_{d}.json'
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data_store[d] = json.load(f)
            print(f"[OK] Загружен: {filename}")
        else:
            print(f"[SKIP] Файл {filename} не найден.")
    return data_store

def save_plots(data_store):
    if not data_store:
        print("Нет данных для построения графиков.")
        return

    densities_found = sorted(data_store.keys())
    count = len(densities_found)
    
    # Настройка стиля
    plt.style.use('seaborn-v0_8-whitegrid')

    fig_time, axes_time = plt.subplots(1, count, figsize=(6 * count, 6))
    if count == 1: axes_time = [axes_time] 
    
    fig_time.suptitle('Benchmark Results: Time Execution', fontsize=16)

    for i, d in enumerate(densities_found):
        res = data_store[d]
        sizes = res['sizes']
        ax = axes_time[i]
        
        ax.plot(sizes, res['old_times'], label='Old Impl', marker='o', linestyle='--', color='red', markersize=4, alpha=0.7)
        ax.plot(sizes, res['new_times'], label='New Impl', marker='o', linestyle='-', color='green', markersize=4)
        
        ax.set_title(f'Density = {d}')
        ax.set_xlabel('Graph Size (N)')
        ax.set_ylabel('Time (seconds)')
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    time_filename = 'benchmark_plot_time.png'
    plt.savefig(time_filename, dpi=300) 
    print(f"Сохранен график времени: {time_filename}")
    plt.close(fig_time) 

    fig_mem, axes_mem = plt.subplots(1, count, figsize=(6 * count, 6))
    if count == 1: axes_mem = [axes_mem]

    fig_mem.suptitle('Benchmark Results: Memory Usage', fontsize=16)

    for i, d in enumerate(densities_found):
        res = data_store[d]
        sizes = res['sizes']
        ax = axes_mem[i]
        
        ax.plot(sizes, res['old_mems'], label='Old Impl', marker='o', linestyle='--', color='red', markersize=4, alpha=0.7)
        ax.plot(sizes, res['new_mems'], label='New Impl', marker='o', linestyle='-', color='blue', markersize=4)
        
        ax.set_title(f'Density = {d}')
        ax.set_xlabel('Graph Size (N)')
        ax.set_ylabel('Memory (KB)')
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    mem_filename = 'benchmark_plot_memory.png'
    plt.savefig(mem_filename, dpi=300) 
    print(f"Сохранен график памяти:  {mem_filename}")
    plt.close(fig_mem)

if __name__ == "__main__":
    data = load_data(DENSITIES)
    save_plots(data)
