import argparse
import os
import sys

from audio_processor import read_annotation_file, process_all_tracks


def parse_args() -> argparse.Namespace:
    """
    Парсинг аргументов командной строки.
    Единое действие: Чтение аргументов, переданных через терминал.
    """
    parser = argparse.ArgumentParser(
        description="Программа для пакетной обработки аудиофайлов по списку из аннотации Lab 2.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "input_annotation",
        type=str,
        help="Путь к исходному CSV-файлу аннотаций (например, annotation.csv).",
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Путь к папке, куда будут сохранены обработанные аудиофайлы и графики.",
    )
    parser.add_argument(
        "-f",
        "--factor",
        type=float,
        default=0.5,
        help="Коэффициент уменьшения амплитуды (float от 0.0 до 1.0).",
    )
    return parser.parse_args()


def main() -> None:
    """
    Точка входа программы: парсинг аргументов, проверка путей и запуск обработки.
    Единое действие: Координация верхнего уровня.
    """
    args = parse_args()

    input_annotation = args.input_annotation
    output_dir = args.output_dir
    reduction_factor = args.factor

    # Проверка существования входного CSV‑файла
    if not os.path.exists(input_annotation):
        print(f"Ошибка: Исходный файл аннотаций не найден по пути: {input_annotation}")
        sys.exit(1)

    # Создание выходной папки (если её нет)
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(
            f"Критическая ошибка: Не удалось создать выходную папку {output_dir}. Причина: {e}"
        )
        sys.exit(1)

    # Основной цикл обработки
    try:
        # Чтение CSV и запуск цикла полностью вынесены в audio_processor.py
        tracks_data = read_annotation_file(input_annotation)
        processed_count = process_all_tracks(tracks_data, output_dir, reduction_factor)

        print(
            f"\n--- Обработка завершена. Успешно обработано: {processed_count} файлов. ---"
        )
        print(f"Аудиофайлы и графики сохранены в папке: {output_dir}")

    except Exception as e:
        print(
            f"\nКритическая ошибка: Произошла ошибка во время обработки. Причина: {e}."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
