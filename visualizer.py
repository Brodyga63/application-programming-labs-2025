import os

import numpy as np
import matplotlib.pyplot as plt


def create_visualization_figure(
    data_original: np.ndarray,
    data_processed: np.ndarray,
    samplerate: int,
    filename: str,
    factor: float,
) -> plt.Figure:
    """
    Единое действие: Построение фигуры Matplotlib.
    """
    num_samples = data_original.shape[0]
    duration = num_samples / samplerate
    time_axis = np.linspace(0.0, duration, num_samples)

    fig = plt.figure(figsize=(14, 6))

    plt.subplot(2, 1, 1)
    plt.plot(time_axis, data_original, color="blue", linewidth=0.5)
    plt.title(
        f"Исходный сигнал: {filename} (Макс. |Амплитуда|: {np.max(np.abs(data_original)):.4f})"
    )
    plt.ylabel("Амплитуда")
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.subplot(2, 1, 2)
    plt.plot(time_axis, data_processed, color="red", linewidth=0.5)
    plt.title(
        f"Результат: Амплитуда уменьшена на {factor}x (Макс. |Амплитуда|: {np.max(np.abs(data_processed)):.4f})"
    )
    plt.ylabel("Амплитуда")
    plt.xlabel("Время (секунды)")
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    return fig


def save_figure_to_png(fig: plt.Figure, output_path: str) -> None:
    """
    Единое действие: Сохранение готовой фигуры в PNG-файл.
    """
    plot_output_path = os.path.splitext(output_path)[0] + ".png"
    fig.savefig(plot_output_path)