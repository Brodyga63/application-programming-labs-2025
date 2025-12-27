# audio_iterator.py

import os
import pandas as pd
from typing import Optional, List, Dict
import math


class AudioDatasetIterator:
    """
    Класс-итератор, который читает пути и метаданные (длительность)
    из предоставленного CSV-файла аннотации.
    """

    def __init__(self, annotation_path: str):
        self.annotation_path = annotation_path
        self.dataset: List[Dict] = []
        self.index = -1
        self._load_data()

    def _format_duration(self, seconds: float) -> str:
        """Преобразует длительность из секунд в формат 'MM:SS'."""
        if seconds < 0 or not math.isfinite(seconds):
            return "---"
        total_seconds = int(round(seconds))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _load_data(self):
        """Читает CSV, определяет пути и собирает список данных."""
        if not os.path.exists(self.annotation_path):
            raise FileNotFoundError(f"Файл аннотации не найден: {self.annotation_path}")

        try:
            df = pd.read_csv(self.annotation_path, encoding="utf-8-sig")

            path_col = (
                "absolute_path" if "absolute_path" in df.columns else df.columns[0]
            )
            duration_col = "duration_sec" if "duration_sec" in df.columns else None

            for _, row in df.iterrows():
                file_path = str(row[path_col])

                if file_path and os.path.exists(file_path):
                    duration_sec = -1.0
                    if (
                        duration_col
                        and duration_col in row
                        and pd.notna(row[duration_col])
                    ):
                        try:
                            duration_sec = float(row[duration_col])
                        except (ValueError, TypeError):
                            pass

                    duration_str = self._format_duration(duration_sec)
                    name = os.path.basename(file_path)

                    self.dataset.append(
                        {
                            "path": file_path,
                            "name": name,
                            "duration": duration_str,
                        }
                    )

            if not self.dataset:
                raise ValueError(
                    f"В аннотации {self.annotation_path} не найдено ни одного существующего аудиофайла."
                )

        except Exception as e:
            raise Exception(f"Ошибка при обработке аннотации: {e}")

    def next_item(self) -> Optional[Dict]:
        """Возвращает следующий элемент датасета по циклу."""
        if not self.dataset:
            return None
        self.index = (self.index + 1) % len(self.dataset)
        return self.dataset[self.index]

    def prev_item(self) -> Optional[Dict]:
        """Возвращает ПРЕДЫДУЩИЙ элемент датасета по циклу."""
        if not self.dataset:
            return None
        # Циклическое движение назад: (текущий индекс - 1) % длина
        self.index = (self.index - 1) % len(self.dataset)
        return self.dataset[self.index]

    def get_current_path(self) -> Optional[str]:
        """Возвращает путь к текущему аудиофайлу."""
        if 0 <= self.index < len(self.dataset):
            return self.dataset[self.index]["path"]
        return None
