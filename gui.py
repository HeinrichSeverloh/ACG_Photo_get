"""简易 PyQt6 GUI for ACG_Photo_get

功能概览
- 直接在窗口中配置脚本的主要参数（目标数量、并发、标签、R18、分辨率过滤等）
- 点击 *开始下载* 后在下方日志框实时显示 `logging` 输出
- 下载过程在后台线程运行，避免阻塞 GUI

使用方法
```bash
python gui.py
```
"""

import sys
import os
import logging
from pathlib import Path

# Ensure the project root is in sys.path when running this file directly
sys.path.append(os.path.abspath('.'))

import main

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
)

class QtLogHandler(QtCore.QObject, logging.Handler):
    """Logging handler that emits log records to a QTextEdit via a Qt signal.
    Uses Qt's thread‑safe signal/slot mechanism so logs from background threads
    appear correctly in the GUI.
    """
    log_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        logging.Handler.__init__(self)
        self.log_signal.connect(parent.append_log)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)

class Worker(QtCore.QThread):
    """Runs ``main.main`` in a separate thread and emits a finished signal.
    The ``result`` attribute holds the exit code returned by ``main.main``.
    """
    finished = QtCore.pyqtSignal(int)

    def run(self):
        try:
            result = main.main()
        except Exception:
            logging.exception('Exception in worker thread')
            result = 1
        self.finished.emit(result)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ACG Photo Downloader')
        self.resize(720, 560)
        central = QWidget()
        self.setCentralWidget(central)

        # ---------- Layout ----------
        main_layout = QVBoxLayout(central)
        grid = QGridLayout()
        main_layout.addLayout(grid)

        # Row 0: target count, workers, R18, filter, API source
        grid.addWidget(QLabel('目标数量:'), 0, 0)
        self.target_spin = QSpinBox()
        self.target_spin.setRange(1, 10000)
        self.target_spin.setValue(main.CONFIG.get('TARGET_COUNT', 30))
        grid.addWidget(self.target_spin, 0, 1)

        grid.addWidget(QLabel('并发线程:'), 0, 2)
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 64)
        self.workers_spin.setValue(main.CONFIG.get('MAX_WORKERS', 5))
        grid.addWidget(self.workers_spin, 0, 3)

        self.r18_check = QCheckBox('R18 (explicit)')
        self.r18_check.setChecked(main.CONFIG.get('R18', False))
        grid.addWidget(self.r18_check, 0, 4)

        self.filter_check = QCheckBox('分辨率过滤')
        self.filter_check.setChecked(main.CONFIG.get('FILTER_RESOLUTION', False))
        grid.addWidget(self.filter_check, 0, 5)

        grid.addWidget(QLabel('API 源:'), 0, 6)
        self.api_combo = QComboBox()
        self.api_combo.addItems(['nekos', 'lolicon'])
        api_idx = 0 if main.CONFIG.get('API_SOURCE', 'nekos') == 'nekos' else 1
        self.api_combo.setCurrentIndex(api_idx)
        grid.addWidget(self.api_combo, 0, 7)

        # Row 1: save path + browse button
        grid.addWidget(QLabel('保存路径:'), 1, 0)
        self.save_path_edit = QLineEdit(str(main.CONFIG.get('SAVE_DIR', '')))
        self.save_path_edit.setReadOnly(True)
        grid.addWidget(self.save_path_edit, 1, 1, 1, 4)
        browse_btn = QPushButton('浏览...')
        browse_btn.clicked.connect(self.select_save_path)
        grid.addWidget(browse_btn, 1, 5)

        # Row 2: min width / min height
        grid.addWidget(QLabel('最小宽度:'), 2, 0)
        self.min_w_spin = QSpinBox()
        self.min_w_spin.setRange(1, 10000)
        self.min_w_spin.setValue(main.CONFIG.get('MIN_WIDTH', 1920))
        grid.addWidget(self.min_w_spin, 2, 1)
        grid.addWidget(QLabel('最小高度:'), 2, 2)
        self.min_h_spin = QSpinBox()
        self.min_h_spin.setRange(1, 10000)
        self.min_h_spin.setValue(main.CONFIG.get('MIN_HEIGHT', 1080))
        grid.addWidget(self.min_h_spin, 2, 3)

        # Row 3: start button (right aligned)
        self.start_btn = QPushButton('开始下载')
        self.start_btn.clicked.connect(self.start_download)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.start_btn)
        main_layout.addLayout(btn_layout)

        # Log output area
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        main_layout.addWidget(self.log_edit, 1)

        # Configure logging to send messages to the QTextEdit
        logger = logging.getLogger()
        for h in list(logger.handlers):
            if isinstance(h, logging.StreamHandler):
                logger.removeHandler(h)
        qt_handler = QtLogHandler(parent=self)
        logger.addHandler(qt_handler)
        logger.setLevel(logging.INFO)

        self.worker = None

    def append_log(self, msg: str):
        """Slot invoked from QtLogHandler to append a line to the log widget."""
        self.log_edit.append(msg)
        self.log_edit.verticalScrollBar().setValue(self.log_edit.verticalScrollBar().maximum())

    def select_save_path(self):
        directory = QFileDialog.getExistingDirectory(self, '选择保存目录', self.save_path_edit.text() or str(Path.home()))
        if directory:
            self.save_path_edit.setText(directory)
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                logging.warning(f'创建保存目录失败: {e}')

    def apply_gui_config(self):
        main.CONFIG['TARGET_COUNT'] = self.target_spin.value()
        main.CONFIG['MAX_WORKERS'] = self.workers_spin.value()
        main.CONFIG['R18'] = self.r18_check.isChecked()
        main.CONFIG['FILTER_RESOLUTION'] = self.filter_check.isChecked()
        main.CONFIG['MIN_WIDTH'] = self.min_w_spin.value()
        main.CONFIG['MIN_HEIGHT'] = self.min_h_spin.value()
        main.CONFIG['SAVE_DIR'] = self.save_path_edit.text()
        main.CONFIG['API_SOURCE'] = self.api_combo.currentText()

    def start_download(self):
        self.start_btn.setEnabled(False)
        self.apply_gui_config()
        self.log_edit.clear()
        self.worker = Worker()
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, exit_code: int):
        if exit_code == 0:
            QMessageBox.information(self, '完成', f'下载完成，成功数量: {main.CONFIG.get("TARGET_COUNT", 0)}')
        else:
            QMessageBox.warning(self, '未完成', f'未达到目标，已下载 {main.CONFIG.get("TARGET_COUNT", 0)} 张')
        self.start_btn.setEnabled(True)
        self.worker = None

def main_gui():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main_gui()
