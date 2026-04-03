import matplotlib
matplotlib.use('Agg')  # Используем неинтерактивный бэкенд
import matplotlib.pyplot as plt
import os

def generate_income_graph(history, filename="temp_plot.png"):
    if not history:
        # Если нет данных, создаём пустой график с сообщением
        plt.figure(figsize=(6, 4))
        plt.text(0.5, 0.5, "Нет данных о сборах", ha='center', va='center', fontsize=14)
        plt.axis('off')
    else:
        plt.figure(figsize=(6, 4))
        plt.plot(range(1, len(history)+1), history, marker='o', linestyle='-', color='green')
        plt.title("Доходы с каждого сбора")
        plt.xlabel("Номер сбора")
        plt.ylabel("Очки")
        plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename, dpi=100)
    plt.close()
    return filename
