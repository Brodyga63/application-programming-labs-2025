import sys
import argparse  # Импорт argparse для парсера

# Импорт модулей
try:
    from audio_processor import AudioProcessor
    from audio_visualizer import plot_duration_line
except ImportError as e:
    print(
        f"Ошибка импорта модуля. Убедитесь, что все файлы находятся в одной папке: {e}"
    )
    sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """
    Парсит аргументы командной строки, задавая пути и параметры фильтрации.
    """
    parser = argparse.ArgumentParser(
        description="Анализ и визуализация длительности аудиофайлов из аннотации."
    )
    parser.add_argument(
        "--input-csv",
        type=str,
        default="annotation.csv",
        help="Путь к входному CSV файлу аннотации. По умолчанию: annotation.csv",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="analyzed_audio_data.csv",
        help="Путь для сохранения CSV файла с анализированными данными. По умолчанию: analyzed_audio_data.csv",
    )
    parser.add_argument(
        "--output-plot",
        type=str,
        default="audio_duration_plot.png",
        help="Путь для сохранения графика. По умолчанию: audio_duration_plot.png",
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=10.0,
        help="Минимальная длительность (в секундах) для фильтрации данных. По умолчанию: 10.0",
    )
    return parser.parse_args()


def main() -> None:
    """Основная функция для выполнения анализа."""

    # 1. Парсинг аргументов
    args = parse_arguments()
    print("--- Запуск Анализа Аудиоданных (ЛР №4) ---")

    try:
        # 2. Инициализация и обработка данных
        processor = AudioProcessor(args.input_csv)
        processor.rename_columns()

        # Добавление колонки длительности
        processor.add_duration_column()

        # 3. Сортировка по длительности (по возрастанию)
        sorted_df = processor.sort_by_column(column="duration_sec", ascending=True)

        # 4. Фильтрация (используем значение из парсера)
        print(f"\nПример фильтрации:")
        filtered_df = processor.filter_by_value(
            column="duration_sec", min_value=args.min_duration
        )

        # 5. Построение и сохранение графика для всех отсортированных данных
        plot_duration_line(sorted_df, args.output_plot)

        # 6. Сохранение итогового DataFrame
        processor.save_csv(args.output_csv)
        print(f"✅ Итоговый DataFrame сохранён: {args.output_csv}")

    except FileNotFoundError as e:
        print(f"\nОшибка: {e}")
        print("Проверьте, правильно ли указан путь к файлу аннотации.")
    except Exception as e:
        print(f"\nКритическая Ошибка: {e}")


if __name__ == "__main__":
    main()
