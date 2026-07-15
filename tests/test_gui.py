"""Test that the GUI can be imported and instantiated without a real Tkinter environment.
We provide a lightweight stub for the `tkinter` package and its submodules.
The test only checks that `gui.App` can be created and that it sets up logging
without raising exceptions.  No actual window is shown.
"""
import sys
import types

# ---- Create a minimal stub for tkinter ----
stub_tk = types.SimpleNamespace()
# Stub for Tk class
class DummyTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args, **kwargs):
        pass
    def geometry(self, *args, **kwargs):
        pass
    def mainloop(self, *args, **kwargs):
        pass
    def destroy(self):
        pass
    def quit(self):
        pass

stub_tk.Tk = DummyTk
stub_tk.END = 'end'
# ttk submodule with Frame, Label, Entry, Checkbutton, Button, etc.
stub_ttk = types.SimpleNamespace()
class DummyWidget:
    def __init__(self, *a, **k):
        pass
    def pack(self, *a, **k):
        pass
    def grid(self, *a, **k):
        pass
    def configure(self, *a, **k):
        pass
    def insert(self, *a, **k):
        pass
    def see(self, *a, **k):
        pass
    def bind(self, *a, **k):
        pass
    def set(self, *a, **k):
        pass

stub_ttk.Frame = DummyWidget
stub_ttk.Label = DummyWidget
stub_ttk.Entry = DummyWidget
stub_ttk.Checkbutton = DummyWidget
stub_ttk.Button = DummyWidget
stub_ttk.Scrollbar = DummyWidget
# ttk variable classes
class DummyVar:
    def __init__(self, *a, **k):
        # Accept `value=` kwarg like tkinter variables
        self._value = k.get('value') if isinstance(k, dict) else None
    def get(self):
        return self._value
    def set(self, v):
        self._value = v

stub_ttk.IntVar = DummyVar
stub_ttk.BooleanVar = DummyVar
stub_ttk.StringVar = DummyVar

# Also expose these variable classes directly on the tkinter stub
stub_tk.IntVar = DummyVar
stub_tk.BooleanVar = DummyVar
stub_tk.StringVar = DummyVar

# scrolledtext submodule
stub_scrolledtext = types.SimpleNamespace()
stub_scrolledtext.ScrolledText = DummyWidget
# messagebox submodule
stub_messagebox = types.SimpleNamespace()
stub_messagebox.showinfo = lambda *a, **k: None
stub_messagebox.showwarning = lambda *a, **k: None
stub_messagebox.showerror = lambda *a, **k: None

# Assemble the tkinter stub package hierarchy
stub_tk.ttk = stub_ttk
stub_tk.scrolledtext = stub_scrolledtext
stub_tk.messagebox = stub_messagebox
# filedialog stub
stub_filedialog = types.SimpleNamespace(askdirectory=lambda *a, **k: '/tmp/download')
stub_tk.filedialog = stub_filedialog
# Insert stub into sys.modules before importing gui
sys.modules.setdefault('tkinter', stub_tk)
sys.modules.setdefault('tkinter.ttk', stub_ttk)
sys.modules.setdefault('tkinter.scrolledtext', stub_scrolledtext)
sys.modules.setdefault('tkinter.messagebox', stub_messagebox)
sys.modules.setdefault('tkinter.filedialog', stub_filedialog)

# Now import the GUI module
import importlib
gui = importlib.import_module('gui')

def test_app_instantiation():
    # Instantiate the App – should not raise any exception
    app = gui.App()
    # Clean up (destroy the dummy Tk window)
    app.destroy()
    assert True
