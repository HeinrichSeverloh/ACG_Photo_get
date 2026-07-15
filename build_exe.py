#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cross‑platform build helper.

Usage (run on the *target* OS):
    python build_exe.py           # default: GUI mode (windowed)
    python build_exe.py --cli    # build CLI version (keeps console)
    python build_exe.py --gui    # explicit GUI mode

The script detects the running platform and:
  • macOS – builds a .app bundle via ``py2app`` (recommended) or falls back to
    PyInstaller if you prefer a single‑file binary.
  • Linux – builds a single ELF executable with PyInstaller.
  • Windows – builds a single .exe with PyInstaller (already functional in the
    repository).

After a successful build the temporary ``build/`` directory, the generated
``*.spec`` file and any extra files inside ``dist/`` are removed, leaving only
the final executable (or .app bundle) inside ``dist/``.
"""

import sys
import shutil
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration – adjust only if you rename entry points or the final app name
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.resolve()
# Choose the entry script you want to ship.  ``gui.py`` for the GUI version,
# ``main.py`` for the pure‑CLI version.
ENTRY_SCRIPT = PROJECT_ROOT / "gui.py"
APP_NAME = "ACGPhotoGet"
# ---------------------------------------------------------------------------

def run_cmd(cmd):
    """Run a command via subprocess, raising on failure."""
    print("\n>>>", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)

def clean_up(build_dir: Path, dist_dir: Path, spec_file: Path, keep_name: str | None):
    """Delete all intermediate artefacts, keeping only ``keep_name``.
    ``keep_name`` should be the exact filename of the final executable (e.g.
    ``ACGPhotoGet.exe`` on Windows, ``ACGPhotoGet`` on Linux, or the ``.app``
    bundle on macOS).  Pass ``None`` to keep the whole ``dist`` directory
    (used for macOS .app bundles).
    """
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if spec_file.exists():
        spec_file.unlink()
    if dist_dir.is_dir():
        for item in dist_dir.iterdir():
            if keep_name is None:
                # macOS – keep the whole .app directory, delete everything else
                if item.is_dir() and item.name.endswith('.app'):
                    continue
                if item.is_file() and item.name == keep_name:
                    continue
            else:
                # Linux / Windows – keep only the single executable
                if item.name != keep_name:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

def build_pyinstaller(gui: bool):
    """Build with PyInstaller (works on Linux, Windows and optionally macOS)."""
    build_dir = PROJECT_ROOT / "build"
    dist_dir = PROJECT_ROOT / "dist"
    spec_file = PROJECT_ROOT / f"{ENTRY_SCRIPT.stem}.spec"

    args = [sys.executable, "-m", "PyInstaller", "--onefile", "--clean", "--name", APP_NAME]
    if gui:
        # macOS uses --windowed, Linux/Windows use --noconsole (same effect)
        if sys.platform.startswith('darwin'):
            args.append('--windowed')
        else:
            args.append('--noconsole')
    args.append(str(ENTRY_SCRIPT))

    run_cmd(args)

    exe_name = APP_NAME + ('.exe' if sys.platform.startswith('win') else '')
    clean_up(build_dir, dist_dir, spec_file, exe_name)
    final_path = dist_dir / exe_name
    if not final_path.is_file():
        sys.exit(f"❌ Build failed – missing {final_path}")
    print(f"\n✅ Build succeeded → {final_path}\n")
    return final_path

def build_py2app():
    """macOS specific: build a proper .app bundle using py2app.
    This requires a ``setup.py`` in the project root (provided alongside this
    file).  The ``--alias`` flag is used for development; for a production build
    remove it or replace with ``--no-alias``.
    """
    # Ensure py2app is available – the CI step installs it, on a local macOS
    # machine you can ``uv pip install py2app`` manually.
    run_cmd([sys.executable, "setup.py", "py2app", "--dist-dir", "dist", "--clean"])
    # ``dist`` now contains ``ACGPhotoGet.app``.  Remove temporary artefacts.
    build_dir = PROJECT_ROOT / "build"
    spec_file = PROJECT_ROOT / f"{ENTRY_SCRIPT.stem}.spec"
    clean_up(build_dir, PROJECT_ROOT / "dist", spec_file, keep_name=None)
    app_path = PROJECT_ROOT / "dist" / f"{APP_NAME}.app"
    if not app_path.is_dir():
        sys.exit("❌ py2app did not produce the .app bundle")
    print(f"\n✅ macOS .app bundle created → {app_path}\n")
    return app_path

def main():
    gui = True  # default to GUI mode
    if "--cli" in sys.argv:
        gui = False
    if "--gui" in sys.argv:
        gui = True

    if sys.platform.startswith('darwin'):
        # macOS – preferred to use py2app for a native .app bundle.
        # If you really want a single .exe via PyInstaller, uncomment the next line.
        # build_pyinstaller(gui)
        build_py2app()
    elif sys.platform.startswith('win'):
        build_pyinstaller(gui)
    elif sys.platform.startswith('linux'):
        build_pyinstaller(gui)
    else:
        sys.exit('⚠️ Unsupported platform')

if __name__ == '__main__':
    main()
