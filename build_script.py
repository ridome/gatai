
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
    '--name=ExcelMerger', # Renamed
    '--windowed',
    '--onefile',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
]

print("Starting PyInstaller Build...")
PyInstaller.__main__.run(args)
print("Build Complete. Executable is in dist/ExcelMerger.exe")
