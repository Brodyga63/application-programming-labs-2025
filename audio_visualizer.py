import pandas as pd
import matplotlib.pyplot as plt


def plot_duration_line(sorted_df: pd.DataFrame, output_path: str) -> None:
    """
    Построение линейного графика длительности для отсортированных данных.
    Ось X: номер файла в отсортированном списке.
    Ось Y: длительность аудиофайла.
    """

    # Отфильтровываем ошибочные значения (-1.0) перед построением графика
    data_to_plot = sorted_df[sorted_df["duration_sec"] != -1.0].reset_index(drop=True)

    if data_to_plot.empty:
        print(" Нет корректных данных для построения графика.")
        return

    plt.figure(figsize=(12, 6))

    # Ось X: индексы (номера) в отсортированном списке
    x_values = data_to_plot.index
    # Ось Y: длительность в секундах
    y_values = data_to_plot["duration_sec"]

    plt.plot(
        x_values,
        y_values,
        marker="o",
        linestyle="-",
        color="blue",
        markersize=3,
        alpha=0.7,
    )

    # Подписи и заголовок
    plt.title("Длительность Аудиофайлов (Отсортировано по Длительности)", fontsize=14)
    plt.xlabel("Номер Аудиофайла в Отсортированном Списке", fontsize=12)
    plt.ylabel("Длительность (секунды)", fontsize=12)

    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    try:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f" График сохранён: {output_path}")
        #
    except Exception as e:
        print(f" Ошибка при сохранении графика: {e}")
    finally:
        plt.close()
