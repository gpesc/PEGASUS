"""External GMAT loader. Python and GMAT native API must have matching ABI."""
import importlib
import json
import os
from pathlib import Path
import runpy
import sys
import traceback

__all__ = ['gmat', 'GmatInstall', 'GmatBinPath']
STATE = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'Pegasus'
STATE.mkdir(parents=True, exist_ok=True)
CONFIG = STATE / 'gmat.json'
_handles = []

def choose_root():
    from tkinter import Tk, filedialog, messagebox
    saved = ''
    try:
        saved = json.loads(CONFIG.read_text(encoding='utf-8'))['root']
    except (OSError, ValueError, KeyError):
        pass
    if '--configurar-gmat' not in sys.argv and saved and (Path(saved)/'bin').is_dir():
        return Path(saved)
    ui = Tk()
    ui.withdraw()
    try:
        while True:
            chosen = filedialog.askdirectory(parent=ui, title='Selecione a pasta do GMAT que contem bin e api')
            if not chosen:
                raise SystemExit(0)
            root = Path(chosen)
            if (root/'bin').is_dir() and (root/'api'/'BuildApiStartupFile.py').is_file():
                return root
            messagebox.showerror('Pegasus', 'Selecione a pasta que contem bin e api.', parent=ui)
    finally:
        ui.destroy()

def initialize():
    root = choose_root().resolve()
    binary = root / 'bin'
    startup = binary / 'api_startup_file.txt'
    sys.path.insert(0, str(root / 'api'))
    # Run the official generator using the embedded interpreter (no Python install needed).
    if not startup.is_file():
        previous = Path.cwd()
        previous_args = sys.argv[:]
        try:
            os.chdir(root / 'api')
            sys.argv = [str(root / 'api' / 'BuildApiStartupFile.py')]
            runpy.run_path(sys.argv[0], run_name='__main__')
        finally:
            sys.argv = previous_args
            os.chdir(previous)
    if not startup.is_file():
        raise RuntimeError('O gerador do GMAT nao criou bin/api_startup_file.txt. Configure a API desta distribuicao do GMAT.')
    for folder in (binary, root/'api'):
        sys.path.insert(0, str(folder))
    if hasattr(os, 'add_dll_directory'):
        _handles.append(os.add_dll_directory(str(binary)))
    os.environ['PATH'] = str(binary) + os.pathsep + os.environ.get('PATH', '')
    module = importlib.import_module('gmatpy')
    previous = Path.cwd()
    try:
        os.chdir(binary)
        result = module.Setup(str(startup))
        if result is False:
            raise RuntimeError('GMAT Setup retornou False.')
    finally:
        os.chdir(previous)
    if not all(callable(getattr(module, name, None)) for name in ('Clear', 'LoadScript', 'RunScript')):
        raise RuntimeError('API GMAT incompleta.')
    CONFIG.write_text(json.dumps({'root': str(root)}, indent=2), encoding='utf-8')
    return module, str(root), str(binary)

try:
    gmat, GmatInstall, GmatBinPath = initialize()
except Exception as error:
    log = STATE / 'erro_gmat.txt'
    log.write_text(traceback.format_exc(), encoding='utf-8')
    from tkinter import Tk, messagebox
    ui = Tk()
    ui.withdraw()
    messagebox.showerror('Pegasus - integracao GMAT',
        f'Nao foi possivel iniciar a API do GMAT.\n\n{error}\n\n'
        f'Python incorporado: {sys.version}\nLog: {log}\n\n'
        'Verifique a compatibilidade da API e as permissoes de escrita do GMAT. '
        'Se acabou de mover o GMAT, regenere seu arquivo de inicializacao. '
        'Para escolher outra pasta, inicie com --configurar-gmat.', parent=ui)
    ui.destroy()
    raise SystemExit(1)
