import os
import io
import json
import hashlib
import struct
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QMessageBox,
    QSplitter, QLabel, QMenu, QDialog, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QSizePolicy,
    QSlider, QStyle, QComboBox, QDialogButtonBox, QFormLayout, QStyleFactory
)
from PyQt6.QtCore import Qt, QMimeData, QByteArray, QSize, QTranslator, QLibraryInfo, QLocale, QBuffer, QIODevice
from PyQt6.QtGui import QPixmap, QImage, QDrag, QAction, QIcon, QFont, QColor, QPalette
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
import sys

def split_by_magic(data: bytes, magic: bytes) -> list[bytes]:
    result = []
    start = 0
    while True:
        idx = data.find(magic, start)
        if idx == -1:
            result.append(data[start:])
            break
        result.append(data[start:idx])
        start = idx + len(magic)
    return result

# Конфигурационные файлы
SIGNATURES_FILE = "signatures.json"
LANG_FILE = "lang.json"
CONFIG_FILE = "config.json"

# Стандартные сигнатуры файлов (если файл не существует)
DEFAULT_SIGNATURES = {
    "signatures": [
        {"magic": "89504E47", "extension": ".png", "description": "PNG Image"},
        {"magic": "FFD8FF", "extension": ".jpg", "description": "JPEG Image"},
        {"magic": "4F676753", "extension": ".ogg", "description": "Ogg Vorbis Audio"},
        {"magic": "52494646", "extension": ".wav", "description": "WAV Audio"},
        {"magic": "494433", "extension": ".mp3", "description": "MP3 Audio"},
        {"magic": "664C6143", "extension": ".flac", "description": "FLAC Audio"},
        {"magic": "1A45DFA3", "extension": ".mkv", "description": "Matroska Video"},
        {"magic": "0000002066747970", "extension": ".mp4", "description": "MP4 Video"},
        {"magic": "25504446", "extension": ".pdf", "description": "PDF Document"},
        {"magic": "7B5C727466", "extension": ".rtf", "description": "Rich Text Format"},
        {"magic": "504B0304", "extension": ".zip", "description": "ZIP Archive"},
        {"magic": "7F454C46", "extension": ".elf", "description": "ELF Executable"},
        {"magic": "4D5A", "extension": ".exe", "description": "Windows Executable"},
        {"magic": "2321", "extension": ".sh", "description": "Shell Script"},
        {"magic": "47494638", "extension": ".gif", "description": "GIF Image"},
        {"magic": "52617221", "extension": ".rar", "description": "RAR Archive"},
        {"magic": "1F8B08", "extension": ".gz", "description": "GZIP Archive"}
    ]
}

# Стандартные языковые настройки
DEFAULT_LANGUAGES = {
    "languages": {
        "en": {
            "app_title": "Ren'Py RPA Archiver",
            "file_menu": "File",
            "new_archive": "New Archive",
            "open_archive": "Open Archive",
            "save": "Save",
            "save_as": "Save As",
            "add_files": "Add Files",
            "exit": "Exit",
            "edit_menu": "Edit",
            "extract_selected": "Extract Selected",
            "extract_all": "Extract All",
            "delete_selected": "Delete Selected",
            "view_menu": "View",
            "info": "File Info",
            "settings": "Settings",
            "about": "About",
            "tools": "Tools",
            "info_title": "File Information",
            "preview_title": "Preview",
            "select_file": "Select a file to preview",
            "ready": "Ready",
            "archive_loaded": "Archive loaded: {} files",
            "file_copied": "File copied to clipboard",
            "file_replaced": "File replaced: {}",
            "files_added": "Added {} files to archive",
            "files_deleted": "Deleted {} files",
            "files_extracted": "Extracted {} files to {}",
            "all_files_extracted": "All files extracted to {}",
            "archive_saved": "Archive saved: {}",
            "new_archive_created": "New archive created",
            "unsaved_changes": "You have unsaved changes. Close anyway?",
            "confirm_delete": "Are you sure you want to delete {} file(s)?",
            "size_warning": "New file size is {} bytes {} than original. Continue?",
            "language": "Language",
            "icon_style": "Icon Style",
            "about_title": "About Ren'Py RPA Archiver",
            "about_text": "This is a powerful tool for working with Ren'Py RPA archives.\n\nVersion: 1.0\nDeveloped by Бюро переводов 'Феникс & Ко'",
            "play": "Play",
            "pause": "Pause",
            "stop": "Stop"
        },
        "ru": {
            "app_title": "Ren'Py RPA Archiver",
            "file_menu": "Файл",
            "new_archive": "Новый архив",
            "open_archive": "Открыть архив",
            "save": "Сохранить",
            "save_as": "Сохранить как",
            "add_files": "Добавить файлы",
            "exit": "Выход",
            "edit_menu": "Правка",
            "extract_selected": "Извлечь выбранное",
            "extract_all": "Извлечь всё",
            "delete_selected": "Удалить выбранное",
            "view_menu": "Вид",
            "info": "Информация о файле",
            "settings": "Настройки",
            "about": "О программе",
            "tools": "Инструменты",
            "info_title": "Информация о файле",
            "preview_title": "Предпросмотр",
            "select_file": "Выберите файл для предпросмотра",
            "ready": "Готов",
            "archive_loaded": "Архив загружен: {} файлов",
            "file_copied": "Файл скопирован в буфер обмена",
            "file_replaced": "Файл перезаписан: {}",
            "files_added": "Добавлено {} файлов в архив",
            "files_deleted": "Удалено {} файлов",
            "files_extracted": "Извлечено {} файлов в {}",
            "all_files_extracted": "Все файлы извлечены в {}",
            "archive_saved": "Архив сохранён: {}",
            "new_archive_created": "Создан новый архив",
            "unsaved_changes": "У вас есть несохраненные изменения. Закрыть программу?",
            "confirm_delete": "Вы уверены, что хотите удалить {} файл(ов)?",
            "size_warning": "Новый размер файла {} байт {} чем оригинал. Продолжить?",
            "language": "Язык",
            "icon_style": "Стиль иконок",
            "about_title": "О программе Ren'Py RPA Archiver",
            "about_text": "Это мощный инструмент для работы с архивами Ren'Py RPA.\n\nВерсия: 1.0\nРазработано командой Бюро переводов 'Феникс & Ко'",
            "play": "Воспроизвести",
            "pause": "Пауза",
            "stop": "Стоп"
        },
        "uk": {
            "app_title": "Ren'Py RPA Archiver",
            "file_menu": "Файл",
            "new_archive": "Новий архів",
            "open_archive": "Відкрити архів",
            "save": "Зберегти",
            "save_as": "Зберегти як",
            "add_files": "Додати файли",
            "exit": "Вихід",
            "edit_menu": "Правка",
            "extract_selected": "Видобути вибране",
            "extract_all": "Видобути все",
            "delete_selected": "Видалити вибране",
            "view_menu": "Вигляд",
            "info": "Інформація про файл",
            "settings": "Налаштування",
            "about": "Про програму",
            "tools": "Інструменти",
            "info_title": "Інформація про файл",
            "preview_title": "Попередній перегляд",
            "select_file": "Виберіть файл для попереднього перегляду",
            "ready": "Готово",
            "archive_loaded": "Архів завантажено: {} файлів",
            "file_copied": "Файл скопійовано в буфер обміну",
            "file_replaced": "Файл перезаписано: {}",
            "files_added": "Додано {} файлів до архіву",
            "files_deleted": "Видалено {} файлів",
            "files_extracted": "Видобуто {} файлів в {}",
            "all_files_extracted": "Усі файли видобуто в {}",
            "archive_saved": "Архів збережено: {}",
            "new_archive_created": "Створено новий архів",
            "unsaved_changes": "У вас є незбережені зміни. Закрити програму?",
            "confirm_delete": "Ви впевнені, що хочете видалити {} файл(ів)?",
            "size_warning": "Новий розмір файлу {} байт {} ніж оригінал. Продовжити?",
            "language": "Мова",
            "icon_style": "Стиль іконок",
            "about_title": "Про програму Ren'Py RPA Archiver",
            "about_text": "Це потужний інструмент для роботи з архівами Ren'Py RPA.\n\nВерсія: 1.0\nРозроблено командою Бюро переводов 'Феникс & Ко'",
            "play": "Відтворити",
            "pause": "Пауза",
            "stop": "Стоп"
        },
        "ja": {
            "app_title": "Ren'Py RPA 解凍ツール",
            "file_menu": "ファイル",
            "new_archive": "新規アーカイブ",
            "open_archive": "アーカイブを開く",
            "save": "保存",
            "save_as": "名前を付けて保存",
            "add_files": "ファイルを追加",
            "exit": "終了",
            "edit_menu": "編集",
            "extract_selected": "選択したものを抽出",
            "extract_all": "すべて抽出",
            "delete_selected": "選択したものを削除",
            "view_menu": "表示",
            "info": "ファイル情報",
            "settings": "設定",
            "about": "バージョン情報",
            "tools": "ツール",
            "info_title": "ファイル情報",
            "preview_title": "プレビュー",
            "select_file": "プレビューするファイルを選択",
            "ready": "準備完了",
            "archive_loaded": "アーカイブを読み込み: {} ファイル",
            "file_copied": "ファイルをクリップボードにコピーしました",
            "file_replaced": "ファイルを置換しました: {}",
            "files_added": "{} ファイルをアーカイブに追加しました",
            "files_deleted": "{} ファイルを削除しました",
            "files_extracted": "{} ファイルを {} に抽出しました",
            "all_files_extracted": "すべてのファイルを {} に抽出しました",
            "archive_saved": "アーカイブを保存しました: {}",
            "new_archive_created": "新しいアーカイブを作成しました",
            "unsaved_changes": "未保存の変更があります。終了しますか？",
            "confirm_delete": "{} ファイルを削除してもよろしいですか？",
            "size_warning": "新しいファイルサイズは {} バイトで、元のファイルより {} です。続行しますか？",
            "language": "言語",
            "icon_style": "アイコンスタイル",
            "about_title": "Ren'Py RPA 解凍ツール について",
            "about_text": "Ren'Py RPA アーカイブを操作するための強力なツールです。\n\nバージョン: 1.0\nБюро переводов 「Феникс & Ко」 チーム開発",
            "play": "再生",
            "pause": "一時停止",
            "stop": "停止"
        }
    }
}

# Стандартная конфигурация
DEFAULT_CONFIG = {
    "language": "en",
    "icon_style": "Fusion"
}

def load_json_file(filename, default_data):
    """Загружает данные из JSON файла или создает новый со стандартными данными"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)
            return default_data
    except Exception as e:
        print(f"[ERROR] Failed to load {filename}: {str(e)}")
        return default_data

def save_json_file(filename, data):
    """Сохраняет данные в JSON файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save {filename}: {str(e)}")
        return False

# Загрузка сигнатур и языков
signatures_data = load_json_file(SIGNATURES_FILE, DEFAULT_SIGNATURES)
lang_data = load_json_file(LANG_FILE, DEFAULT_LANGUAGES)
config_data = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)

def guess_extension(blob: bytes) -> str:
    """Определяет расширение файла на основе его сигнатуры"""
    for sig in signatures_data["signatures"]:
        magic_bytes = bytes.fromhex(sig["magic"])
        if blob.startswith(magic_bytes):
            return sig["extension"]
    
    # Эвристика для текстовых файлов
    if all(0x20 <= b <= 0x7E or b in (0x09, 0x0A, 0x0D) for b in blob[:1024]):
        return ".txt"
    
    return ".bin"

class MediaPlayerWidget(QWidget):
    """Виджет медиаплеера с элементами управления"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Виджет для видео
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)
        
        # Элементы управления
        self.control_layout = QHBoxLayout()
        
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.play)
        
        self.pause_button = QPushButton()
        self.pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.pause_button.clicked.connect(self.pause)
        
        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_button.clicked.connect(self.stop)
        
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 100)
        
        self.control_layout.addWidget(self.play_button)
        self.control_layout.addWidget(self.pause_button)
        self.control_layout.addWidget(self.stop_button)
        self.control_layout.addWidget(self.position_slider)
        
        self.layout.addLayout(self.control_layout)
        
        # Медиаплеер
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Связывание слайдера с позицией воспроизведения
        self.media_player.positionChanged.connect(self.update_position)
        self.position_slider.sliderMoved.connect(self.set_position)
    
    def update_position(self, position):
        """Обновляет позицию слайдера"""
        if self.media_player.duration() > 0:
            self.position_slider.setValue(int(position / self.media_player.duration() * 100))
    
    def set_position(self, position):
        """Устанавливает позицию воспроизведения"""
        if self.media_player.duration() > 0:
            self.media_player.setPosition(int(position / 100 * self.media_player.duration()))
    
    def set_source(self, blob: bytes):
        """Устанавливает медиа-контент для воспроизведения"""
        self.media_player.stop()
        
        # Создаем QBuffer вместо BytesIO
        self.buffer = QBuffer()
        self.buffer.setData(blob)
        self.buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        
        self.media_player.setSourceDevice(self.buffer)
    
    def play(self):
        """Начинает воспроизведение"""
        self.media_player.play()
    
    def pause(self):
        """Приостанавливает воспроизведение"""
        self.media_player.pause()
    
    def stop(self):
        """Останавливает воспроизведение"""
        self.media_player.stop()
    
    def clear(self):
        """Очищает плеер"""
        self.media_player.stop()
        if hasattr(self, 'buffer'):
            self.buffer.close()
        self.media_player.setSourceDevice(None)

class PreviewWidget(QWidget):
    """Виджет предпросмотра файлов"""
    def __init__(self, tr, parent=None):
        super().__init__(parent)
        self.tr = tr
        self.layout = QVBoxLayout(self)
        
        # Заголовок
        self.title_label = QLabel(tr["preview_title"])
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)
        
        # Основной виджет контента
        self.content_stack = QWidget()
        self.stack_layout = QVBoxLayout(self.content_stack)
        
        # Текстовый виджет
        self.text_widget = QLabel(tr["select_file"])
        self.text_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_widget.setWordWrap(True)
        self.stack_layout.addWidget(self.text_widget)
        
        # Виджет изображения
        self.image_widget = QLabel()
        self.image_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack_layout.addWidget(self.image_widget)
        self.image_widget.hide()
        
        # Виджет медиаплеера
        self.media_player = MediaPlayerWidget()
        self.stack_layout.addWidget(self.media_player)
        self.media_player.hide()
        
        # Виджет для бинарных файлов
        self.binary_widget = QLabel()
        self.binary_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.binary_widget.setWordWrap(True)
        self.stack_layout.addWidget(self.binary_widget)
        self.binary_widget.hide()
        
        self.layout.addWidget(self.content_stack)
    
    def clear(self):
        """Очищает предпросмотр"""
        self.text_widget.show()
        self.text_widget.setText(self.tr["select_file"])
        self.image_widget.hide()
        self.media_player.hide()
        self.media_player.clear()
        self.binary_widget.hide()
    
    def set_data(self, blob: bytes, ext: str):
        """Устанавливает данные для предпросмотра"""
        self.clear()
        
        try:
            # Изображения
            if ext in (".png", ".jpg", ".gif"):
                pixmap = QPixmap()
                pixmap.loadFromData(blob)
                if not pixmap.isNull():
                    self.image_widget.setPixmap(pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))
                    self.image_widget.show()
                    self.text_widget.hide()
                else:
                    self.text_widget.setText("Failed to load image")
            
            # Текстовые файлы
            elif ext in (".txt", ".sh", ".py", ".json", ".xml", ".html", ".csv", ".rtf"):
                text = blob.decode('utf-8', errors='replace')[:5000]
                if len(blob) > 5000:
                    text += "\n\n... [first 5000 bytes shown]"
                self.text_widget.setText(text)
            
            # Аудио и видео файлы
            elif ext in (".mp3", ".wav", ".ogg", ".flac", ".mp4", ".mkv", ".avi"):
                self.media_player.set_source(blob)
                self.media_player.show()
                self.text_widget.hide()
            
            # Бинарные файлы
            else:
                self.binary_widget.setText(
                    f"Binary file: {len(blob)} bytes\n" +
                    f"MD5: {hashlib.md5(blob).hexdigest()}"
                )
                self.binary_widget.show()
                self.text_widget.hide()
        
        except Exception as e:
            self.text_widget.setText(f"Preview error: {str(e)}")

class FileInfoDialog(QDialog):
    """Диалог с информацией о файле"""
    def __init__(self, items, tr, parent=None):
        super().__init__(parent)
        self.tr = tr
        self.setWindowTitle(tr["info_title"])
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
        self.populate_info(items)
    
    def populate_info(self, items):
        """Заполняет таблицу информацией о файле(ах)"""
        if not items:
            return
        
        # Для одного файла
        if len(items) == 1:
            item = items[0]
            blob = item.data(0, Qt.ItemDataRole.UserRole)
            ext = item.text(1)
            size = len(blob)
            
            info = {
                "File name": item.text(0),
                "Type": ext,
                "Size": f"{size} bytes ({size / 1024:.2f} KB)",
                "MD5": hashlib.md5(blob).hexdigest(),
                "SHA-1": hashlib.sha1(blob).hexdigest(),
                "First 4 bytes": str(blob[:4]) if len(blob) >= 4 else "N/A",
                "Magic number": guess_extension(blob),
            }
            
            # Информация об изображениях
            if ext in (".png", ".jpg", ".bmp", ".gif"):
                img = QImage()
                img.loadFromData(blob)
                if not img.isNull():
                    info["Resolution"] = f"{img.width()}x{img.height()}"
                    info["Color depth"] = f"{img.depth()} bits"
            
            # Информация о исполняемых файлах
            elif ext == ".exe":
                if size > 64:
                    try:
                        pe_offset = struct.unpack('<I', blob[0x3C:0x40])[0]
                        if pe_offset < size - 64:
                            machine = struct.unpack('<H', blob[pe_offset+4:pe_offset+6])[0]
                            arch = "x64" if machine == 0x8664 else "x86"
                            info["Architecture"] = arch
                    except:
                        pass
            
            self.table.setRowCount(len(info))
            for i, (key, value) in enumerate(info.items()):
                self.table.setItem(i, 0, QTableWidgetItem(key))
                self.table.setItem(i, 1, QTableWidgetItem(str(value)))
        
        # Для нескольких файлов
        else:
            total_size = 0
            exts = {}
            for item in items:
                blob = item.data(0, Qt.ItemDataRole.UserRole)
                ext = item.text(1)
                total_size += len(blob)
                exts[ext] = exts.get(ext, 0) + 1
            
            info = {
                "Number of files": str(len(items)),
                "Total size": f"{total_size} bytes ({total_size / (1024*1024):.2f} MB)",
                "File types": ", ".join([f"{k} ({v})" for k, v in exts.items()])
            }
            
            self.table.setRowCount(len(info))
            for i, (key, value) in enumerate(info.items()):
                self.table.setItem(i, 0, QTableWidgetItem(key))
                self.table.setItem(i, 1, QTableWidgetItem(value))

class SettingsDialog(QDialog):
    """Диалог настроек программы"""
    def __init__(self, tr, current_lang, current_style, parent=None):
        super().__init__(parent)
        self.tr = tr
        self.setWindowTitle(tr["settings"])
        self.setGeometry(300, 300, 400, 200)
        
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Выбор языка
        self.lang_combo = QComboBox()
        for lang_code, lang_name in [("en", "English"), ("ru", "Русский"), ("uk", "Українська"), ("ja", "日本語")]:
            self.lang_combo.addItem(lang_name, lang_code)
        
        # Установка текущего языка
        index = self.lang_combo.findData(current_lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        
        layout.addRow(tr["language"], self.lang_combo)
        
        # Выбор стиля иконок
        self.style_combo = QComboBox()
        for style in QStyleFactory.keys():
            self.style_combo.addItem(style)
        
        # Установка текущего стиля
        index = self.style_combo.findText(current_style)
        if index >= 0:
            self.style_combo.setCurrentIndex(index)
        
        layout.addRow(tr["icon_style"], self.style_combo)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_selected_language(self):
        """Возвращает выбранный язык"""
        return self.lang_combo.currentData()
    
    def get_selected_style(self):
        """Возвращает выбранный стиль"""
        return self.style_combo.currentText()

class AboutDialog(QDialog):
    """Диалог 'О программе'"""
    def __init__(self, tr, parent=None):
        super().__init__(parent)
        self.tr = tr
        self.setWindowTitle(tr["about"])
        self.setGeometry(300, 300, 500, 300)
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Логотип
        self.logo_label = QLabel()
        if os.path.exists("bpfc.jpg"):
            pixmap = QPixmap("bpfc.jpg").scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("BPFC Logo")
        
        layout.addWidget(self.logo_label)
        
        # Информация
        info_layout = QVBoxLayout()
        
        title_label = QLabel(tr["about_title"])
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        info_layout.addWidget(title_label)
        
        text_label = QLabel(tr["about_text"])
        text_label.setWordWrap(True)
        info_layout.addWidget(text_label)
        
        # Кнопка закрытия
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        info_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(info_layout)

class RPAExtractor(QMainWindow):
    """Главное окно приложения"""
    def __init__(self):
        super().__init__()
        
        # Загрузка конфигурации
        self.config = config_data
        self.lang = lang_data["languages"][self.config["language"]]
        
        # Инициализация интерфейса
        self.init_ui()
        
        # Инициализация данных
        self.current_archive_path = ""
        self.chunks = []
        self.is_modified = False
        self.magic = bytes([
            0x4d, 0x61, 0x64, 0x65,
            0x20, 0x77, 0x69, 0x74,
            0x68, 0x20, 0x52, 0x65,
            0x6e, 0x27, 0x50, 0x79,
            0x2e
        ])
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle(self.lang["app_title"])
        self.setGeometry(100, 100, 1200, 800)
        
        # Главный виджет и компоновка
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Создание меню
        self.create_menus()
        
        # Создание панели инструментов
        self.create_toolbar()
        
        # Разделитель для дерева файлов и предпросмотра
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Виджет дерева файлов
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File", "Type", "Size"])
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemSelectionChanged.connect(self.update_preview)
        self.splitter.addWidget(self.tree)
        
        # Виджет предпросмотра
        self.preview = PreviewWidget(self.lang)
        self.splitter.addWidget(self.preview)
        self.splitter.setSizes([600, 400])
        
        # Строка состояния
        self.status_bar = self.statusBar()
        self.status_bar.showMessage(self.lang["ready"])
    
    def create_menus(self):
        """Создает меню приложения"""
        menu_bar = self.menuBar()
        
        # Меню Файл
        file_menu = menu_bar.addMenu(self.lang["file_menu"])
        
        new_action = QAction(self.lang["new_archive"], self)
        new_action.triggered.connect(self.new_archive)
        file_menu.addAction(new_action)
        
        open_action = QAction(self.lang["open_archive"], self)
        open_action.triggered.connect(self.open_archive)
        file_menu.addAction(open_action)
        
        save_action = QAction(self.lang["save"], self)
        save_action.triggered.connect(self.save_archive)
        file_menu.addAction(save_action)
        
        save_as_action = QAction(self.lang["save_as"], self)
        save_as_action.triggered.connect(self.save_archive_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        add_action = QAction(self.lang["add_files"], self)
        add_action.triggered.connect(self.add_files)
        file_menu.addAction(add_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(self.lang["exit"], self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Правка
        edit_menu = menu_bar.addMenu(self.lang["edit_menu"])
        
        extract_action = QAction(self.lang["extract_selected"], self)
        extract_action.triggered.connect(self.extract_selected)
        edit_menu.addAction(extract_action)
        
        extract_all_action = QAction(self.lang["extract_all"], self)
        extract_all_action.triggered.connect(self.extract_all)
        edit_menu.addAction(extract_all_action)
        
        delete_action = QAction(self.lang["delete_selected"], self)
        delete_action.triggered.connect(self.delete_selected)
        edit_menu.addAction(delete_action)
        
        # Меню Вид
        view_menu = menu_bar.addMenu(self.lang["view_menu"])
        
        info_action = QAction(self.lang["info"], self)
        info_action.triggered.connect(self.show_file_info)
        view_menu.addAction(info_action)
        
        # Меню Настройки
        settings_menu = menu_bar.addMenu(self.lang["settings"])
        
        settings_action = QAction(self.lang["settings"], self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)
        
        # Меню Помощь
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction(self.lang["about"], self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Создает панель инструментов"""
        toolbar = self.addToolBar(self.lang["tools"])
        toolbar.setIconSize(QSize(32, 32))
        
        # Новый архив
        new_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon), self.lang["new_archive"], self)
        new_action.triggered.connect(self.new_archive)
        toolbar.addAction(new_action)
        
        # Открыть архив
        open_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton), self.lang["open_archive"], self)
        open_action.triggered.connect(self.open_archive)
        toolbar.addAction(open_action)
        
        # Сохранить
        save_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), self.lang["save"], self)
        save_action.triggered.connect(self.save_archive)
        toolbar.addAction(save_action)
        
        # Добавить файлы
        add_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder), self.lang["add_files"], self)
        add_action.triggered.connect(self.add_files)
        toolbar.addAction(add_action)
        
        toolbar.addSeparator()
        
        # Извлечь выбранное
        extract_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown), self.lang["extract_selected"], self)
        extract_action.triggered.connect(self.extract_selected)
        toolbar.addAction(extract_action)
        
        # Извлечь всё
        extract_all_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DriveFDIcon), self.lang["extract_all"], self)
        extract_all_action.triggered.connect(self.extract_all)
        toolbar.addAction(extract_all_action)
        
        # Удалить
        delete_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon), self.lang["delete_selected"], self)
        delete_action.triggered.connect(self.delete_selected)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        # Информация
        info_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView), self.lang["info"], self)
        info_action.triggered.connect(self.show_file_info)
        toolbar.addAction(info_action)
        
        # Настройки
        settings_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView), self.lang["settings"], self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
        
        # О программе
        about_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation), self.lang["about"], self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def new_archive(self):
        """Создает новый архив"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, 
                self.lang["unsaved_changes"],
                self.lang["unsaved_changes"],
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.chunks = []
        self.current_archive_path = ""
        self.tree.clear()
        self.preview.clear()
        self.is_modified = False
        self.status_bar.showMessage(self.lang["new_archive_created"])
    
    def open_archive(self):
        """Открывает архив"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, 
                self.lang["unsaved_changes"],
                self.lang["unsaved_changes"],
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        path, _ = QFileDialog.getOpenFileName(self, self.lang["open_archive"], "", "All files (*.*)")
        if not path:
            return
        
        try:
            with open(path, 'rb') as f:
                data = f.read()
            
            self.chunks = split_by_magic(data, self.magic)
            self.current_archive_path = path
            self.tree.clear()
            self.preview.clear()
            self.is_modified = False
            
            for i, blob in enumerate(self.chunks):
                ext = guess_extension(blob)
                size = len(blob)
                size_str = f"{size} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                
                item = QTreeWidgetItem([f"chunk_{i}{ext}", ext, size_str])
                item.setData(0, Qt.ItemDataRole.UserRole, blob)
                self.tree.addTopLevelItem(item)
            
            self.status_bar.showMessage(self.lang["archive_loaded"].format(len(self.chunks)))
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open archive:\n{str(e)}")
    
    def save_archive(self):
        """Сохраняет текущий архив"""
        if not self.current_archive_path:
            self.save_archive_as()
            return
        
        self._save_archive(self.current_archive_path)
    
    def save_archive_as(self):
        """Сохраняет архив под новым именем"""
        path, _ = QFileDialog.getSaveFileName(
            self, 
            self.lang["save_as"], 
            self.current_archive_path or "new_archive.rpa", 
            "Ren'Py Archives (*.rpa);;All files (*.*)"
        )
        
        if not path:
            return
        
        self._save_archive(path)
        self.current_archive_path = path
    
    def _save_archive(self, path: str):
        """Внутренняя функция сохранения архива"""
        if not self.chunks:
            QMessageBox.warning(self, "Warning", "No data to save")
            return
        
        try:
            # Сборка данных архива
            data = self.magic.join(self.chunks)
            
            with open(path, 'wb') as f:
                f.write(data)
            
            self.is_modified = False
            self.status_bar.showMessage(self.lang["archive_saved"].format(path))
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save archive:\n{str(e)}")
    
    def update_preview(self):
        """Обновляет предпросмотр при изменении выбора"""
        selected = self.tree.selectedItems()
        if not selected:
            self.preview.clear()
            return
        
        item = selected[0]
        blob = item.data(0, Qt.ItemDataRole.UserRole)
        ext = item.text(1)
        self.preview.set_data(blob, ext)
    
    def show_context_menu(self, position):
        """Показывает контекстное меню"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        
        menu = QMenu()
        
        # Копировать
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        menu.addAction(copy_action)
        
        # Перезаписать
        overwrite_action = QAction("Replace", self)
        overwrite_action.triggered.connect(self.overwrite_file)
        menu.addAction(overwrite_action)
        
        # Извлечь
        extract_action = QAction("Extract", self)
        extract_action.triggered.connect(self.extract_selected)
        menu.addAction(extract_action)
        
        # Удалить
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Информация
        info_action = QAction("Info", self)
        info_action.triggered.connect(self.show_file_info)
        menu.addAction(info_action)
        
        menu.exec(self.tree.viewport().mapToGlobal(position))
    
    def copy_to_clipboard(self):
        """Копирует файл в буфер обмена"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        
        # Для одного файла
        if len(selected_items) == 1:
            item = selected_items[0]
            blob = item.data(0, Qt.ItemDataRole.UserRole)
            mime_data.setData("application/octet-stream", QByteArray(blob))
            clipboard.setMimeData(mime_data)
            self.status_bar.showMessage(self.lang["file_copied"])
        
        # Для нескольких файлов
        else:
            file_list = []
            for item in selected_items:
                file_list.append(f"{item.text(0)} ({len(item.data(0, Qt.ItemDataRole.UserRole))} bytes)")
            
            mime_data.setText("\n".join(file_list))
            clipboard.setMimeData(mime_data)
            self.status_bar.showMessage("File info copied")
    
    def overwrite_file(self):
        """Заменяет выбранный файл"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        
        if len(selected_items) > 1:
            QMessageBox.warning(self, "Warning", "Select only one file to replace")
            return
        
        item = selected_items[0]
        old_blob = item.data(0, Qt.ItemDataRole.UserRole)
        old_size = len(old_blob)
        
        path, _ = QFileDialog.getOpenFileName(self, "Select replacement file")
        if not path:
            return
        
        try:
            with open(path, 'rb') as f:
                new_blob = f.read()
            
            new_size = len(new_blob)
            size_diff = new_size - old_size
            
            # Предупреждение при изменении размера
            if old_size != new_size:
                diff_type = "larger" if size_diff > 0 else "smaller"
                diff_msg = self.lang["size_warning"].format(abs(size_diff), diff_type)
                
                reply = QMessageBox.question(
                    self, "Size changed", diff_msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Обновление данных
            idx = self.tree.indexOfTopLevelItem(item)
            if 0 <= idx < len(self.chunks):
                self.chunks[idx] = new_blob
                self.is_modified = True
                
                # Обновление элемента дерева
                ext = guess_extension(new_blob)
                size_str = f"{new_size} bytes" if new_size < 1024 else f"{new_size/1024:.1f} KB"
                
                item.setText(0, f"chunk_{idx}{ext}")
                item.setText(1, ext)
                item.setText(2, size_str)
                item.setData(0, Qt.ItemDataRole.UserRole, new_blob)
                
                self.status_bar.showMessage(self.lang["file_replaced"].format(path))
            
            self.update_preview()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to replace file:\n{str(e)}")
    
    def add_files(self):
        """Добавляет файлы в архив"""
        paths, _ = QFileDialog.getOpenFileNames(
            self, 
            self.lang["add_files"], 
            "", 
            "All files (*.*)"
        )
        
        if not paths:
            return
        
        try:
            for path in paths:
                with open(path, 'rb') as f:
                    blob = f.read()
                
                self.chunks.append(blob)
                ext = guess_extension(blob)
                size = len(blob)
                size_str = f"{size} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                
                filename = os.path.basename(path)
                if not filename.endswith(ext):
                    filename += ext
                
                item = QTreeWidgetItem([filename, ext, size_str])
                item.setData(0, Qt.ItemDataRole.UserRole, blob)
                self.tree.addTopLevelItem(item)
            
            self.is_modified = True
            self.status_bar.showMessage(self.lang["files_added"].format(len(paths)))
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add files:\n{str(e)}")
    
    def delete_selected(self):
        """Удаляет выбранные файлы"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Select files to delete")
            return
        
        reply = QMessageBox.question(
            self, "Confirm deletion",
            self.lang["confirm_delete"].format(len(selected_items)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Сбор индексов для удаления (в обратном порядке)
            indices_to_delete = []
            for item in selected_items:
                idx = self.tree.indexOfTopLevelItem(item)
                if idx >= 0:
                    indices_to_delete.append(idx)
            
            # Сортировка в обратном порядке для удаления с конца
            indices_to_delete.sort(reverse=True)
            
            # Удаление из данных и дерева
            for idx in indices_to_delete:
                if 0 <= idx < len(self.chunks):
                    del self.chunks[idx]
                    self.tree.takeTopLevelItem(idx)
            
            self.is_modified = True
            self.status_bar.showMessage(self.lang["files_deleted"].format(len(indices_to_delete)))
            self.preview.clear()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete files:\n{str(e)}")
    
    def extract_selected(self):
        """Извлекает выбранные файлы"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Select files to extract")
            return
        
        dir_path = QFileDialog.getExistingDirectory(self, "Select extraction folder")
        if not dir_path:
            return
        
        try:
            extracted_count = 0
            for item in selected_items:
                blob = item.data(0, Qt.ItemDataRole.UserRole)
                filename = item.text(0)
                
                # Безопасное имя файла
                safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ")
                if not safe_name:
                    safe_name = f"file_{extracted_count}"
                
                file_path = os.path.join(dir_path, safe_name)
                
                # Обработка дубликатов
                counter = 1
                base_name, ext = os.path.splitext(safe_name)
                while os.path.exists(file_path):
                    file_path = os.path.join(dir_path, f"{base_name}_{counter}{ext}")
                    counter += 1
                
                with open(file_path, 'wb') as f:
                    f.write(blob)
                
                extracted_count += 1
            
            self.status_bar.showMessage(self.lang["files_extracted"].format(extracted_count, dir_path))
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Extraction error:\n{str(e)}")
    
    def extract_all(self):
        """Извлекает все файлы"""
        if not self.chunks:
            QMessageBox.warning(self, "Warning", "No files to extract")
            return
        
        dir_path = QFileDialog.getExistingDirectory(self, "Select extraction folder")
        if not dir_path:
            return
        
        try:
            for i, blob in enumerate(self.chunks):
                # Получение имени файла
                if i < self.tree.topLevelItemCount():
                    filename = self.tree.topLevelItem(i).text(0)
                else:
                    ext = guess_extension(blob)
                    filename = f"chunk_{i}{ext}"
                
                # Безопасное имя файла
                safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ")
                if not safe_name:
                    safe_name = f"file_{i}"
                
                file_path = os.path.join(dir_path, safe_name)
                
                # Обработка дубликатов
                counter = 1
                base_name, ext = os.path.splitext(safe_name)
                while os.path.exists(file_path):
                    file_path = os.path.join(dir_path, f"{base_name}_{counter}{ext}")
                    counter += 1
                
                with open(file_path, 'wb') as f:
                    f.write(blob)
            
            self.status_bar.showMessage(self.lang["all_files_extracted"].format(dir_path))
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Extraction error:\n{str(e)}")
    
    def show_file_info(self):
        """Показывает информацию о файле"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Select files to view info")
            return
        
        info_dialog = FileInfoDialog(selected_items, self.lang, self)
        info_dialog.exec()
    
    def open_settings(self):
        """Открывает диалог настроек"""
        dialog = SettingsDialog(
            self.lang,
            self.config["language"],
            self.config["icon_style"],
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_lang = dialog.get_selected_language()
            new_style = dialog.get_selected_style()
            
            # Сохраняем настройки
            if new_lang != self.config["language"] or new_style != self.config["icon_style"]:
                self.config["language"] = new_lang
                self.config["icon_style"] = new_style
                save_json_file(CONFIG_FILE, self.config)
                
                # Перезапускаем приложение для применения изменений
                QMessageBox.information(
                    self, 
                    "Restart Required", 
                    "Application will restart to apply changes"
                )
                QApplication.exit(100)
    
    def show_about(self):
        """Показывает окно 'О программе'"""
        dialog = AboutDialog(self.lang, self)
        dialog.exec()
    
    def closeEvent(self, event):
        """Обрабатывает событие закрытия окна"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, 
                self.lang["unsaved_changes"],
                self.lang["unsaved_changes"],
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        
        event.accept()

def main():
    # Создание приложения
    app = QApplication([])
    
    # Загрузка конфигурации
    config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
    
    # Установка стиля
    app.setStyle(config["icon_style"])
    
    # Создание и запуск главного окна
    win = RPAExtractor()
    win.show()
    
    # Запуск основного цикла
    result = app.exec()
    
    # Перезапуск приложения при необходимости
    if result == 100:
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    return result

if __name__ == '__main__':
    sys.exit(main())