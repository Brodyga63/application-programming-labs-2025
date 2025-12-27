# main_window.py

import sys
import os
import argparse
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from typing import Optional, Dict

# Импорт класса итератора
try:
    from audio_iterator import AudioDatasetIterator
except ImportError:
    print(
        "Ошибка: Не удалось импортировать AudioDatasetIterator. Убедитесь, что файл audio_iterator.py существует."
    )
    sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """Парсит аргументы командной строки, задавая путь к файлу аннотации."""
    parser = argparse.ArgumentParser(
        description="GUI приложение для просмотра аудио датасета."
    )
    parser.add_argument(
        "--input-csv",
        type=str,
        default="annotation.csv",
        help="Путь к входному CSV файлу аннотации. По умолчанию: annotation.csv",
    )
    return parser.parse_args()


def set_dark_style(app: QApplication):
    """Применяет к приложению простой темный стиль через Qt Style Sheets."""
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #2e2e2e; 
            color: #ffffff;
            font-family: Arial, sans-serif;
        }
        
        QLabel#TrackInfo, QLabel#DurationInfo {
            font-size: 16pt;
            font-weight: bold;
            color: #4CAF50; /* Ярко-зеленый */
        }
        
        QLabel#FilePath {
            font-size: 10pt;
            color: #aaaaaa;
            margin-bottom: 10px;
        }

        QPushButton {
            background-color: #555555;
            border: 2px solid #666666;
            color: #ffffff;
            padding: 10px 15px;
            font-size: 14pt;
            border-radius: 8px;
            min-height: 40px;
        }

        QPushButton:hover {
            background-color: #666666;
            border-color: #ffffff;
        }

        QPushButton:pressed {
            background-color: #444444;
        }
        
        QPushButton:disabled {
            background-color: #3e3e3e;
            color: #888888;
            border-color: #333333;
        }
    """)


class AudioPlayerWindow(QMainWindow):
    """
    Главное окно приложения: просмотрщик аудиодатасета.
    """

    def __init__(self, default_csv_path: str):
        super().__init__()
        self.setWindowTitle("Просмотрщик Аудио Датасета (ЛР №5) - Улучшенный вид")
        self.setGeometry(100, 100, 600, 300)

        self.media_player = QMediaPlayer()
        self.is_playing = False
        self.iterator: Optional[AudioDatasetIterator] = None

        self._setup_ui()
        self._connect_signals()

        self.init_iterator_with_default(default_csv_path)

    def _setup_ui(self):
        """Настройка виджетов и компоновки."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)

        # 1. Выбор файла аннотации
        self.path_label = QLabel("Аннотация: (Не выбрана)")
        self.path_label.setObjectName("FilePath")
        self.path_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.path_label)

        self.select_button = QPushButton("🗂️ Выбрать Файл Аннотации")
        main_layout.addWidget(self.select_button)

        main_layout.addSpacing(25)

        # 2. Информация о треке
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setAlignment(Qt.AlignCenter)

        self.name_label = QLabel("--- Название Композиции ---")
        self.name_label.setObjectName("TrackInfo")
        self.name_label.setAlignment(Qt.AlignCenter)

        self.duration_label = QLabel("Длительность: ---")
        self.duration_label.setObjectName("DurationInfo")
        self.duration_label.setAlignment(Qt.AlignCenter)

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.duration_label)
        main_layout.addWidget(info_widget)

        main_layout.addSpacing(25)

        # 3. Кнопки управления (Добавлена кнопка "Предыдущий")
        control_layout = QHBoxLayout()
        control_layout.setAlignment(Qt.AlignCenter)

        self.prev_button = QPushButton("⏪ Предыдущий")  # <-- НОВАЯ КНОПКА
        self.play_stop_button = QPushButton("▶️ Проиграть")
        self.next_button = QPushButton("⏩ Следующий Файл")

        self.prev_button.setEnabled(False)  # Изначально отключена
        self.play_stop_button.setEnabled(False)
        self.next_button.setEnabled(False)

        control_layout.addWidget(self.prev_button)  # Добавлена в layout
        control_layout.addWidget(self.play_stop_button)
        control_layout.addWidget(self.next_button)
        main_layout.addLayout(control_layout)

    def _connect_signals(self):
        """Связывание сигналов и слотов."""
        self.select_button.clicked.connect(self.select_annotation_file)
        self.prev_button.clicked.connect(self.load_prev_audio)  # <-- НОВОЕ ПОДКЛЮЧЕНИЕ
        self.next_button.clicked.connect(self.load_next_audio)
        self.play_stop_button.clicked.connect(self.toggle_playback)
        self.media_player.stateChanged.connect(self.media_state_changed)

    def init_iterator_with_default(self, default_path: str):
        """Попытка загрузить итератор при старте."""
        if os.path.exists(default_path):
            self.init_iterator(default_path)

    def init_iterator(self, path: str):
        """Инициализирует итератор и обновляет GUI."""
        try:
            self.iterator = AudioDatasetIterator(path)
            self.path_label.setText(f"Аннотация: {os.path.basename(path)}")
            self.next_button.setEnabled(True)
            self.prev_button.setEnabled(True)  # <-- Активируем кнопку Предыдущий

            # При инициализации загружаем первый трек, вызывая next_item()
            first_item = self.iterator.next_item()
            self._load_item(first_item)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка Инициализации",
                f"Не удалось инициализировать итератор:\n{e}",
            )
            self.path_label.setText("Аннотация: ОШИБКА")
            self.next_button.setEnabled(False)
            self.prev_button.setEnabled(False)

    def select_annotation_file(self):
        """Открывает диалог для выбора файла аннотации."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать файл аннотации", "", "CSV Files (*.csv)"
        )
        if file_path:
            self.init_iterator(file_path)

    def stop_current_audio(self):
        """Останавливает текущее воспроизведение."""
        if self.is_playing:
            self.media_player.stop()

    def _load_item(self, item: Optional[Dict]):
        """Универсальная функция для загрузки медиаконтента и обновления UI."""
        if item:
            file_path = item["path"]

            if not os.path.exists(file_path):
                self.update_info(item["name"], item["duration"], "Файл не найден!")
                self.play_stop_button.setEnabled(False)
                return

            content = QMediaContent(QUrl.fromLocalFile(file_path))
            self.media_player.setMedia(content)
            self.update_info(item["name"], item["duration"])
            self.play_stop_button.setEnabled(True)
        else:
            self.update_info("Конец датасета", "---")
            self.play_stop_button.setEnabled(False)

    def load_next_audio(self):
        """Останавливает предыдущий и загружает следующий."""
        self.stop_current_audio()
        if not self.iterator:
            return

        next_item = self.iterator.next_item()
        self._load_item(next_item)

    def load_prev_audio(self):
        """Останавливает предыдущий и загружает предыдущий трек."""
        self.stop_current_audio()
        if not self.iterator:
            return

        prev_item = self.iterator.prev_item()  # <-- Используем новый метод итератора
        self._load_item(prev_item)

    def update_info(self, name: str, duration: str, status: str = ""):
        """Обновляет метки информации о композиции."""
        self.name_label.setText(name)
        self.duration_label.setText(f"Длительность: {duration}")
        if status:
            self.name_label.setText(f"{name} ({status})")

    def toggle_playback(self):
        """Переключает состояние воспроизведения (Проиграть/Пауза)."""
        if self.is_playing:
            self.media_player.pause()
        else:
            self.media_player.play()

    def media_state_changed(self, state):
        """Обрабатывает изменения состояния медиаплеера для обновления кнопки."""
        if state == QMediaPlayer.PlayingState:
            self.is_playing = True
            self.play_stop_button.setText("⏸️ Пауза")
        elif state == QMediaPlayer.PausedState:
            self.is_playing = False
            self.play_stop_button.setText("▶️ Проиграть")
        elif state == QMediaPlayer.StoppedState:
            self.is_playing = False
            self.play_stop_button.setText("▶️ Проиграть")

    def closeEvent(self, event):
        """Останавливает плеер при закрытии окна."""
        self.media_player.stop()
        event.accept()


# --- Основной блок ---

if __name__ == "__main__":
    args = parse_arguments()

    app = QApplication(sys.argv)
    set_dark_style(app)

    window = AudioPlayerWindow(args.input_csv)
    window.show()
    sys.exit(app.exec_())
