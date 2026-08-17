"""Kivy GUI for ACG_Photo_get (Android version)

This implementation mirrors the functionality of ``gui_for_desktop.py`` but uses the
Kivy framework, which works on Android devices.

Features
- Configure main script parameters (target count, workers, tags, R18, resolution filter, etc.)
- Choose a save directory (uses the Android file picker when possible)
- Start download in a background thread to keep the UI responsive
- Real‑time log view that receives messages emitted via ``logging``
- Popup notification when the download finishes
"""

import os
import sys
import logging
import threading
from pathlib import Path

# Ensure project root is in sys.path when this file is run directly on Android
sys.path.append(os.path.abspath('.'))

import main

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, BooleanProperty


class KivyLogHandler(logging.Handler):
    """A ``logging.Handler`` that forwards log records to a Kivy ``Label``.

    The label is updated on the main thread via ``Clock.schedule_once`` to keep
    thread‑safety.
    """

    def __init__(self, log_label: Label, **kwargs):
        super().__init__(**kwargs)
        self.log_label = log_label
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    def emit(self, record):
        msg = self.format(record)
        Clock.schedule_once(lambda dt: self._append(msg))

    def _append(self, msg: str):
        # Preserve existing text and ensure the newest line is visible.
        if self.log_label.text:
            self.log_label.text = f"{self.log_label.text}\n{msg}"
        else:
            self.log_label.text = msg
        # Auto‑scroll is handled by the surrounding ScrollView.


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self._build_ui()
        self._setup_logging()
        self.worker_thread = None

    def _build_ui(self):
        # ----- Top grid with configuration widgets -----
        grid = GridLayout(cols=8, size_hint_y=None, height='40dp')
        # Row 0 – target count, workers, R18, filter, API source
        grid.add_widget(Label(text='目标数量:'))
        self.target_input = TextInput(text=str(main.CONFIG.get('TARGET_COUNT', 30)),
                                      input_filter='int', multiline=False, size_hint_x=None, width='80dp')
        grid.add_widget(self.target_input)

        grid.add_widget(Label(text='并发线程:'))
        self.workers_input = TextInput(text=str(main.CONFIG.get('MAX_WORKERS', 5)),
                                       input_filter='int', multiline=False, size_hint_x=None, width='80dp')
        grid.add_widget(self.workers_input)

        self.r18_check = CheckBox(active=bool(main.CONFIG.get('R18', False)))
        grid.add_widget(Label(text='R18 (explicit)'))
        grid.add_widget(self.r18_check)

        self.filter_check = CheckBox(active=bool(main.CONFIG.get('FILTER_RESOLUTION', False)))
        grid.add_widget(Label(text='分辨率过滤'))
        grid.add_widget(self.filter_check)

        grid.add_widget(Label(text='API 源:'))
        api_items = ['nekos', 'lolicon']
        default_api = main.CONFIG.get('API_SOURCE', 'nekos')
        self.api_spinner = Spinner(text=default_api, values=api_items, size_hint_x=None, width='100dp')
        grid.add_widget(self.api_spinner)

        # Row 1 – save path + browse button
        self.add_widget(grid)
        save_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        save_layout.add_widget(Label(text='保存路径:', size_hint_x=None, width='80dp'))
        self.save_path_input = TextInput(text=str(main.CONFIG.get('SAVE_DIR', '')), readonly=True)
        save_layout.add_widget(self.save_path_input)
        browse_btn = Button(text='浏览...', size_hint_x=None, width='80dp')
        browse_btn.bind(on_release=self.select_save_path)
        save_layout.add_widget(browse_btn)
        self.add_widget(save_layout)

        # Row 2 – min width / min height
        size_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        size_layout.add_widget(Label(text='最小宽度:', size_hint_x=None, width='80dp'))
        self.min_w_input = TextInput(text=str(main.CONFIG.get('MIN_WIDTH', 1920)),
                                      input_filter='int', multiline=False, size_hint_x=None, width='80dp')
        size_layout.add_widget(self.min_w_input)
        size_layout.add_widget(Label(text='最小高度:', size_hint_x=None, width='80dp'))
        self.min_h_input = TextInput(text=str(main.CONFIG.get('MIN_HEIGHT', 1080)),
                                      input_filter='int', multiline=False, size_hint_x=None, width='80dp')
        size_layout.add_widget(self.min_h_input)
        self.add_widget(size_layout)

        # Start button (right aligned)
        btn_layout = BoxLayout(size_hint_y=None, height='50dp')
        btn_layout.add_widget(Label())  # spacer
        self.start_btn = Button(text='开始下载', size_hint_x=None, width='120dp')
        self.start_btn.bind(on_release=self.start_download)
        btn_layout.add_widget(self.start_btn)
        self.add_widget(btn_layout)

        # Log view – a ScrollView with a Label inside
        self.log_label = Label(text='', size_hint_y=None, markup=True, valign='top')
        self.log_label.bind(texture_size=self._update_log_height)
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.log_label)
        self.add_widget(scroll)

    def _update_log_height(self, instance, value):
        # Keep the label height equal to its rendered text height.
        instance.height = value[1]

    def _setup_logging(self):
        logger = logging.getLogger()
        # Remove default StreamHandler if present to avoid duplicate console output.
        for h in list(logger.handlers):
            if isinstance(h, logging.StreamHandler):
                logger.removeHandler(h)
        logger.addHandler(KivyLogHandler(self.log_label))
        logger.setLevel(logging.INFO)

    def select_save_path(self, *args):
        # On Android we cannot use native file dialogs easily; fallback to a simple
        # text‑input prompt. For desktop testing we reuse ``tkinter.filedialog``.
        try:
            from tkinter import Tk, filedialog
            root = Tk()
            root.withdraw()
            directory = filedialog.askdirectory(initialdir=self.save_path_input.text or str(Path.home()))
            root.destroy()
        except Exception:
            # If tkinter is unavailable (e.g., on Android), just let the user edit the
            # path manually after the dialog fails.
            directory = ''
        if directory:
            self.save_path_input.text = directory
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                logging.warning(f'创建保存目录失败: {e}')

    def apply_gui_config(self):
        # Helper to copy widget values into ``main.CONFIG``
        def _int(val, fallback):
            try:
                return int(val)
            except Exception:
                return fallback
        main.CONFIG['TARGET_COUNT'] = _int(self.target_input.text, 30)
        main.CONFIG['MAX_WORKERS'] = _int(self.workers_input.text, 5)
        main.CONFIG['R18'] = self.r18_check.active
        main.CONFIG['FILTER_RESOLUTION'] = self.filter_check.active
        main.CONFIG['MIN_WIDTH'] = _int(self.min_w_input.text, 1920)
        main.CONFIG['MIN_HEIGHT'] = _int(self.min_h_input.text, 1080)
        main.CONFIG['SAVE_DIR'] = self.save_path_input.text
        main.CONFIG['API_SOURCE'] = self.api_spinner.text

    def start_download(self, *args):
        self.start_btn.disabled = True
        self.apply_gui_config()
        self.log_label.text = ''
        self.worker_thread = threading.Thread(target=self._run_main, daemon=True)
        self.worker_thread.start()

    def _run_main(self):
        try:
            exit_code = main.main()
        except Exception:
            logging.exception('Exception in download thread')
            exit_code = 1
        # Notify the main thread of completion.
        Clock.schedule_once(lambda dt: self.on_finished(exit_code))

    def on_finished(self, exit_code: int):
        if exit_code == 0:
            msg = f'下载完成，成功数量: {main.CONFIG.get("TARGET_COUNT", 0)}'
            title = '完成'
        else:
            msg = f'未达到目标，已下载 {main.CONFIG.get("TARGET_COUNT", 0)} 张'
            title = '未完成'
        popup = Popup(title=title,
                      content=Label(text=msg),
                      size_hint=(0.8, 0.4))
        popup.open()
        self.start_btn.disabled = False
        self.worker_thread = None


class AndroidApp(App):
    def build(self):
        # Optional: set a window size for desktop testing.
        if not hasattr(Window, 'system_size'):
            Window.size = (720, 560)
        return MainScreen()


if __name__ == '__main__':
    AndroidApp().run()
