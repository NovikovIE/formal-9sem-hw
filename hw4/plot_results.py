import json
import matplotlib.pyplot as plt

def plot_benchmark():
    # 1. Загружаем данные
    try:
        with open('benchmark_results.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Файл 'benchmark_results.json' не найден.")
        return

    sizes = data['sizes']
    raw_old = data['old_times']
    raw_new = data['new_times']

    # 2. Агрегация данных (считаем среднее для каждого N)
    # Твой скрипт сохраняет 5 измерений на каждый размер.
    # Нам нужно превратить [t1_1, t1_2, ..., t2_1...] в [avg_t1, avg_t2...]
    
    # Вычисляем, сколько было итераций на один размер
    iterations = len(raw_old) // len(sizes)
    
    avg_old = []
    avg_new = []

    for i in range(len(sizes)):
        start = i * iterations
        end = start + iterations
        
        # Берем срез (кусок) из 5 измерений для текущего N
        chunk_old = raw_old[start:end]
        chunk_new = raw_new[start:end]
        
        # Считаем среднее
        avg_old.append(sum(chunk_old) / len(chunk_old))
        avg_new.append(sum(chunk_new) / len(chunk_new))

    # 3. Построение графика
    plt.figure(figsize=(10, 6))
    
    # Линия старой реализации (красная)
    plt.plot(sizes, avg_old, label='Naive Implementation (O(N^5))', 
             color='red', marker='o', markersize=4, linestyle='--')
    
    # Линия новой реализации (зеленая)
    plt.plot(sizes, avg_new, label='Optimized Implementation', 
             color='green', marker='s', markersize=4)

    # Оформление
    plt.title('Сравнение производительности CYK для графов', fontsize=14)
    plt.xlabel('Количество вершин (N)', fontsize=12)
    plt.ylabel('Время выполнения (сек)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, which="both", ls="-", alpha=0.4)

    # Опционально: логарифмическая шкала (раскомментируй, если разница огромная)
    # plt.yscale('log') 

    plt.tight_layout()
    
    # Сохранение и показ
    output_file = 'cyk_benchmark_plot.png'
    plt.savefig(output_file)
    print(f"График сохранен в файл: {output_file}")

if __name__ == '__main__':
    plot_benchmark()