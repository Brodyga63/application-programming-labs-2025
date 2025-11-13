import argparse
import re
from typing import List


def capitalize_name(name: str) -> str:
    """
    Приводит первую букву имени или фамилии к заглавной,
    остальные — к строчным.
    """
    return name.capitalize()


def fix_lines(lines: List[str]) -> List[str]:
    """
    Исправляет регистр значений в строках, соответствующих
    шаблону 'Имя: ...' или 'Фамилия: ...'.
    Использует регулярные выражения для надёжного сопоставления.
    """
    fixed_lines = []
    pattern = re.compile(r"^(Имя|Фамилия):\s*(.+)$")
    for line in lines:
        stripped = line.rstrip('\n')
        match = pattern.match(stripped)
        if match:
            key, value = match.groups()
            corrected = f"{key}: {capitalize_name(value)}\n"
            fixed_lines.append(corrected)
        else:

            fixed_lines.append(line if line.endswith('\n') else line + '\n')
    return fixed_lines


def process_file(input_file: str) -> None:
    """
    Читает входной файл, исправляет регистр имён и фамилий с помощью
    регулярных выражений,
    сохраняет результат в выходной файл с именем fixed_<input_file> и
    выводит сообщение об успешном завершении.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f_in:
            lines = f_in.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл '{input_file}' не найден.")
    except Exception as e:
        raise Exception(f"Ошибка при чтении файла: {e}")

    save_fixed_file(input_file, lines)


def save_fixed_file(input_file: str, lines: List[str]) -> None:
    output_file = "fixed_" + input_file
    fixed_lines = fix_lines(lines)
    try:
        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.writelines(fixed_lines)
    except Exception as e:
        raise Exception(f"Ошибка при записи в файл '{output_file}': {e}")
    print(f"Исправленные данные сохранены в {output_file}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Исправление регистра имён и фамилий в файле анкет."
    )
    parser.add_argument(
        "-f", "--filename",
        type=str,
        help="Имя входного файла с анкетами",
        required=True)
    return parser.parse_args()


def main() -> None:
    """
    Основная функция: обрабатывает файл.
    """
    args = parse_arguments()
    try:
        process_file(args.filename)
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
