import os
import pandas as pd
import librosa
from typing import Optional

class AudioProcessor:
    """
    Класс для работы с DataFrame, содержащим аудиофайлы:
    загрузка, обработка (вычисление длительности), сортировка и фильтрация.
    """

    def __init__(self, csv_path: str) -> None:
        self.csv_full_path = os.path.abspath(csv_path)
        self.csv_dir = os.path.dirname(self.csv_full_path)

        if not os.path.exists(self.csv_full_path):
            raise FileNotFoundError(f"Файл аннотации не найден: {self.csv_full_path}")

        try:
            self.df: pd.DataFrame = pd.read_csv(
                self.csv_full_path, encoding="utf-8-sig"
            )
            print(f"Файл аннотации загружен: {csv_path}")
        except Exception as e:
            raise IOError(f"Ошибка при чтении CSV файла: {e}")

    def rename_columns(self) -> None:
        """Переименовывает столбцы 'Абсолютный путь' и 'Относительный путь'."""
        new_names = {
            "Абсолютный путь": "absolute_path",
            "Относительный путь": "relative_path",
        }
        actual_columns = {
            old: new for old, new in new_names.items() if old in self.df.columns
        }
        if actual_columns:
            self.df.rename(columns=actual_columns, inplace=True)
            print("   -> Колонки переименованы.")

    def _resolve_path(self, row: pd.Series) -> Optional[str]:
        """Определяет реальный путь к файлу: сначала абсолютный, потом относительный."""
        abs_p = row.get("absolute_path")
        if abs_p and os.path.exists(str(abs_p)):
            return str(abs_p)

        rel_p = row.get("relative_path")
        if rel_p:
            clean_rel = str(rel_p).replace("\\", "/").lstrip("./")
            candidate = os.path.join(self.csv_dir, clean_rel)
            if os.path.exists(candidate):
                return candidate
        return None

    @staticmethod
    def _calculate_duration(audio_path: str) -> float:
        """Вычисление длительности аудиофайла с помощью librosa."""
        try:
            duration = librosa.get_duration(path=audio_path)
            return duration
        except Exception:
            return -1.0

    def add_duration_column(self) -> None:
        """Добавление новой колонки 'duration_sec' (длительность аудиофайла)."""
        self.df["full_path"] = self.df.apply(self._resolve_path, axis=1)

        def get_duration(path):
            if path and os.path.exists(path):
                return self._calculate_duration(path)
            return -1.0

        self.df["duration_sec"] = self.df["full_path"].apply(get_duration)
        self.df.drop(columns=["full_path"], inplace=True)
        errors_count = len(self.df[self.df["duration_sec"] == -1.0])
        print(
            f"   -> Колонка 'duration_sec' добавлена. Обнаружено {errors_count} ошибок при чтении аудио."
        )

    def sort_by_column(
        self, column: str = "duration_sec", ascending: bool = True
    ) -> pd.DataFrame:
        """Реализация функции сортировки по заданной колонке."""
        if column not in self.df.columns:
            raise KeyError(f"Колонка {column} отсутствует.")

        return self.df.sort_values(by=column, ascending=ascending, inplace=False)

    def filter_by_value(
        self, column: str = "duration_sec", min_value: float = 10.0
    ) -> pd.DataFrame:
        """Реализация функции фильтрации: оставить только файлы с длительностью больше min_value."""
        if column not in self.df.columns:
            raise KeyError(f"Колонка {column} отсутствует.")

        filtered_df = self.df[self.df[column] > min_value].copy()
        print(
            f"   -> DataFrame отфильтрован: {len(filtered_df)} файлов, где {column} > {min_value}."
        )
        return filtered_df

    def save_csv(self, output_path: str) -> None:
        """Сохранение итогового DataFrame в CSV файл."""
        self.df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"   -> Файл аннотации сохранен: {output_path}")
