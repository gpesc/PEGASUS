import os
from pathlib import Path
import subprocess
import sys
import json
import platform

if sys.platform != 'win32':
    raise SystemExit('Execute este script no Windows, com o Python que executa o Pegasus atual.')
os.chdir(Path(__file__).resolve().parent)
# Preflight in a separate process: do not leave GMAT DLLs loaded into the build process.
subprocess.run([sys.executable, '-c', 'import load_gmat; print("API GMAT carregada com sucesso")'], check=True)
import numpy, scipy, PIL, tkinter, PyInstaller
Path('ambiente_compilacao.json').write_text(json.dumps({
    'python': sys.version, 'bits': platform.architecture()[0],
    'numpy': numpy.__version__, 'scipy': scipy.__version__,
    'Pillow': PIL.__version__, 'PyInstaller': PyInstaller.__version__,
}, indent=2), encoding='utf-8')
subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
    '--onefile', '--windowed', '--name', 'Pegasus',
    '--icon', 'pegasus_icon.ico', '--add-data', 'pegasus_icon.ico;.',
    '--add-data', 'pegasus_banner.png;.',
    '--exclude-module', 'gmatpy', '--exclude-module', '_gmatpy',
    'Pegasus.py'], check=True)
print('Executavel criado: dist\\Pegasus.exe')
