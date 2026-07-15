from setuptools import setup

APP = ['gui.py']  # or 'main.py' if you want the CLI version

OPTIONS = {
    'argv_emulation': True,
    'compressed': True,
    'iconfile': None,  # e.g. 'icon.icns' – put an .icns file next to this script if you have one
    'plist': {
        'CFBundleName': 'ACGPhotoGet',
        'CFBundleDisplayName': 'ACG Photo Downloader',
        'CFBundleIdentifier': 'com.example.acgphotoget',
        'CFBundleVersion': '1.0.0',
        'LSUIElement': False,  # set True to hide from Dock (menu‑bar only app)
    },
}

setup(
    app=APP,
    name='ACGPhotoGet',
    version='1.0.0',
    description='二次元图片自动搬运工 (GUI)',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
