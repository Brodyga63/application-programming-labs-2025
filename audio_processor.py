import numpy as np
import os
import csv
import soundfile as sf
import matplotlib.pyplot as plt


from typing import List, Dict, Tuple

from visualizer import create_visualization_figure, save_figure_to_png


def reduce_amplitude(data: np.ndarray, reduction_factor: float) -> np.ndarray:
    """
    Единое действие: Уменьшение амплитуды сэмплов аудиофайла.
    """
    if not (0.0 < reduction_factor <= 1.0):
        raise ValueError("Коэффициент уменьшения должен быть в диапазоне (0.0, 1.0].")

    processed_data = data * reduction_factor
    processed_data = np.clip(processed_data, -1.0, 1.0)

    return processed_data


def read_annotation_file(input_path: str) -> List[Dict[str, str]]:
    """
    Единое действие: Чтение CSV-файла, содержащего список аудиофайлов.
    """
    with open(input_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def read_audio_file(abs_path: str) -> Tuple[np.ndarray, int]:
    """
    Единое действие: Загрузка аудиофайла с помощью soundfile.
    """
    data, samplerate = sf.read(abs_path)
    return data, samplerate


def save_audio_file(output_path: str, data: np.ndarray, samplerate: int) -> None:
    """
    Единое действие: Сохранение обработанного аудиофайла.
    """
    sf.write(output_path, data, samplerate)


def process_all_tracks(
    tracks_data: List[Dict[str, str]], output_dir: str, reduction_factor: float
) -> int:
    """
    Единое действие: Итерация по всем трекам, выполнение I/O, обработки и визуализации.
    """
    processed_count = 0

    for row in tracks_data:
        abs_path = row.get("absolute_path")

        if not abs_path or not os.path.exists(abs_path):
            print(f"Пропущено: Файл не найден или путь некорректен: {abs_path}")
            continue

        filename = os.path.basename(abs_path)
        output_filename = f"processed_{filename}"
        output_path = os.path.join(output_dir, output_filename)

        print(f"Обработка: {filename}...")

        # --- 1. Чтение аудиофайла (I/O) ---
        data, samplerate = read_audio_file(abs_path)

        size_bytes = os.path.getsize(abs_path)
        print(f"  Размер файла: {size_bytes} байт.")

        # --- 2. Уменьшение амплитуды (Math) ---
        processed_data = reduce_amplitude(data, reduction_factor)

        # --- 3. Подготовка данных для графика ---
        plot_data_original = data[:, 0] if data.ndim > 1 else data
        plot_data_processed = (
            processed_data[:, 0] if processed_data.ndim > 1 else processed_data
        )

        # --- 4. Создание и сохранение графика ---
        fig = create_visualization_figure(
            plot_data_original,
            plot_data_processed,
            samplerate,
            filename,
            reduction_factor,
        )
        save_figure_to_png(fig, output_path)

        # Отображение первого графика для проверки
        if processed_count == 0:
            print(
                "Отображение графика первого файла для проверки. Закройте окно для продолжения пакетной обработки."
            )
            plt.show()

        plt.close(fig)

        # --- 5. Сохранение обработанного аудиофайла (I/O) ---
        save_audio_file(output_path, processed_data, samplerate)

        processed_count += 1

    return processed_count
