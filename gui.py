"""简易 Tkinter GUI for ACG_Photo_get

功能概览
- 直接在窗口中配置脚本的主要参数（目标数量、并发、标签、R18、分辨率过滤等）
- 点击 *开始下载* 后在下方日志框实时显示 `logging` 输出
- 下载过程在后台线程运行，避免阻塞 GUI

使用方法
```bash
python gui.py
```
"""

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import sys
import logging

# 把项目根目录加入路径（如果直接以模块方式运行）
import os
sys.path.append(os.path.abspath('.'))

import main  # 主脚本，已经实现了所有业务逻辑和配置对象

# ---------- 自定义日志处理器，将日志写入 Text widget ----------
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.configure(state='disabled')

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')

# ---------- GUI 主体 ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('ACG Photo Downloader')
        self.geometry('720x560')
        self.create_widgets()
        self.configure_logging()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(fill='x', padx=10, pady=5)

        # 目标数量
        ttk.Label(frm, text='目标数量:').grid(row=0, column=0, sticky='e')
        self.target_var = tk.IntVar(value=main.CONFIG.get('TARGET_COUNT', 30))
        ttk.Entry(frm, textvariable=self.target_var, width=8).grid(row=0, column=1, sticky='w')

        # 并发线程数
        ttk.Label(frm, text='并发线程:').grid(row=0, column=2, sticky='e')
        self.workers_var = tk.IntVar(value=main.CONFIG.get('MAX_WORKERS', 5))
        ttk.Entry(frm, textvariable=self.workers_var, width=5).grid(row=0, column=3, sticky='w')

        # R18 开关
        self.r18_var = tk.BooleanVar(value=main.CONFIG.get('R18', False))
        ttk.Checkbutton(frm, text='R18 (explicit)', variable=self.r18_var).grid(row=0, column=4, padx=5)

        # 分辨率过滤开关
        self.filter_var = tk.BooleanVar(value=main.CONFIG.get('FILTER_RESOLUTION', False))
        ttk.Checkbutton(frm, text='分辨率过滤', variable=self.filter_var).grid(row=0, column=5, padx=5)

        # API 源选择
        ttk.Label(frm, text='API 源:').grid(row=0, column=6, sticky='e')
        self.api_var = tk.StringVar(value=main.CONFIG.get('API_SOURCE', 'nekos'))
        api_combo = ttk.Combobox(frm, textvariable=self.api_var, values=['nekos', 'lolicon'], state='readonly', width=10)
        api_combo.grid(row=0, column=7, sticky='w')
        api_combo.current(0 if self.api_var.get() == 'nekos' else 1)

        # 下载路径选择
        ttk.Label(frm, text='保存路径:').grid(row=1, column=0, sticky='e')
        self.save_path_var = tk.StringVar(value=main.CONFIG.get('SAVE_DIR', ''))
        ttk.Entry(frm, textvariable=self.save_path_var, width=40, state='readonly').grid(row=1, column=1, columnspan=4, sticky='w')
        ttk.Button(frm, text='浏览...', command=self.select_save_path).grid(row=1, column=5, sticky='w')

        # 分辨率阈值（当过滤开启时生效）
        ttk.Label(frm, text='最小宽度:').grid(row=2, column=0, sticky='e')
        self.min_w_var = tk.IntVar(value=main.CONFIG.get('MIN_WIDTH', 1920))
        ttk.Entry(frm, textvariable=self.min_w_var, width=6).grid(row=2, column=1, sticky='w')
        ttk.Label(frm, text='最小高度:').grid(row=2, column=2, sticky='e')
        self.min_h_var = tk.IntVar(value=main.CONFIG.get('MIN_HEIGHT', 1080))
        ttk.Entry(frm, textvariable=self.min_h_var, width=6).grid(row=2, column=3, sticky='w')

        # 开始按钮
        self.start_btn = ttk.Button(frm, text='开始下载', command=self.start_download_thread)
        self.start_btn.grid(row=3, column=5, pady=5)

        # 日志显示区
        self.log_text = scrolledtext.ScrolledText(self, wrap='word', height=20)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=5)

    def select_save_path(self):
        # 打开文件夹选择对话框，更新保存路径变量
        selected = filedialog.askdirectory(initialdir=self.save_path_var.get() or os.getcwd())
        if selected:
            self.save_path_var.set(selected)
        # Ensure the directory exists (create if needed)
        try:
            os.makedirs(self.save_path_var.get(), exist_ok=True)
        except Exception as e:
            logging.warning(f"创建保存目录失败: {e}")

    def configure_logging(self):
        # 把主脚本的 logging 处理器追加到 TextHandler
        logger = logging.getLogger()
        # 移除可能已经添加的 StreamHandler（避免重复打印到控制台）
        for h in list(logger.handlers):
            if isinstance(h, logging.StreamHandler):
                logger.removeHandler(h)
        # 添加自定义 TextHandler
        text_handler = TextHandler(self.log_text)
        fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        text_handler.setFormatter(fmt)
        logger.addHandler(text_handler)
        logger.setLevel(logging.INFO)

    def apply_gui_config(self):
        # 将 GUI 中的值写回 main.CONFIG
        main.CONFIG['TARGET_COUNT'] = self.target_var.get()
        main.CONFIG['MAX_WORKERS'] = self.workers_var.get()
        main.CONFIG['R18'] = self.r18_var.get()
        main.CONFIG['FILTER_RESOLUTION'] = self.filter_var.get()
        main.CONFIG['MIN_WIDTH'] = self.min_w_var.get()
        main.CONFIG['MIN_HEIGHT'] = self.min_h_var.get()
        main.CONFIG['SAVE_DIR'] = self.save_path_var.get()
        main.CONFIG['API_SOURCE'] = self.api_var.get()

    def start_download_thread(self):
        # 防止重复点击
        self.start_btn.config(state='disabled')
        self.apply_gui_config()
        threading.Thread(target=self.run_main, daemon=True).start()

    def run_main(self):
        try:
            # 主函数会返回退出码，0 为成功
            exit_code = main.main()
            if exit_code == 0:
                messagebox.showinfo('完成', f'下载完成，成功数量: {main.CONFIG["TARGET_COUNT"]}')
            else:
                messagebox.showwarning('未完成', f'未达到目标，已下载 {main.CONFIG["TARGET_COUNT"]} 张')
        except Exception as e:
            logging.exception('运行主程序时出错')
            messagebox.showerror('错误', str(e))
        finally:
            self.start_btn.config(state='normal')

if __name__ == '__main__':
    import logging
    App().mainloop()
