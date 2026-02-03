
import PyInstaller.__main__
import os
import shutil

# Clean up previous build
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

# Define build arguments
args = [
    'main.py',
    '--name=OCRConverter',
    '--windowed',  # No console window
    '--onefile',   # Single executable
    '--icon=NONE', # Can add an icon if available
    # Hidden imports often needed for Paddle/Pandas
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
    '--hidden-import=paddleocr',
    '--hidden-import=paddlex',
    '--hidden-import=shapely',
    '--hidden-import=scipy',
    '--hidden-import=skimage',
    '--hidden-import=pyclipper',
    # PaddleOCR usually needs layout models/configs.
    # With --onefile, we might need to instruct user to keep models folder or bundle them.
    # However, PaddleOCR downloads models to ~/.paddleocr by default.
    # On Windows, this is C:\Users\User\.paddleocr.
    # So the EXE should work if it can download models or finds them.
]

print("Starting PyInstaller Build...")
PyInstaller.__main__.run(args)
print("Build Complete. Executable is in dist/OCRConverter.exe")
