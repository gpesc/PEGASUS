# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 06:59:28 2025

@author: Caldas
"""

from datetime import datetime, timedelta
import bisect
import builtins
import math
import threading
import numpy as np
import os
import sys
import re
from pathlib import Path
import subprocess
_log_dir = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Pegasus"
_log_dir.mkdir(parents=True, exist_ok=True)
if sys.stdout is None:
    sys.stdout = open(_log_dir / "execucao.log", "a", encoding="utf-8", buffering=1)
if sys.stderr is None:
    sys.stderr = sys.stdout

try:
    from scipy.spatial.transform import Rotation
    scipy_disponivel = True
except ImportError:
    Rotation = None
    scipy_disponivel = False
    print("AVISO: scipy não encontrado. A interface e o script GMAT funcionarão, mas a análise de potência solar dependerá do scipy.")
try:
    import tkinter as tk
    from tkinter import ttk

    class MessageBoxWrapper:
        @staticmethod
        def showerror(title, message, parent=None):
            _idioma = globals().get("idioma_selecionado", "PT")
            confirmacao_personalizada(title, message, parent, _idioma, tipo="info")
        @staticmethod
        def showinfo(title, message, parent=None):
            _idioma = globals().get("idioma_selecionado", "PT")
            confirmacao_personalizada(title, message, parent, _idioma, tipo="info")
        @staticmethod
        def showwarning(title, message, parent=None):
            _idioma = globals().get("idioma_selecionado", "PT")
            confirmacao_personalizada(title, message, parent, _idioma, tipo="info")

    messagebox = MessageBoxWrapper()
    tkinter_disponivel = True
except ImportError:
    tkinter_disponivel = False
gmat_disponivel = False
try:
    from load_gmat import *
    gmat_disponivel = True
except ImportError:
    print("AVISO: load_gmat não encontrado. O script GMAT será gerado, mas não poderá ser executado daqui.")

try:
    from PIL import Image, ImageTk
    pil_disponivel = True
except ImportError:
    pil_disponivel = False

estado_tema = {
    "escuro": True
}

TRANSLATIONS_EN = {
    "{}: digite um número válido.": "{}: enter a valid number.",
    "{}: digite um número inteiro válido.": "{}: enter a valid integer.",
    "{}: o valor mínimo permitido é {}.": "{}: the minimum allowed value is {}.",
    "{}: o valor máximo permitido é {}.": "{}: the maximum allowed value is {}.",
    "Erro de entrada": "Input error",
    "3b. Modos de operação": "3b. Operating modes",
    "Dimensão X [m]": "Dimension X [m]",
    "Dimensão Y [m]": "Dimension Y [m]",
    "Dimensão Z [m]": "Dimension Z [m]",
    "Massa [kg]": "Mass [kg]",
    "load_gmat não foi encontrado; a execução ficará desativada.": "load_gmat was not found; execution will be disabled.",
    "Densidade": "Density",
    "Dimensão X": "Dimension X",
    "Dimensão Y": "Dimension Y",
    "Dimensão Z": "Dimension Z",
    "Elevação mínima": "Minimum elevation",
    "Fator de preenchimento": "Fill factor",
    "Fator de segurança": "Safety factor",
    "Fator de segurança da bateria": "Battery safety factor",
    "Massa": "Mass",
    "Células por face 1U": "Cells per 1U face",
    "Área da célula": "Cell area",
    "Número de bancos": "Number of banks",
    "Pe da bateria": "Battery Pe",
    "Tempo de missão": "Mission time",
    "Tempo de missão da bateria": "Battery mission time",
    "Tempo de simulação": "Simulation time",
    "Massa seca do satélite": "Dry satellite mass",
    "Coeficiente de arrasto": "Drag coefficient",
    "Coeficiente de reflexão solar": "Solar reflection coefficient",
    "Eficiência da célula (padrão 0,30)": "Cell efficiency (default 0.30)",
    "Degradação por ano em % (padrão 2,75)": "Degradation per year in % (default 2.75)",
    "Degradação inerente de projeto (padrão 0,77)": "Inherent design degradation (default 0.77)",
    "Fração da face coberta por células (padrão 0,6062).": "Fraction of the face covered by cells (default 0.6062).",
    "Área de cada célula solar em cm² (padrão 30,31).": "Area of each solar cell in cm² (default 30.31).",
    "Parte 1 - Órbita": "Part 1 - Orbit",
    "Configuração": "Configuration",
    "SMA [km] - Semi-eixo maior (mín. {:.3f})": "SMA [km] - Semi-major axis (min. {:.3f})",
    "ECC - Excentricidade (0 a <1)": "ECC - Eccentricity (0 to <1)",
    "INC [graus] - Inclinação orbital (0 a 180º)": "INC [deg] - Orbital inclination (0 to 180º)",
    "RAAN [graus] - Ascensão reta do nó ascendente (0 a 360º)": "RAAN [deg] - Right Ascension of Ascending Node (0 to 360º)",
    "AOP [graus] - Argumento do perigeu (0 a 360º)": "AOP [deg] - Argument of Perigee (0 to 360º)",
    "TA [graus] - Anomalia verdadeira (0 a 360º)": "TA [deg] - True Anomaly (0 to 360º)",
    "Parte 2 - Satélite": "Part 2 - Satellite",
    "Tamanho": "Size",
    "Dimensão X [m] - Largura no eixo X": "Dimension X [m] - Width on X axis",
    "Dimensão Y [m] - Largura no eixo Y": "Dimension Y [m] - Width on Y axis",
    "Dimensão Z [m] - Comprimento no eixo Z": "Dimension Z [m] - Length on Z axis",
    "Massa [kg] - Massa seca do satélite": "Mass [kg] - Dry mass of the satellite",
    "Cd - Coeficiente de arrasto": "Cd - Drag coefficient",
    "Cr - Coeficiente de reflexão solar": "Cr - Solar reflection coefficient",
    "Parte 3 - Atitude e painéis solares": "Part 3 - Attitude and solar panels",
    "Nadir": "Nadir",
    "Velocidade": "Velocity",
    "Painéis": "Panels",
    "Parte 4 - Estação terrena e simulação": "Part 4 - Ground station and simulation",
    "Simular contato com estação terrena": "Simulate contact with ground station",
    "Lat [graus]": "Lat [degrees]",
    "Lon [graus]": "Lon [degrees]",
    "Alt [km]": "Alt [km]",
    "Elevação mínima [graus]": "Minimum elevation [degrees]",
    "Data de início (UTC)": "Start Date (UTC)",
    "Data de início (UTC) [DD Mon AAAA HH:MM:SS.mmm]": "Start Date (UTC) [DD Mon YYYY HH:MM:SS.mmm]",
    "Data de início (UTC) [DD/MM/AAAA + HH:MM]": "Start Date (UTC) [DD/MM/YYYY + HH:MM]",
    "Data de início (UTC) [DD/MM/AAAA]": "Start Date (UTC) [DD/MM/YYYY]",
    "Horário de início (UTC) [HH:MM]": "Start Time (UTC) [HH:MM]",
    "Data inválida": "Invalid date",
    "A data de início deve estar entre 04 Oct 1957 e 28 Feb 2100.": "The start date must be between 04 Oct 1957 and 28 Feb 2100.",
    "Duração da simulação": "Simulation Duration",
    "Passo de integração [s]": "Integration Step [s]",
    "Semi-eixo maior em km. Mínimo: {:.3f} km.": "Semi-major axis in km. Minimum: {:.3f} km.",
    "Excentricidade entre 0 e menor que 1.": "Eccentricity between 0 and less than 1.",
    "Inclinação orbital em graus, de 0 a 180.": "Orbital inclination in degrees, from 0 to 180.",
    "RAAN em graus, de 0 a 360.": "RAAN in degrees, from 0 to 360.",
    "Argumento do perigeu em graus, de 0 a 360.": "Argument of perigee in degrees, from 0 to 360.",
    "Anomalia verdadeira em graus, de 0 a 360.": "True anomaly in degrees, from 0 to 360.",
    "Dimensão X do satélite em metros.": "Satellite X dimension in meters.",
    "Dimensão Y do satélite em metros.": "Satellite Y dimension in meters.",
    "Dimensão Z do satélite em metros.": "Satellite Z dimension in meters.",
    "Massa seca do satélite em kg.": "Dry satellite mass in kg.",
    "Coeficiente de arrasto.": "Drag coefficient.",
    "Coeficiente de reflexão solar.": "Solar reflection coefficient.",
    "Data no formato DD/MM/AAAA.": "Date must be DD/MM/YYYY.",
    "Horário UTC no formato HH:MM.": "UTC time must be HH:MM.",
    "Posição norte/sul de -90º a 90º.": "North/south position from -90º to 90º.",
    "Posição leste/oeste de -180º a 180º.": "East/west position from -180º to 180º.",
    "Altura da estação em metros.": "Station altitude in meters.",
    "Ângulo mínimo de visada de 0º a 90º.": "Minimum look angle from 0º to 90º.",
    "Duração da propagação em dias.": "Propagation duration in days.",
    "Parte 5 - Arquitetura de potência": "Part 5 - Power Architecture",
    "Topologia": "Topology",
    "Eficiência do conversor (0 a 1)": "Converter Efficiency (0 to 1)",
    "Eficiência do painel (0 a 1)": "Panel Efficiency (0 to 1)",
    "Parte 6 - Painéis solares": "Part 6 - Solar Panels",
    "Área das células": "Cell Area",
    "P_id [W/m²] - Potência ideal": "P_id [W/m²] - Ideal Power",
    "Análise de painéis solares": "Solar panel analysis",
    "A configuração orbital indica eclipse total.": "Orbital configuration indicates total eclipse.",
    "Semi-eixo maior em km. Mínimo: {:.3f}": "Semi-major axis in km. Minimum: {:.3f}",
    "Excentricidade (0 a <1)": "Eccentricity (0 to <1)",
    "Inclinação orbital (0 a 180º)": "Orbital inclination (0 to 180º)",
    "Ascensão reta do nó ascendente (0 a 360º)": "Right Ascension of Ascending Node (0 to 360º)",
    "Argumento do perigeu (0 a 360º)": "Argument of Perigee (0 to 360º)",
    "Anomalia verdadeira (0 a 360º)": "True Anomaly (0 to 360º)",
    "Largura no eixo X": "Width on X axis",
    "Largura no eixo Y": "Width on Y axis",
    "Comprimento no eixo Z": "Length on Z axis",
    "A sequência de rotações Euler é 321": "The Euler rotation sequence is 321",
    "Semi-eixo maior em km. Mínimo: {:.3f} km.": "Semi-major axis in km. Minimum: {:.3f} km.",
    "Tempo de missão em anos (mín. 0)": "Mission time in years (min. 0)",
    "Potência máxima consumida no eclipse": "Maximum power consumed in eclipse",
    "Potência máxima consumida no sol": "Maximum power consumed in sun",
    "Eficiência de descarga (0 a 1)": "Discharge efficiency (0 to 1)",
    "Eficiência de carga (0 a 1)": "Charge efficiency (0 to 1)",
    "Profundidade de descarga": "Depth of discharge",
    "Eficiência de transmissão": "Transmission efficiency",
    "Resultados por Período de Iluminação": "Results by Illumination Period",
    "Período": "Period",
    "Duração": "Duration",
    "P_media": "Avg_Power",
        "Parte 7 - Bateria": "Part 7 - Battery",
    "Tempo de missão [anos] (mín. 0)": "Mission time [years] (min. 0)",
    "Potência máxima consumida no eclipse Pe [W]": "Maximum power consumed in eclipse Pe [W]",
    "Potência máxima consumida no sol Pd [W]": "Maximum power consumed in sun Pd [W]",
    "Eficiência de descarga Xe (0 a 1)": "Discharge efficiency Xe (0 to 1)",
    "Eficiência de carga Xd (0 a 1)": "Charge efficiency Xd (0 to 1)",
    "Profundidade de descarga DoD (0 a 1)": "Depth of Discharge DoD (0 to 1)",
    "Densidade [Wh/kg] (mín. 0.001)": "Density [Wh/kg] (min. 0.001)",
    "Bancos independentes (mín. 1)": "Independent banks (min. 1)",
    "Eficiência de transmissão n (0 a 1)": "Transmission efficiency n (0 to 1)",

    "Tipo": "Type",
    "Densidade [Wh/kg]": "Density [Wh/kg]",
    "Bancos independentes": "Independent banks",
    "Eficiência de transmissão (0 a 1)": "Transmission efficiency (0 to 1)",
    "Análise de bateria": "Battery analysis",
    "Outra": "Other",
    "Resetar visualização": "Reset view",
    "Tema": "Theme",
    "Cancelar e usar terminal": "Cancel and use terminal",
    "Próximo": "Next",
    "Voltar": "Back",
    "Aviso": "Warning",
    "Por favor, configure todos os campos obrigatórios.": "Please configure all required fields.",
    "Todos os parâmetros foram configurados!": "All parameters have been configured!",
    "Dados incompletos": "Incomplete data",
    "Preencha todos os campos corretamente.": "Please fill in all fields correctly.",
    "A face de velocidade não pode ser igual nem oposta à face nadir.": "The velocity face cannot be equal or opposite to the nadir face.",
    "Face nadir": "Nadir face",
    "A face nadir não recebe células solares nesta configuração.": "The nadir face does not receive solar cells in this configuration.",
    "Face inválida": "Invalid face",
    "Fluxo sequencial de análise do CubeSat": "CubeSat sequential analysis flow",
    "Seção": "Section",
    "1. Dados preliminares": "1. Preliminary data",
    "2. Script / GMAT": "2. Script / GMAT",
    "3. Painéis solares": "3. Solar panels",
    "4. Baterias": "4. Batteries",
    "GMAT está rodando...": "GMAT is running...",
    "Aguarde a propagação e a geração dos arquivos de resultado.": "Please wait for the propagation and generation of the result files.",
    "Erro": "Error",
    "GMAT": "GMAT",
    "Pegasus - Interface de Configuração": "PEGASUS - Configuration Interface",
    "Pegasus - Saída e Resumo": "PEGASUS - Output and Summary",
    "Entrada inválida": "Invalid input",
    "Gerar script": "Generate script",
    "Massa inválida: a massa do satélite precisa ser maior que zero.": "Invalid mass: the satellite mass must be greater than zero.",
    "Cd inválido: o coeficiente de arrasto não pode ser negativo.": "Invalid Cd: the drag coefficient cannot be negative.",
    "Cr inválido: o coeficiente de reflexão solar não pode ser negativo.": "Invalid Cr: the solar reflection coefficient cannot be negative.",
    "Atitude inválida: a face de velocidade não pode ser igual nem oposta à face nadir.\n\nMotivo: o GMAT precisa de dois eixos independentes para definir a atitude Nadir Pointing.": "Invalid attitude: the velocity face cannot be equal or opposite to the nadir face.\n\nReason: GMAT requires two independent axes to define the Nadir Pointing attitude.",
    "Confirme as faces usadas na análise": "Confirm the faces used in the analysis",
    "Executar análise de painéis": "Execute solar panel analysis",
    "Tempo de missão [anos] (mín. 0)": "Mission time [years] (min. 0)",
    "Potência máxima consumida no eclipse Pe [W]": "Maximum power consumed in eclipse Pe [W]",
    "Potência máxima consumida no sol Pd [W]": "Maximum power consumed in sun Pd [W]",
    "Outra: informe manualmente Xe e Xd": "Other: manually inform Xe and Xd",
    "Eficiência de descarga Xe (0 a 1)": "Discharge efficiency Xe (0 to 1)",
    "Eficiência de carga Xd (0 a 1)": "Charge efficiency Xd (0 to 1)",
    "Cancelar": "Cancel",
    "Confirmar": "Confirm",
    "Executar análise de bateria": "Execute battery analysis",
    "Profundidade de descarga máxima (DoD) (0 a 1)": "Maximum Depth of Discharge (DoD) (0 to 1)",
    "Tipo de bateria": "Battery type",
    "Densidade de energia [Wh/kg]": "Energy density [Wh/kg]",
    "Número de bancos independentes": "Number of independent banks",
    "Confirme os parâmetros da bateria": "Confirm battery parameters",
    "Órbita": "Orbit",
    "Satélite": "Satellite",
    "Atitude / Painéis": "Attitude / Panels",
    "Estação / Simulação": "Station / Simulation",
    "Dados inválidos": "Invalid data",
    "Nenhuma face com painel solar foi configurada.": "No face with solar panel was configured.",
    "Informar estação terrena": "Specify ground station",
    "Latitude [graus] - Posição norte/sul (-90º a 90º)": "Latitude [deg] - North/south position (-90º to 90º)",
    "Longitude [graus] - Posição leste/oeste (-180º a 180º)": "Longitude [deg] - East/west position (-180º to 180º)",
    "Altitude [m] - Altura da estação": "Altitude [m] - Station height",
    "Elevação mínima [graus] - Ângulo mínimo de visada (0º a 90º)": "Min. elevation [deg] - Minimum look angle (0º to 90º)",
    "Tempo de simulação [dias] - Duração da propagação": "Simulation time [days] - Propagation duration",
    "Executar GMAT após gerar o script": "Run GMAT after generating the script",
    "Executar após o GMAT concluir": "Run after GMAT completes",
    "Executar após a análise de painéis": "Run after solar panel analysis",
    "DoD - Profundidade de descarga (0 a 1)": "DoD - Depth of Discharge (0 to 1)",
    "Visualização (conforme CDS Rev. 14): arraste para girar, use a roda do mouse para aproximar": "Visualization (CDS Rev. 14): drag to rotate, scroll to zoom",
    "Parte 5 - Script / GMAT": "Part 5 - Script / GMAT",
    "Mission Tree": "Mission Tree",
    "Painéis solares": "Solar panels",
    "LEO exemplo": "LEO example",
    "Geoestacionária": "Geostationary",
    "Personalizada": "Personalized",
    "Arquitetura de potência": "Power Architecture",
}

def _(texto, idioma):
    if idioma == "EN":
        return TRANSLATIONS_EN.get(texto, texto)
    return texto

def set_dark_titlebar(window, use_dark=True):
    def apply_dark():
        try:
            window.update()
            if sys.platform == "win32":
                import ctypes
                try:
                    hwnd = int(window.wm_frame(), 16)
                except Exception:
                    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
                value = ctypes.c_int(2 if use_dark else 0)
                try:
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
                except Exception:
                    pass
                value = ctypes.c_int(1 if use_dark else 0)
                try:
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
                except Exception:
                    pass
                try:
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(value), ctypes.sizeof(value))
                except Exception:
                    pass
        except Exception:
            pass
    apply_dark()
    try:
        window.after(100, apply_dark)
    except Exception:
        pass

def definir_icone(root_win):

    if not tkinter_disponivel:
        return
    local_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pegasus_icon.png")
    local_ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pegasus_icon.ico")
    
    if sys.platform == "win32":
        try:
            if not os.path.exists(local_ico) and os.path.exists(local_png) and pil_disponivel:
                img_pil = Image.open(local_png)
                img_pil.save(local_ico, format="ICO")
            if os.path.exists(local_ico):
                root_win.iconbitmap(local_ico)
                return
        except Exception as e:
            print(f"Erro ao usar iconbitmap: {e}")

    if os.path.exists(local_png):
        try:
            if pil_disponivel:
                img_pil = Image.open(local_png)
                icon_img = ImageTk.PhotoImage(img_pil)
            else:
                icon_img = tk.PhotoImage(file=local_png)
            root_win.iconphoto(True, icon_img)
            root_win.icon_img_ref = icon_img
        except Exception as e:
            print(_pi(f"Erro ao carregar ícone: {e}", f"Error loading icon: {e}"))



def obter_base_dir():
    destino = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Pegasus"
    destino.mkdir(parents=True, exist_ok=True)
    return str(destino)


def abrir_pasta_no_sistema(caminho, titulo="Pasta", criar=True, parent=None):
    try:
        caminho = os.path.abspath(caminho)
        if criar and not os.path.exists(caminho):
            os.makedirs(caminho, exist_ok=True)

        if not os.path.exists(caminho):
            if tkinter_disponivel:
                messagebox.showerror(titulo, _p(f"Pasta não encontrada:\n{caminho}",
                                                f"Folder not found:\n{caminho}"), parent=parent)
            else:
                print(_p(f"Pasta não encontrada: {caminho}", f"Folder not found: {caminho}"))
            return False

        if sys.platform == "win32":
            os.startfile(caminho)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", caminho])
        else:
            subprocess.Popen(["xdg-open", caminho])
        return True
    except Exception as erro:
        if tkinter_disponivel:
            messagebox.showerror(titulo, _p(f"Não foi possível abrir:\n{caminho}\n\nErro: {erro}",
                                            f"Could not open:\n{caminho}\n\nError: {erro}"), parent=parent)
        else:
            print(_p(f"Não foi possível abrir {caminho}: {erro}", f"Could not open {caminho}: {erro}"))
        return False


def iniciar_gmat_externo(executavel, script):
    # Restore the Windows DLL search path for the external GMAT process.
    import ctypes
    frozen = getattr(sys, "frozen", False) and sys.platform == "win32"
    if frozen:
        ctypes.windll.kernel32.SetDllDirectoryW(None)
    try:
        return subprocess.Popen([executavel, script], cwd=os.path.dirname(executavel))
    finally:
        if frozen:
            ctypes.windll.kernel32.SetDllDirectoryW(sys._MEIPASS)


def localizar_executavel_gmat():
    candidatos = []

    try:
        _load_path = os.path.join(obter_base_dir(), "load_gmat.py")
        if os.path.exists(_load_path):
            with open(_load_path, "r", encoding="utf-8", errors="replace") as _lf:
                for _linha in _lf:
                    _m = re.match(r'\s*GmatBinPath\s*=\s*r?"([^"]+)"', _linha)
                    if not _m:
                        _m = re.match(r"\s*GmatBinPath\s*=\s*r?'([^']+)'", _linha)
                    if _m:
                        _bin_path = _m.group(1)
                        candidatos.extend([
                            os.path.join(_bin_path, "GMAT.exe"),
                            os.path.join(_bin_path, "GMAT_Beta.exe"),
                            os.path.join(_bin_path, "gmat.exe"),
                            os.path.join(_bin_path, "GmatConsole.exe"),
                        ])
                        break
    except Exception:
        pass

    gmat_bin = globals().get("GmatBinPath", "")
    if gmat_bin:
        candidatos.extend([
            os.path.join(gmat_bin, "GMAT.exe"),
            os.path.join(gmat_bin, "GMAT_Beta.exe"),
            os.path.join(gmat_bin, "gmat.exe"),
            os.path.join(gmat_bin, "GmatConsole.exe"),
        ])

    for candidato in candidatos:
        if candidato and os.path.exists(candidato):
            return candidato
    return None


def inserir_graficos_no_script(caminho_script):
    try:
        if not os.path.exists(caminho_script):
            return
        with open(caminho_script, "r", encoding="utf-8", errors="replace") as _f:
            conteudo = _f.read()
        if "OpenFramesInterface" in conteudo or "GroundTrack" in conteudo:
            return 
        graficos_block = """
%----------------------------------------
%---------- Visualizacao orbital
%----------------------------------------

Create OpenFramesInterface DefaultOrbitView;
DefaultOrbitView.SolverIterations = Current;
DefaultOrbitView.UpperLeft = [ 0.019 0.040 ];
DefaultOrbitView.Size = [ 0.599 0.599 ];
DefaultOrbitView.RelativeZOrder = 27;
DefaultOrbitView.Maximized = false;
DefaultOrbitView.Add = {DefaultSC, Earth};
DefaultOrbitView.View = {DefaultOrbitView_View};
DefaultOrbitView.CoordinateSystem = EarthMJ2000Eq;
DefaultOrbitView.DrawObject = [ true true ];
DefaultOrbitView.DrawTrajectory = [ true true ];
DefaultOrbitView.DrawAxes = [ false false ];
DefaultOrbitView.DrawXYPlane = [ false false ];
DefaultOrbitView.DrawLabel = [ true true ];
DefaultOrbitView.DrawUsePropLabel = [ false false ];
DefaultOrbitView.DrawCenterPoint = [ true true ];
DefaultOrbitView.DrawEndPoints = [ true true ];
DefaultOrbitView.DrawVelocity = [ false false ];
DefaultOrbitView.DrawGrid = [ false false ];
DefaultOrbitView.DrawLineWidth = [ 2 2 ];
DefaultOrbitView.DrawMarkerSize = [ 10 10 ];
DefaultOrbitView.DrawFontSize = [ 20 20 ];
DefaultOrbitView.Axes = On;
DefaultOrbitView.AxesLength = 12756.2726;
DefaultOrbitView.AxesLabels = On;
DefaultOrbitView.FrameLabel = Off;
DefaultOrbitView.XYPlane = On;
DefaultOrbitView.EclipticPlane = Off;
DefaultOrbitView.EnableStars = On;
DefaultOrbitView.StarCatalog = 'inp_StarsHYGv3.txt';
DefaultOrbitView.StarCount = 40000;
DefaultOrbitView.MinStarMag = -2;
DefaultOrbitView.MaxStarMag = 6;
DefaultOrbitView.MinStarPixels = 1;
DefaultOrbitView.MaxStarPixels = 10;
DefaultOrbitView.MinStarDimRatio = 0.5;
DefaultOrbitView.ShowPlot = true;
DefaultOrbitView.ShowToolbar = true;
DefaultOrbitView.SolverIterLastN = 0;
DefaultOrbitView.ShowVR = false;
DefaultOrbitView.PlaybackTimeScale = 3600;
DefaultOrbitView.MultisampleAntiAliasing = On;
DefaultOrbitView.MSAASamples = 2;
DefaultOrbitView.DrawFontPosition = {'Top-Right', 'Top-Right'};

Create GroundTrack DefaultGroundTrackPlot;
DefaultGroundTrackPlot.SolverIterations = Current;
DefaultGroundTrackPlot.UpperLeft = [ 0.272 0.514 ];
DefaultGroundTrackPlot.Size = [ 0.500 0.450 ];
DefaultGroundTrackPlot.RelativeZOrder = 32;
DefaultGroundTrackPlot.Maximized = true;
DefaultGroundTrackPlot.CentralBody = Earth;
DefaultGroundTrackPlot.Add = {DefaultSC};
DefaultGroundTrackPlot.DataCollectFrequency = 1;
DefaultGroundTrackPlot.UpdatePlotFrequency = 50;
DefaultGroundTrackPlot.NumPointsToRedraw = 0;
DefaultGroundTrackPlot.MaxPlotPoints = 20000;
DefaultGroundTrackPlot.ShowPlot = true;

Create OpenFramesView DefaultOrbitView_View;
DefaultOrbitView_View.ViewFrame = CoordinateSystem;
DefaultOrbitView_View.ViewTrajectory = Off;
DefaultOrbitView_View.InertialFrame = Off;
DefaultOrbitView_View.SetDefaultLocation = On;
DefaultOrbitView_View.DefaultEye = [ 30000 0 0 ];
DefaultOrbitView_View.DefaultCenter = [ 0 0 0 ];
DefaultOrbitView_View.DefaultUp = [ 0 0 1 ];
DefaultOrbitView_View.SetCurrentLocation = Off;
DefaultOrbitView_View.FOVy = 45;

"""
        conteudo = conteudo.replace("BeginMissionSequence;", graficos_block + "BeginMissionSequence;", 1)
        with open(caminho_script, "w", encoding="utf-8") as _f:
            _f.write(conteudo)
        print(_pi(f"Gráficos adicionados ao script: {os.path.basename(caminho_script)}",
                  f"Charts added to the script: {os.path.basename(caminho_script)}"))
    except Exception as e:
        print(_pi(f"Aviso: não foi possível adicionar gráficos ao script: {e}",
                  f"Warning: could not add charts to the script: {e}"))


def abrir_gmat(parent=None):
    gmat_exe = localizar_executavel_gmat()
    if gmat_exe is None:
        _idioma = globals().get("idioma_selecionado", "PT")
        if _idioma == "EN":
            msg = "Could not find the GMAT executable.\n\nCheck if load_gmat.py points to the correct folder."
        else:
            msg = "Não encontrei o executável do GMAT.\n\nVerifique se o arquivo load_gmat.py aponta para a pasta correta."
        if tkinter_disponivel:
            messagebox.showerror("GMAT", msg, parent=parent)
        else:
            print(msg)
        return False

    try:
        _idioma = globals().get("idioma_selecionado", "PT")
        _pasta = "Generated_Scripts_Pegasus" if _idioma == "EN" else "Scripts_Gerados_Pegasus"
        _pasta_path = os.path.join(obter_base_dir(), _pasta)
        
        if "epoch_campos_para_gmat" in globals():
            globals()["epoch_campos_para_gmat"]()
        
        _conteudo = globals().get("conteudo_script_gmat", "")
        if _conteudo:
            os.makedirs(_pasta_path, exist_ok=True)
            _caminho_novo = os.path.join(_pasta_path, f"Script_Pegasus_Execucao.script")
            with open(_caminho_novo, "w", encoding="utf-8") as f:
                try:
                    from __main__ import remover_acentos
                    f.write(remover_acentos(_conteudo))
                except:
                    f.write(_conteudo)
            
            if globals().get("visualizador", 's') == 's':
                try:
                    from __main__ import inserir_graficos_no_script
                    inserir_graficos_no_script(_caminho_novo)
                except:
                    pass
            
            import subprocess
            iniciar_gmat_externo(gmat_exe, _caminho_novo)
            return True
            
    except Exception as e:
        print(f"Erro ao abrir GMAT: {e}")
        pass
    return False


def abrir_pasta_scripts(parent=None):
    _idioma = globals().get("idioma_selecionado", "PT")
    _pasta = "Generated_Scripts_Pegasus" if _idioma == "EN" else "Scripts_Gerados_Pegasus"
    return abrir_pasta_no_sistema(
        os.path.join(obter_base_dir(), _pasta),
        titulo="Scripts GMAT",
        criar=True,
        parent=parent,
    )


def abrir_pasta_resultados(parent=None):
    _idioma = globals().get("idioma_selecionado", "PT")
    _pasta = "Results_Pegasus" if _idioma == "EN" else "Resultados_Pegasus"
    return abrir_pasta_no_sistema(
        os.path.join(obter_base_dir(), _pasta),
        titulo="Resultados Pegasus",
        criar=True,
        parent=parent,
    )



def confirmacao_personalizada(titulo, mensagem, parent, idioma, tipo="confirm"):
    resposta = [False]
    dialog = tk.Toplevel(parent)
    dialog.title(titulo)
    dialog.geometry("380x180")
    dialog.resizable(False, False)
    if parent: dialog.transient(parent)
    
    try:
        escuro = estado_tema.get("escuro", True)
    except:
        escuro = True
        
    bg_color = "#111827" if escuro else "#e5e7eb"
    fg_color = "#f3f4f6" if escuro else "#111827"
    dialog.config(bg=bg_color)
    
    tk.Label(dialog, text=mensagem, bg=bg_color, fg=fg_color, wraplength=340, justify="left").pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
    
    frame_btn = tk.Frame(dialog, bg=bg_color)
    frame_btn.pack(side=tk.BOTTOM, pady=10)
    
    def on_sim(): resposta[0] = True; dialog.destroy()
    def on_nao(): resposta[0] = False; dialog.destroy()
    
    btn_bg = "#eab308" if escuro else "#d1d5db"
    if tipo == "confirm":
        btn_sim = tk.Button(frame_btn, text="Yes" if idioma=="EN" else "Sim", width=10, bg=btn_bg, fg="black", font=("Segoe UI", 9, "bold"), command=on_sim)
        btn_sim.pack(side=tk.LEFT, padx=10)
        btn_nao = tk.Button(frame_btn, text="No" if idioma=="EN" else "Não", width=10, bg="#374151" if escuro else "#cbd5e1", fg="white" if escuro else "black", command=on_nao)
        btn_nao.pack(side=tk.LEFT, padx=10)
    else:
        btn_ok = tk.Button(frame_btn, text="OK", width=10, bg=btn_bg, fg="black", font=("Segoe UI", 9, "bold"), command=on_sim)
        btn_ok.pack(side=tk.LEFT, padx=10)
    
    dialog.grab_set()
    if parent:
        parent.wait_window(dialog)
    else:
        dialog.wait_window(dialog)
    return resposta[0]

def mostrar_erro_input(mensagem, parent=None, idioma="PT"):
    if not tkinter_disponivel:
        print(mensagem)
        return
    BORDO     = "#6e1423"
    BORDO_HDR = "#4a0d18"
    dialog = tk.Toplevel(parent) if parent is not None else tk.Tk()
    try:
        definir_icone(dialog)
    except Exception:
        pass
    dialog.title(_("Entrada inválida", idioma))
    dialog.geometry("420x190")
    dialog.resizable(False, False)
    if parent is not None:
        dialog.transient(parent)
    dialog.configure(bg=BORDO)
    try:
        set_dark_titlebar(dialog, True)
    except Exception:
        pass
    tk.Label(dialog, text="⚠  " + (_("Erro de entrada", idioma) if idioma != "EN" else "Input error"),
             bg=BORDO_HDR, fg="white", font=("Segoe UI", 11, "bold"),
             anchor="w", padx=12, pady=8).pack(fill=tk.X)
    tk.Label(dialog, text=mensagem, bg=BORDO, fg="#ffdede", wraplength=380, justify="left",
             font=("Segoe UI", 10)).pack(pady=18, padx=18, fill=tk.BOTH, expand=True)
    tk.Button(dialog, text="OK", width=10, bg="#f3d2d2", fg="#4a0d18",
              font=("Segoe UI", 9, "bold"), command=dialog.destroy).pack(side=tk.BOTTOM, pady=12)
    dialog.grab_set()
    if parent is not None:
        parent.wait_window(dialog)
    else:
        dialog.wait_window(dialog)

def reiniciar_aplicacao(parent=None, confirmar=True, idioma="PT"):
    try:
        if confirmar and tkinter_disponivel:
            _msg = "Deseja voltar ao menu inicial?\n\nA ferramenta será reiniciada em uma nova janela. Confira se você salvou ou copiou as informações necessárias antes de continuar." if idioma != "EN" else "Do you want to return to the main menu?\n\nThe tool will be restarted in a new window. Make sure you have saved or copied any necessary information before continuing."
            resposta = confirmacao_personalizada(
                "Pegasus",
                _msg,
                parent=parent,
                idioma=idioma
            )
            if not resposta:
                return False

        script_atual = os.path.abspath(__file__)
        _idioma_atual = globals().get("idioma_selecionado", "PT")
        if getattr(sys, "frozen", False):
            subprocess.Popen([sys.executable, _idioma_atual],
                             env={**os.environ, "PYINSTALLER_RESET_ENVIRONMENT": "1"})
        else:
            subprocess.Popen([sys.executable, script_atual, _idioma_atual], cwd=os.path.dirname(script_atual))

        try:
            if parent is not None:
                parent.destroy()
        except Exception:
            pass

        sys.exit(0)
    except SystemExit:
        raise
    except Exception as erro:
        if tkinter_disponivel:
            _err_msg = f"Não foi possível voltar ao menu inicial.\n\nErro: {erro}" if idioma != "EN" else f"Could not return to the main menu.\n\nError: {erro}"
            messagebox.showerror("Pegasus", _err_msg, parent=parent)
        else:
            print(f"Não foi possível voltar ao menu inicial: {erro}")
        return False




class ToolTip:
    _TIMEOUT_MS = 4000 

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self._after_id = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
        widget.bind("<FocusIn>", self.show)
        widget.bind("<FocusOut>", self.hide)
        widget.bind("<ButtonPress>", self.hide)

    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 18
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            lbl = tk.Label(
                tw,
                text=self.text,
                justify=tk.LEFT,
                background="#111827",
                foreground="white",
                relief=tk.SOLID,
                borderwidth=1,
                padx=7,
                pady=4,
                font=("Segoe UI", 9),
                wraplength=360,
            )
            lbl.pack()
            self._after_id = self.widget.after(self._TIMEOUT_MS, self.hide)
        except Exception:
            self.tipwindow = None

    def hide(self, event=None):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        try:
            if self.tipwindow:
                self.tipwindow.destroy()
        except Exception:
            pass
        self.tipwindow = None


def configurar_validacao_visual(entry, var, validador, mensagem="", status_label=None):
    def get_cores():
        try:
            escuro = globals().get("estado_tema", {}).get("escuro", False)
        except Exception:
            escuro = False
        return {"ok": "#e5e7eb" if not escuro else "#374151", "erro": "#450a0a" if escuro else "#fee2e2"}

    try:
        entry.configure(bg=get_cores()["ok"])
    except Exception:
        pass
    if mensagem:
        try:
            ToolTip(entry, mensagem)
        except Exception:
            pass

    def validar(*_args):
        cores = get_cores()
        try:
            validador(var.get())
            try:
                entry.configure(bg=cores["ok"])
            except Exception:
                pass
            if status_label is not None:
                status_label.config(text="", fg="#16a34a")
            return True
        except Exception as erro:
            try:
                entry.configure(bg=cores["erro"])
            except Exception:
                pass
            if status_label is not None:
                status_label.config(text=f"⚠ {erro}", fg="#ef4444" if get_cores()["ok"] == "#374151" else "#dc2626")
            return False

    try:
        var.trace_add("write", validar)
    except Exception:
        pass
    try:
        entry.bind("<FocusOut>", lambda e: validar())
    except Exception:
        pass
    validar()
    return validar


def exportar_texto_resumo(texto, parent=None, nome_padrao="relatorio_pegasus.txt"):
    if not tkinter_disponivel:
        return
    try:
        from tkinter import filedialog
        caminho = filedialog.asksaveasfilename(
            parent=parent,
            title=_p("Exportar relatório", "Export report"),
            defaultextension=".txt",
            initialfile=nome_padrao,
            filetypes=[(_p("Arquivo de texto", "Text file"), "*.txt"),
                       (_p("Todos os arquivos", "All files"), "*.*")],
        )
        if not caminho:
            return
        Path(caminho).write_text(texto, encoding="utf-8")
        messagebox.showinfo("Pegasus", _p(f"Relatório salvo em:\n{caminho}", f"Report saved to:\n{caminho}"), parent=parent)
    except Exception as erro:
        messagebox.showerror("Pegasus", _p(f"Não foi possível exportar o relatório.\n\nErro: {erro}",
                                           f"Could not export the report.\n\nError: {erro}"), parent=parent)


def criar_treeview_periodos(parent, texto_saida):
    _idioma = globals().get("idioma_selecionado", "PT")
    res_orbitas = globals().get("_res_orbitas_periodos", None)

    _escuro = estado_tema.get("escuro", True)
    _bg = "#111827" if _escuro else "#d7dce2"
    _fg = "#f3f4f6" if _escuro else "#111827"
    _row_bg = "#1f2937" if _escuro else "#e5e7eb"
    _sel_bg = "#2563eb"

    def _aplicar_estilo_treeview(top, style_name):
        style = ttk.Style(top)
        style.theme_use("clam")
        style.configure(style_name,
            background=_row_bg, foreground=_fg,
            fieldbackground=_row_bg,
            rowheight=26, font=("Consolas", 10))
        style.configure(f"{style_name}.Heading",
            background="#374151" if _escuro else "#94a3b8",
            foreground=_fg, font=("Segoe UI", 10, "bold"))
        style.map(style_name, background=[("selected", _sel_bg)])

    def _criar_top(titulo, geom):
        top = tk.Toplevel(parent)
        top.title(titulo)
        top.geometry(geom)
        top.configure(bg=_bg)
        definir_icone(top)
        set_dark_titlebar(top, _escuro)
        return top

    if res_orbitas:
        top = _criar_top("Periods Table" if _idioma == "EN" else "Tabela de Períodos", "520x360")
        _aplicar_estilo_treeview(top, "Periodos.Treeview")

        frame = tk.Frame(top, bg=_bg)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ("num", "duracao", "p_media", "n_pts")
        hdrs = ("Period", "Duration (s)", "Avg Power (W)", "Timesteps") if _idioma == "EN" else ("Período", "Duração (s)", "P_media (W)", "Pontos")
        tree = ttk.Treeview(frame, columns=cols, show="headings", style="Periodos.Treeview")
        for col, hdr in zip(cols, hdrs):
            tree.heading(col, text=hdr)
            tree.column(col, width=110, anchor="center")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        for i, r in enumerate(res_orbitas, start=1):
            tree.insert("", tk.END, values=(i, f"{r['duracao_s']:.1f}", f"{r['P_media']:.4f}", r.get("n_timesteps", "")))
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return top

    linhas = texto_saida.splitlines()
    candidatos = []
    for linha in linhas:
        if re.match(r"^\s*\d+\s+", linha) and any(ch in linha for ch in [":", "."]):
            partes = linha.split()
            if len(partes) >= 3:
                candidatos.append(partes)
    if not candidatos:
        _msg = "No period table available. Run solar panel analysis first." if _idioma == "EN" else "Nenhuma tabela disponível. Execute primeiro a análise de painéis solares."
        messagebox.showwarning("Pegasus", _msg, parent=parent)
        return None

    top = _criar_top("Periods Table" if _idioma == "EN" else "Tabela de Períodos", "600x300")
    _aplicar_estilo_treeview(top, "Periodos.Treeview")

    frame = tk.Frame(top, bg=_bg)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree = ttk.Treeview(frame, columns=("c1", "c2", "c3", "c4", "c5"), show="headings", style="Periodos.Treeview")
    for i, col in enumerate(tree["columns"], start=1):
        tree.heading(col, text=f"Campo {i}")
        tree.column(col, width=110, anchor="center")

    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    for partes in candidatos:
        vals = (partes + [""] * 5)[:5]
        tree.insert("", tk.END, values=vals)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    return top


def _pi(pt, en):
    return en if globals().get("idioma_selecionado") == "EN" else pt

def input_float(prompt, min_val=None, max_val=None, default=None):
    while True:
        try:
            _raw = input(prompt)
            if default is not None and str(_raw).strip() == "":
                return default
            valor = float(_raw)
            if min_val is not None and valor < min_val:
                print(_pi(f"  ERRO: O valor mínimo permitido é {min_val}. Tente novamente.",
                          f"  ERROR: The minimum allowed value is {min_val}. Try again."))
                continue
            if max_val is not None and valor > max_val:
                print(_pi(f"  ERRO: O valor máximo permitido é {max_val}. Tente novamente.",
                          f"  ERROR: The maximum allowed value is {max_val}. Try again."))
                continue
            return valor
        except ValueError:
            print(_pi("  ERRO: Entrada inválida. Digite um número.",
                      "  ERROR: Invalid input. Enter a number."))

def input_int(prompt, opcoes_validas=None, min_val=None, max_val=None):
    while True:
        try:
            valor = int(input(prompt))
            if opcoes_validas is not None and valor not in opcoes_validas:
                print(_pi(f"  ERRO: Opção inválida. Escolha entre: {opcoes_validas}.",
                          f"  ERROR: Invalid option. Choose from: {opcoes_validas}."))
                continue
            if min_val is not None and valor < min_val:
                print(_pi(f"  ERRO: O valor mínimo permitido é {min_val}. Tente novamente.",
                          f"  ERROR: The minimum allowed value is {min_val}. Try again."))
                continue
            if max_val is not None and valor > max_val:
                print(_pi(f"  ERRO: O valor máximo permitido é {max_val}. Tente novamente.",
                          f"  ERROR: The maximum allowed value is {max_val}. Try again."))
                continue
            return valor
        except ValueError:
            print(_pi("  ERRO: Entrada inválida. Digite um número inteiro.",
                      "  ERROR: Invalid input. Enter an integer."))

def input_sn(prompt):
    while True:
        resposta = input(prompt).strip().lower()
        if resposta in ('s', 'n', 'y'):
            return 's' if resposta == 'y' else resposta
        _err_sn = "  ERROR: Enter 'y' for yes or 'n' for no." if idioma_selecionado == "EN" else "  ERRO: Digite 's' para sim ou 'n' para não."
        print(_err_sn)

def input_texto(prompt, default=""):
    valor = input(prompt).strip()
    return valor if valor else default



def areas_cubesat(dx, dy, dz):
    return {
        '+X': dy * dz,
        '-X': dy * dz,
        '+Y': dx * dz,
        '-Y': dx * dz,
        '+Z': dx * dy,
        '-Z': dx * dy,}
FACES = {
    '+X': np.array([ 1.,  0.,  0.]),
    '-X': np.array([-1.,  0.,  0.]),
    '+Y': np.array([ 0.,  1.,  0.]),
    '-Y': np.array([ 0., -1.,  0.]),
    '+Z': np.array([ 0.,  0.,  1.]),
    '-Z': np.array([ 0.,  0., -1.]),
}

FACE_OPOSTA = {'+X': '-X', '-X': '+X', '+Y': '-Y', '-Y': '+Y', '+Z': '-Z', '-Z': '+Z'}


FILL_FACTOR = 6062.0 / 10000.0
RAIO_TERRA_KM = 6378.137
ALTITUDE_MINIMA_ORBITA_KM = 140.0
SMA_MINIMO_KM = RAIO_TERRA_KM + ALTITUDE_MINIMA_ORBITA_KM
ENCERRAR_INTERFACE = "__ENCERRAR_INTERFACE__"


def grade_cubesat(tamanho_u):
    grades = {
        1: (1, 1, 1),
        2: (1, 1, 2),
        3: (1, 1, 3),
        6: (1, 2, 3),
        12: (2, 2, 3),
    }
    return grades.get(tamanho_u, (1, 1, 1))


def projetar_iso(x, y, z, escala=62, origem=(390, 285)):
    px = origem[0] + escala * (x - y)
    py = origem[1] + escala * (0.52 * (x + y) - z)
    return px, py


def desenhar_seta(canvas, origem, destino, cor, texto):
    canvas.create_line(*origem, *destino, fill=cor, width=3, arrow=tk.LAST, arrowshape=(14, 18, 6))
    canvas.create_text(destino[0] + 12, destino[1], text=texto, fill=cor, font=("Segoe UI", 10, "bold"))


def coletar_geometria_por_interface(tamanho_u, areas, face_nadir_inicial='+Z', face_vel_inicial='+X'):
    if not tkinter_disponivel:
        return None

    lista_faces = list(FACES.keys())
    estado = {
        "modo": "nadir",
        "face_nadir": face_nadir_inicial,
        "face_vel": face_vel_inicial,
        "faces_solares": set(lista_faces),
        "confirmado": False,
    }

    try:
        root = tk.Tk()
    except tk.TclError:
        return None

    _escuro_geo = estado_tema.get("escuro", True)
    _bg_geo = "#111827" if _escuro_geo else "#d7dce2"
    _fg_geo = "#f3f4f6" if _escuro_geo else "#111827"
    _panel_geo = "#1f2937" if _escuro_geo else "#e5e7eb"
    _canvas_bg = "#1f2937" if _escuro_geo else "#e5e7eb"

    _idioma_geo = globals().get("idioma_selecionado", "PT")

    root.title("CubeSat Configuration - CDS Rev.14" if _idioma_geo == "EN" else "Configuração do CubeSat - CDS Rev.14")
    root.geometry("1060x720")
    root.minsize(980, 680)
    root.configure(bg=_bg_geo)
    set_dark_titlebar(root, _escuro_geo)
    definir_icone(root)

    cores_face = {
        "normal": "#475569" if _escuro_geo else "#d7dee8",
        "solar": "#f6c445",
        "nadir": "#9b6ef3",
        "vel": "#4f8df7",
        "bloqueada": "#334155" if _escuro_geo else "#9aa4b2",
    }
    _fg_face_sel = "#111827"
    _fg_face_normal = "white" if _escuro_geo else "#111827"
    _fg_face_blocked = "#6b7280" if _escuro_geo else "#475569"

    _left = tk.Frame(root, bg=_bg_geo)
    _left.pack(side=tk.LEFT, fill=tk.Y)
    _canvas_left = tk.Canvas(_left, bg=_bg_geo, highlightthickness=0, width=380)
    _sb_left = ttk.Scrollbar(_left, orient="vertical", command=_canvas_left.yview)
    _sb_left.pack(side=tk.RIGHT, fill=tk.Y)
    _canvas_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    _canvas_left.configure(yscrollcommand=_sb_left.set)
    painel = tk.Frame(_canvas_left, padx=14, pady=14, bg=_bg_geo)
    _win_left = _canvas_left.create_window((0, 0), window=painel, anchor="nw")
    painel.bind("<Configure>", lambda e: _canvas_left.configure(scrollregion=_canvas_left.bbox("all")))
    _canvas_left.bind("<Configure>", lambda e: _canvas_left.itemconfigure(_win_left, width=e.width))

    def _rolar_geo(ev):
        if painel.winfo_reqheight() > _canvas_left.winfo_height():
            _canvas_left.yview_scroll(int(-ev.delta / 120), "units")
    _canvas_left.bind("<Enter>", lambda e: _canvas_left.bind_all("<MouseWheel>", _rolar_geo))
    _canvas_left.bind("<Leave>", lambda e: _canvas_left.unbind_all("<MouseWheel>"))

    area_desenho = tk.Frame(root, padx=8, pady=8, bg=_panel_geo)
    area_desenho.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    _titulo_geo = "Face Configuration" if _idioma_geo == "EN" else "Configuração das faces"
    _ref_geo = "Reference CDS Rev.14: +X/-X, +Y/-Y, +Z/-Z" if _idioma_geo == "EN" else "Referencial CDS Rev.14: +X/-X, +Y/-Y, +Z/-Z"
    tk.Label(painel, text=_titulo_geo, font=("Segoe UI", 16, "bold"), anchor="w", bg=_bg_geo, fg=_fg_geo).pack(fill=tk.X)
    tk.Label(
        painel,
        text=_ref_geo,
        font=("Segoe UI", 9),
        fg="#9ca3af" if _escuro_geo else "#445",
        bg=_bg_geo,
        anchor="w",
    ).pack(fill=tk.X, pady=(0, 12))

    instrucao = tk.Label(painel, text="", justify=tk.LEFT, wraplength=300, anchor="w", font=("Segoe UI", 10), bg=_bg_geo, fg=_fg_geo)
    instrucao.pack(fill=tk.X, pady=(0, 10))

    modo_var = tk.StringVar(value=estado["modo"])

    def set_modo(modo):
        estado["modo"] = modo
        modo_var.set(modo)
        atualizar()

    botoes_modo = tk.Frame(painel, bg=_bg_geo)
    botoes_modo.pack(fill=tk.X, pady=(0, 12))
    _modos_geo = [("Nadir" if _idioma_geo != "EN" else "Nadir", "nadir"),
                  ("Velocidade" if _idioma_geo != "EN" else "Velocity", "vel"),
                  ("Painéis" if _idioma_geo != "EN" else "Panels", "solar")]
    for texto, modo in _modos_geo:
        tk.Radiobutton(
            botoes_modo,
            text=texto,
            value=modo,
            variable=modo_var,
            command=lambda m=modo: set_modo(m),
            bg=_bg_geo, fg=_fg_geo,
            selectcolor={"nadir": "#9b6ef3", "vel": "#4f8df7", "solar": "#f6c445"}[modo],
            activebackground=_bg_geo, activeforeground=_fg_geo,
            indicatoron=False,
            width=10,
            padx=4,
            pady=7,
        ).pack(side=tk.LEFT, padx=(0, 6))

    _qf_txt = "Selectable faces" if _idioma_geo == "EN" else "Faces selecionáveis"
    quadro_faces = tk.LabelFrame(painel, text=_qf_txt, padx=10, pady=10, bg=_bg_geo, fg=_fg_geo)
    quadro_faces.pack(fill=tk.X)
    botoes_faces = {}

    def face_permitida_para_vel(face):
        return face != estado["face_nadir"] and face != FACE_OPOSTA[estado["face_nadir"]]

    def selecionar_face(face):
        if estado["modo"] == "nadir":
            estado["face_nadir"] = face
            if estado["face_vel"] == face or estado["face_vel"] == FACE_OPOSTA[face]:
                opcoes = [f for f in lista_faces if f != face and f != FACE_OPOSTA[face]]
                estado["face_vel"] = opcoes[0]
            estado["faces_solares"].discard(face)
        elif estado["modo"] == "vel":
            if not face_permitida_para_vel(face):
                _t = "Invalid face" if _idioma_geo == "EN" else "Face inválida"
                _m = "The velocity face cannot be equal or opposite to the nadir face." if _idioma_geo == "EN" else "A face de velocidade não pode ser igual nem oposta à face nadir."
                messagebox.showwarning(_t, _m, parent=root)
                return
            estado["face_vel"] = face
        else:
            if face in estado["faces_solares"]:
                estado["faces_solares"].remove(face)
            else:
                estado["faces_solares"].add(face)
        atualizar()

    for i, face in enumerate(lista_faces):
        botao = tk.Button(
            quadro_faces,
            text=f"{face}\n{areas[face]*1e4:.0f} cm²",
            width=10,
            height=2,
            bg=cores_face["normal"],
            fg=_fg_face_normal,
            activebackground=cores_face["normal"],
            command=lambda f=face: selecionar_face(f),
        )
        botao.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="nsew")
        botoes_faces[face] = botao

    _res_txt = "Summary" if _idioma_geo == "EN" else "Resumo"
    resumo = tk.LabelFrame(painel, text=_res_txt, padx=10, pady=10, bg=_bg_geo, fg=_fg_geo)
    resumo.pack(fill=tk.X, pady=12)
    label_resumo = tk.Label(resumo, justify=tk.LEFT, anchor="w", font=("Consolas", 10), bg=_bg_geo, fg=_fg_geo)
    label_resumo.pack(fill=tk.X)

    _legenda_txt = "Colors: purple = nadir, blue = velocity, yellow = solar panel." if _idioma_geo == "EN" else "Cores: roxo = nadir, azul = velocidade, amarelo = painel solar."
    tk.Label(
        painel,
        text=_legenda_txt,
        wraplength=300,
        justify=tk.LEFT,
        fg="#9ca3af" if _escuro_geo else "#334",
        bg=_bg_geo,
    ).pack(fill=tk.X, pady=(0, 12))

    canvas = tk.Canvas(area_desenho, bg=_canvas_bg, highlightthickness=1, highlightbackground="#4b5563" if _escuro_geo else "#cbd5e1")
    canvas.pack(expand=True, fill=tk.BOTH)

    def cor_da_face_3d(face):
        if face == estado["face_nadir"]:
            return cores_face["nadir"]
        if face == estado["face_vel"]:
            return cores_face["vel"]
        if face in estado["faces_solares"]:
            return cores_face["solar"]
        return cores_face["normal"]

    def desenhar_cubo(ix, iy, iz, nx, ny, nz):
        x0 = ix - nx / 2
        x1 = ix + 1 - nx / 2
        y0 = iy - ny / 2
        y1 = iy + 1 - ny / 2
        z0 = iz - nz / 2
        z1 = iz + 1 - nz / 2

        pontos = {
            "000": projetar_iso(x0, y0, z0),
            "100": projetar_iso(x1, y0, z0),
            "010": projetar_iso(x0, y1, z0),
            "110": projetar_iso(x1, y1, z0),
            "001": projetar_iso(x0, y0, z1),
            "101": projetar_iso(x1, y0, z1),
            "011": projetar_iso(x0, y1, z1),
            "111": projetar_iso(x1, y1, z1),
        }

        faces_visiveis = [
            ("+Y", [pontos["010"], pontos["110"], pontos["111"], pontos["011"]]),
            ("+X", [pontos["100"], pontos["110"], pontos["111"], pontos["101"]]),
            ("+Z", [pontos["001"], pontos["101"], pontos["111"], pontos["011"]]),
        ]
        for face, pts in faces_visiveis:
            canvas.create_polygon(pts, fill=cor_da_face_3d(face), outline="#64748b", width=1.2)

    def desenhar_satelite():
        nx, ny, nz = grade_cubesat(tamanho_u)
        for iz in range(nz):
            for iy in range(ny):
                for ix in range(nx):
                    desenhar_cubo(ix, iy, iz, nx, ny, nz)

        origem = projetar_iso(0, 0, -nz / 2 - 0.1)
        desenhar_seta(canvas, origem, projetar_iso(nx / 2 + 1.0, 0, -nz / 2 - 0.1), "#dc2626", "+X")
        desenhar_seta(canvas, origem, projetar_iso(0, ny / 2 + 1.0, -nz / 2 - 0.1), "#16a34a", "+Y")
        desenhar_seta(canvas, origem, projetar_iso(0, 0, nz / 2 + 0.9), "#2563eb", "+Z")

        _txt_fill = "#f3f4f6" if _escuro_geo else "#1f2937"
        _txt_sub = "#9ca3af" if _escuro_geo else "#475569"
        canvas.create_text(390, 34, text=f"CubeSat {tamanho_u}U", font=("Segoe UI", 15, "bold"), fill=_txt_fill)
        _hidden_txt = "Hidden faces (-X, -Y, -Z) are also configured via the buttons." if _idioma_geo == "EN" else "Faces ocultas (-X, -Y e -Z) também são configuradas pelos botões à esquerda."
        canvas.create_text(390, 58, text=_hidden_txt, font=("Segoe UI", 10), fill=_txt_sub)

    def atualizar():
        if estado["modo"] == "nadir":
            _txt = "Choose the face pointing toward Earth (nadir)." if _idioma_geo == "EN" else "Escolha a face que aponta para a Terra (nadir)."
        elif estado["modo"] == "vel":
            _txt = "Choose the face aligned with orbital velocity. Cannot be the nadir face or its opposite." if _idioma_geo == "EN" else "Escolha a face alinhada com a velocidade orbital. Não pode ser a face nadir nem a oposta."
        else:
            _txt = "Click faces that will have solar cells. Any face can be selected." if _idioma_geo == "EN" else "Clique nas faces que terão células solares. Qualquer face pode ser selecionada."
        instrucao.config(text=_txt)

        for face, botao in botoes_faces.items():
            bg = cores_face["normal"]
            estado_botao = tk.NORMAL
            if estado["modo"] == "nadir":
                if face == estado["face_nadir"]: bg = cores_face["nadir"]
            elif estado["modo"] == "vel":
                if face == estado["face_vel"]: bg = cores_face["vel"]
                elif not face_permitida_para_vel(face): bg = cores_face["bloqueada"]
            elif estado["modo"] == "solar":
                if face in estado["faces_solares"]: bg = cores_face["solar"]

            if estado["modo"] == "vel" and not face_permitida_para_vel(face):
                estado_botao = tk.DISABLED

            _blocked = bg == cores_face["bloqueada"]
            _selected = bg not in (cores_face["normal"], cores_face["bloqueada"])
            _fg_btn = _fg_face_sel if _selected else (_fg_face_blocked if _blocked else _fg_face_normal)
            botao.config(bg=bg, activebackground=bg, fg=_fg_btn, state=estado_botao)

        _none_txt = "none" if _idioma_geo == "EN" else "nenhuma"
        solares = ", ".join(sorted(estado["faces_solares"])) or _none_txt
        _vel_lbl = "Velocity" if _idioma_geo == "EN" else "Velocidade"
        _pan_lbl = "Panels" if _idioma_geo == "EN" else "Painéis"
        label_resumo.config(
            text=(
                f"Nadir:      {estado['face_nadir']}\n"
                f"{_vel_lbl}: {estado['face_vel']}\n"
                f"{_pan_lbl}:    {solares}"
            )
        )
        canvas.delete("all")
        desenhar_satelite()

    def confirmar():
        estado["confirmado"] = True
        root.destroy()

    _btn_conf_txt = "Confirm configuration" if _idioma_geo == "EN" else "Confirmar configuração"
    _btn_cancel_txt = "Cancel and use terminal" if _idioma_geo == "EN" else "Cancelar e usar terminal"
    btn_sim_bg = "#eab308" if _escuro_geo else "#243447"
    btn_sim_fg = "#111827" if _escuro_geo else "white"
    tk.Button(painel, text=_btn_conf_txt, font=("Segoe UI", 10, "bold"), command=confirmar, height=2, bg=btn_sim_bg, fg=btn_sim_fg).pack(fill=tk.X, pady=(4, 8))
    tk.Button(painel, text=_btn_cancel_txt, command=root.destroy, bg=_bg_geo, fg=_fg_geo).pack(fill=tk.X)

    atualizar()
    root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
    abrir_maximizada(root, 1060, 720)
    root.mainloop()

    if not estado["confirmado"]:
        return None
    return estado["face_nadir"], estado["face_vel"], {f: (f in estado["faces_solares"]) for f in lista_faces}


def coletar_parametros_por_interface(gmat_disponivel, root=None, idioma="PT"):
    if not tkinter_disponivel:
        return None

    if root is None:
        try:
            root = tk.Tk()
            definir_icone(root)
        except tk.TclError:
            return None
    else:
        for widget in root.winfo_children():
            widget.destroy()
        root.resizable(True, True)

    resultado = {"dados": None}
    lista_faces = list(FACES.keys())
    face_nadir = {"valor": "+Z"}
    face_vel = {"valor": "+X"}
    faces_solares = set(lista_faces)

    orbitas = {
        "LEO exemplo": {"codigo": 4, "sma": 6778.0, "ecc": 0.01, "inc": 49.11, "raan": 30.0, "aop": 0.0, "ta": 0.0},
        "Molnya": {"codigo": 2, "sma": 26553.0, "ecc": 0.737, "inc": 63.4, "raan": 0.0, "aop": 0.0, "ta": 0.0},
        "Geoestacionária": {"codigo": 3, "sma": 42178.0, "ecc": 0.0, "inc": 0.0, "raan": 0.0, "aop": 0.0, "ta": 0.0},
        "Personalizada": {"codigo": 1, "sma": SMA_MINIMO_KM, "ecc": 0.0, "inc": 0.0, "raan": 0.0, "aop": 0.0, "ta": 0.0},
    }
    cubesats = {
        "1U": {"codigo": 1, "dx": 0.100, "dy": 0.100, "dz": 0.1135, "grade": (1, 1, 1), "massa": 2.0},
        "2U": {"codigo": 2, "dx": 0.100, "dy": 0.100, "dz": 0.2270, "grade": (1, 1, 2), "massa": 4.0},
        "3U": {"codigo": 3, "dx": 0.100, "dy": 0.100, "dz": 0.3405, "grade": (1, 1, 3), "massa": 6.0},
        "6U": {"codigo": 6, "dx": 0.100, "dy": 0.2263, "dz": 0.3405, "grade": (1, 2, 3), "massa": 12.0},
        "12U": {"codigo": 12, "dx": 0.2263, "dy": 0.2263, "dz": 0.3405, "grade": (2, 2, 3), "massa": 24.0},
    }

    root.title(_("Pegasus - Interface de Configuração", idioma))
    root.geometry("1280x780")
    root.minsize(1120, 700)
    try:
        root.state("zoomed")
    except Exception:
        pass
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=0, minsize=380)
    root.grid_columnconfigure(1, weight=1)

    painel_esquerdo = tk.Frame(root, bg="#e5e7eb", padx=10, pady=10, width=430)
    painel_esquerdo.grid(row=0, column=0, sticky="nsew")
    painel_esquerdo.grid_propagate(False)
    painel_esquerdo.grid_rowconfigure(0, weight=1)
    painel_esquerdo.grid_rowconfigure(2, weight=0)
    painel_esquerdo.grid_columnconfigure(0, weight=1)

    _form_container = tk.Frame(painel_esquerdo, bg="#e5e7eb")
    _form_container.grid(row=0, column=0, sticky="nsew")
    _canvas_form = tk.Canvas(_form_container, bg="#e5e7eb", highlightthickness=0)
    _sb_form = ttk.Scrollbar(_form_container, orient="vertical", command=_canvas_form.yview)
    _sb_form.pack(side=tk.RIGHT, fill=tk.Y)
    _canvas_form.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    _canvas_form.configure(yscrollcommand=_sb_form.set)
    notebook = tk.Frame(_canvas_form, bg="#e5e7eb")
    _win_form = _canvas_form.create_window((0, 0), window=notebook, anchor="nw")
    notebook.bind("<Configure>", lambda e: _canvas_form.configure(scrollregion=_canvas_form.bbox("all")))
    _canvas_form.bind("<Configure>", lambda e: _canvas_form.itemconfigure(_win_form, width=e.width))

    def _rolar_form(ev):
        if notebook.winfo_reqheight() > _canvas_form.winfo_height():
            _canvas_form.yview_scroll(int(-ev.delta / 120), "units")
    _canvas_form.bind("<Enter>", lambda e: _canvas_form.bind_all("<MouseWheel>", _rolar_form))
    _canvas_form.bind("<Leave>", lambda e: _canvas_form.unbind_all("<MouseWheel>"))

    form = tk.Frame(notebook, bg="#e5e7eb")

    status_validacao = tk.Label(
        painel_esquerdo,
        text="",
        bg="#e5e7eb",
        fg="#dc2626",
        anchor="w",
        font=("Segoe UI", 9),
        wraplength=480,
    )
    status_validacao.grid(row=1, column=0, sticky="ew", pady=(8, 0))

    comandos_esquerda = tk.Frame(painel_esquerdo, bg="#e5e7eb")
    comandos_esquerda.grid(row=2, column=0, sticky="ew", pady=(10, 0))

    area_visual = tk.Frame(root, bg="#e5e7eb", padx=10, pady=10)
    area_visual.grid(row=0, column=1, sticky="nsew")
    area_visual.grid_rowconfigure(1, weight=1)
    area_visual.grid_columnconfigure(0, weight=1)

    titulo = tk.Label(
        area_visual,
        text=_("Visualização (conforme CDS Rev. 14): arraste para girar, use a roda do mouse para aproximar", idioma),
        bg="#e5e7eb",
        fg="#111827",
        font=("Segoe UI", 12, "bold"),
        anchor="w",
    )
    titulo.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    canvas = tk.Canvas(area_visual, bg="#e5e7eb", highlightthickness=1, highlightbackground="#cbd5e1")
    canvas.grid(row=1, column=0, sticky="nsew")

    rodape = tk.Frame(area_visual, bg="#e5e7eb")
    rodape.grid(row=2, column=0, sticky="ew", pady=(8, 0))

    def secao(titulo, parent=None):
        titulo = _(titulo, idioma)
        if parent is None:
            parent = form
        frame = tk.LabelFrame(parent, text=titulo, padx=12, pady=12, bg="#e5e7eb", font=("Segoe UI", 11, "bold"), bd=1)
        frame.pack(fill=tk.X, padx=10, pady=8)
        return frame

    def linha(parent):
        frame = tk.Frame(parent, bg="#e5e7eb")
        frame.pack(fill=tk.X, pady=3)
        return frame

    def campo(parent, texto, var, state=tk.NORMAL, width=15):
        texto = _(texto, idioma)
        frame = linha(parent)
        tk.Label(frame, text=texto, bg="#e5e7eb", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ent = tk.Entry(frame, textvariable=var, width=width, state=state)
        ent.pack(side=tk.RIGHT)
        return ent

    def menu(parent, texto, var, opcoes, comando=None):
        texto = _(texto, idioma)
        opcoes = [_(op, idioma) for op in opcoes]
        frame = linha(parent)
        tk.Label(frame, text=texto, bg="#e5e7eb", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        opt = tk.OptionMenu(frame, var, *opcoes, command=comando)
        opt.config(width=15, highlightthickness=0, bd=1)
        opt.pack(side=tk.RIGHT)
        return opt

    def checkbox(parent, texto, var, comando=None):
        texto = _(texto, idioma)
        chk = tk.Checkbutton(parent, text=texto, variable=var, command=comando, bg="#e5e7eb", anchor="w", highlightthickness=0, bd=0)
        chk.pack(fill=tk.X, pady=3)
        return chk

    def set_estado(widgets, habilitado):
        estado = tk.NORMAL if habilitado else tk.DISABLED
        for widget in widgets:
            widget.config(state=estado)

    def ler_float(var, nome, minimo=None, maximo=None):
        try:
            valor = float(str(var.get()).replace(",", "."))
        except ValueError:
            raise ValueError(_("{}: digite um número válido.", idioma).format(_(nome, idioma)))
        if minimo is not None and valor < minimo:
            raise ValueError(_("{}: o valor mínimo permitido é {}.", idioma).format(_(nome, idioma), minimo))
        if maximo is not None and valor > maximo:
            raise ValueError(_("{}: o valor máximo permitido é {}.", idioma).format(_(nome, idioma), maximo))
        return valor

    def ler_int(var, nome, minimo=None, maximo=None):
        try:
            valor = int(str(var.get()))
        except ValueError:
            raise ValueError(_("{}: digite um número inteiro válido.", idioma).format(_(nome, idioma)))
        if minimo is not None and valor < minimo:
            raise ValueError(_("{}: o valor mínimo permitido é {}.", idioma).format(_(nome, idioma), minimo))
        if maximo is not None and valor > maximo:
            raise ValueError(_("{}: o valor máximo permitido é {}.", idioma).format(_(nome, idioma), maximo))
        return valor

    quadro_orbita = secao("Parte 1 - Órbita", notebook)
    _orbitas_pt = list(orbitas.keys())
    _orbitas_display = [_(k, idioma) for k in _orbitas_pt]
    _display_to_pt = {_(k, idioma): k for k in _orbitas_pt}
    orbita_display_var = tk.StringVar(value=_orbitas_display[0])
    orbita_var = tk.StringVar(value=_orbitas_pt[0])
    sma_var = tk.StringVar()
    ecc_var = tk.StringVar()
    inc_var = tk.StringVar()
    raan_var = tk.StringVar()
    aop_var = tk.StringVar()
    ta_var = tk.StringVar()
    entradas_orbita = {}

    def _on_orbita_change(_=None):
        orbita_var.set(_display_to_pt.get(orbita_display_var.get(), _orbitas_pt[0]))
        atualizar_orbita()

    _frame_orb = linha(quadro_orbita)
    tk.Label(_frame_orb, text=_("Configuração", idioma), bg="#e5e7eb", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
    _opt_orb = tk.OptionMenu(_frame_orb, orbita_display_var, *_orbitas_display, command=_on_orbita_change)
    _opt_orb.config(width=15, highlightthickness=0, bd=1)
    _opt_orb.pack(side=tk.RIGHT)

    entradas_orbita["sma"] = campo(quadro_orbita, "SMA [km]", sma_var)
    ToolTip(entradas_orbita["sma"], f"Semi-major axis in km. Minimum: {SMA_MINIMO_KM:.3f}" if idioma == "EN" else f"Semi-eixo maior em km. Mínimo: {SMA_MINIMO_KM:.3f}")
    entradas_orbita["ecc"] = campo(quadro_orbita, "ECC", ecc_var)
    ToolTip(entradas_orbita["ecc"], _("Excentricidade (0 a <1)", idioma))
    entradas_orbita["inc"] = campo(quadro_orbita, "INC [deg]", inc_var)
    ToolTip(entradas_orbita["inc"], _("Inclinação orbital (0 a 180º)", idioma))
    entradas_orbita["raan"] = campo(quadro_orbita, "RAAN [deg]", raan_var)
    ToolTip(entradas_orbita["raan"], _("Ascensão reta do nó ascendente (0 a 360º)", idioma))
    entradas_orbita["aop"] = campo(quadro_orbita, "AOP [deg]", aop_var)
    ToolTip(entradas_orbita["aop"], _("Argumento do perigeu (0 a 360º)", idioma))
    entradas_orbita["ta"] = campo(quadro_orbita, "TA [deg]", ta_var)
    ToolTip(entradas_orbita["ta"], _("Anomalia verdadeira (0 a 360º)", idioma))
    tk.Button(
        quadro_orbita,
        text="Restaurar padrões da órbita" if idioma != "EN" else "Restore orbit defaults",
        command=lambda: atualizar_orbita(),
        bg="#e5e7eb",
    ).pack(fill=tk.X, pady=(8, 0))

    quadro_sat = secao("Parte 2 - Satélite", notebook)
    cubesat_var = tk.StringVar(value="3U")
    dx_var = tk.StringVar()
    dy_var = tk.StringVar()
    dz_var = tk.StringVar()
    nx_var = tk.StringVar(value="1")
    ny_var = tk.StringVar(value="1")
    nz_var = tk.StringVar(value="3")
    massa_var = tk.StringVar(value="6")
    cd_var = tk.StringVar(value="2.2")
    cr_var = tk.StringVar(value="1.8")
    
    atitude_var = tk.StringVar(value="NadirPointing")
    tipo_ci_var = tk.StringVar(value="EulerAngles")
    ea1_var = tk.StringVar(value="0")
    ea2_var = tk.StringVar(value="0")
    ea3_var = tk.StringVar(value="0")
    ea_seq_var = tk.StringVar(value="321")
    q1_var = tk.StringVar(value="0")
    q2_var = tk.StringVar(value="0")
    q3_var = tk.StringVar(value="0")
    q4_var = tk.StringVar(value="1")
    ear1_var = tk.StringVar(value="0")
    ear2_var = tk.StringVar(value="0")
    ear3_var = tk.StringVar(value="0")

    entradas_sat = {}
    menu(quadro_sat, "Tamanho", cubesat_var, list(cubesats.keys()), lambda _=None: atualizar_cubesat())
    entradas_sat["dx"] = campo(quadro_sat, "Dimensão X [m]", dx_var)
    ToolTip(entradas_sat["dx"], _("Largura no eixo X", idioma))
    entradas_sat["dy"] = campo(quadro_sat, "Dimensão Y [m]", dy_var)
    ToolTip(entradas_sat["dy"], _("Largura no eixo Y", idioma))
    entradas_sat["dz"] = campo(quadro_sat, "Dimensão Z [m]", dz_var)
    ToolTip(entradas_sat["dz"], _("Comprimento no eixo Z", idioma))
    massa_entry = campo(quadro_sat, "Massa [kg]", massa_var)
    ToolTip(massa_entry, _("Massa seca do satélite", idioma))
    cd_entry = campo(quadro_sat, "Cd", cd_var)
    ToolTip(cd_entry, _("Coeficiente de arrasto", idioma))
    cr_entry = campo(quadro_sat, "Cr", cr_var)
    ToolTip(cr_entry, _("Coeficiente de reflexão solar", idioma))

    tk.Frame(quadro_sat, bg="#94a3b8", height=1).pack(fill=tk.X, pady=(10, 4))
    _frame_at = tk.Frame(quadro_sat, bg="#e5e7eb")
    _frame_at.pack(fill=tk.X, pady=(0, 4))
    _atit_lbl = "Tipo de atitude:" if idioma != "EN" else "Attitude type:"
    tk.Label(_frame_at, text=_atit_lbl, bg="#e5e7eb", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _atualizar_atitude(_=None):
        if atitude_var.get() == "Tumbling":
            for rb in rbs_nadir: rb.pack_forget()
            for rb in rbs_tumbling: rb.pack(side=tk.LEFT, padx=5)
            modo_face_var.set("ci")
            frame_modos.pack(anchor="center", pady=(0, 6))
        else:
            for rb in rbs_tumbling: rb.pack_forget()
            for rb in rbs_nadir: rb.pack(side=tk.LEFT, padx=5)
            modo_face_var.set("nadir")
            frame_modos.pack(anchor="center", pady=(0, 6))
        atualizar_tudo()

    _opt_at = tk.OptionMenu(_frame_at, atitude_var, "NadirPointing", "Tumbling", command=_atualizar_atitude)
    _opt_at.config(width=13, highlightthickness=0, bd=1)
    _opt_at.pack(side=tk.RIGHT)

    tk.Button(
        quadro_sat,
        text="Restaurar padrões do satélite" if idioma != "EN" else "Restore satellite defaults",
        command=lambda: atualizar_cubesat(),
        bg="#e5e7eb",
    ).pack(fill=tk.X, pady=(8, 0))

    quadro_faces = secao("Parte 3 - Atitude e painéis solares", notebook)
    modo_face_var = tk.StringVar(value="nadir")
    modo_face_var.set("nadir")
    frame_modos = tk.Frame(quadro_faces, bg="#e5e7eb")
    cores_modo = {"nadir": "#9b6ef3", "vel": "#4f8df7", "solar": "#f6c445"}
    
    rbs_nadir = []
    for texto, modo in [("Nadir", "nadir"), ("Velocidade", "vel"), ("Painéis", "solar")]:
        rb = tk.Radiobutton(frame_modos, text=_(texto, idioma), value=modo, variable=modo_face_var, indicatoron=False, command=lambda: atualizar_tudo(), width=12, bg="#e5e7eb", selectcolor=cores_modo[modo])
        rbs_nadir.append(rb)
        
    rbs_tumbling = []
    for _txt_pt, _txt_en, modo in [
        ("Condições Iniciais", "Initial Conditions", "ci"),
        ("Taxas Angulares",    "Angular Rates",      "rates"),
        ("Painéis",            "Panels",             "solar"),
    ]:
        _txt_rb = _txt_en if idioma == "EN" else _txt_pt
        rb = tk.Radiobutton(frame_modos, text=_txt_rb, value=modo, variable=modo_face_var, indicatoron=False, command=lambda: atualizar_tudo(), width=15, bg="#e5e7eb", selectcolor=cores_modo["solar"])
        rbs_tumbling.append(rb)

    frame_ci_container = tk.Frame(quadro_faces, bg="#e5e7eb")
    frame_rates_container = tk.Frame(quadro_faces, bg="#e5e7eb")

    def _atualizar_ci(_=None):
        if tipo_ci_var.get() == "Quaternion":
            frame_euler_ci.pack_forget()
            frame_quat_ci.pack(fill=tk.X, pady=(0, 4))
        else:
            frame_quat_ci.pack_forget()
            frame_euler_ci.pack(fill=tk.X, pady=(0, 4))

    _frame_ci = tk.Frame(frame_ci_container, bg="#e5e7eb")
    _frame_ci.pack(fill=tk.X, pady=(0, 2))
    _ci_lbl = "Condição inicial:" if idioma != "EN" else "Initial condition:"
    tk.Label(_frame_ci, text=_ci_lbl, bg="#e5e7eb", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
    _opt_ci = tk.OptionMenu(_frame_ci, tipo_ci_var, "EulerAngles", "Quaternion", command=_atualizar_ci)
    _opt_ci.config(width=12, highlightthickness=0, bd=1)
    _opt_ci.pack(side=tk.RIGHT)
    tk.Label(frame_ci_container, text=_("A sequência de rotações Euler é 321", idioma),
             bg="#e5e7eb", fg="#6b7280", font=("Segoe UI", 8), anchor="w").pack(fill=tk.X, pady=(0, 4))

    ea_seq_var.set("321")
    frame_euler_ci = tk.Frame(frame_ci_container, bg="#e5e7eb")
    for _txt_ea, _var_ea in [
        ("Ângulo de Euler x [graus]:" if idioma != "EN" else "Euler Angle x [deg]:", ea1_var),
        ("Ângulo de Euler y [graus]:" if idioma != "EN" else "Euler Angle y [deg]:", ea2_var),
        ("Ângulo de Euler z [graus]:" if idioma != "EN" else "Euler Angle z [deg]:", ea3_var),
    ]:
        _rf = tk.Frame(frame_euler_ci, bg="#e5e7eb")
        _rf.pack(fill=tk.X, pady=2)
        tk.Label(_rf, text=_txt_ea, bg="#e5e7eb", anchor="w", font=("Segoe UI", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Entry(_rf, textvariable=_var_ea, width=10).pack(side=tk.RIGHT)
    frame_euler_ci.pack(fill=tk.X, pady=(0, 4))

    frame_quat_ci = tk.Frame(frame_ci_container, bg="#e5e7eb")
    for _txt_q, _var_q in [("Q1", q1_var), ("Q2", q2_var), ("Q3", q3_var), ("Q4", q4_var)]:
        _rf = tk.Frame(frame_quat_ci, bg="#e5e7eb")
        _rf.pack(fill=tk.X, pady=2)
        tk.Label(_rf, text=_txt_q, bg="#e5e7eb", anchor="w", font=("Segoe UI", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Entry(_rf, textvariable=_var_q, width=10).pack(side=tk.RIGHT)

    _rates_lbl = "Taxas angulares:" if idioma != "EN" else "Angular rates:"
    tk.Label(frame_rates_container, text=_rates_lbl, bg="#e5e7eb", anchor="w", font=("Segoe UI", 9, "bold")).pack(fill=tk.X, pady=(6, 2))
    for _txt_r, _var_r in [("Taxa angular x [graus/s]:" if idioma != "EN" else "Angular rate x [deg/s]:", ear1_var), 
                           ("Taxa angular y [graus/s]:" if idioma != "EN" else "Angular rate y [deg/s]:", ear2_var), 
                           ("Taxa angular z [graus/s]:" if idioma != "EN" else "Angular rate z [deg/s]:", ear3_var)]:
        _rf = tk.Frame(frame_rates_container, bg="#e5e7eb")
        _rf.pack(fill=tk.X, pady=2)
        tk.Label(_rf, text=_txt_r, bg="#e5e7eb", anchor="w", font=("Segoe UI", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Entry(_rf, textvariable=_var_r, width=10).pack(side=tk.RIGHT)

    for rb in rbs_nadir: rb.pack(side=tk.LEFT, padx=5)
    frame_modos.pack(anchor="center", pady=(0, 6))

    frame_faces = tk.Frame(quadro_faces, bg="#e5e7eb")
    frame_faces.pack(anchor="center", pady=(0, 8))
    frame_faces.grid_columnconfigure(0, weight=1)
    frame_faces.grid_columnconfigure(1, weight=1)
    botoes_faces = {}
    _escuro_ini = estado_tema.get("escuro", True)
    for i, face in enumerate(lista_faces):
        _bg_ini = "#475569" if _escuro_ini else "#cbd5e1"
        _fg_ini = "white" if _escuro_ini else "#111827"
        botao = tk.Button(frame_faces, width=11, height=2, bg=_bg_ini, fg=_fg_ini, activebackground=_bg_ini, command=lambda f=face: selecionar_face(f))
        botao.grid(row=i // 2, column=i % 2, padx=4, pady=4, sticky="nsew")
        botoes_faces[face] = botao

    resumo_faces = tk.Label(quadro_faces, text="", bg="#e5e7eb", justify=tk.LEFT, anchor="w", font=("Consolas", 9))
    resumo_faces.pack(fill=tk.X, pady=(6, 0))


    quadro_sim = secao("Parte 4 - Estação terrena e simulação", notebook)
    gs_var = tk.BooleanVar(value=False)
    lat_var = tk.StringVar(value="0")
    lon_var = tk.StringVar(value="0")
    alt_var = tk.StringVar(value="0")
    elev_var = tk.StringVar(value="10")
    tempo_var = tk.StringVar(value="10")
    entradas_gs = []
    checkbox(quadro_sim, _("Informar estação terrena", idioma), gs_var, lambda: atualizar_gs())
    entradas_gs.append(campo(quadro_sim, _("Latitude [graus] - Posição norte/sul (-90º a 90º)", idioma), lat_var))
    entradas_gs.append(campo(quadro_sim, _("Longitude [graus] - Posição leste/oeste (-180º a 180º)", idioma), lon_var))
    entradas_gs.append(campo(quadro_sim, _("Altitude [m] - Altura da estação", idioma), alt_var))
    entradas_gs.append(campo(quadro_sim, _("Elevação mínima [graus] - Ângulo mínimo de visada (0º a 90º)", idioma), elev_var))
    tempo_entry = campo(quadro_sim, _("Tempo de simulação [dias] - Duração da propagação", idioma), tempo_var)

    epoch_date_var = tk.StringVar(value="01/01/2025")
    epoch_time_var = tk.StringVar(value="12:00")

    _frame_date = linha(quadro_sim)
    _lbl_date_txt = _("Data de início (UTC) [DD/MM/AAAA]", idioma)
    tk.Label(_frame_date, text=_lbl_date_txt, bg="#e5e7eb", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
    _ent_date = tk.Entry(_frame_date, textvariable=epoch_date_var, width=13)
    _ent_date.pack(side=tk.RIGHT)

    def _fmt_data(event=None):
        raw = "".join(c for c in epoch_date_var.get() if c.isdigit())[:8]
        if len(raw) >= 5:
            epoch_date_var.set(raw[:2] + "/" + raw[2:4] + "/" + raw[4:])
        elif len(raw) >= 3:
            epoch_date_var.set(raw[:2] + "/" + raw[2:])
        elif raw:
            epoch_date_var.set(raw)
    _ent_date.bind("<FocusOut>", _fmt_data)
    _ent_date.bind("<Return>", _fmt_data)

    _frame_time = linha(quadro_sim)
    _lbl_time_txt = _("Horário de início (UTC) [HH:MM]", idioma)
    tk.Label(_frame_time, text=_lbl_time_txt, bg="#e5e7eb", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
    _ent_time = tk.Entry(_frame_time, textvariable=epoch_time_var, width=7)
    _ent_time.pack(side=tk.RIGHT)

    def _fmt_hora(event=None):
        raw = "".join(c for c in epoch_time_var.get() if c.isdigit())[:4]
        if len(raw) >= 3:
            epoch_time_var.set(raw[:2] + ":" + raw[2:])
        elif raw:
            epoch_time_var.set(raw)
    _ent_time.bind("<FocusOut>", _fmt_hora)
    _ent_time.bind("<Return>", _fmt_hora)

    def restaurar_simulacao():
        gs_var.set(False)
        lat_var.set("0")
        lon_var.set("0")
        alt_var.set("0")
        elev_var.set("10")
        tempo_var.set("10")
        epoch_date_var.set("01/01/2025")
        epoch_time_var.set("12:00")
        atualizar_gs()

    tk.Button(
        quadro_sim,
        text="Restaurar padrões da simulação" if idioma != "EN" else "Restore simulation defaults",
        command=restaurar_simulacao,
        bg="#e5e7eb",
    ).pack(fill=tk.X, pady=(8, 0))

    def _valid_float_range(minimo=None, maximo=None, nome="Campo"):
        def _v(valor):
            try:
                valor = float(str(valor).replace(",", "."))
            except ValueError:
                raise ValueError(f"{nome}: " + ("enter a valid number" if idioma == "EN" else "digite um número válido"))
            if minimo is not None and valor < minimo:
                raise ValueError(f"{nome}: " + ("minimum" if idioma == "EN" else "mínimo") + f" {minimo}")
            if maximo is not None and valor > maximo:
                raise ValueError(f"{nome}: " + ("maximum" if idioma == "EN" else "máximo") + f" {maximo}")
            return True
        return _v


    def _valid_data_fmt(fmt, msg):
        def _v(valor):
            try:
                datetime.strptime(str(valor), fmt)
                return True
            except ValueError:
                raise ValueError(msg)
        return _v

    _validadores_visuais = []
    _validadores_visuais.append(configurar_validacao_visual(entradas_orbita["sma"], sma_var, _valid_float_range(SMA_MINIMO_KM, None, "SMA"), _("Semi-eixo maior em km. Mínimo: {:.3f} km.", idioma).format(SMA_MINIMO_KM), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_orbita["ecc"], ecc_var, _valid_float_range(0.0, 0.9999, "ECC"), _("Excentricidade entre 0 e menor que 1.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_orbita["inc"], inc_var, _valid_float_range(0.0, 180.0, "INC"), _("Inclinação orbital em graus, de 0 a 180.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_orbita["raan"], raan_var, _valid_float_range(0.0, 360.0, "RAAN"), _("Ascensão reta do nó ascendente (0 a 360º)", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_orbita["aop"], aop_var, _valid_float_range(0.0, 360.0, "AOP"), _("Argumento do perigeu em graus, de 0 a 360.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_orbita["ta"], ta_var, _valid_float_range(0.0, 360.0, "TA"), _("Anomalia verdadeira em graus, de 0 a 360.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_sat["dx"], dx_var, _valid_float_range(0.001, None, "Dimensão X"), _("Dimensão X do satélite em metros.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_sat["dy"], dy_var, _valid_float_range(0.001, None, "Dimensão Y"), _("Dimensão Y do satélite em metros.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_sat["dz"], dz_var, _valid_float_range(0.001, None, "Dimensão Z"), _("Dimensão Z do satélite em metros.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(massa_entry, massa_var, _valid_float_range(0.001, None, "Massa"), _("Massa seca do satélite em kg.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(cd_entry, cd_var, _valid_float_range(0.0, None, "Cd"), _("Coeficiente de arrasto.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(cr_entry, cr_var, _valid_float_range(0.0, None, "Cr"), _("Coeficiente de reflexão solar.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(_ent_date, epoch_date_var, _valid_data_fmt("%d/%m/%Y", _("Data no formato DD/MM/AAAA.", idioma)), _("Data no formato DD/MM/AAAA.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(_ent_time, epoch_time_var, _valid_data_fmt("%H:%M", _("Horário UTC no formato HH:MM.", idioma)), _("Horário UTC no formato HH:MM.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_gs[0], lat_var, _valid_float_range(-90.0, 90.0, "Latitude"), _("Posição norte/sul de -90º a 90º.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_gs[1], lon_var, _valid_float_range(-180.0, 180.0, "Longitude"), _("Posição leste/oeste de -180º a 180º.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_gs[2], alt_var, _valid_float_range(0.0, None, "Altitude"), _("Altura da estação em metros.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(entradas_gs[3], elev_var, _valid_float_range(0.0, 90.0, "Elevação mínima"), _("Ângulo mínimo de visada de 0º a 90º.", idioma), status_validacao))
    _validadores_visuais.append(configurar_validacao_visual(tempo_entry, tempo_var, _valid_float_range(0.01, None, "Tempo de simulação"), _("Duração da propagação em dias.", idioma), status_validacao))

    def epoch_campos_para_gmat():
        _MESES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                  7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
        _fmt_data()   
        _fmt_hora()   
        partes_d = epoch_date_var.get().strip().split("/")
        if len(partes_d) != 3:
            return None
        try:
            dd, mm, yyyy = int(partes_d[0]), int(partes_d[1]), int(partes_d[2])
            mes = _MESES.get(mm)
            if mes is None:
                return None
        except ValueError:
            return None
        partes_t = epoch_time_var.get().strip().split(":")
        try:
            hh = int(partes_t[0]) if len(partes_t) >= 1 and partes_t[0] else 0
            mn = int(partes_t[1]) if len(partes_t) >= 2 and partes_t[1] else 0
        except ValueError:
            hh, mn = 0, 0
        return f"{dd:02d} {mes} {yyyy} {hh:02d}:{mn:02d}:00.000"


    quadro_exec = secao("Parte 5 - Script / GMAT", notebook)
    executar_var = tk.BooleanVar(value=bool(gmat_disponivel))
    placa_var = tk.BooleanVar(value=True)
    bateria_var = tk.BooleanVar(value=True)
    checkbox(quadro_exec, "Executar GMAT após gerar o script", executar_var)
    if not gmat_disponivel:
        tk.Label(quadro_exec, text=_("load_gmat não foi encontrado; a execução ficará desativada.", idioma), bg="#e5e7eb", fg="#b45309", wraplength=380, justify=tk.LEFT).pack(fill=tk.X)

    frame_botoes_gmat = tk.Frame(quadro_exec, bg="#e5e7eb")
    frame_botoes_gmat.pack(fill=tk.X, pady=(8, 0))

    btn_gerar_script = tk.Button(
        frame_botoes_gmat,
        text=_("Gerar script", idioma),
        bg="#eab308",
        fg="#111827",
        font=("Segoe UI", 11, "bold"),
        height=2,
        relief=tk.RAISED,
        bd=2,
    )

    def confirmar_com_loading():
        try:
            btn_gerar_script.config(
                text="⏳ Gerando script / aguardando GMAT..." if idioma != "EN" else "⏳ Generating script / waiting for GMAT...",
                state=tk.DISABLED,
            )
            root.update_idletasks()
            confirmar()
        except Exception:
            try:
                btn_gerar_script.config(text=_("Gerar script", idioma), state=tk.NORMAL)
            except Exception:
                pass
            raise

    btn_gerar_script.config(command=confirmar_com_loading)
    btn_gerar_script.pack(fill=tk.X, pady=(0, 7))

    def _btn_abrir_gmat_parte5():
        _d = _coletar_dados_formulario()
        if _d is None:
            return
        _exe = localizar_executavel_gmat()
        if _exe is None:
            _msg = "GMAT executable not found.\nCheck load_gmat.py configuration." if idioma == "EN" else "Executável GMAT não encontrado.\nVerifique a configuração do load_gmat.py."
            messagebox.showerror("GMAT", _msg, parent=root)
            return
        try:
            import subprocess as _sp2
            _bd = obter_base_dir()
            _pasta_s = os.path.join(_bd, "Generated_Scripts_Pegasus" if idioma == "EN" else "Scripts_Gerados_Pegasus")
            os.makedirs(_pasta_s, exist_ok=True)
            _cam = os.path.join(_pasta_s, "Script_Preview_Interface.script")

            _epoch  = _d["epoch"]
            _sma    = _d["sma"]
            _ecc    = _d["ecc"]
            _inc    = _d["inc"]
            _raan   = _d["raan"]
            _aop    = _d["aop"]
            _ta     = _d["ta"]
            _m      = _d["m_sat"]
            _cd     = _d["cd_sat"]
            _cr     = _d["cr_sat"]
            _dx     = _d["dx"]
            _dy     = _d["dy"]
            _dz     = _d["dz"]
            _tempo  = _d["tempo"]

            _pasta_res = os.path.join(_bd, "Results_Pegasus" if idioma == "EN" else "Resultados_Pegasus")
            os.makedirs(_pasta_res, exist_ok=True)
            _rep = os.path.join(_pasta_res, "Preview_Report.txt").replace("\\", "/")

            _drag_area = _dx * _dy
            _srp_area  = max(_dx * _dy, _dx * _dz, _dy * _dz)

            _fv_map = {'+X':(1,0,0),'-X':(-1,0,0),'+Y':(0,1,0),'-Y':(0,-1,0),'+Z':(0,0,1),'-Z':(0,0,-1)}
            _atit_tipo = _d.get("atitude_tipo", "NadirPointing")
            if _atit_tipo == "Tumbling":
                _tipo_ci = _d.get("tipo_ci", "EulerAngles")
                _ear1 = _d.get("ear1", 0.0); _ear2 = _d.get("ear2", 0.0); _ear3 = _d.get("ear3", 0.0)
                if _tipo_ci == "Quaternion":
                    _q1=_d.get("q1",0.0); _q2=_d.get("q2",0.0); _q3=_d.get("q3",0.0); _q4=_d.get("q4",1.0)
                    _atit_linhas = [
                        "DefaultSC.Attitude = Spinner;",
                        "DefaultSC.AttitudeDisplayStateType = 'Quaternion';",
                        "DefaultSC.AttitudeRateDisplayStateType = 'AngularVelocity';",
                        "DefaultSC.EulerAngleSequence = '321';",
                        f"DefaultSC.Q1 = {_q1};", f"DefaultSC.Q2 = {_q2};",
                        f"DefaultSC.Q3 = {_q3};", f"DefaultSC.Q4 = {_q4};",
                        f"DefaultSC.AngularVelocityX = {_ear1};",
                        f"DefaultSC.AngularVelocityY = {_ear2};",
                        f"DefaultSC.AngularVelocityZ = {_ear3};",
                    ]
                else:
                    _ea1=_d.get("ea1",0.0); _ea2=_d.get("ea2",0.0); _ea3=_d.get("ea3",0.0)
                    _atit_linhas = [
                        "DefaultSC.Attitude = Spinner;",
                        "DefaultSC.AttitudeDisplayStateType = 'EulerAngles';",
                        "DefaultSC.AttitudeRateDisplayStateType = 'AngularVelocity';",
                        "DefaultSC.EulerAngleSequence = '321';",
                        f"DefaultSC.EulerAngle1 = {_ea1};", f"DefaultSC.EulerAngle2 = {_ea2};",
                        f"DefaultSC.EulerAngle3 = {_ea3};",
                        f"DefaultSC.AngularVelocityX = {_ear1};",
                        f"DefaultSC.AngularVelocityY = {_ear2};",
                        f"DefaultSC.AngularVelocityZ = {_ear3};",
                    ]
            else:  
                _av = _fv_map.get(_d.get("face_nadir", "+Z"), (0,0,1))
                _cv = _fv_map.get(_d.get("face_vel",   "+X"), (1,0,0))
                _atit_linhas = [
                    "DefaultSC.Attitude = NadirPointing;",
                    "DefaultSC.AttitudeReferenceBody = Earth;",
                    "DefaultSC.AttitudeConstraintType = Velocity;",
                    f"DefaultSC.BodyAlignmentVectorX = {_av[0]};",
                    f"DefaultSC.BodyAlignmentVectorY = {_av[1]};",
                    f"DefaultSC.BodyAlignmentVectorZ = {_av[2]};",
                    f"DefaultSC.BodyConstraintVectorX = {_cv[0]};",
                    f"DefaultSC.BodyConstraintVectorY = {_cv[1]};",
                    f"DefaultSC.BodyConstraintVectorZ = {_cv[2]};",
                ]

            _linhas = [
                "%% Script generated by Pegasus - Preview (Interface)",
                "",
                "Create Spacecraft DefaultSC;",
                f"DefaultSC.Epoch.UTCGregorian = '{_epoch}';",
                f"DefaultSC.SMA = {_sma};",
                f"DefaultSC.ECC = {_ecc};",
                f"DefaultSC.INC = {_inc};",
                f"DefaultSC.RAAN = {_raan};",
                f"DefaultSC.AOP = {_aop};",
                f"DefaultSC.TA = {_ta};",
                f"DefaultSC.DryMass = {_m};",
                f"DefaultSC.Cd = {_cd};",
                f"DefaultSC.Cr = {_cr};",
                f"DefaultSC.DragArea = {_drag_area:.6f};",
                f"DefaultSC.SRPArea = {_srp_area:.6f};",
            ] + _atit_linhas + [
                "",
                "Create ForceModel DefaultProp_ForceModel;",
                "DefaultProp_ForceModel.CentralBody = Earth;",
                "DefaultProp_ForceModel.PrimaryBodies = {Earth};",
                "DefaultProp_ForceModel.Drag.AtmosphereModel = JacchiaRoberts;",
                "DefaultProp_ForceModel.Drag.F107 = 150;",
                "DefaultProp_ForceModel.Drag.F107A = 150;",
                "DefaultProp_ForceModel.GravityField.Earth.Degree = 4;",
                "DefaultProp_ForceModel.GravityField.Earth.Order = 4;",
                "DefaultProp_ForceModel.SRP = On;",
                "",
                "Create Propagator DefaultProp;",
                "DefaultProp.FM = DefaultProp_ForceModel;",
                "DefaultProp.Type = RungeKutta89;",
                "DefaultProp.InitialStepSize = 60;",
                "DefaultProp.MinStep = 0;",
                "",
                "Create ReportFile ReportFile1;",
                f"ReportFile1.Filename = '{_rep}';",
                "ReportFile1.Add = {DefaultSC.UTCGregorian, DefaultSC.EarthMJ2000Eq.X, DefaultSC.EarthMJ2000Eq.Y, DefaultSC.EarthMJ2000Eq.Z};",
                "ReportFile1.WriteHeaders = true;",
                "",
                "Create OpenFramesView DefaultOrbitView_View;",
                "DefaultOrbitView_View.ViewFrame = CoordinateSystem;",
                "DefaultOrbitView_View.ViewTrajectory = Off;",
                "DefaultOrbitView_View.InertialFrame = Off;",
                "DefaultOrbitView_View.SetDefaultLocation = On;",
                "DefaultOrbitView_View.DefaultEye = [ 30000 0 0 ];",
                "DefaultOrbitView_View.DefaultCenter = [ 0 0 0 ];",
                "DefaultOrbitView_View.DefaultUp = [ 0 0 1 ];",
                "DefaultOrbitView_View.SetCurrentLocation = Off;",
                "DefaultOrbitView_View.FOVy = 45;",
                "",
                "Create OpenFramesInterface DefaultOrbitView;",
                "DefaultOrbitView.SolverIterations = Current;",
                "DefaultOrbitView.UpperLeft = [ 0 0 ];",
                "DefaultOrbitView.Size = [ 0.4994117647058823 0.4987623762376238 ];",
                "DefaultOrbitView.RelativeZOrder = 20;",
                "DefaultOrbitView.Maximized = false;",
                "DefaultOrbitView.Add = {DefaultSC, Earth};",
                "DefaultOrbitView.View = {DefaultOrbitView_View};",
                "DefaultOrbitView.CoordinateSystem = EarthMJ2000Eq;",
                "DefaultOrbitView.DrawObject = [ true true ];",
                "DefaultOrbitView.DrawTrajectory = [ true true ];",
                "DefaultOrbitView.DrawAxes = [ false false ];",
                "DefaultOrbitView.DrawXYPlane = [ false false ];",
                "DefaultOrbitView.DrawLabel = [ true true ];",
                "DefaultOrbitView.DrawUsePropLabel = [ false false ];",
                "DefaultOrbitView.DrawCenterPoint = [ true true ];",
                "DefaultOrbitView.DrawEndPoints = [ true true ];",
                "DefaultOrbitView.DrawVelocity = [ false false ];",
                "DefaultOrbitView.DrawGrid = [ false false ];",
                "DefaultOrbitView.DrawLineWidth = [ 2 2 ];",
                "DefaultOrbitView.DrawMarkerSize = [ 10 10 ];",
                "DefaultOrbitView.DrawFontSize = [ 20 20 ];",
                "DefaultOrbitView.Axes = On;",
                "DefaultOrbitView.AxesLength = 12756.2726;",
                "DefaultOrbitView.AxesLabels = On;",
                "DefaultOrbitView.FrameLabel = Off;",
                "DefaultOrbitView.XYPlane = On;",
                "DefaultOrbitView.EclipticPlane = Off;",
                "DefaultOrbitView.EnableStars = On;",
                "DefaultOrbitView.StarCatalog = 'inp_StarsHYGv3.txt';",
                "DefaultOrbitView.StarCount = 40000;",
                "DefaultOrbitView.MinStarMag = -2;",
                "DefaultOrbitView.MaxStarMag = 6;",
                "DefaultOrbitView.MinStarPixels = 1;",
                "DefaultOrbitView.MaxStarPixels = 10;",
                "DefaultOrbitView.MinStarDimRatio = 0.5;",
                "DefaultOrbitView.ShowPlot = true;",
                "DefaultOrbitView.ShowToolbar = true;",
                "DefaultOrbitView.SolverIterLastN = 1;",
                "DefaultOrbitView.ShowVR = false;",
                "DefaultOrbitView.PlaybackTimeScale = 3600;",
                "DefaultOrbitView.MultisampleAntiAliasing = On;",
                "DefaultOrbitView.MSAASamples = 2;",
                "DefaultOrbitView.DrawFontPosition = {'Top-Right', 'Top-Right'};",
                
                "Create GroundTrack GroundTrackPlot1;",
                "GroundTrackPlot1.SolverIterations = Current;",
                "GroundTrackPlot1.UpperLeft = [ 0 0.4987623762376238 ];",
                "GroundTrackPlot1.Size = [ 0.5 0.4504950495049505 ];",
                "GroundTrackPlot1.RelativeZOrder = 21;",
                "GroundTrackPlot1.Maximized = false;",
                "GroundTrackPlot1.CentralBody = Earth;",
                "GroundTrackPlot1.Add = {DefaultSC};",
                "GroundTrackPlot1.DataCollectFrequency = 1;",
                "GroundTrackPlot1.UpdatePlotFrequency = 50;",
                "GroundTrackPlot1.NumPointsToRedraw = 0;",
                "GroundTrackPlot1.MaxPlotPoints = 20000;",
                "GroundTrackPlot1.ShowPlot = true;",
                "GroundTrackPlot1.ShowPlot = true;",
                "",
                "BeginMissionSequence;",
                f"Propagate DefaultProp(DefaultSC) " + "{" + f"DefaultSC.ElapsedDays = {_tempo}" + "};",
            ]
            _script = "\n".join(_linhas) + "\n"

            with open(_cam, "w", encoding="ascii", errors="replace") as _f:
                _f.write(_script)
            iniciar_gmat_externo(_exe, _cam)
        except Exception as _e2:
            messagebox.showerror("GMAT", f"{'Error' if idioma == 'EN' else 'Erro'}: {_e2}", parent=root)

    tk.Button(
        frame_botoes_gmat,
        text="Abrir GMAT" if idioma != "EN" else "Open GMAT",
        command=_btn_abrir_gmat_parte5,
        height=2,
        bg="#374151" if estado_tema.get("escuro", True) else "#e5e7eb",
        fg="white" if estado_tema.get("escuro", True) else "#111827",
    ).pack(fill=tk.X, pady=(0, 5))

    tk.Button(
        frame_botoes_gmat,
        text="Abrir pasta de resultados" if idioma != "EN" else "Open results folder",
        command=lambda: abrir_pasta_resultados(parent=root),
        height=2,
        bg="#374151" if estado_tema.get("escuro", True) else "#e5e7eb",
        fg="white" if estado_tema.get("escuro", True) else "#111827",
    ).pack(fill=tk.X, pady=(0, 5))

    tk.Button(
        frame_botoes_gmat,
        text="Abrir pasta de scripts GMAT" if idioma != "EN" else "Open GMAT scripts folder",
        command=lambda: abrir_pasta_scripts(parent=root),
        height=2,
        bg="#374151" if estado_tema.get("escuro", True) else "#e5e7eb",
        fg="white" if estado_tema.get("escuro", True) else "#111827",
    ).pack(fill=tk.X, pady=(0, 5))

    tk.Button(
        frame_botoes_gmat,
        text="⬅ Menu inicial / Novo dimensionamento" if idioma != "EN" else "⬅ Main menu / New sizing",
        command=lambda: reiniciar_aplicacao(parent=root, idioma=idioma),
        height=2,
    ).pack(fill=tk.X, pady=(0, 5))

    quadro_placa = secao("Parte 6 - Painéis solares", notebook)
    tm_var = tk.StringVar(value="1")
    pe_var = tk.StringVar(value="5")
    pd_var = tk.StringVar(value="5")
    arq_var = tk.StringVar(value="DET")
    xe_var = tk.StringVar(value="0.65")
    xd_var = tk.StringVar(value="0.85")
    checkbox(quadro_placa, "Executar após o GMAT concluir", placa_var, lambda: atualizar_fluxo_analises())
    campo(quadro_placa, "Tempo de missão [anos] (mín. 0)", tm_var)
    campo(quadro_placa, "Potência máxima consumida no eclipse Pe [W]", pe_var)
    campo(quadro_placa, "Potência máxima consumida no sol Pd [W]", pd_var)
    menu(quadro_placa, "Topologia", arq_var, ["DET", "PPT", "Outra"], lambda _=None: atualizar_arquitetura())
    ent_xe = campo(quadro_placa, "Eficiência de descarga Xe (0 a 1)", xe_var)
    ent_xd = campo(quadro_placa, "Eficiência de carga Xd (0 a 1)", xd_var)

    quadro_bat = secao("Parte 7 - Bateria", notebook)
    bat_pe_var = tk.StringVar(value="5")
    bat_tm_var = tk.StringVar(value="1")
    dod_var = tk.StringVar(value="0.3")
    tipo_bat_var = tk.StringVar(value="Li-ion")
    dens_var = tk.StringVar(value="150")
    bancos_var = tk.StringVar(value="1")
    eta_bat_var = tk.StringVar(value="0.9")
    chk_bateria = checkbox(quadro_bat, "Executar após a análise de painéis", bateria_var, lambda: atualizar_fluxo_analises())
    tk.Label(
        quadro_bat,
        text="This step uses Pe and mission time defined in the solar panel analysis." if idioma == "EN" else "Esta etapa usa Pe e tempo de missão definidos na análise de painéis.",
        bg="#e5e7eb",
        fg="#334155",
        wraplength=380,
        justify=tk.LEFT,
    ).pack(fill=tk.X, pady=(0, 5))
    campo(quadro_bat, "Profundidade de descarga máxima (DoD) (0 a 1)", dod_var)
    menu(quadro_bat, "Tipo de bateria", tipo_bat_var, ["NiCd", "NiH2", "Li-ion", "Outra"], lambda _=None: atualizar_bateria())
    ent_dens = campo(quadro_bat, "Densidade de energia [Wh/kg]", dens_var)
    campo(quadro_bat, "Número de bancos independentes", bancos_var)
    campo(quadro_bat, "Eficiência de transmissão (0 a 1)", eta_bat_var)

    view = {"yaw": -0.65, "pitch": 0.45, "zoom": 70.0, "last": None}

    def areas_atuais():
        return areas_cubesat(float(dx_var.get()), float(dy_var.get()), float(dz_var.get()))

    def grade_atual():
        return (
            max(1, int(float(nx_var.get()))),
            max(1, int(float(ny_var.get()))),
            max(1, int(float(nz_var.get()))),
        )

    def face_permitida_para_vel(face):
        return face != face_nadir["valor"] and face != FACE_OPOSTA[face_nadir["valor"]]

    def selecionar_face(face):
        modo = modo_face_var.get()
        if modo == "nadir":
            face_nadir["valor"] = face
            faces_solares.discard(face)
            if not face_permitida_para_vel(face_vel["valor"]):
                face_vel["valor"] = next(f for f in lista_faces if face_permitida_para_vel(f))
        elif modo == "vel":
            if not face_permitida_para_vel(face):
                messagebox.showerror(_("Face inválida", idioma),
                                     _("A face de velocidade não pode ser igual nem oposta à face nadir.", idioma),
                                     parent=root)
                return
            face_vel["valor"] = face
        else:
            if face in faces_solares:
                faces_solares.remove(face)
            else:
                faces_solares.add(face)
        atualizar_tudo()

    def cor_face_3d(face):
        neutra = "#475569" if estado_tema["escuro"] else "#cbd5e1"
        if pagina_atual["idx"] < 2:            
            return neutra
        if atitude_var.get() != "Tumbling":    
            if face == face_nadir["valor"]:
                return "#9333ea"
            if face == face_vel["valor"]:
                return "#2563eb"
        if face in faces_solares:              
            return "#eab308"
        return neutra


    def rotacionar(ponto):
        x, y, z = ponto
        cy, sy = math.cos(view["yaw"]), math.sin(view["yaw"])
        cp, sp = math.cos(view["pitch"]), math.sin(view["pitch"])
        x1 = cy * x + sy * z
        z1 = -sy * x + cy * z
        y1 = y
        y2 = cp * y1 - sp * z1
        z2 = sp * y1 + cp * z1
        return x1, y2, z2

    def projetar(ponto):
        largura = max(canvas.winfo_width(), 1)
        altura = max(canvas.winfo_height(), 1)
        x, y, z = rotacionar(ponto)
        return largura / 2 + x * view["zoom"], altura / 2 - y * view["zoom"], z

    def desenhar_eixo(inicio, fim, cor, texto):
        x0, y0, _ = projetar(inicio)
        x1, y1, _ = projetar(fim)
        canvas.create_line(x0, y0, x1, y1, fill=cor, width=3, arrow=tk.LAST, arrowshape=(12, 16, 5))
        canvas.create_text(x1 + 12, y1, text=texto, fill=cor, font=("Segoe UI", 10, "bold"))

    def desenhar_visual():
        canvas.delete("all")
        escuro = estado_tema.get("escuro", False)
        try:
            nx, ny, nz = grade_atual()
        except ValueError:
            return

        specs = {
            "+X": [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)],
            "-X": [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],
            "+Y": [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)],
            "-Y": [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
            "+Z": [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
            "-Z": [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)],
        }
        faces_para_desenhar = []
        for ix in range(nx):
            for iy in range(ny):
                for iz in range(nz):
                    limites = {
                        "+X": ix == nx - 1,
                        "-X": ix == 0,
                        "+Y": iy == ny - 1,
                        "-Y": iy == 0,
                        "+Z": iz == nz - 1,
                        "-Z": iz == 0,
                    }
                    for face, externa in limites.items():
                        if not externa:
                            continue
                        pontos_3d = []
                        profundidade = 0.0
                        for vx, vy, vz in specs[face]:
                            p = (ix + vx - nx / 2, iy + vy - ny / 2, iz + vz - nz / 2)
                            pontos_3d.append(p)
                            profundidade += rotacionar(p)[2]
                        pontos_2d = [(projetar(p)[0], projetar(p)[1]) for p in pontos_3d]
                        faces_para_desenhar.append((profundidade / 4, face, pontos_2d))

        faces_para_desenhar.sort(key=lambda item: item[0])
        outline_color = "#ffffff" if estado_tema.get("escuro", False) else "#64748b"
        mostrar_cores = pagina_atual["idx"] >= 2   
        tumbling = atitude_var.get() == "Tumbling"
        for _prof, face, pts in faces_para_desenhar:
            if not mostrar_cores:
                destaque = False
            elif tumbling:
                destaque = face in faces_solares
            else:
                destaque = face in (face_nadir["valor"], face_vel["valor"]) or face in faces_solares
            canvas.create_polygon(
                pts,
                fill=cor_face_3d(face),
                outline="#f9fafb" if destaque else outline_color,
                width=2.8 if destaque else 1.1,
            )
        comprimento = max(nx, ny, nz) / 2 + 1.0
        desenhar_eixo((0, 0, 0), (comprimento, 0, 0), "#dc2626", "+X")
        desenhar_eixo((0, 0, 0), (-comprimento, 0, 0), "#991b1b", "-X")
        desenhar_eixo((0, 0, 0), (0, comprimento, 0), "#16a34a", "+Y")
        desenhar_eixo((0, 0, 0), (0, -comprimento, 0), "#166534", "-Y")
        desenhar_eixo((0, 0, 0), (0, 0, comprimento), "#2563eb", "+Z")
        desenhar_eixo((0, 0, 0), (0, 0, -comprimento), "#1e3a8a", "-Z")
        lbl_color = "#f3f4f6" if estado_tema["escuro"] else "#334155"
        lx, ly = 18, 18
        if mostrar_cores:
            if tumbling:
                legendas = [("Painel solar" if idioma != "EN" else "Solar panel", "#eab308")]
            else:
                legendas = [
                    ("Nadir", "#9333ea"),
                    ("Velocidade" if idioma != "EN" else "Velocity", "#2563eb"),
                    ("Painel solar" if idioma != "EN" else "Solar panel", "#eab308"),
                ]
            n_leg = len(legendas)
            y_info = ly + n_leg * 22 + 4         
            canvas.create_rectangle(lx - 8, ly - 8, lx + 170, y_info + 12, fill="#111827" if escuro else "#f8fafc", outline="#64748b")
            for j, (txt, cor) in enumerate(legendas):
                y = ly + j * 22
                canvas.create_rectangle(lx, y, lx + 16, y + 12, fill=cor, outline="#ffffff")
                canvas.create_text(lx + 24, y + 6, text=txt, anchor="w", fill=lbl_color, font=("Segoe UI", 9, "bold"))
        else:
            y_info = ly + 2
        canvas.create_text(
            lx,
            y_info,
            text=f"Yaw={math.degrees(view['yaw']):.0f}° | Pitch={math.degrees(view['pitch']):.0f}°",
            anchor="w",
            fill=lbl_color,
            font=("Segoe UI", 8),
        )


    def atualizar_orbita():
        dados = orbitas[orbita_var.get()]
        for chave, var in [("sma", sma_var), ("ecc", ecc_var), ("inc", inc_var), ("raan", raan_var), ("aop", aop_var), ("ta", ta_var)]:
            var.set(str(dados[chave]))
        personalizado = orbita_var.get() == "Personalizada"
        leo = orbita_var.get() == "LEO exemplo"
        set_estado([entradas_orbita["sma"], entradas_orbita["ecc"], entradas_orbita["inc"]], personalizado)
        set_estado([entradas_orbita["raan"], entradas_orbita["aop"], entradas_orbita["ta"]], personalizado or not leo)

    def atualizar_cubesat():
        dados = cubesats[cubesat_var.get()]
        dx_var.set(f"{dados['dx']:.4f}")
        dy_var.set(f"{dados['dy']:.4f}")
        dz_var.set(f"{dados['dz']:.4f}")
        nx_var.set(str(dados["grade"][0]))
        ny_var.set(str(dados["grade"][1]))
        nz_var.set(str(dados["grade"][2]))
        massa_var.set(f"{dados['massa']:.1f}")
        set_estado(entradas_sat.values(), False)
        atualizar_tudo()

    def atualizar_fluxo_analises():
        if bateria_var.get() and not placa_var.get():
            placa_var.set(True)
        if not placa_var.get():
            bateria_var.set(False)
            chk_bateria.config(state=tk.DISABLED)
        else:
            chk_bateria.config(state=tk.NORMAL)

    def atualizar_gs():
        set_estado(entradas_gs, gs_var.get())

    def atualizar_arquitetura():
        val = arq_var.get()
        outra_val = _("Outra", idioma)
        habilitado = val in ("Outra", "Other", outra_val)
        set_estado([ent_xe, ent_xd], habilitado)
        if val == "DET":
            xe_var.set("0.65")
            xd_var.set("0.85")
        elif val == "PPT":
            xe_var.set("0.60")
            xd_var.set("0.80")

    def atualizar_bateria():
        tipo = tipo_bat_var.get()
        set_estado([ent_dens], tipo in ("Outra", "Other", _("Outra", idioma)))
        if tipo in ("NiCd", _("NiCd", idioma)):
            dens_var.set("40")
        elif tipo in ("NiH2", _("NiH2", idioma)):
            dens_var.set("55")
        elif tipo in ("Li-ion", _("Li-ion", idioma)):
            dens_var.set("150")

    def atualizar_tudo():
        try:
            areas = areas_atuais()
        except ValueError:
            areas = {face: 0.0 for face in lista_faces}
        modo = modo_face_var.get()
        escuro = estado_tema.get("escuro", False)
        def colorir_rb(rb, is_selected):
            if is_selected:
                rb.config(fg="#111827")
            else:
                rb.config(fg="#f3f4f6" if escuro else "#111827")
        try:
            for rb in rbs_nadir + rbs_tumbling:
                colorir_rb(rb, rb.cget("value") == modo_face_var.get())
                rb.bind("<Configure>", lambda e, r=rb: colorir_rb(r, r.cget("value") == modo_face_var.get()))
        except Exception:
            pass

        for face, botao in botoes_faces.items():
            estado_botao = tk.NORMAL
            cor = "#475569" if escuro else "#cbd5e1"
            if modo == "nadir":
                if face == face_nadir["valor"]: cor = "#9333ea"
            elif modo == "vel":
                if face == face_vel["valor"]: cor = "#2563eb"
                elif not face_permitida_para_vel(face): cor = "#334155" if escuro else "#94a3b8"
            elif modo == "solar":
                if face in faces_solares: cor = "#eab308"

            if modo == "vel" and not face_permitida_para_vel(face):
                estado_botao = tk.DISABLED
            
            _escuro_face = estado_tema.get("escuro", True)
            _cor_normal_face = "#475569" if _escuro_face else "#cbd5e1"
            _cor_disabled_face = "#334155" if _escuro_face else "#94a3b8"
            _fg_face = "#111827" if cor not in (_cor_normal_face, _cor_disabled_face) else ("white" if _escuro_face else "#111827")
            botao.config(
                text=f"{face}\n{areas[face]*1e4:.0f} cm²",
                bg=cor,
                activebackground=cor,
                fg=_fg_face,
                state=estado_botao,
            )
        _nenhuma = "None" if idioma == "EN" else "nenhuma"
        _pan_lbl = "Panels" if idioma == "EN" else "Painéis"
        solares = ", ".join(sorted(faces_solares)) or _nenhuma

        if atitude_var.get() == "Tumbling":
            if tipo_ci_var.get() == "Quaternion":
                ci_str = f"Q=[{q1_var.get()}, {q2_var.get()}, {q3_var.get()}, {q4_var.get()}]"
            else:
                ci_str = f"Euler=[{ea1_var.get()}°, {ea2_var.get()}°, {ea3_var.get()}°]"
            
            rates_str = f"Rates=[{ear1_var.get()}°/s, {ear2_var.get()}°/s, {ear3_var.get()}°/s]"
            resumo_faces.config(text=f"{ci_str}\n{rates_str}\n{_pan_lbl}:    {solares}")
        else:
            _nadir_lbl = "Nadir" if idioma == "EN" else "Nadir"
            _vel_lbl = "Velocity" if idioma == "EN" else "Velocidade"
            resumo_faces.config(text=f"{_nadir_lbl}:      {face_nadir['valor']}\n{_vel_lbl}: {face_vel['valor']}\n{_pan_lbl}:    {solares}")
        desenhar_visual()
        if modo == "ci":
            frame_rates_container.pack_forget()
            frame_faces.pack_forget()
            resumo_faces.pack_forget()
            frame_ci_container.pack(fill=tk.X, pady=(4, 8))
        elif modo == "rates":
            frame_ci_container.pack_forget()
            frame_faces.pack_forget()
            resumo_faces.pack_forget()
            frame_rates_container.pack(fill=tk.X, pady=(4, 8))
        else:
            frame_ci_container.pack_forget()
            frame_rates_container.pack_forget()
            frame_faces.pack(anchor="center", pady=(0, 8))
            resumo_faces.pack(fill=tk.X, pady=(6, 0))


    def iniciar_arrasto(event):
        view["last"] = (event.x, event.y)

    def arrastar(event):
        if view["last"] is None:
            view["last"] = (event.x, event.y)
            return
        lx, ly = view["last"]
        view["yaw"] += (event.x - lx) * 0.012
        view["pitch"] += (event.y - ly) * 0.012
        view["pitch"] = max(-1.45, min(1.45, view["pitch"]))
        view["last"] = (event.x, event.y)
        desenhar_visual()

    def zoom(event):
        if getattr(event, "delta", 0) > 0:
            view["zoom"] *= 1.08
        else:
            view["zoom"] /= 1.08
        view["zoom"] = max(28, min(160, view["zoom"]))
        desenhar_visual()

    def resetar_visual():
        view["yaw"] = -0.65
        view["pitch"] = 0.45
        view["zoom"] = 70.0
        desenhar_visual()

    def validar_epoch_campos():
        _EPOCH_MIN = datetime(1957, 10, 4, 12, 0, 0)
        _EPOCH_MAX = datetime(2100, 2, 28, 0, 0, 0)
        epoch_str = epoch_campos_para_gmat()
        if epoch_str is None:
            if idioma == "EN":
                return None, "Invalid date. Use DD/MM/YYYY format and HH:MM for time.\nExample: 04/10/1957 + 12:00"
            else:
                return None, "Data inválida. Use o formato DD/MM/AAAA para a data e HH:MM para a hora.\nExemplo: 04/10/1957 + 12:00"
        try:
            dt = datetime.strptime(epoch_str.split('.')[0], '%d %b %Y %H:%M:%S')
        except ValueError:
            if idioma == "EN":
                return None, "Invalid date or time values."
            else:
                return None, "Valores de data ou horário inválidos."
        if dt < _EPOCH_MIN:
            if idioma == "EN":
                return None, "Start date too early. Minimum: 04/10/1957 at 12:00."
            else:
                return None, "Data de início muito antiga. Mínimo: 04/10/1957 às 12:00."
        if dt > _EPOCH_MAX:
            if idioma == "EN":
                return None, "Start date too late. Maximum: 28/02/2100 at 00:00."
            else:
                return None, "Data de início muito avançada. Máximo: 28/02/2100 às 00:00."
        return dt, None

    def _coletar_dados_formulario():
        try:
            orb = orbitas[orbita_var.get()]["codigo"]
            cubo = cubesats[cubesat_var.get()]["codigo"]
            nx, ny, nz = grade_atual()
            _epoch_dt_val, epoch_err = validar_epoch_campos()
            if epoch_err:
                messagebox.showerror(_("Dados inválidos", idioma), epoch_err, parent=root)
                return None
            epoch_gmat = epoch_campos_para_gmat()
            dados = {
                "orbit": orb,
                "sma": ler_float(sma_var, "SMA", SMA_MINIMO_KM),
                "ecc": ler_float(ecc_var, "ECC", 0.0, 0.9999),
                "inc": ler_float(inc_var, "INC", 0.0, 180.0),
                "raan": ler_float(raan_var, "RAAN", 0.0, 360.0),
                "aop": ler_float(aop_var, "AOP", 0.0, 360.0),
                "ta": ler_float(ta_var, "TA", 0.0, 360.0),
                "tamanho_u": cubo,
                "dx": ler_float(dx_var, "Dimensão X", 0.001),
                "dy": ler_float(dy_var, "Dimensão Y", 0.001),
                "dz": ler_float(dz_var, "Dimensão Z", 0.001),
                "grade_visual": (nx, ny, nz),
                "m_sat": ler_float(massa_var, "Massa", 0.001),
                "cd_sat": ler_float(cd_var, "Cd", 0.0),
                "cr_sat": ler_float(cr_var, "Cr", 0.0),
                "face_nadir": face_nadir["valor"],
                "face_vel": face_vel["valor"],
                "faces_com_celula": {f: (f in faces_solares) for f in lista_faces},
                "atitude_tipo": atitude_var.get(),
                "tipo_ci": tipo_ci_var.get(),
                "ea1": float(ea1_var.get().replace(",", ".") or "0") if atitude_var.get() == "Tumbling" and tipo_ci_var.get() == "EulerAngles" else 0.0,
                "ea2": float(ea2_var.get().replace(",", ".") or "0") if atitude_var.get() == "Tumbling" and tipo_ci_var.get() == "EulerAngles" else 0.0,
                "ea3": float(ea3_var.get().replace(",", ".") or "0") if atitude_var.get() == "Tumbling" and tipo_ci_var.get() == "EulerAngles" else 0.0,
                "ea_seq": ea_seq_var.get() if atitude_var.get() == "Tumbling" else "321",
                "q1": float(q1_var.get().replace(",", ".") or "0") if atitude_var.get() == "Tumbling" and tipo_ci_var.get() == "Quaternion" else 0.0,
                "q2": float(q2_var.get().replace(",", ".") or "0") if atitude_var.get() == "Tumbling" and tipo_ci_var.get() == "Quaternion" else 0.0,
                "q3": float(q3_var.get().replace(",", ".") or "0") if atitude_var.get() == "Tumbling" and tipo_ci_var.get() == "Quaternion" else 0.0,
                "q4": float(q4_var.get().replace(",", ".") or "1") if atitude_var.get() == "Tumbling" and tipo_ci_var.get() == "Quaternion" else 1.0,
                "ear1": float(ear1_var.get().replace(",", ".") or "0") if atitude_var.get() == "Tumbling" else 0.0,
                "ear2": float(ear2_var.get().replace(",", ".") or "0") if atitude_var.get() == "Tumbling" else 0.0,
                "ear3": float(ear3_var.get().replace(",", ".") or "0") if atitude_var.get() == "Tumbling" else 0.0,
                "gs": "s" if gs_var.get() else "n",
                "lat": ler_float(lat_var, "Latitude", -90.0, 90.0),
                "lon": ler_float(lon_var, "Longitude", -180.0, 180.0),
                "alt": ler_float(alt_var, "Altitude", 0.0) / 1000.0,
                "elev": ler_float(elev_var, "Elevação mínima", 0.0, 90.0),
                "tempo": ler_float(tempo_var, "Tempo de simulação", 0.01),
                "epoch": epoch_gmat,
                "executar": "s" if executar_var.get() and gmat_disponivel else "n",
                "Placa": "s" if placa_var.get() else "n",
                "Tm": ler_float(tm_var, "Tempo de missão", 0.0),
                "Pe": ler_float(pe_var, "Pe", 0.0),
                "Pd": ler_float(pd_var, "Pd", 0.0),
                "X": {"DET": 1, "PPT": 2, "Outra": 3}.get(arq_var.get(), 3),
                "Xe": ler_float(xe_var, "Xe", 0.00001, 1.0),
                "Xd": ler_float(xd_var, "Xd", 0.00001, 1.0),
                "Bateria": "s" if bateria_var.get() else "n",
                "BatPe": ler_float(bat_pe_var, "Pe da bateria", 0.0),
                "BatTm": ler_float(bat_tm_var, "Tempo de missão da bateria", 0.0),
                "Dod": ler_float(dod_var, "DoD", 0.00001, 1.0),
                "tipo_bat": {"NiCd": 1, "NiH2": 2, "Li-ion": 3, "Outra": 4}.get(tipo_bat_var.get(), 4),
                "densidade": ler_float(dens_var, "Densidade", 0.001),
                "N": ler_int(bancos_var, "Número de bancos", 1),
                "n": ler_float(eta_bat_var, "Eficiência de transmissão", 0.000001, 1.0),
            }
            return dados
        except ValueError as erro:
            messagebox.showerror(_("Dados inválidos", idioma), str(erro), parent=root)
            return None

    def confirmar():
        dados = _coletar_dados_formulario()
        if dados is None:
            return
        resultado["dados"] = dados
        root.destroy()

    def cancelar():
        resultado["dados"] = None
        root.destroy()

    def fechar_interface():
        resultado["dados"] = ENCERRAR_INTERFACE
        root.destroy()

    paginas = [
        (_("Órbita", idioma), [quadro_orbita]),
        (_("Satélite", idioma), [quadro_sat]),
        (_("Atitude / Painéis", idioma), [quadro_faces]),
        (_("Estação / Simulação", idioma), [quadro_sim]),
        ("Script / GMAT", [quadro_exec]),
    ]
    secoes_ocultas = [quadro_placa, quadro_bat]
    pagina_atual = {"idx": 0}
    fluxo_frame = tk.Frame(notebook, padx=8, pady=8)
    def _atualizar_cor_fluxo():
        _esc = estado_tema.get("escuro", False)
        _bg = "#4b5563" if _esc else "#d7dce2"
        _fg = "white" if _esc else "#111827"
        fluxo_frame.config(bg=_bg)
        lbl_titulo.config(bg=_bg, fg=_fg)

    fluxo_frame.pack(fill=tk.X, padx=10, pady=(8, 2))
    lbl_titulo = tk.Label(
        fluxo_frame,
        text=_("Mission Tree", idioma) if idioma == "EN" else "Mission Tree",
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    )
    lbl_titulo.pack(fill=tk.X, pady=(0, 5))
    labels_fluxo = []
    for indice, (nome, _secoes) in enumerate(paginas, start=1):
        label = tk.Label(
            fluxo_frame,
            text=f"{indice}. {nome}",
            anchor="w",
            padx=8,
            pady=5,
            font=("Segoe UI", 9),
        )
        label.pack(fill=tk.X, pady=2)
        labels_fluxo.append(label)
    _atualizar_cor_fluxo()

    def mostrar_pagina():
        for _nome, secoes in paginas:
            for sec in secoes:
                sec.pack_forget()
        for sec in secoes_ocultas:
            sec.pack_forget()

        idx = pagina_atual["idx"]
        for sec in paginas[idx][1]:
            sec.pack(fill=tk.X, padx=10, pady=7)

        for i, label in enumerate(labels_fluxo):
            escuro = estado_tema.get("escuro", False)
            if i == idx:
                label.config(bg="#4b5563" if escuro else "#475569", fg="white", font=("Segoe UI", 9, "bold"))
            elif i < idx:
                label.config(bg="#374151" if escuro else "#b8c2cc", fg="#cbd5e1" if escuro else "#111827", font=("Segoe UI", 9))
            else:
                label.config(bg="#1f2937" if escuro else "#cbd5e1", fg="#9ca3af" if escuro else "#111827", font=("Segoe UI", 9))

        escuro = estado_tema.get("escuro", False)
        bg_next = "#eab308" if escuro else "#d1d5db"
        fg_next = "#111827"
        
        btn_voltar.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        if idx == len(paginas) - 1:
            btn_proximo.config(text=_("Gerar script", idioma), font=("Segoe UI", 10, "bold"), command=confirmar, bg="#eab308", fg="#111827")
        else:
            btn_proximo.config(text=_("Próximo", idioma), font=("Segoe UI", 10, "bold" if escuro else "normal"), command=avancar_pagina, bg=bg_next, fg=fg_next)

        desenhar_visual()

    def erro_validacao(mensagem):
        messagebox.showerror(_("Entrada inválida", idioma), mensagem, parent=root)
        return False

    def validar_pagina_atual():
        idx = pagina_atual["idx"]
        try:
            if idx == 0:
                sma_val = ler_float(sma_var, "SMA")
                ler_float(ecc_var, "ECC", 0.0, 0.9999)
                ler_float(inc_var, "INC", 0.0, 180.0)
                ler_float(raan_var, "RAAN", 0.0, 360.0)
                ler_float(aop_var, "AOP", 0.0, 360.0)
                ler_float(ta_var, "TA", 0.0, 360.0)
                if sma_val < SMA_MINIMO_KM:
                    msg = "SMA inválido: use pelo menos {:.3f} km.\n\nEste mínimo é o raio da Terra ({:.3f} km) + {:.0f} km de altitude. Um valor menor colocaria a órbita dentro da Terra ou baixa demais para a propagação." if idioma != "EN" else "Invalid SMA: use at least {:.3f} km.\n\nThis minimum is the Earth radius ({:.3f} km) + {:.0f} km altitude. A lower value would place the orbit inside the Earth or too low for propagation."
                    return erro_validacao(msg.format(SMA_MINIMO_KM, RAIO_TERRA_KM, ALTITUDE_MINIMA_ORBITA_KM))
            elif idx == 1:
                ler_float(dx_var, "Dimensão X", 0.001)
                ler_float(dy_var, "Dimensão Y", 0.001)
                ler_float(dz_var, "Dimensão Z", 0.001)
                massa = ler_float(massa_var, "Massa")
                cd = ler_float(cd_var, "Cd")
                cr = ler_float(cr_var, "Cr")
                if massa <= 0:
                    return erro_validacao(_("Massa inválida: a massa do satélite precisa ser maior que zero.", idioma))
                if cd < 0:
                    return erro_validacao(_("Cd inválido: o coeficiente de arrasto não pode ser negativo.", idioma))
                if cr < 0:
                    return erro_validacao(_("Cr inválido: o coeficiente de reflexão solar não pode ser negativo.", idioma))
            elif idx == 2:
                if face_vel["valor"] == face_nadir["valor"] or face_vel["valor"] == FACE_OPOSTA[face_nadir["valor"]]:
                    return erro_validacao(_("Atitude inválida: a face de velocidade não pode ser igual nem oposta à face nadir.\n\nMotivo: o GMAT precisa de dois eixos independentes para definir a atitude Nadir Pointing.", idioma))
            elif idx == 3:
                if gs_var.get():
                    ler_float(lat_var, "Latitude", -90.0, 90.0)
                    ler_float(lon_var, "Longitude", -180.0, 180.0)
                    ler_float(alt_var, "Altitude", 0.0)
                    ler_float(elev_var, "Elevação mínima", 0.0, 90.0)
                ler_float(tempo_var, "Tempo de simulação", 0.01)
                _, _epoch_err = validar_epoch_campos()
                if _epoch_err:
                    return erro_validacao(_epoch_err)
        except ValueError as erro:
            return erro_validacao(str(erro))
        return True

    def avancar_pagina():
        if not validar_pagina_atual():
            return
            
        idx = pagina_atual["idx"]
        if idx == 2:
            modo = modo_face_var.get()
            if atitude_var.get() == "Tumbling":
                if modo == "ci":
                    modo_face_var.set("rates")
                    atualizar_tudo()
                    return
                elif modo == "rates":
                    modo_face_var.set("solar")
                    atualizar_tudo()
                    return
            else:
                if modo == "nadir":
                    modo_face_var.set("vel")
                    atualizar_tudo()
                    return
                elif modo == "vel":
                    modo_face_var.set("solar")
                    atualizar_tudo()
                    return

        if pagina_atual["idx"] < len(paginas) - 1:
            pagina_atual["idx"] += 1
            mostrar_pagina()

    def voltar_pagina():
        idx = pagina_atual["idx"]
        if idx == 2:
            modo = modo_face_var.get()
            if atitude_var.get() == "Tumbling":
                if modo == "solar":
                    modo_face_var.set("rates")
                    atualizar_tudo()
                    return
                elif modo == "rates":
                    modo_face_var.set("ci")
                    atualizar_tudo()
                    return
            else:
                if modo == "solar":
                    modo_face_var.set("vel")
                    atualizar_tudo()
                    return
                elif modo == "vel":
                    modo_face_var.set("nadir")
                    atualizar_tudo()
                    return

        if pagina_atual["idx"] > 0:
            pagina_atual["idx"] -= 1
            mostrar_pagina()

    canvas.bind("<ButtonPress-1>", iniciar_arrasto)
    canvas.bind("<B1-Motion>", arrastar)
    canvas.bind("<MouseWheel>", zoom)
    canvas.bind("<Configure>", lambda _event=None: desenhar_visual())

    def aplicar_tema_wizard(escuro):
        set_dark_titlebar(root, escuro)
        bg_color = "#111827" if escuro else "#e5e7eb"
        fg_color = "#f3f4f6" if escuro else "#111827"
        entry_bg = "#374151" if escuro else "#dfe3e8"
        entry_fg = "#f3f4f6" if escuro else "#111827"
        border_color = "#374151" if escuro else "#cbd5e1"
        canvas_3d_bg = "#0b0f19" if escuro else "#e5e7eb"

        root.configure(bg=bg_color)
        form.configure(bg=bg_color)
        area_visual.configure(bg=bg_color)
        _form_container.configure(bg=bg_color)
        _canvas_form.configure(bg=bg_color)
        notebook.configure(bg=bg_color)
        canvas.configure(bg=canvas_3d_bg, highlightbackground=border_color)
        rodape.configure(bg=bg_color)
        titulo.configure(bg=bg_color, fg=fg_color)

        def estilizar(w):
            w_class = w.winfo_class()
            if w_class == "Labelframe":
                w.configure(bg=bg_color, fg=fg_color)
            elif w_class == "Frame":
                w.configure(bg=bg_color)
            elif w_class == "Label":
                if w != titulo:
                    w.configure(bg=w.master.cget("bg"), fg=fg_color)
            elif w_class == "Entry":
                disabled_bg = "#1f2937" if escuro else "#cbd5e1"
                disabled_fg = "#9ca3af" if escuro else "#374151"
                w.configure(bg=entry_bg, fg=entry_fg, insertbackground=fg_color, disabledbackground=disabled_bg, disabledforeground=disabled_fg)
            elif w_class == "Checkbutton":
                w.configure(bg=w.master.cget("bg"), fg=fg_color, activebackground=bg_color, activeforeground=fg_color, selectcolor=entry_bg)
            elif w_class == "Radiobutton":
                w.configure(bg=w.master.cget("bg"), fg=fg_color, activebackground=bg_color, activeforeground=fg_color)
            elif w_class in ("Button", "Menubutton"):
                try:
                    txt = str(w.cget("text"))
                    if "Gerar script" not in txt and "Generate script" not in txt and "⏳" not in txt:
                        w.configure(bg="#374151" if escuro else "#d1d5db", fg="white" if escuro else "#111827", relief=tk.FLAT, bd=1)
                except Exception:
                    w.configure(bg="#374151" if escuro else "#d1d5db", fg="white" if escuro else "#111827", relief=tk.FLAT, bd=1)
                
                if w_class == "Menubutton":
                    try:
                        m = w.nametowidget(w.cget("menu"))
                        m.configure(bg="#374151" if escuro else "#d1d5db", fg="white" if escuro else "#111827")
                    except Exception:
                        pass
            elif w_class == "Text":
                w.configure(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)
            
            for child in w.winfo_children():
                estilizar(child)

        estilizar(painel_esquerdo)
        estilizar(rodape)
        
        if escuro:
            btn_proximo.configure(bg="#eab308", fg="#111827", font=("Segoe UI", 10, "bold"))
        else:
            btn_proximo.configure(bg="#d1d5db", fg="#111827", font=("Segoe UI", 10))

    def alternar_tema_wizard():
        estado_tema["escuro"] = not estado_tema["escuro"]
        atualizar_tema_wizard_ui()

    def atualizar_tema_wizard_ui():
        escuro = estado_tema["escuro"]
        aplicar_tema_wizard(escuro)
        btn_tema_wiz.config(text="🌓 " + _("Tema", idioma))
        desenhar_visual()
        mostrar_pagina()

    tk.Button(rodape, text=_("Resetar visualização", idioma), command=resetar_visual).pack(side=tk.LEFT)
    
    btn_tema_wiz = tk.Button(rodape, text="", command=alternar_tema_wizard, width=10)
    btn_tema_wiz.pack(side=tk.LEFT, padx=(8, 0))

    comandos_esquerda.grid_columnconfigure(0, weight=1)
    botoes_navegacao = tk.Frame(comandos_esquerda, bg="#e5e7eb")
    botoes_navegacao.pack(anchor="center", pady=(0, 8))
    btn_voltar = tk.Button(botoes_navegacao, text=_("Voltar", idioma), command=voltar_pagina, width=12, height=2)
    btn_voltar.pack(side=tk.LEFT, padx=(0, 8))
    btn_proximo = tk.Button(botoes_navegacao, text=_("Próximo", idioma), command=avancar_pagina, width=12, height=2)
    btn_proximo.pack(side=tk.LEFT)

    botoes_cancelar = tk.Frame(comandos_esquerda, bg="#e5e7eb")
    botoes_cancelar.pack(anchor="center", pady=(8, 0))
    tk.Button(botoes_cancelar, text=_("Cancelar e usar terminal", idioma), command=cancelar, width=26, height=2).pack()

    atualizar_orbita()
    atualizar_cubesat()
    atualizar_gs()
    mostrar_pagina()
    atualizar_fluxo_analises()
    atualizar_arquitetura()
    atualizar_bateria()
    atualizar_tudo()
    atualizar_tema_wizard_ui()
    
    root.protocol("WM_DELETE_WINDOW", fechar_interface)
    root.mainloop()
    return resultado["dados"]



def criar_janela_saida_interface(idioma="PT"):
    if not tkinter_disponivel:
        return None

    try:
        janela = tk.Tk()
        definir_icone(janela)
    except tk.TclError:
        return None

    escuro = estado_tema.get("escuro", False)
    set_dark_titlebar(janela, escuro)
    janela.title(_("Pegasus - Saída e Resumo", idioma))
    janela.resizable(True, True)
    janela.minsize(860, 560)
    abrir_maximizada(janela, 980, 640)
    fundo = "#111827" if escuro else "#e5e7eb"
    painel = "#1f2937" if escuro else "#d7dce2"
    janela.configure(bg=fundo)
    janela.grid_columnconfigure(1, weight=1)
    janela.grid_rowconfigure(1, weight=1)

    cabecalho = tk.Label(
        janela,
        text=_("Fluxo sequencial de análise do CubeSat", idioma),
        bg=fundo,
        fg="#f3f4f6" if escuro else "#111827",
        font=("Segoe UI", 13, "bold"),
        anchor="w",
        padx=12,
        pady=10,
    )
    cabecalho.grid(row=0, column=0, columnspan=2, sticky="ew")

    etapas_frame = tk.Frame(janela, bg=painel, padx=10, pady=10)
    etapas_frame.grid(row=1, column=0, sticky="nsw", padx=(10, 0), pady=(0, 10))
    tk.Label(etapas_frame, text=_("Seção", idioma), bg=painel, fg="#f3f4f6" if escuro else "#111827", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

    etapas = {}
    for nome in ["1. Dados preliminares", "2. Script / GMAT", "3. Painéis solares", "4. Baterias"]:
        label = tk.Label(
            etapas_frame,
            text=_(nome, idioma),
            bg="#1f2937" if escuro else "#cbd5e1",
            fg="#9ca3af" if escuro else "#111827",
            anchor="w",
            width=22,
            padx=8,
            pady=7,
            font=("Segoe UI", 9),
        )
        label.pack(fill=tk.X, pady=4)
        etapas[nome] = label

    saida_frame = tk.Frame(janela, bg=fundo, padx=10, pady=0)
    saida_frame.grid(row=1, column=1, sticky="nsew", pady=(0, 10))
    saida_frame.grid_rowconfigure(1, weight=1)
    saida_frame.grid_columnconfigure(0, weight=1)

    etapa_atual = tk.StringVar(value=_("1. Dados preliminares", idioma))
    tk.Label(
        saida_frame,
        textvariable=etapa_atual,
        bg=fundo,
        fg="#f3f4f6" if escuro else "#111827",
        anchor="w",
        font=("Segoe UI", 11, "bold"),
    ).grid(row=0, column=0, sticky="ew", pady=(0, 6))

    texto = tk.Text(
        saida_frame,
        bg="#374151" if escuro else "#dfe3e8",
        fg="#f3f4f6" if escuro else "#111827",
        insertbackground="#f3f4f6" if escuro else "#111827",
        relief=tk.FLAT,
        wrap=tk.WORD,
        font=("Consolas", 10),
        padx=12,
        pady=12,
    )
    rolagem = tk.Scrollbar(saida_frame, command=texto.yview)
    texto.configure(yscrollcommand=rolagem.set)
    texto.tag_configure("resultado_suficiente", foreground="#15803d", font=("Consolas", 10, "bold"))
    texto.tag_configure("resultado_insuficiente", foreground="#dc2626", font=("Consolas", 10, "bold"))
    texto.tag_configure("numero", foreground="#2563eb", font=("Consolas", 10, "bold"))
    texto.grid(row=1, column=0, sticky="nsew")
    rolagem.grid(row=1, column=1, sticky="ns")

    def set_etapa(nome):
        etapa_atual.set(_(nome, idioma))
        for chave, label in etapas.items():
            if chave == nome:
                label.config(bg="#4b5563" if escuro else "#475569", fg="white", font=("Segoe UI", 9, "bold"))
            else:
                label.config(bg="#1f2937" if escuro else "#cbd5e1", fg="#9ca3af" if escuro else "#111827", font=("Segoe UI", 9))
        try:
            janela.update_idletasks()
            janela.update()
        except tk.TclError:
            pass

    def escrever(mensagem):
        try:
            termos = [
                ("INSUFFICIENT", "resultado_insuficiente"),
                ("INSUFICIENTE", "resultado_insuficiente"),
                ("SUFFICIENT", "resultado_suficiente"),
                ("SUFICIENTE", "resultado_suficiente"),
            ]

            padrao = re.compile(r"(INSUFFICIENT|INSUFICIENTE|SUFFICIENT|SUFICIENTE|[-+]?\d+(?:[\\.,]\d+)?\\s*(?:W|Wh|kg|m²|m2|s|min|h|%|km|graus|deg)?)", re.IGNORECASE)
            pos = 0
            for match in padrao.finditer(mensagem):
                if match.start() > pos:
                    texto.insert(tk.END, mensagem[pos:match.start()])
                trecho = match.group(0)
                trecho_upper = trecho.upper()
                tag = None
                for termo, tag_nome in termos:
                    if termo in trecho_upper:
                        tag = tag_nome
                        break
                if tag is None and re.search(r"\d", trecho):
                    tag = "numero"
                texto.insert(tk.END, trecho, tag if tag else "")
                pos = match.end()
            if pos < len(mensagem):
                texto.insert(tk.END, mensagem[pos:])

            texto.see(tk.END)
            janela.update_idletasks()
            janela.update()
        except tk.TclError:
            pass

    def fechar():
        try:
            acao_var.set("fechar")
        except Exception:
            pass
        try:
            janela.destroy()
        except tk.TclError:
            pass

    barra_nav = tk.Frame(janela, bg=fundo)
    barra_nav.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

    tk.Button(
        barra_nav,
        text="⬅ Menu inicial / Novo dimensionamento" if idioma != "EN" else "⬅ Main menu / New sizing",
        command=lambda: reiniciar_aplicacao(parent=janela, idioma=idioma),
        height=2,
        bg="#374151" if escuro else "#d1d5db",
        fg="white" if escuro else "#111827",
    ).pack(side=tk.LEFT, padx=(0, 8))

    tk.Button(
        barra_nav,
        text="Abrir GMAT" if idioma != "EN" else "Open GMAT",
        command=lambda: abrir_gmat(parent=janela),
        height=2,
    ).pack(side=tk.LEFT, padx=(0, 8))

    tk.Button(
        barra_nav,
        text="Abrir resultados" if idioma != "EN" else "Open results",
        command=lambda: abrir_pasta_resultados(parent=janela),
        height=2,
    ).pack(side=tk.LEFT, padx=(0, 8))

    tk.Button(
        barra_nav,
        text="Abrir scripts" if idioma != "EN" else "Open scripts",
        command=lambda: abrir_pasta_scripts(parent=janela),
        height=2,
    ).pack(side=tk.LEFT, padx=(0, 8))

    tk.Button(
        barra_nav,
        text="Exportar TXT" if idioma != "EN" else "Export TXT",
        command=lambda: exportar_texto_resumo(texto.get("1.0", tk.END), parent=janela),
        height=2,
    ).pack(side=tk.LEFT, padx=(0, 8))

    tk.Button(
        barra_nav,
        text="Tabela de períodos" if idioma != "EN" else "Periods table",
        command=lambda: criar_treeview_periodos(saida_frame, texto.get("1.0", tk.END)) and janela.update_idletasks(),
        height=2,
    ).pack(side=tk.LEFT, padx=(0, 8))

    acao_var = tk.StringVar(value="nenhuma")

    def acao_recalcular():
        acao_var.set("recalcular")

    btn_recalcular = tk.Button(
        barra_nav,
        text="Recalcular Placa/Bateria" if idioma != "EN" else "Recalculate Panel/Battery",
        command=acao_recalcular,
        height=2,
        state=tk.DISABLED,
    )
    btn_recalcular.pack(side=tk.LEFT, padx=(0, 8))

    tk.Button(
        barra_nav,
        text="Fechar" if idioma != "EN" else "Close",
        command=fechar,
        height=2,
        bg="#991b1b" if escuro else "#fecaca",
        fg="white" if escuro else "#111827",
    ).pack(side=tk.RIGHT)

    janela.protocol("WM_DELETE_WINDOW", fechar)
    set_etapa("1. Dados preliminares")
    return {"janela": janela, "escrever": escrever, "set_etapa": set_etapa, "fechar": fechar,
            "btn_recalcular": btn_recalcular, "acao_var": acao_var,
            "ler_log": lambda: texto.get("1.0", tk.END)}


def abrir_aviso_gmat_rodando(parent, idioma="PT"):
    if not tkinter_disponivel:
        return None
    try:
        janela = tk.Toplevel(parent) if parent is not None else tk.Tk()
        definir_icone(janela)
        escuro = estado_tema.get("escuro", False)
        set_dark_titlebar(janela, escuro)
        bg_color = "#111827" if escuro else "#d7dce2"
        fg_color = "#f3f4f6" if escuro else "#111827"
        header_bg = "#1f2937" if escuro else "#243447"
        
        janela.title("GMAT")
        janela.geometry("340x130")
        janela.resizable(False, False)
        janela.configure(bg=bg_color)
        tk.Label(
            janela,
            text=_("GMAT está rodando...", idioma),
            bg=header_bg,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            padx=12,
            pady=10,
        ).pack(fill=tk.X)
        tk.Label(
            janela,
            text=_("Aguarde a propagação e a geração dos arquivos de resultado.", idioma),
            bg=bg_color,
            fg=fg_color,
            wraplength=300,
            justify=tk.CENTER,
            padx=16,
            pady=18,
        ).pack(fill=tk.BOTH, expand=True)
        if parent is not None:
            janela.transient(parent)
        janela.update_idletasks()
        janela.update()
        return janela
    except tk.TclError:
        return None


def fechar_aviso(janela):
    if janela is None:
        return
    try:
        janela.destroy()
    except tk.TclError:
        pass


def criar_corpo_rolavel(janela, bg, padx=14, pady=12, largura_max=680):
    container = tk.Frame(janela, bg=bg)
    container.pack(fill=tk.BOTH, expand=True)
    canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
    barra = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    corpo = tk.Frame(canvas, bg=bg, padx=padx, pady=pady)
    _win = canvas.create_window((0, 0), window=corpo, anchor="nw")
    canvas.configure(yscrollcommand=barra.set)
    barra.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _ajustar_regiao(_=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
    corpo.bind("<Configure>", _ajustar_regiao)

    def _ajustar_largura(e):
        canvas.itemconfigure(_win, width=min(e.width, largura_max) if largura_max else e.width)
    canvas.bind("<Configure>", _ajustar_largura)

    def _rolar(ev):
        if corpo.winfo_reqheight() > canvas.winfo_height():
            canvas.yview_scroll(int(-ev.delta / 120), "units")
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _rolar))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    return corpo


def abrir_maximizada(janela, largura, altura):
    janela.geometry(f"{int(largura)}x{int(altura)}")

    def _maximizar():
        try:
            janela.state("zoomed")
        except Exception:
            pass

    _maximizar()
    janela.after(30, _maximizar)


def solicitar_analise_por_interface(parent, faces_ativas, tamanho_u_atual=1,
                                    tem_contato=True, ler_log=None, idioma="PT"):
    if not tkinter_disponivel:
        return ["n"]

    janela = tk.Toplevel(parent) if parent is not None else tk.Tk()
    definir_icone(janela)
    escuro = estado_tema.get("escuro", False)
    set_dark_titlebar(janela, escuro)
    bg_color = "#111827" if escuro else "#d7dce2"
    fg_color = "#f3f4f6" if escuro else "#111827"
    panel_color = "#1f2937" if escuro else "#d7dce2"
    entry_bg = "#374151" if escuro else "#dfe3e8"
    entry_fg = "#f3f4f6" if escuro else "#111827"
    header_bg = "#000000" if escuro else "#243447"
    disabled_bg = "#1f2937" if escuro else "#c4ccd5"

    janela.title("Power analysis" if idioma == "EN" else "Análise de potência")
    janela.resizable(True, True)
    janela.configure(bg=bg_color)
    resultado = {"respostas": ["n"]}
    dados = {}

    tk.Label(janela, text=("Power analysis" if idioma == "EN" else "Análise de potência"),
             bg=header_bg, fg="white", font=("Segoe UI", 12, "bold"),
             anchor="w", padx=12, pady=9).pack(fill=tk.X)

    rodape = tk.Frame(janela, bg=bg_color, padx=14, pady=10)
    rodape.pack(side=tk.BOTTOM, fill=tk.X)

    meio = tk.Frame(janela, bg=bg_color)
    meio.pack(fill=tk.BOTH, expand=True)

    esquerda = tk.Frame(meio, bg=panel_color, width=700)
    esquerda.pack(side=tk.LEFT, fill=tk.Y)
    esquerda.pack_propagate(False)

    direita = tk.Frame(meio, bg=bg_color, padx=10, pady=8)
    direita.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    tk.Label(direita, text=("Configuration preview" if idioma == "EN"
                            else "Prévia da configuração"),
             bg=bg_color, fg=fg_color, anchor="w", font=("Segoe UI", 10, "bold")).pack(fill=tk.X)
    _prev_frame = tk.Frame(direita, bg=bg_color)
    _prev_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
    preview = tk.Text(_prev_frame, bg="#374151" if escuro else "#dfe3e8",
                      fg=fg_color, insertbackground=fg_color, relief=tk.FLAT,
                      wrap=tk.NONE, font=("Consolas", 9), padx=10, pady=8)
    _prev_sb = ttk.Scrollbar(_prev_frame, orient="vertical", command=preview.yview)
    preview.configure(yscrollcommand=_prev_sb.set)
    _prev_sb.pack(side=tk.RIGHT, fill=tk.Y)
    preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    try:
        preview.insert("1.0", ler_log() if callable(ler_log) else (ler_log or ""))
        preview.see(tk.END)
    except Exception:
        pass
    preview.configure(state=tk.DISABLED)

    etapas_frame = tk.Frame(esquerda, bg=panel_color, padx=12, pady=8)
    etapas_frame.pack(fill=tk.X)
    _nomes_etapas = [("placa",   "1. Solar panels" if idioma == "EN" else "1. Painéis solares"),
                     ("modos",   "2. Operating modes" if idioma == "EN" else "2. Modos de operação"),
                     ("bateria", "3. Battery" if idioma == "EN" else "3. Bateria")]
    lbls_etapa = {}
    for chave, nome in _nomes_etapas:
        lb = tk.Label(etapas_frame, text=nome, anchor="w", padx=8, pady=4,
                      font=("Segoe UI", 9), bg=panel_color, fg=fg_color)
        lb.pack(side=tk.LEFT, padx=(0, 6))
        lbls_etapa[chave] = lb

    area_paginas = tk.Frame(esquerda, bg=panel_color)
    area_paginas.pack(fill=tk.BOTH, expand=True)

    def _erro(msg):
        mostrar_erro_input(msg, janela, idioma)

    def ler_float(var, nome, minimo=None, maximo=None):
        try:
            valor = float(var.get().replace(",", "."))
        except ValueError:
            raise ValueError(_("{}: digite um número válido.", idioma).format(_(nome, idioma)))
        if minimo is not None and valor < minimo:
            raise ValueError(_("{}: o valor mínimo permitido é {}.", idioma).format(_(nome, idioma), minimo))
        if maximo is not None and valor > maximo:
            raise ValueError(_("{}: o valor máximo permitido é {}.", idioma).format(_(nome, idioma), maximo))
        return valor

    def ler_int(var, nome, minimo=None):
        try:
            valor = int(var.get())
        except ValueError:
            raise ValueError(_("{}: digite um número inteiro válido.", idioma).format(_(nome, idioma)))
        if minimo is not None and valor < minimo:
            raise ValueError(_("{}: o valor mínimo permitido é {}.", idioma).format(_(nome, idioma), minimo))
        return valor

    def campo(pai, rotulo, var):
        frame = tk.Frame(pai, bg=panel_color)
        frame.pack(fill=tk.X, pady=4)
        tk.Label(frame, text=_(rotulo, idioma), bg=panel_color, fg=fg_color,
                 anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ent = tk.Entry(frame, textvariable=var, bg=entry_bg, fg=entry_fg,
                       insertbackground=fg_color, width=14, justify=tk.RIGHT,
                       disabledbackground=disabled_bg, disabledforeground="#6b7280")
        ent.pack(side=tk.RIGHT)
        return ent

    # ---------------------------------------------- PÁGINA 1: PAINÉIS ---------------------
    pag_placa = tk.Frame(area_paginas, bg=panel_color)
    corpo_placa = criar_corpo_rolavel(pag_placa, panel_color, largura_max=660)

    potencia_padrao = max(1, int(tamanho_u_atual) - 0.5)
    executar_var = tk.BooleanVar(value=bool(faces_ativas))
    tm_var = tk.StringVar(value="1")
    eff_var = tk.StringVar(value="0.30")
    deg_var = tk.StringVar(value="2.75")
    id_var = tk.StringVar(value="0.77")
    pe_var = tk.StringVar(value=str(potencia_padrao))
    pd_var = tk.StringVar(value=str(potencia_padrao))
    fos_var = tk.StringVar(value="0")
    arq_var = tk.StringVar(value="DET")
    arq_desc_var = tk.StringVar(value="DET: Direct Energy Transfer")
    xe_var = tk.StringVar(value="0.65")
    xd_var = tk.StringVar(value="0.85")
    fill_factor_var = tk.StringVar(value="0.6062")
    n_cel_var = tk.StringVar(value="2")
    area_cel_var = tk.StringVar(value="30.31")

    tk.Label(corpo_placa, text=_("Confirme as faces usadas na análise", idioma), bg=panel_color,
             fg=fg_color, anchor="w", font=("Segoe UI", 9, "bold")).pack(fill=tk.X)
    frame_faces = tk.Frame(corpo_placa, bg=panel_color)
    frame_faces.pack(fill=tk.X, pady=(4, 10))
    faces_vars = {}
    for i, face in enumerate(FACES.keys()):
        v = tk.BooleanVar(value=face in faces_ativas)
        tk.Checkbutton(frame_faces, text=face, variable=v, bg=panel_color, fg=fg_color,
                       selectcolor=entry_bg, activebackground=panel_color,
                       activeforeground=fg_color, width=7, anchor="w"
                       ).grid(row=i // 3, column=i % 3, sticky="w", padx=4, pady=2)
        faces_vars[face] = v

    tk.Checkbutton(corpo_placa, text=_("Executar análise de painéis", idioma), variable=executar_var,
                   bg=panel_color, fg=fg_color, selectcolor=entry_bg, activebackground=panel_color,
                   activeforeground=fg_color, command=lambda: atualizar_nav()).pack(anchor="w", pady=(0, 8))

    ent_tm = campo(corpo_placa, "Mission time [years]" if idioma == "EN" else "Tempo de missão [anos]", tm_var)
    ToolTip(ent_tm, _("Tempo de missão em anos (mín. 0)", idioma))
    ent_eff = campo(corpo_placa, "Cell eff. Eff [0-1]" if idioma == "EN" else "Eficiência Eff [0 a 1]", eff_var)
    ToolTip(ent_eff, _("Eficiência da célula (padrão 0,30)", idioma))
    ent_deg = campo(corpo_placa, "Annual degr. [%/yr]" if idioma == "EN" else "Degradação anual [%/ano]", deg_var)
    ToolTip(ent_deg, _("Degradação por ano em % (padrão 2,75)", idioma))
    ent_id = campo(corpo_placa, "Inherent degr. Id [0-1]" if idioma == "EN" else "Degr. inerente Id [0 a 1]", id_var)
    ToolTip(ent_id, _("Degradação inerente de projeto (padrão 0,77)", idioma))

    _rot_direto = "Pe and Pd directly" if idioma == "EN" else "Pe e Pd diretos"
    _rot_modos = "By operating modes" if idioma == "EN" else "Por modos de operação"
    consumo_var = tk.StringVar(value=_rot_direto)
    fr_consumo = tk.Frame(corpo_placa, bg=panel_color)
    fr_consumo.pack(fill=tk.X, pady=(8, 2))
    tk.Label(fr_consumo, text=("Load source" if idioma == "EN" else "Origem do consumo"),
             bg=panel_color, fg=fg_color, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
    _opt_consumo = tk.OptionMenu(fr_consumo, consumo_var, _rot_direto, _rot_modos,
                                 command=lambda v: atualizar_consumo(v))
    _opt_consumo.config(width=22, bg=entry_bg, fg=entry_fg, activebackground=entry_bg,
                        activeforeground=entry_fg, anchor="w")
    _opt_consumo.pack(side=tk.RIGHT)
    lbl_consumo = tk.Label(corpo_placa, text="", bg=panel_color,
                           fg="#9ca3af" if escuro else "#334155", anchor="w", font=("Segoe UI", 9))
    lbl_consumo.pack(fill=tk.X, pady=(0, 4))

    ent_pe = campo(corpo_placa, "Pe [W]", pe_var)
    ToolTip(ent_pe, _("Potência máxima consumida no eclipse", idioma))
    ent_pd = campo(corpo_placa, "Pd [W]", pd_var)
    ToolTip(ent_pd, _("Potência máxima consumida no sol", idioma))

    def atualizar_consumo(_v=None):
        if consumo_var.get() == _rot_modos:
            ent_pe.config(state=tk.DISABLED)
            ent_pd.config(state=tk.DISABLED)
            lbl_consumo.config(text=("Modes are filled in the next step." if idioma == "EN"
                                     else "Os modos são preenchidos na etapa seguinte."))
        else:
            ent_pe.config(state=tk.NORMAL)
            ent_pd.config(state=tk.NORMAL)
            lbl_consumo.config(text="")
        atualizar_nav()

    ent_fos = campo(corpo_placa, "Panel safety factor [adm]" if idioma == "EN"
                    else "Fator de segurança da placa [adm]", fos_var)
    ToolTip(ent_fos, "Dimensionless margin applied to the required panel power: (1+FS)·Psa (e.g. 0.2 = +20%; default 0)"
                     if idioma == "EN" else
                     "Margem adimensional aplicada à potência de placa requerida: (1+FS)·Psa (ex.: 0,2 = +20%; padrão 0)")

    fr_arq = tk.Frame(corpo_placa, bg=panel_color)
    fr_arq.pack(fill=tk.X, pady=4)
    tk.Label(fr_arq, text=_("Arquitetura de potência", idioma), bg=panel_color, fg=fg_color,
             anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
    _opt_arq = tk.OptionMenu(fr_arq, arq_var, "DET", "PPT", _("Outra", idioma),
                             command=lambda v: atualizar_arquitetura(v))
    _opt_arq.config(width=8, bg=entry_bg, fg=entry_fg, activebackground=entry_bg, activeforeground=entry_fg)
    _opt_arq.pack(side=tk.RIGHT)
    tk.Label(corpo_placa, textvariable=arq_desc_var, bg=panel_color,
             fg="#9ca3af" if escuro else "#334155", anchor="w",
             font=("Segoe UI", 9)).pack(fill=tk.X, pady=(0, 4))
    ent_xe = campo(corpo_placa, "Xe", xe_var)
    ToolTip(ent_xe, _("Eficiência de descarga (0 a 1)", idioma))
    ent_xd = campo(corpo_placa, "Xd", xd_var)
    ToolTip(ent_xd, _("Eficiência de carga (0 a 1)", idioma))

    def atualizar_arquitetura(_v=None):
        val = arq_var.get()
        if val == "DET":
            arq_desc_var.set("DET: Direct Energy Transfer")
            xe_var.set("0.65"); xd_var.set("0.85")
            ent_xe.config(state=tk.DISABLED); ent_xd.config(state=tk.DISABLED)
        elif val == "PPT":
            arq_desc_var.set("PPT: Peak Power Tracking")
            xe_var.set("0.60"); xd_var.set("0.80")
            ent_xe.config(state=tk.DISABLED); ent_xd.config(state=tk.DISABLED)
        else:
            arq_desc_var.set(_("Outra: informe manualmente Xe e Xd", idioma))
            ent_xe.config(state=tk.NORMAL); ent_xd.config(state=tk.NORMAL)

    _rot_fill_area = "By area [0-1]" if idioma == "EN" else "Por área [0 a 1]"
    _rot_fill_1u = "By 1U face (cells)" if idioma == "EN" else "Por face 1U (células)"
    fill_mode_var = tk.StringVar(value=_rot_fill_area)
    fr_fill = tk.Frame(corpo_placa, bg=panel_color)
    fr_fill.pack(fill=tk.X, pady=(8, 2))
    tk.Label(fr_fill, text=("Fill factor mode" if idioma == "EN" else "Modo do fator de preenchimento"),
             bg=panel_color, fg=fg_color, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
    _opt_fill = tk.OptionMenu(fr_fill, fill_mode_var, _rot_fill_area, _rot_fill_1u,
                              command=lambda v: atualizar_fill(v))
    _opt_fill.config(width=22, bg=entry_bg, fg=entry_fg, activebackground=entry_bg,
                     activeforeground=entry_fg, anchor="w")
    _opt_fill.pack(side=tk.RIGHT)
    ent_fill = campo(corpo_placa, "Fill factor [0-1]" if idioma == "EN"
                     else "Fator de preenchimento [0 a 1]", fill_factor_var)
    ToolTip(ent_fill, _("Fração da face coberta por células (padrão 0,6062).", idioma))
    ent_ncel = campo(corpo_placa, "Cells per 1U face" if idioma == "EN" else "Células por face 1U", n_cel_var)
    ToolTip(ent_ncel, "Number of cells on a 1U (100 cm²) face; scales with face size (a 3U face fits 3x)."
                      if idioma == "EN" else
                      "Número de células numa face 1U (100 cm²); escala com o tamanho (face 3U cabe 3x).")
    ent_acel = campo(corpo_placa, "Cell area [cm²]" if idioma == "EN" else "Área da célula [cm²]", area_cel_var)
    ToolTip(ent_acel, _("Área de cada célula solar em cm² (padrão 30,31).", idioma))

    def atualizar_fill(_v=None):
        if fill_mode_var.get() == _rot_fill_1u:
            ent_fill.config(state=tk.DISABLED)
            ent_ncel.config(state=tk.NORMAL); ent_acel.config(state=tk.NORMAL)
        else:
            ent_fill.config(state=tk.NORMAL)
            ent_ncel.config(state=tk.DISABLED); ent_acel.config(state=tk.DISABLED)

    # ---------------------------------------------- PÁGINA 2: MODOS -----------------------
    pag_modos = tk.Frame(area_paginas, bg=panel_color)
    tk.Label(pag_modos, text=("Pd = Σ P·duty (sunlight)  |  Pe = Σ P·duty (eclipse)  —  SMAD"
                              if idioma == "EN" else
                              "Pd = Σ P·duty (no Sol)  |  Pe = Σ P·duty (no eclipse)  —  SMAD"),
             bg=panel_color, fg="#9ca3af" if escuro else "#334155", anchor="w",
             padx=12, font=("Segoe UI", 9)).pack(fill=tk.X, pady=(8, 0))
    _dica_modos = ("The phase decides whether the mode enters Pd, Pe or both."
                   if idioma == "EN" else
                   "A fase decide se o modo entra em Pd, em Pe ou em ambos.")
    if tem_contato:
        _dica_modos += ("   Contact duty = total contact time / total time of the phase."
                        if idioma == "EN" else
                        "   Duty do contato = tempo total de contato / tempo total da fase.")
    tk.Label(pag_modos, text=_dica_modos, bg=panel_color,
             fg="#9ca3af" if escuro else "#334155", anchor="w", padx=12,
             font=("Segoe UI", 8), wraplength=650, justify=tk.LEFT).pack(fill=tk.X, pady=(0, 6))

    FASES_ROT = [("sempre", 1, "Always" if idioma == "EN" else "Sempre"),
                 ("sol", 2, "Sun only" if idioma == "EN" else "Só no Sol"),
                 ("eclipse", 3, "Eclipse only" if idioma == "EN" else "Só no eclipse")]
    _rot_por_fase = {f[0]: f[2] for f in FASES_ROT}
    _fase_por_rot = {f[2]: (f[0], f[1]) for f in FASES_ROT}
    _rotulos_fase = [f[2] for f in FASES_ROT]

    COL_NOME, COL_P, COL_FASE, COL_DUTY, COL_AUTO, COL_RM = 170, 70, 125, 75, 105, 34

    def celula(pai, largura, altura=28):
        c = tk.Frame(pai, bg=panel_color, width=largura, height=altura)
        c.pack_propagate(False)
        c.pack(side=tk.LEFT, padx=1)
        return c

    cab_modos = tk.Frame(pag_modos, bg=panel_color, padx=12, pady=4)
    cab_modos.pack(fill=tk.X)
    _cols = [("Mode" if idioma == "EN" else "Modo", COL_NOME, "w"),
             ("P [W]", COL_P, "w"),
             ("Phase" if idioma == "EN" else "Fase", COL_FASE, "w"),
             ("Duty [0-1]", COL_DUTY, "w")]
    if tem_contato:
        _cols.append(("Duty from\ncontact" if idioma == "EN" else "Duty do\ncontato", COL_AUTO, "center"))
    _cols.append(("", COL_RM, "w"))
    for _txt, _w, _anc in _cols:
        _c = celula(cab_modos, _w, 32)
        tk.Label(_c, text=_txt, bg=panel_color, fg=fg_color, anchor=_anc, justify=tk.CENTER,
                 font=("Segoe UI", 9, "bold")).pack(fill=tk.BOTH, expand=True)

    cont_modos = tk.Frame(pag_modos, bg=panel_color)
    cont_modos.pack(fill=tk.BOTH, expand=True, padx=12)
    cv_modos = tk.Canvas(cont_modos, bg=panel_color, highlightthickness=0)
    sb_modos = ttk.Scrollbar(cont_modos, orient="vertical", command=cv_modos.yview)
    inner_modos = tk.Frame(cv_modos, bg=panel_color)
    _win_modos = cv_modos.create_window((0, 0), window=inner_modos, anchor="nw")
    cv_modos.configure(yscrollcommand=sb_modos.set)
    sb_modos.pack(side=tk.RIGHT, fill=tk.Y)
    cv_modos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    inner_modos.bind("<Configure>", lambda e: cv_modos.configure(scrollregion=cv_modos.bbox("all")))
    cv_modos.bind("<Configure>", lambda e: cv_modos.itemconfigure(_win_modos, width=e.width))

    def _rolar_modos(ev):
        if inner_modos.winfo_reqheight() > cv_modos.winfo_height():
            cv_modos.yview_scroll(int(-ev.delta / 120), "units")
    cv_modos.bind("<Enter>", lambda e: cv_modos.bind_all("<MouseWheel>", _rolar_modos))
    cv_modos.bind("<Leave>", lambda e: cv_modos.unbind_all("<MouseWheel>"))

    linhas_modos = []

    def adicionar_modo(nome="", pw="", fase="sempre", duty="1", auto=False):
        fr = tk.Frame(inner_modos, bg=panel_color)
        fr.pack(fill=tk.X, pady=2)
        v_nome = tk.StringVar(value=nome)
        v_pw = tk.StringVar(value=pw)
        v_fase = tk.StringVar(value=_rot_por_fase.get(fase, _rotulos_fase[0]))
        v_duty = tk.StringVar(value=duty)
        v_auto = tk.BooleanVar(value=auto)
        _c = celula(fr, COL_NOME)
        tk.Entry(_c, textvariable=v_nome, bg=entry_bg, fg=entry_fg,
                 insertbackground=fg_color).pack(fill=tk.BOTH, expand=True)
        _c = celula(fr, COL_P)
        tk.Entry(_c, textvariable=v_pw, bg=entry_bg, fg=entry_fg, insertbackground=fg_color,
                 justify=tk.RIGHT).pack(fill=tk.BOTH, expand=True)
        _c = celula(fr, COL_FASE)
        _om = tk.OptionMenu(_c, v_fase, *_rotulos_fase)
        _om.config(bg=entry_bg, fg=entry_fg, activebackground=entry_bg,
                   activeforeground=entry_fg, anchor="w")
        _om.pack(fill=tk.BOTH, expand=True)
        _c = celula(fr, COL_DUTY)
        e_duty = tk.Entry(_c, textvariable=v_duty, bg=entry_bg, fg=entry_fg,
                          insertbackground=fg_color, justify=tk.RIGHT,
                          disabledbackground=disabled_bg, disabledforeground="#6b7280")
        e_duty.pack(fill=tk.BOTH, expand=True)

        def alternar_auto():
            e_duty.config(state=tk.DISABLED if v_auto.get() else tk.NORMAL)

        if tem_contato:
            _c = celula(fr, COL_AUTO)
            tk.Checkbutton(_c, variable=v_auto, command=alternar_auto, bg=panel_color,
                           fg=fg_color, selectcolor=entry_bg, activebackground=panel_color,
                           activeforeground=fg_color).pack(expand=True)
        reg = {"nome": v_nome, "pw": v_pw, "fase": v_fase, "duty": v_duty, "auto": v_auto}

        def remover():
            fr.destroy()
            if reg in linhas_modos:
                linhas_modos.remove(reg)

        _c = celula(fr, COL_RM)
        tk.Button(_c, text="✕", command=remover, bg="#374151" if escuro else "#d1d5db",
                  fg="white" if escuro else "#111827").pack(fill=tk.BOTH, expand=True)
        linhas_modos.append(reg)
        alternar_auto()

    adicionar_modo("Nominal", "", "sempre", "1", False)
    tk.Button(pag_modos, text=("+ Add mode" if idioma == "EN" else "+ Adicionar modo"),
              command=lambda: adicionar_modo(), bg="#374151" if escuro else "#d1d5db",
              fg="white" if escuro else "#111827").pack(anchor="w", padx=12, pady=(6, 8))

    # ---------------------------------------------- PÁGINA 3: BATERIA ---------------------
    pag_bateria = tk.Frame(area_paginas, bg=panel_color)
    corpo_bat = criar_corpo_rolavel(pag_bateria, panel_color, largura_max=660)

    exec_bat_var = tk.BooleanVar(value=True)
    dod_var = tk.StringVar(value="0.3")
    tipo_var = tk.StringVar(value="Li-ion")
    dens_var = tk.StringVar(value="150")
    bancos_var = tk.StringVar(value="1")
    eta_var = tk.StringVar(value="0.9")
    fos_bat_var = tk.StringVar(value="0")

    tk.Checkbutton(corpo_bat, text=_("Executar análise de bateria", idioma), variable=exec_bat_var,
                   bg=panel_color, fg=fg_color, selectcolor=entry_bg, activebackground=panel_color,
                   activeforeground=fg_color).pack(anchor="w", pady=(0, 8))
    ent_dod = campo(corpo_bat, "DoD", dod_var)
    ToolTip(ent_dod, _("Profundidade de descarga", idioma))
    fr_tipo = tk.Frame(corpo_bat, bg=panel_color)
    fr_tipo.pack(fill=tk.X, pady=4)
    tk.Label(fr_tipo, text=_("Tipo de bateria", idioma), bg=panel_color, fg=fg_color,
             anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
    _opt_tipo = tk.OptionMenu(fr_tipo, tipo_var, "NiCd", "NiH2", "Li-ion", _("Outra", idioma),
                              command=lambda v: atualizar_tipo(v))
    _opt_tipo.config(width=12, bg=entry_bg, fg=entry_fg, activebackground=entry_bg,
                     activeforeground=entry_fg)
    _opt_tipo.pack(side=tk.RIGHT)
    ent_dens = campo(corpo_bat, "Densidade [Wh/kg]", dens_var)
    ent_bancos = campo(corpo_bat, "Independent banks (min. 1)" if idioma == "EN"
                       else "Bancos independentes (mín. 1)", bancos_var)
    ToolTip(ent_bancos, _("Bancos independentes", idioma))
    ent_eta = campo(corpo_bat, "n", eta_var)
    ToolTip(ent_eta, _("Eficiência de transmissão", idioma))
    ent_fos_bat = campo(corpo_bat, "Battery safety factor [adm]" if idioma == "EN"
                        else "Fator de segurança da bateria [adm]", fos_bat_var)
    ToolTip(ent_fos_bat, "Dimensionless margin applied to the required capacity: (1+FS)·C (e.g. 0.2 = +20%; default 0)"
                         if idioma == "EN" else
                         "Margem adimensional aplicada à capacidade requerida: (1+FS)·C (ex.: 0,2 = +20%; padrão 0)")

    def atualizar_tipo(_v=None):
        t = tipo_var.get()
        if t == "NiCd":
            dens_var.set("40"); ent_dens.config(state=tk.DISABLED)
        elif t == "NiH2":
            dens_var.set("55"); ent_dens.config(state=tk.DISABLED)
        elif t == "Li-ion":
            dens_var.set("150"); ent_dens.config(state=tk.DISABLED)
        else:
            ent_dens.config(state=tk.NORMAL)

    # ---------------------------------------------- NAVEGAÇÃO -----------------------------
    def paginas_ativas():
        if not executar_var.get():
            return ["placa"]
        if consumo_var.get() == _rot_modos:
            return ["placa", "modos", "bateria"]
        return ["placa", "bateria"]

    idx_pag = {"i": 0}
    _frames_pag = {"placa": pag_placa, "modos": pag_modos, "bateria": pag_bateria}

    def mostrar_pagina():
        for fr in _frames_pag.values():
            fr.pack_forget()
        ativas = paginas_ativas()
        idx_pag["i"] = max(0, min(idx_pag["i"], len(ativas) - 1))
        atual = ativas[idx_pag["i"]]
        _frames_pag[atual].pack(fill=tk.BOTH, expand=True)
        for chave, lb in lbls_etapa.items():
            if chave == atual:
                lb.config(bg="#4b5563" if escuro else "#475569", fg="white",
                          font=("Segoe UI", 9, "bold"))
            elif chave in ativas:
                lb.config(bg="#1f2937" if escuro else "#cbd5e1",
                          fg="#9ca3af" if escuro else "#111827", font=("Segoe UI", 9))
            else:
                lb.config(bg=panel_color, fg="#4b5563" if escuro else "#94a3b8",
                          font=("Segoe UI", 9))
        atualizar_nav()

    def atualizar_nav():
        ativas = paginas_ativas()
        ultimo = idx_pag["i"] >= len(ativas) - 1
        btn_voltar_pag.config(state=tk.NORMAL if idx_pag["i"] > 0 else tk.DISABLED)
        if ultimo:
            btn_proximo.config(text=_("Confirmar", idioma), command=confirmar,
                               bg="#eab308" if escuro else "#243447",
                               fg="#111827" if escuro else "white")
        else:
            btn_proximo.config(text=_("Próximo", idioma), command=avancar,
                               bg="#374151" if escuro else "#d1d5db",
                               fg="white" if escuro else "#111827")

    def validar_placa():
        if not executar_var.get():
            return True
        if not [f for f, v in faces_vars.items() if v.get()]:
            _erro(_("Nenhuma face com painel solar foi configurada.", idioma))
            return False
        usar_modos = consumo_var.get() == _rot_modos
        try:
            dados["tm"] = ler_float(tm_var, "Tempo de missão", 0.0)
            dados["eff"] = ler_float(eff_var, "Eff", 0.0, 1.0)
            dados["deg"] = ler_float(deg_var, "Deg", 0.0)
            dados["id"] = ler_float(id_var, "Id", 0.0, 1.0)
            dados["pe"] = 0.0 if usar_modos else ler_float(pe_var, "Pe", 0.0)
            dados["pd"] = 0.0 if usar_modos else ler_float(pd_var, "Pd", 0.0)
            dados["fos"] = ler_float(fos_var, "Fator de segurança", 0.0)
            dados["xe"] = ler_float(xe_var, "Xe", 0.0, 1.0)
            dados["xd"] = ler_float(xd_var, "Xd", 0.0, 1.0)
            if fill_mode_var.get() == _rot_fill_1u:
                dados["fill_modo"] = 2
                dados["n_cel"] = ler_float(n_cel_var, "Células por face 1U", 0.0)
                dados["a_cel"] = ler_float(area_cel_var, "Área da célula", 0.0)
            else:
                dados["fill_modo"] = 1
                dados["fill"] = ler_float(fill_factor_var, "Fator de preenchimento", 0.0, 1.0)
        except ValueError as e:
            _erro(str(e))
            return False
        dados["usar_modos"] = usar_modos
        dados["faces"] = [f for f, v in faces_vars.items() if v.get()]
        if arq_var.get().startswith("DET"):
            dados["arq"] = 1
        elif arq_var.get().startswith("PPT"):
            dados["arq"] = 2
        else:
            dados["arq"] = 3
        return True

    def validar_modos():
        modos = []
        for i, reg in enumerate(linhas_modos, start=1):
            nome = reg["nome"].get().strip()
            pw_s = reg["pw"].get().strip()
            if not nome and not pw_s:
                continue
            try:
                pw = float(pw_s.replace(",", "."))
            except ValueError:
                _erro(_("{}: digite um número válido.", idioma).format(f"P [W] ({nome or i})"))
                return False
            if pw < 0:
                _erro(_("{}: o valor mínimo permitido é {}.", idioma).format(f"P [W] ({nome or i})", 0))
                return False
            _f, fase_int = _fase_por_rot.get(reg["fase"].get(), ("sempre", 1))
            auto = bool(reg["auto"].get())
            duty = 0.0
            if not auto:
                try:
                    duty = float(reg["duty"].get().replace(",", "."))
                except ValueError:
                    _erro(_("{}: digite um número válido.", idioma).format(f"Duty ({nome or i})"))
                    return False
                if not (0.0 <= duty <= 1.0):
                    _erro(_("{}: o valor máximo permitido é {}.", idioma).format(f"Duty ({nome or i})", 1))
                    return False
            modos.append({"nome": nome or f"Modo {i}", "P_W": pw,
                          "fase_int": fase_int, "auto": auto, "duty": duty})
        if not modos:
            _erro("Add at least one mode." if idioma == "EN" else "Adicione ao menos um modo.")
            return False
        dados["modos"] = modos
        return True

    def validar_bateria():
        if not exec_bat_var.get():
            dados["bateria"] = None
            return True
        try:
            dod = ler_float(dod_var, "DoD", 0.0, 1.0)
            densidade = ler_float(dens_var, "Densidade", 0.001)
            bancos = ler_int(bancos_var, "Bancos independentes", 1)
            eta = ler_float(eta_var, "Eficiência de transmissão", 0.0, 1.0)
            fos_bat = ler_float(fos_bat_var, "Fator de segurança da bateria", 0.0)
        except ValueError as e:
            _erro(str(e))
            return False
        tipo = {"NiCd": 1, "NiH2": 2, "Li-ion": 3, _("Outra", idioma): 4}.get(tipo_var.get(), 4)
        dados["bateria"] = {"dod": dod, "tipo": tipo, "densidade": densidade,
                            "bancos": bancos, "eta": eta, "fos": fos_bat}
        return True

    _validadores = {"placa": validar_placa, "modos": validar_modos, "bateria": validar_bateria}

    def validar_atual():
        return _validadores[paginas_ativas()[idx_pag["i"]]]()

    def avancar():
        if not validar_atual():
            return
        idx_pag["i"] += 1
        mostrar_pagina()

    def voltar_pagina():
        if idx_pag["i"] > 0:
            idx_pag["i"] -= 1
            mostrar_pagina()

    def confirmar():
        if not validar_atual():
            return
        if not executar_var.get():
            resultado["respostas"] = ["n"]
            janela.destroy()
            return
        r = ["s", dados["tm"], dados["eff"], dados["deg"], dados["id"]]
        if dados["usar_modos"]:
            r.append(2)
        else:
            r.extend([1, dados["pe"], dados["pd"]])
        r.extend([dados["fos"], dados["arq"]])
        if dados["arq"] == 3:
            r.extend([dados["xe"], dados["xd"]])
        if dados["fill_modo"] == 2:
            r.extend([2, dados["n_cel"], dados["a_cel"]])
        else:
            r.extend([1, dados["fill"]])
        if dados["usar_modos"]:
            r.append(len(dados["modos"]))
            for m in dados["modos"]:
                r.extend([m["nome"], m["P_W"], m["fase_int"], "s" if m["auto"] else "n"])
                if not m["auto"]:
                    r.append(m["duty"])
        bat = dados.get("bateria")
        if bat is None:
            r.append("n")
        else:
            r.extend(["s", bat["dod"], bat["tipo"]])
            if bat["tipo"] == 4:
                r.append(bat["densidade"])
            r.extend([bat["bancos"], bat["eta"], bat["fos"]])
        faces_ativas[:] = dados["faces"]
        resultado["respostas"] = [str(v) for v in r]
        janela.destroy()

    def cancelar():
        resultado["respostas"] = ["n"]
        janela.destroy()

    btn_voltar_pag = tk.Button(rodape, text=_("Voltar", idioma), command=voltar_pagina,
                               width=12, bg="#374151" if escuro else "#d1d5db",
                               fg="white" if escuro else "#111827")
    btn_voltar_pag.pack(side=tk.LEFT)
    tk.Button(rodape, text="Menu inicial" if idioma != "EN" else "Main menu",
              command=lambda: reiniciar_aplicacao(parent=janela),
              bg="#374151" if escuro else "#d1d5db",
              fg="white" if escuro else "#111827").pack(side=tk.LEFT, padx=(8, 0))
    tk.Button(rodape, text=_("Cancelar", idioma), command=cancelar,
              bg="#374151" if escuro else "#d1d5db",
              fg="white" if escuro else "#111827").pack(side=tk.RIGHT, padx=(8, 0))
    btn_proximo = tk.Button(rodape, text=_("Próximo", idioma), command=avancar, width=14,
                            font=("Segoe UI", 10, "bold"))
    btn_proximo.pack(side=tk.RIGHT)

    atualizar_arquitetura()
    atualizar_consumo()
    atualizar_fill()
    atualizar_tipo()
    mostrar_pagina()
    janela.protocol("WM_DELETE_WINDOW", cancelar)
    abrir_maximizada(janela, 1180, 740)
    janela.grab_set()
    janela.lift()
    janela.focus_force()
    janela.wait_window()
    try:
        cv_modos.unbind_all("<MouseWheel>")
    except Exception:
        pass
    return resultado["respostas"]


def montar_respostas_interface(dados):
    respostas = [dados["orbit"]]
    if dados["orbit"] == 1:
        respostas.extend([dados["sma"], dados["ecc"], dados["inc"], dados["raan"], dados["aop"], dados["ta"]])
    elif dados["orbit"] in (2, 3):
        respostas.extend([dados["raan"], dados["aop"], dados["ta"]])

    respostas.extend([dados["tamanho_u"]])
    respostas.extend([dados["m_sat"], dados["cd_sat"], dados["cr_sat"]])

    respostas.append(dados["gs"])
    if dados["gs"] == "s":
        respostas.extend([dados["lat"], dados["lon"], dados["alt"], dados["elev"]])
    respostas.append(dados["tempo"])
    _MONTHS_REV = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06",
                   "Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
    _gp = str(dados["epoch"]).split()
    if len(_gp) >= 3 and _gp[1] in _MONTHS_REV:
        _ep_data = f"{int(_gp[0]):02d}/{_MONTHS_REV[_gp[1]]}/{_gp[2]}"
        _ep_hora = _gp[3][:5] if len(_gp) > 3 else "12:00"
    else:
        _ep_data, _ep_hora = "01/01/2025", "12:00"
    respostas.append(_ep_data)
    respostas.append(_ep_hora)
    return [str(valor) for valor in respostas]



FASES_MODO = {1: "sempre", 2: "sol", 3: "eclipse"}


def duty_por_contato(fase, t_sol_s, t_eclipse_s, t_contato_s):
    if t_contato_s <= 0:
        return 0.0
    base = {"sempre": t_sol_s + t_eclipse_s, "sol": t_sol_s, "eclipse": t_eclipse_s}.get(fase, 0.0)
    if base <= 0:
        return 0.0
    return min(1.0, t_contato_s / base)


def calcular_consumo_por_modos(modos):
    """
    Referência: SMAD, no orçamento de potência, Pd e Pe são as potências médias requeridas
    durante a luz solar e o eclipse, obtidas somando cada carga ponderada pelo seu duty cycle:
        Pd = Σ (P_i · duty_i)   sobre os modos ativos no sol
        Pe = Σ (P_i · duty_i)   sobre os modos ativos no eclipse
"""
    Pd = 0.0
    Pe = 0.0
    detalhes = []
    for m in modos:
        contrib = m["P_W"] * m["duty"]
        c_sol = contrib if m["fase"] in ("sempre", "sol") else 0.0
        c_ecl = contrib if m["fase"] in ("sempre", "eclipse") else 0.0
        Pd += c_sol
        Pe += c_ecl
        d = dict(m)
        d["c_sol"] = c_sol
        d["c_ecl"] = c_ecl
        detalhes.append(d)
    return Pd, Pe, detalhes


def analisar_contatos(caminho_arquivo):
    tempo_total_s  = 0.0
    menor_evento_s = float('inf')
    num_eventos    = 0
    por_dia        = {}   
    try:
        with open(caminho_arquivo, 'r') as f:
            for linha in f:
                linha_limpa = linha.strip()
                if not linha_limpa or not linha_limpa[0].isdigit():
                    continue
                partes    = linha_limpa.split()
                duracao_s = float(partes[-1])
                tempo_total_s += duracao_s
                if duracao_s < menor_evento_s:
                    menor_evento_s = duracao_s
                num_eventos += 1
                try:
                    dia = f"{partes[0]} {partes[1]} {partes[2]}"
                    d = por_dia.setdefault(dia, {"n": 0, "s": 0.0})
                    d["n"] += 1
                    d["s"] += duracao_s
                except Exception:
                    pass
        if num_eventos == 0:
            menor_evento_s = 0.0
        return {"total_s": tempo_total_s, "menor_evento_s": menor_evento_s,
                "num_eventos": num_eventos, "por_dia": por_dia}
    except FileNotFoundError:
        print(_p(f"AVISO: Arquivo de contato '{caminho_arquivo}' não encontrado.",
                 f"WARNING: Contact file '{caminho_arquivo}' not found."))
        return None
    except Exception as e:
        print(f"ERRO ao analisar contatos: {e}")
        return None


def analisar_eclipses(caminho_arquivo):
    eventos_processados = set()
    tempo_total_s       = 0.0
    maior_evento_s      = 0.0
    try:
        with open(caminho_arquivo, 'r') as f:
            for linha in f:
                linha_limpa = linha.strip()
                if not linha_limpa or not linha_limpa[0].isdigit():
                    continue
                partes = linha_limpa.split()
                try:
                    num_evento           = int(partes[11])
                    duracao_total_evento = float(partes[-1])
                except (IndexError, ValueError) as e:
                    print(f"Aviso: linha ignorada em {os.path.basename(caminho_arquivo)}: '{linha_limpa}' ({e})")
                    continue
                if num_evento not in eventos_processados:
                    eventos_processados.add(num_evento)
                    tempo_total_s += duracao_total_evento
                    if duracao_total_evento > maior_evento_s:
                        maior_evento_s = duracao_total_evento
        num_eventos_totais = len(eventos_processados)
        if num_eventos_totais == 0:
            return None
        return {"total_s": tempo_total_s, "maior_evento_s": maior_evento_s, "num_eventos": num_eventos_totais}
    except FileNotFoundError:
        print(_p(f"AVISO: Arquivo '{caminho_arquivo}' não encontrado.",
                 f"WARNING: File '{caminho_arquivo}' not found."))
        return None
    except Exception as e:
        print(f"ERRO ao ler '{caminho_arquivo}': {e}")
        return None


def _ultimo_ponto_report(caminho):
    try:
        with open(caminho, 'rb') as f:
            f.seek(0, 2)
            tam = f.tell()
            f.seek(max(0, tam - 8192))
            dados = f.read().decode('utf-8', 'replace')
        for ln in reversed(dados.splitlines()):
            ln = ln.strip()
            if ln and ln[0].isdigit():
                p = ln.split()
                tai = float(p[0])
                try:
                    alt = math.sqrt(float(p[1])**2 + float(p[2])**2 + float(p[3])**2) - 6378.137
                except (IndexError, ValueError):
                    alt = None
                return tai, alt
    except Exception:
        return None, None
    return None, None


def analisar_luz_solar(caminho_arquivo, epoch_gregorian_str, tempo_dias):
    eventos_eclipse   = {}
    formato_data_base = '%d %b %Y %H:%M:%S'
    try:
        inicio_sim_dt = datetime.strptime(epoch_gregorian_str.split('.')[0], formato_data_base)
        fim_sim_dt    = inicio_sim_dt + timedelta(days=tempo_dias)
    except Exception as e:
        print(_p(f"ERRO: Formato de data inválido: {epoch_gregorian_str}. {e}",
                 f"ERROR: Invalid date format: {epoch_gregorian_str}. {e}"))
        return None
    try:
        with open(caminho_arquivo, 'r') as f:
            for linha in f:
                linha_limpa = linha.strip()
                if not linha_limpa or not linha_limpa[0].isdigit():
                    continue
                partes = linha_limpa.split()
                try:
                    num_evento = int(partes[11])
                    start_str  = f"{partes[0]} {partes[1]} {partes[2]} {partes[3]}"
                    stop_str   = f"{partes[4]} {partes[5]} {partes[6]} {partes[7]}"
                    try:
                        start_time = datetime.strptime(start_str, formato_data_base + '.%f')
                    except ValueError:
                        start_time = datetime.strptime(start_str, formato_data_base)
                    try:
                        stop_time = datetime.strptime(stop_str, formato_data_base + '.%f')
                    except ValueError:
                        stop_time = datetime.strptime(stop_str, formato_data_base)
                    if num_evento not in eventos_eclipse:
                        eventos_eclipse[num_evento] = {'start': start_time, 'stop': stop_time}
                    else:
                        if start_time < eventos_eclipse[num_evento]['start']:
                            eventos_eclipse[num_evento]['start'] = start_time
                        if stop_time > eventos_eclipse[num_evento]['stop']:
                            eventos_eclipse[num_evento]['stop'] = stop_time
                except (IndexError, ValueError) as e:
                    print(f"Aviso: linha ignorada em {os.path.basename(caminho_arquivo)}: '{linha_limpa}' ({e})")
                    continue

        _j2000_dt  = datetime(2000, 1, 1, 12, 0, 0)
        _tai_epoch = 21545.0 + (inicio_sim_dt - _j2000_dt).total_seconds() / 86400.0

        if not eventos_eclipse:
            tempo_total = tempo_dias * 86400.0
            periodos_tai = [(tempo_total, _tai_epoch, _tai_epoch + tempo_dias)]
            return {
                "total_s":        tempo_total,
                "menor_evento_s": tempo_total,
                "num_eventos":    1,
                "tai_pior_start": _tai_epoch,
                "tai_pior_stop":  _tai_epoch + tempo_dias,
                "periodos_tai":   periodos_tai,
            }

        lista_eclipses_ordenada = sorted(eventos_eclipse.values(), key=lambda e: e['start'])

        periodos_completos = []

        dur_inicio = (lista_eclipses_ordenada[0]['start'] - inicio_sim_dt).total_seconds()
        if dur_inicio > 0.1:
            periodos_completos.append((dur_inicio, inicio_sim_dt, lista_eclipses_ordenada[0]['start']))

        for i in range(len(lista_eclipses_ordenada) - 1):
            dur = (lista_eclipses_ordenada[i+1]['start'] - lista_eclipses_ordenada[i]['stop']).total_seconds()
            if dur > 0.1:
                periodos_completos.append((dur, lista_eclipses_ordenada[i]['stop'], lista_eclipses_ordenada[i+1]['start']))

        dur_fim = (fim_sim_dt - lista_eclipses_ordenada[-1]['stop']).total_seconds()
        if dur_fim > 0.1:
            periodos_completos.append((dur_fim, lista_eclipses_ordenada[-1]['stop'], fim_sim_dt))

        if not periodos_completos:
            return {
                "total_s":        0.0,
                "menor_evento_s": 0.0,
                "num_eventos":    0,
                "tai_pior_start": None,
                "tai_pior_stop":  None,
                "periodos_tai":   [],
            }

        periodos_tai = [
            (
                dur,
                _tai_epoch + (start - inicio_sim_dt).total_seconds() / 86400.0,
                _tai_epoch + (stop  - inicio_sim_dt).total_seconds() / 86400.0,
            )
            for (dur, start, stop) in periodos_completos
        ]

        periodos_completos.sort(key=lambda x: x[0])
        idx_ref = 2 if len(periodos_completos) > 2 else 0
        dur_ref, start_ref, stop_ref = periodos_completos[idx_ref]

        tai_pior_start = _tai_epoch + (start_ref - inicio_sim_dt).total_seconds() / 86400.0
        tai_pior_stop  = _tai_epoch + (stop_ref  - inicio_sim_dt).total_seconds() / 86400.0

        return {
            "total_s":        sum(p[0] for p in periodos_completos),
            "menor_evento_s": dur_ref,
            "num_eventos":    len(periodos_completos),
            "tai_pior_start": tai_pior_start,
            "tai_pior_stop":  tai_pior_stop,
            "periodos_tai":   periodos_tai,
        }
    except FileNotFoundError:
        print(_p(f"AVISO: Arquivo '{caminho_arquivo}' não encontrado.",
                 f"WARNING: File '{caminho_arquivo}' not found."))
        return None
    except Exception as e:
        print(f"ERRO ao analisar luz solar em '{caminho_arquivo}': {e}")
        return None


def shadow_factor(r_icrf_sun, r_icrf):
    # Referência: Vallado, D. A. Fundamentals of Astrodynamics and Applications.
    r_p    = 6378136.688
    alfau  = 0.264121687
    alfap  = 0.269007205
    cos_g  = np.dot(r_icrf_sun, r_icrf) / (np.linalg.norm(r_icrf_sun) * np.linalg.norm(r_icrf))
    cos_g  = np.clip(cos_g, -1.0, 1.0)
    gama   = np.arccos(cos_g)
    sathor = np.linalg.norm(r_icrf) * np.cos(gama)
    satver = np.linalg.norm(r_icrf) * np.sin(gama)
    x      = r_p / np.sin(np.radians(alfap))
    y      = r_p / np.sin(np.radians(alfau))
    penver = np.tan(np.radians(alfap)) * (x + sathor)
    if sathor > 0:
        return 1.0
    if satver <= penver:
        umbver = np.tan(np.radians(alfau)) * (y - sathor)
        if satver <= umbver:
            return 0.0
        return 0.5
    return 1.0




def _quat_tumbling_elapsed(elapsed_s, omega, q0):
    wx, wy, wz = omega
    wn = math.sqrt(wx * wx + wy * wy + wz * wz)
    if wn < 1e-12:
        return list(q0)
    theta = math.radians(wn * elapsed_s)        
    h = theta / 2.0
    s = math.sin(h) / wn
    q_spin = (wx * s, wy * s, wz * s, math.cos(h)) 
    x0, y0, z0, w0 = q0
    x1, y1, z1, w1 = q_spin
    return [
        w0 * x1 + x0 * w1 + y0 * z1 - z0 * y1,
        w0 * y1 - x0 * z1 + y0 * w1 + z0 * x1,
        w0 * z1 + x0 * y1 - y0 * x1 + z0 * w1,
        w0 * w1 - x0 * x1 - y0 * y1 - z0 * z1,
    ]


def _quat_tumbling_tai(tai, initial_epoch, omega, q0):
    return _quat_tumbling_elapsed((tai - initial_epoch) * 86400.0, omega, q0)


def _tumbling_ativo():
    return bool(globals().get("_ATITUDE_ANALITICA", False))


def analisar_potencia_solar(caminho_report, faces_ativas, areas, Eff, Id, Ld, tai_start, tai_stop):
    # Referência: Markley & Crassidis. Fundamentals of spacecraft attitude determination and control.
    S = 1367.0

    potencias_total    = []
    potencias_por_face = {f: [] for f in faces_ativas}

    try:
        with open(caminho_report, 'r') as f:
            for linha in f:
                linha_limpa = linha.strip()
                if not linha_limpa or not linha_limpa[0].isdigit():
                    continue
                partes = linha_limpa.split()
                if len(partes) < 14:
                    continue
                try:
                    tai        = float(partes[0])
                    pos_sc_km  = np.array([float(partes[1]), float(partes[2]), float(partes[3])])
                    pos_sol_km = np.array([float(partes[7]), float(partes[8]), float(partes[9])])
                    if _tumbling_ativo():
                        q = _quat_tumbling_tai(tai, globals().get("initial_epoch", tai),
                                               globals().get("_TUMB_OMEGA", (0.0, 0.0, 0.0)),
                                               globals().get("_TUMB_Q0", (0.0, 0.0, 0.0, 1.0)))
                    else:
                        q = [float(partes[10]), float(partes[11]), float(partes[12]), float(partes[13])]
                except (ValueError, IndexError):
                    continue
                if tai < tai_start or tai > tai_stop:
                    continue


                sf = shadow_factor(pos_sol_km * 1e3, pos_sc_km * 1e3)


                sun_eci = pos_sol_km - pos_sc_km
                _sn = np.linalg.norm(sun_eci)
                if _sn < 1.0:
                    continue
                sun_eci = sun_eci / _sn

                R = Rotation.from_quat(q).as_matrix()

                P_total_ts = 0.0
                for f in faces_ativas:
                    n_eci     = R.T @ FACES[f]
                    cos_theta = max(0.0, np.dot(n_eci, sun_eci))
                    P_face    = areas[f] * Eff * S * Id * Ld * cos_theta * sf
                    potencias_por_face[f].append(P_face)
                    P_total_ts += P_face
                potencias_total.append(P_total_ts)

        if not potencias_total:
            return None

        return {
            "P_media_total":    np.mean(potencias_total),
            "P_media_por_face": {f: np.mean(potencias_por_face[f]) for f in faces_ativas},
            "n_timesteps":      len(potencias_total),
        }

    except FileNotFoundError:
        print(_p(f"AVISO: Arquivo de report '{caminho_report}' não encontrado.",
                 f"WARNING: Report file '{caminho_report}' not found."))
        return None
    except Exception as e:
        print(_p(f"ERRO ao analisar potência solar: {e}", f"ERROR analyzing solar power: {e}"))
        return None

def remover_acentos(txt):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')

def processar_report2(caminho):
    try:
        import numpy as np
        from scipy.spatial.transform import Rotation
        linhas_modificadas = []
        
        cabecalho = "       Time (UTCG)          x/Magnitude    y/Magnitude    z/Magnitude     Intensity\n------------------------    -----------    -----------    -----------    ----------\n"
        linhas_modificadas.append(cabecalho)
        
        with open(caminho, 'r') as f:
            for i, linha in enumerate(f):
                if i == 0 and "UTCGregorian" in linha:
                    continue
                linha_limpa = linha.strip()
                if not linha_limpa:
                    continue
                partes = linha_limpa.split()
                try:
                    data_hora = f"{partes[0]} {partes[1]} {partes[2]} {partes[3]}"

                    if _tumbling_ativo():
                        _dt = datetime.strptime(data_hora, "%d %b %Y %H:%M:%S.%f")
                        _ep = globals().get("_TUMB_EPOCH_DT", None)
                        _el = (_dt - _ep).total_seconds() if _ep is not None else 0.0
                        q = np.array(_quat_tumbling_elapsed(_el,
                                     globals().get("_TUMB_OMEGA", (0.0, 0.0, 0.0)),
                                     globals().get("_TUMB_Q0", (0.0, 0.0, 0.0, 1.0))))
                    else:
                        q = np.array([float(partes[4]), float(partes[5]), float(partes[6]), float(partes[7])])
                    pos_sc = np.array([float(partes[8]), float(partes[9]), float(partes[10])]) * 1e3
                    pos_sun = np.array([float(partes[11]), float(partes[12]), float(partes[13])]) * 1e3
                    
                    sun_eci = pos_sun - pos_sc
                    _sn3 = np.linalg.norm(sun_eci)
                    if _sn3 < 1.0:
                        continue
                    sun_eci_unit = sun_eci / _sn3
                    
                    R = Rotation.from_quat(q).as_matrix()
                    sun_body = R.T @ sun_eci_unit
                    
                    sf = shadow_factor(pos_sun, pos_sc)
                    intensity = sf * 100.0
                    
                    linha_formatada = f" {data_hora:<24} {sun_body[0]:>14.6f} {sun_body[1]:>14.6f} {sun_body[2]:>14.6f} {intensity:>13.6f}\n"
                    linhas_modificadas.append(linha_formatada)
                except Exception:
                    continue
                    
        with open(caminho, 'w') as f:
            f.writelines(linhas_modificadas)
    except Exception as e:
        print(_p(f"ERRO ao processar ReportFile2: {e}", f"ERROR processing ReportFile2: {e}"))

def calcular_potencia_por_periodo(caminho_report, faces_ativas, areas, Eff, Id, Ld, periodos_tai):
    S     = 1367.0
    n_per = len(periodos_tai)
    P_sum = [0.0] * n_per
    count = [0]   * n_per
    P_face_sum = [{f: 0.0 for f in faces_ativas} for _ in range(n_per)]


    tai_starts = [p[1] for p in periodos_tai]
    tai_stops  = [p[2] for p in periodos_tai]

    try:
        with open(caminho_report, 'r') as f:
            for linha in f:
                linha_limpa = linha.strip()
                if not linha_limpa or not linha_limpa[0].isdigit():
                    continue
                partes = linha_limpa.split()
                if len(partes) < 14:
                    continue
                try:
                    tai        = float(partes[0])
                    pos_sc_km  = np.array([float(partes[1]), float(partes[2]), float(partes[3])])
                    pos_sol_km = np.array([float(partes[7]), float(partes[8]), float(partes[9])])
                    if _tumbling_ativo():
                        q = _quat_tumbling_tai(tai, globals().get("initial_epoch", tai),
                                               globals().get("_TUMB_OMEGA", (0.0, 0.0, 0.0)),
                                               globals().get("_TUMB_Q0", (0.0, 0.0, 0.0, 1.0)))
                    else:
                        q = [float(partes[10]), float(partes[11]),
                             float(partes[12]), float(partes[13])]
                except (ValueError, IndexError):
                    continue


                idx = bisect.bisect_right(tai_starts, tai) - 1
                if idx < 0 or tai > tai_stops[idx]:
                    continue  

                sf      = shadow_factor(pos_sol_km * 1e3, pos_sc_km * 1e3)
                sun_eci = pos_sol_km - pos_sc_km
                _sn4 = np.linalg.norm(sun_eci)
                if _sn4 < 1.0:
                    continue
                sun_eci = sun_eci / _sn4
                R       = Rotation.from_quat(q).as_matrix()

                P_ts = 0.0
                for f in faces_ativas:
                    n_eci     = R.T @ FACES[f]
                    cos_theta = max(0.0, np.dot(n_eci, sun_eci))
                    p_face    = areas[f] * Eff * S * Id * Ld * cos_theta * sf
                    P_ts                += p_face
                    P_face_sum[idx][f]  += p_face

                P_sum[idx] += P_ts
                count[idx] += 1

        return [
            {
                "duracao_s":   periodos_tai[i][0],
                "P_media":     P_sum[i] / count[i] if count[i] > 0 else 0.0,
                "P_por_face":  {f: (P_face_sum[i][f] / count[i] if count[i] > 0 else 0.0) for f in faces_ativas},
                "n_timesteps": count[i],
            }
            for i in range(n_per)
        ]

    except FileNotFoundError:
        print(_p(f"AVISO: Report '{caminho_report}' não encontrado.",
                 f"WARNING: Report '{caminho_report}' not found."))
        return None
    except Exception as e:
        print(_p(f"ERRO ao calcular potência por período: {e}", f"ERROR computing power per period: {e}"))
        return None




# ---------------------------------------------- TELA INICIAL -----------------------------------------------------------

def mostrar_tela_inicial(idioma_inicial="PT"):
    if not tkinter_disponivel:
        return "iniciar", None, idioma_inicial

    try:
        root = tk.Tk()
    except tk.TclError:
        return "iniciar", None, idioma_inicial

    root.title("PEGASUS - Interface de Configuração" if idioma_inicial == "PT" else "PEGASUS - Configuration Interface")
    root.resizable(True, True)
    root.geometry("760x580")
    root.minsize(700, 520)

    definir_icone(root)

    local_banner = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pegasus_banner.png")

    estado = {
        "idioma": idioma_inicial,
        "acao": "cancelar",
        "modo_escuro": estado_tema["escuro"]
    }

    textos = {
        "PT": {
            "titulo": "PEGASUS - Menu Inicial",
            "iniciar": "🚀 Iniciar Dimensionamento",
            "referencias": "📚 Referências Utilizadas",
            "idioma_btn": "Idioma: Português 🇧🇷",
            "tema_btn_dark": "🌓 Alternar Tema",
            "tema_btn_light": "🌓 Alternar Tema",
            "voltar_btn": "⬅ Voltar",
            "nomes": "Aluna: Maria Eduarda Caldas Santos\nOrientador: Eduardo Escobar Bürger",
            "ref_titulo": "Referências Bibliográficas",
            "ref_conteudo": (
                "REFERÊNCIAS BIBLIOGRÁFICAS UTILIZADAS NO PEGASUS:\n\n"
                "1. LARSON, W. J.; WERTZ, J. R.; D'SOUZA, B. Space Mission Analysis and Design (SMAD III). 3ª ed. Microcosm Press, 2005.\n"
                "   - Base teórica e matemática completa para o dimensionamento preliminar do subsistema de potência (EPS).\n\n"
                "2. ISISPACE Group. ISIS 1U CubeSat Solar Panel Datasheet.\n"
                "   - Referência física utilizada para estimativa da razão de área útil do painel solar no padrão CubeSat.\n\n"
                "3. VALLADO, D. A. Fundamentals of Astrodynamics and Applications. 4ª ed. Microcosm Press, 2013.\n"
                "   - Base matemática para processar com exatidão os períodos orbitais de iluminação solar e de eclipse.\n\n"
                "4. MARKLEY, F. L.; CRASSIDIS, J. L. Fundamentals of spacecraft attitude determination and control. Springer, 2014.\n"
                "   - Base cinemática de atitude para modelar a iluminação solar individual em cada face do satélite.\n\n"
                "5. ETCHELLS, T.; BERTHOUD, L. Developing a power modelling tool for cubesats. 2019.\n"
                "   - Fundamentação conceitual e validação de viabilidade da ferramenta de modelagem de potência."
            )
        },
        "EN": {
            "titulo": "PEGASUS - Main Menu",
            "iniciar": "🚀 Start Sizing",
            "referencias": "📚 References Used",
            "idioma_btn": "Language: English 🇺🇸",
            "tema_btn_dark": "🌓 Toggle Theme",
            "tema_btn_light": "🌓 Toggle Theme",
            "voltar_btn": "⬅ Back",
            "nomes": "Student: Maria Eduarda Caldas Santos\nAdvisor: Eduardo Escobar Bürger",
            "ref_titulo": "Bibliographic References",
            "ref_conteudo": (
                "BIBLIOGRAPHIC REFERENCES USED IN PEGASUS:\n\n"
                "1. LARSON, W. J.; WERTZ, J. R.; D'SOUZA, B. Space Mission Analysis and Design (SMAD III). 3rd ed. Microcosm Press, 2005.\n"
                "   - Complete theoretical and mathematical basis for the preliminary sizing of the electrical power subsystem (EPS).\n\n"
                "2. ISISPACE Group. ISIS 1U CubeSat Solar Panel Datasheet.\n"
                "   - Physical reference used to estimate the useful area ratio of the solar panel in the CubeSat standard.\n\n"
                "3. VALLADO, D. A. Fundamentals of Astrodynamics and Applications. 4th ed. Microcosm Press, 2013.\n"
                "   - Mathematical basis for accurately processing orbital periods of solar illumination and eclipse.\n\n"
                "4. MARKLEY, F. L.; CRASSIDIS, J. L. Fundamentals of spacecraft attitude determination and control. Springer, 2014.\n"
                "   - Attitude kinematics basis to model the individual solar illumination on each satellite face.\n\n"
                "5. ETCHELLS, T.; BERTHOUD, L. Developing a power modelling tool for cubesats. 2019.\n"
                "   - Conceptual foundation and feasibility validation of the power modeling tool."
            )
        }
    }


    root.configure(bg="#e5e7eb")

    banner_frame = tk.Frame(root, width=800, height=360, bg="#111827")
    banner_frame.pack_propagate(False)
    banner_frame.pack(side=tk.TOP, fill=tk.X)

    imagem_carregada = False
    if os.path.exists(local_banner):
        try:
            if pil_disponivel:
                img_pil = Image.open(local_banner)
                img_resized = img_pil.resize((800, 360), Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS)
                img = ImageTk.PhotoImage(img_resized)
            else:
                img_raw = tk.PhotoImage(file=local_banner)
                img = img_raw.subsample(2, 2)
            banner_label = tk.Label(banner_frame, image=img, bg="#111827")
            banner_label.image = img
            banner_label.pack(fill=tk.BOTH, expand=True)
            imagem_carregada = True
        except Exception as e:
            print(f"Aviso ao carregar imagem do banner: {e}")

    if not imagem_carregada:
        canvas_banner = tk.Canvas(banner_frame, width=800, height=360, bg="#111827", highlightthickness=0)
        canvas_banner.pack(fill=tk.BOTH, expand=True)
        canvas_banner.create_text(400, 120, text="PEGASUS", fill="#f6c445", font=("Segoe UI", 36, "bold"))
        canvas_banner.create_text(400, 190, text="Power Evaluation and GMAT Automated Simulation\nfor University Satellites", fill="#e5e7eb", font=("Segoe UI", 12, "italic"), justify=tk.CENTER)

    lbl_nomes = tk.Label(banner_frame, text=textos[estado["idioma"]]["nomes"], bg="#111827", fg="white", font=("Segoe UI", 9, "bold"), justify=tk.RIGHT)
    lbl_nomes.place(relx=0.98, rely=0.96, anchor="se")

    botoes_frame = tk.Frame(root, width=800, height=240, bg="#e5e7eb", padx=20, pady=5)
    botoes_frame.pack_propagate(False)
    botoes_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    botoes_container = tk.Frame(botoes_frame, bg="#e5e7eb", width=400, height=180)
    botoes_container.pack_propagate(False)
    botoes_container.pack(expand=True)

    def on_enter(e, widget, bg_color):
        widget.config(bg=bg_color)

    def on_leave(e, widget, bg_color):
        widget.config(bg=bg_color)

    btn_iniciar = tk.Button(
        botoes_container, 
        text=textos[estado["idioma"]]["iniciar"], 
        font=("Segoe UI", 10, "bold"), 
        bg="#1e293b", 
        fg="white", 
        width=38,
        height=1, 
        relief=tk.RAISED,
        cursor="hand2",
        command=lambda: [estado.update({"acao": "iniciar"}), root.quit()]
    )
    btn_iniciar.pack(pady=4)

    btn_referencias = tk.Button(
        botoes_container, 
        text=textos[estado["idioma"]]["referencias"], 
        font=("Segoe UI", 10, "bold"), 
        bg="#475569", 
        fg="white", 
        width=38,
        height=1, 
        relief=tk.RAISED,
        cursor="hand2",
        command=lambda: mostrar_referencias()
    )
    btn_referencias.pack(pady=4)

    btn_idioma = tk.Button(
        botoes_container, 
        text=textos[estado["idioma"]]["idioma_btn"], 
        font=("Segoe UI", 10, "bold"), 
        bg="#475569", 
        fg="white", 
        width=38,
        height=1, 
        relief=tk.RAISED,
        cursor="hand2",
        command=lambda: alternar_idioma()
    )
    btn_idioma.pack(pady=4)

    btn_tema = tk.Button(
        botoes_container, 
        text=textos[estado["idioma"]]["tema_btn_light"] if estado["modo_escuro"] else textos[estado["idioma"]]["tema_btn_dark"], 
        font=("Segoe UI", 10, "bold"), 
        bg="#475569", 
        fg="white", 
        width=38,
        height=1, 
        relief=tk.RAISED,
        cursor="hand2",
        command=lambda: alternar_tema()
    )
    btn_tema.pack(pady=4)

    referencias_frame = tk.Frame(root, width=800, height=240, bg="#e5e7eb", padx=20, pady=5)
    referencias_frame.pack_propagate(False)

    lbl_ref_titulo = tk.Label(
        referencias_frame,
        text="",
        font=("Segoe UI", 11, "bold"),
        bg="#e5e7eb",
        fg="#1e293b",
        anchor="w"
    )
    lbl_ref_titulo.pack(fill=tk.X, pady=(0, 4))

    ref_txt_frame = tk.Frame(referencias_frame, bg="#e5e7eb")
    ref_txt_frame.pack(fill=tk.BOTH, expand=True)

    txt = tk.Text(ref_txt_frame, bg="white", fg="#1e293b", font=("Consolas", 9), wrap=tk.WORD, padx=8, pady=8, height=5)
    scroll = tk.Scrollbar(ref_txt_frame, command=txt.yview)
    txt.configure(yscrollcommand=scroll.set)

    txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    ref_botoes = tk.Frame(referencias_frame, bg="#e5e7eb")
    ref_botoes.pack(fill=tk.X, pady=(4, 0))

    def voltar_para_menu():
        referencias_frame.pack_forget()
        botoes_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    btn_voltar = tk.Button(
        ref_botoes,
        text=textos[estado["idioma"]]["voltar_btn"],
        font=("Segoe UI", 9, "bold"),
        bg="#475569",
        fg="white",
        width=15,
        command=voltar_para_menu,
        cursor="hand2"
    )
    btn_voltar.pack(side=tk.LEFT)

    def alternar_idioma():
        novo_idioma = "EN" if estado["idioma"] == "PT" else "PT"
        estado["idioma"] = novo_idioma
        t = textos[novo_idioma]

        root.title(t["titulo"])
        btn_iniciar.config(text=t["iniciar"])
        btn_idioma.config(text=t["idioma_btn"])
        btn_referencias.config(text=t["referencias"])
        btn_tema.config(text=t["tema_btn_light"] if estado["modo_escuro"] else t["tema_btn_dark"])
        btn_voltar.config(text=t["voltar_btn"])
        lbl_nomes.config(text=t["nomes"])

    def alternar_tema():
        estado["modo_escuro"] = not estado["modo_escuro"]
        estado_tema["escuro"] = estado["modo_escuro"]
        t = textos[estado["idioma"]]
        btn_tema.config(text=t["tema_btn_light"] if estado["modo_escuro"] else t["tema_btn_dark"])
        aplicar_tema()

    def aplicar_tema():
        escuro = estado["modo_escuro"]
        set_dark_titlebar(root, escuro)
        bg = "#111827" if escuro else "#e5e7eb"
        fg = "#cbd5e1" if escuro else "#1e293b"
        btn_primary_bg = "#f6c445" if escuro else "#1e293b"
        btn_primary_fg = "#111827" if escuro else "white"
        btn_sec_bg = "#374151" if escuro else "#475569"
        btn_sec_fg = "white"

        root.configure(bg=bg)
        botoes_frame.configure(bg=bg)
        botoes_container.configure(bg=bg)
        referencias_frame.configure(bg=bg)
        ref_txt_frame.configure(bg=bg)
        ref_botoes.configure(bg=bg)
        lbl_ref_titulo.configure(bg=bg, fg=fg)

        btn_iniciar.config(bg=btn_primary_bg, fg=btn_primary_fg)
        btn_referencias.config(bg=btn_sec_bg, fg=btn_sec_fg)
        btn_idioma.config(bg=btn_sec_bg, fg=btn_sec_fg)
        btn_tema.config(bg=btn_sec_bg, fg=btn_sec_fg)
        btn_voltar.config(bg=btn_sec_bg, fg=btn_sec_fg)

        btn_iniciar.bind("<Enter>", lambda e: on_enter(e, btn_iniciar, "#d9a321" if escuro else "#0f172a"))
        btn_iniciar.bind("<Leave>", lambda e: on_leave(e, btn_iniciar, btn_primary_bg))

        for btn in [btn_referencias, btn_idioma, btn_tema, btn_voltar]:
            btn.bind("<Enter>", lambda e, b=btn: on_enter(e, b, "#4b5563" if escuro else "#334155"))
            btn.bind("<Leave>", lambda e, b=btn: on_leave(e, b, btn_sec_bg))

        txt.config(bg="#1f2937" if escuro else "white", fg="#f3f4f6" if escuro else "#1e293b")

    def atualizar_referencias():
        t = textos[estado["idioma"]]
        lbl_ref_titulo.config(text=t["ref_titulo"])
        txt.config(state=tk.NORMAL)
        txt.delete("1.0", tk.END)
        txt.insert(tk.END, t["ref_conteudo"])
        txt.config(state=tk.DISABLED)

    def mostrar_referencias():
        atualizar_referencias()
        botoes_frame.pack_forget()
        referencias_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    aplicar_tema()

    root.protocol("WM_DELETE_WINDOW", lambda: [estado.update({"acao": "cancelar"}), root.destroy()])
    root.mainloop()
    return estado["acao"], root, estado["idioma"]


import locale
idioma_selecionado = "PT"
if len(sys.argv) > 1:
    if sys.argv[1].upper() in ["PT", "EN"]:
        idioma_selecionado = sys.argv[1].upper()
else:
    try:
        loc = locale.getlocale()[0]
        if loc and not loc.startswith("pt"):
            idioma_selecionado = "EN"
    except Exception:
        pass

acao_inicial, main_root, idioma_selecionado = mostrar_tela_inicial(idioma_inicial=idioma_selecionado)
if acao_inicial == "cancelar":
    sys.exit(0)


# ---------------------------------------------- 1. COLETA DE INPUTS GERAIS -----------------------------------------------------------

input = builtins.input
print = builtins.print
for _g in ("_atit_modo", "_tumb_tipo_ci", "_tumb_ea1", "_tumb_ea2", "_tumb_ea3",
           "_tumb_q1", "_tumb_q2", "_tumb_q3", "_tumb_q4",
           "_tumb_ear1", "_tumb_ear2", "_tumb_ear3", "Tm"):
    globals().pop(_g, None)

dados_interface = coletar_parametros_por_interface(gmat_disponivel, root=main_root, idioma=idioma_selecionado)
if dados_interface == ENCERRAR_INTERFACE:
    sys.exit(0)
saida_interface = None
if dados_interface is not None:
    saida_interface = criar_janela_saida_interface(idioma=idioma_selecionado)
    respostas_interface = montar_respostas_interface(dados_interface)
    input_terminal = builtins.input
    print_terminal = builtins.print

    def input(prompt=""):
        if respostas_interface:
            return respostas_interface.pop(0)
        prompt_normalizado = prompt.lower()
        parent = saida_interface["janela"] if saida_interface is not None else None
        if "análise de placa solar" in prompt_normalizado or "solar panel analysis" in prompt_normalizado:
            etapa_interface("3. Análise de potência")
            _dc = globals().get("dados_contato")
            _tem_gs = bool(_dc and _dc.get("total_s", 0) > 0)
            _ler_log = saida_interface.get("ler_log") if saida_interface is not None else None
            respostas_modal = solicitar_analise_por_interface(
                parent, faces_ativas, tamanho_u, _tem_gs, _ler_log, idioma=idioma_selecionado)
            if respostas_modal == [ENCERRAR_INTERFACE]:
                sys.exit(0)
            respostas_interface.extend(respostas_modal)
            if not respostas_interface:
                return "n"
            return respostas_interface.pop(0)
        return input_terminal(prompt)

    def print(*args, **kwargs):
        print_terminal(*args, **kwargs)
        if saida_interface is None:
            return
        sep = kwargs.get("sep", " ")
        end = kwargs.get("end", "\n")
        mensagem = sep.join(str(arg) for arg in args) + end
        _escrever = saida_interface["escrever"]
        if threading.current_thread() is threading.main_thread():
            _escrever(mensagem)
        else:
            try:
                saida_interface["janela"].after(0, lambda m=mensagem: _escrever(m))
            except Exception:
                pass

def etapa_interface(nome):
    if saida_interface is not None:
        saida_interface["set_etapa"](nome)

def _p(pt_text, en_text):
    return en_text if idioma_selecionado == "EN" else pt_text

print(_p("--- Definição dos Parâmetros Orbitais ---", "--- Orbital Parameters Definition ---"))
orbit = input_int(
    _p("Tipo de órbita — Outro/manual (1), Molnya (2), Geoestacionária (3), LEO exemplo (4): ",
       "Orbit type — Custom/manual (1), Molnya (2), Geostationary (3), LEO example (4): "),
    opcoes_validas=[1, 2, 3, 4]
)
if orbit == 1:
    sma  = input_float(_p(f"SMA [km] (mín. {SMA_MINIMO_KM:.3f}, 140 km de altitude): ", f"SMA [km] (min. {SMA_MINIMO_KM:.3f}, 140 km altitude): "), min_val=SMA_MINIMO_KM)
    ecc  = input_float(_p("ECC [0 a <1]: ", "ECC [0 to <1]: "), min_val=0.0, max_val=0.9999)
    inc  = input_float(_p("INC [0 a 180°]: ", "INC [0 to 180°]: "), min_val=0.0, max_val=180.0)
    raan = input_float(_p("RAAN [0 a 360°]: ", "RAAN [0 to 360°]: "), min_val=0.0, max_val=360.0)
    aop  = input_float(_p("AOP [0 a 360°]: ", "AOP [0 to 360°]: "), min_val=0.0, max_val=360.0)
    ta   = input_float(_p("TA [0 a 360°]: ", "TA [0 to 360°]: "), min_val=0.0, max_val=360.0)
elif orbit == 2:
    sma, ecc, inc = 26553.0, 0.737, 63.4
    raan = input_float(_p("RAAN [0 a 360°]: ", "RAAN [0 to 360°]: "), min_val=0.0, max_val=360.0)
    aop  = input_float(_p("AOP [0 a 360°]: ", "AOP [0 to 360°]: "), min_val=0.0, max_val=360.0)
    ta   = input_float(_p("TA [0 a 360°]: ", "TA [0 to 360°]: "), min_val=0.0, max_val=360.0)
elif orbit == 3:
    sma, ecc, inc = 42178.0, 0.0, 0.0
    raan = input_float(_p("RAAN [0 a 360°]: ", "RAAN [0 to 360°]: "), min_val=0.0, max_val=360.0)
    aop  = input_float(_p("AOP [0 a 360°]: ", "AOP [0 to 360°]: "), min_val=0.0, max_val=360.0)
    ta   = input_float(_p("TA [0 a 360°]: ", "TA [0 to 360°]: "), min_val=0.0, max_val=360.0)
elif orbit == 4:
    sma  = 6778
    ecc  = 0.01
    inc  = 49.11
    raan = 30
    aop  = 0
    ta   = 0
print(_p("\n--- Definição do Satélite ---", "\n--- Satellite Definition ---"))
tamanho_u = input_int(_p("Tamanho do CubeSat (1, 2, 3, 6, 12 U): ", "CubeSat size (1, 2, 3, 6, 12 U): "), opcoes_validas=[1, 2, 3, 6, 12])
if tamanho_u == 1:
    dx, dy, dz = 0.100, 0.100, 0.1135
elif tamanho_u == 2:
    dx, dy, dz = 0.100, 0.100, 0.2270
elif tamanho_u == 3:
    dx, dy, dz = 0.100, 0.100, 0.3405
elif tamanho_u == 6:
    dx, dy, dz = 0.100, 0.2263, 0.3405
elif tamanho_u == 12:
    dx, dy, dz = 0.2263, 0.2263, 0.3405
m_sat  = input_float(_p("Massa do satélite [kg]: ", "Satellite mass [kg]: "), min_val=0.001)
cd_sat = input_float(_p("Coeficiente de arrasto (Cd): ", "Drag coefficient (Cd): "), min_val=0.0)
cr_sat = input_float(_p("Coeficiente de reflexão solar (Cr): ", "Solar reflection coefficient (Cr): "), min_val=0.0)

areas = areas_cubesat(dx, dy, dz)
print(_p("  Áreas:", "  Face areas:"))
for eixo, area in areas.items():
    print(f"    Face {eixo}: {area*1e4:.2f} cm²")

lista_faces = list(FACES.keys())
if dados_interface is not None:
    config_ui = (
        dados_interface["face_nadir"],
        dados_interface["face_vel"],
        dados_interface["faces_com_celula"],
    )
    _atit_modo = dados_interface.get("atitude_tipo", "NadirPointing")
elif tamanho_u in (1, 2, 3, 6, 12):
    print(_p("\n--- Modo de Atitude ---", "\n--- Attitude Mode ---"))
    _atit_modo_escolha = input_int(
        _p("Modo — NadirPointing (1), Tumbling (2): ",
           "Mode — NadirPointing (1), Tumbling (2): "),
        opcoes_validas=[1, 2]
    )
    if _atit_modo_escolha == 2:
        _atit_modo = "Tumbling"
        print(_p("  Modo Tumbling (Spinner GMAT). Sem orientação fixa.",
                 "  Tumbling mode (GMAT Spinner). No fixed orientation."))
        face_nadir = "+Z"
        face_vel = "+X"
        print(_p("\n--- Condição Inicial (Tumbling) ---", "\n--- Initial Condition (Tumbling) ---"))
        _tci = input_int(_p("  Tipo — EulerAngles (1), Quaternion (2): ",
                            "  Type — EulerAngles (1), Quaternion (2): "), opcoes_validas=[1, 2])
        if _tci == 2:
            globals()["_tumb_tipo_ci"] = "Quaternion"
            globals()["_tumb_q1"] = input_float(_p("  Q1: ", "  Q1: "))
            globals()["_tumb_q2"] = input_float(_p("  Q2: ", "  Q2: "))
            globals()["_tumb_q3"] = input_float(_p("  Q3: ", "  Q3: "))
            globals()["_tumb_q4"] = input_float(_p("  Q4: ", "  Q4: "), min_val=0.0001)
        else:
            globals()["_tumb_tipo_ci"] = "EulerAngles"
            print(_p("  (Sequência Euler fixa: 321)", "  (Euler sequence fixed: 321)"))
            globals()["_tumb_ea1"] = input_float(_p("  Ângulo Euler x [graus]: ", "  Euler Angle x [deg]: "))
            globals()["_tumb_ea2"] = input_float(_p("  Ângulo Euler y [graus]: ", "  Euler Angle y [deg]: "))
            globals()["_tumb_ea3"] = input_float(_p("  Ângulo Euler z [graus]: ", "  Euler Angle z [deg]: "))
        print(_p("\n--- Taxas Angulares [graus/s] ---", "\n--- Angular Rates [deg/s] ---"))
        globals()["_tumb_ear1"] = input_float(_p("  Taxa x: ", "  Rate x: "))
        globals()["_tumb_ear2"] = input_float(_p("  Taxa y: ", "  Rate y: "))
        globals()["_tumb_ear3"] = input_float(_p("  Taxa z: ", "  Rate z: "))
        print(_p("\n--- Células Solares ---", "\n--- Solar Cells ---"))
        _tumb_sol = {}
        for _tf in lista_faces:
            _tr = input_sn(_p(f"  Face {_tf} ({areas[_tf]*1e4:.0f} cm²) possui células solares? (s/n): ",
                              f"  Face {_tf} ({areas[_tf]*1e4:.0f} cm²) has solar cells? (y/n): "))
            _tumb_sol[_tf] = (_tr == 's')
        config_ui = (face_nadir, face_vel, _tumb_sol)
    else:
        _atit_modo = "NadirPointing"
        config_ui = coletar_geometria_por_interface(tamanho_u, areas)
        if config_ui is None and dados_interface is not None:
            sys.exit(0)
else:
    config_ui = None
    if '_atit_modo' not in globals():
        _atit_modo = "NadirPointing"

if config_ui is not None:
    face_nadir, face_vel, faces_com_celula = config_ui
    print(_p("\n--- Configuração pela Interface Rev.14 ---", "\n--- Configuration via Interface Rev.14 ---"))
    if _atit_modo != "Tumbling":
        print(_p(f"  Face {face_nadir} -> Nadir (Terra)", f"  Face {face_nadir} -> Nadir (Earth)"))
        print(_p(f"  Face {face_vel} -> Velocidade orbital", f"  Face {face_vel} -> Orbital velocity"))
    else:
        print(_p("  Modo: Tumbling", "  Mode: Tumbling"))
else:
    print(_p("\n--- Modo de Atitude ---", "\n--- Attitude Mode ---"))
    _atit_modo_term = input_int(
        _p("Modo de atitude — NadirPointing (1), Tumbling (2): ",
           "Attitude mode — NadirPointing (1), Tumbling (2): "),
        opcoes_validas=[1, 2]
    )
    if _atit_modo_term == 2:
        _atit_modo = "Tumbling"
        print(_p("  Modo Tumbling selecionado. As faces serão calculadas sem orientação fixa.",
                 "  Tumbling mode selected. Faces will be computed without fixed orientation."))
        face_nadir = "+Z"
        face_vel = "+X"
    else:
        _atit_modo = "NadirPointing"
        print(_p("\n--- Atitude: Nadir Pointing ---", "\n--- Attitude: Nadir Pointing ---"))
        print(_p(f"  Faces disponíveis: {lista_faces}", f"  Available faces: {lista_faces}"))
        face_nadir = input(_p(f"Qual face aponta para a Terra (nadir)? {lista_faces}: ",
                              f"Which face points toward Earth (nadir)? {lista_faces}: ")).strip()
        while face_nadir not in FACES:
            print(_p(f"  ERRO: Opção inválida. Escolha entre: {lista_faces}.",
                     f"  ERROR: Invalid option. Choose from: {lista_faces}."))
            face_nadir = input(_p(f"Qual face aponta para a Terra (nadir)? {lista_faces}: ",
                                  f"Which face points toward Earth (nadir)? {lista_faces}: ")).strip()

        print(_p("\n--- Atitude: Segundo Eixo ---", "\n--- Attitude: Second Axis ---"))
        opcoes_vel = [f for f in lista_faces if f != face_nadir and f != FACE_OPOSTA[face_nadir]]
        print(_p(f"  Faces disponíveis para alinhamento com a velocidade: {opcoes_vel}",
                 f"  Available faces for velocity alignment: {opcoes_vel}"))
        face_vel = input(_p(f"Qual face aponta na direção da velocidade orbital? {opcoes_vel}: ",
                            f"Which face points in the orbital velocity direction? {opcoes_vel}: ")).strip()
        while face_vel not in opcoes_vel:
            print(_p(f"  ERRO: Opção inválida. Escolha entre: {opcoes_vel}.",
                     f"  ERROR: Invalid option. Choose from: {opcoes_vel}."))
            face_vel = input(_p(f"Qual face aponta na direção da velocidade orbital? {opcoes_vel}: ",
                                f"Which face points in the orbital velocity direction? {opcoes_vel}: ")).strip()

eixo_nadir_vec  = FACES[face_nadir]
eixo_vel_vec    = FACES[face_vel]
eixo_normal_vec = np.cross(eixo_nadir_vec, eixo_vel_vec)
_norm_eixo = np.linalg.norm(eixo_normal_vec)
eixo_normal_vec = eixo_normal_vec / _norm_eixo if _norm_eixo > 1e-10 else np.array([0., 1., 0.])

print(f"\n  " + _p("Atitude configurada:", "Configured attitude:"))
_di = dados_interface if ('dados_interface' in locals() and dados_interface is not None and isinstance(dados_interface, dict)) else (globals().get('dados_interface') if isinstance(globals().get('dados_interface'), dict) else None)
if _di is not None and _di.get("atitude_tipo") == "Tumbling":
    _ci = _di.get("tipo_ci", "EulerAngles")
    print(_p(f"    Modo: Tumbling", f"    Mode: Tumbling"))
    print(_p(f"    Condição Inicial / Taxa Angular: {_ci}", f"    Initial Condition / Angular Rate: {_ci}"))
else:
    print(_p(f"    Face {face_nadir} → Nadir (Terra)", f"    Face {face_nadir} → Nadir (Earth)"))
    print(_p(f"    Face {face_vel}  → Velocidade orbital", f"    Face {face_vel}  → Orbital velocity"))

drag_area = areas[face_vel]
srp_area  = max(areas.values())

print(_p(f"\n  DragArea (face {face_vel}, frontal à velocidade): {drag_area:.6f} m²",
         f"\n  DragArea (face {face_vel}, velocity-facing): {drag_area:.6f} m²"))
print(_p(f"  SRPArea  (maior seção transversal):  {srp_area:.6f} m²",
         f"  SRPArea  (largest cross-section):  {srp_area:.6f} m²"))

if config_ui is None:
    print(_p("\n--- Células Solares ---", "\n--- Solar Cells ---"))
    if _atit_modo != "Tumbling":
        print(_p(f"  A face {face_nadir} (nadir) não recebe células solares.",
                 f"  Face {face_nadir} (nadir) does not receive solar cells."))
    faces_com_celula = {}
    for eixo in lista_faces:
        if _atit_modo != "Tumbling" and eixo == face_nadir:
            faces_com_celula[eixo] = False
            continue
        resp = input_sn(_p(f"  Face {eixo} ({areas[eixo]*1e4:.0f} cm²) possui células solares? (s/n): ",
                           f"  Face {eixo} ({areas[eixo]*1e4:.0f} cm²) has solar cells? (y/n): "))
        faces_com_celula[eixo] = (resp == 's')
faces_ativas = [f for f, tem in faces_com_celula.items() if tem]
print(_p(f"\n  Faces com células solares: {faces_ativas}",
         f"\n  Faces with solar cells: {faces_ativas}"))


# ---------------------------------------------- 2. ESTAÇÃO TERRENA E SIMULAÇÃO -----------------------------------------------------------

print(_p("\n--- Estação Terrena e Simulação ---", "\n--- Ground Station and Simulation ---"))
gs = input_sn(_p("Deseja informar estação terrena? (s/n): ", "Specify ground station? (y/n): "))
if gs == 's':
    lat  = input_float(_p("Latitude [°] (-90 a 90): ", "Latitude [°] (-90 to 90): "), min_val=-90.0, max_val=90.0)
    lon  = input_float(_p("Longitude [°] (-180 a 180): ", "Longitude [°] (-180 to 180): "), min_val=-180.0, max_val=180.0)
    alt  = input_float(_p("Altitude [km]: ", "Altitude [km]: "), min_val=0.0)
    elev = input_float(_p("Elevação mínima [°] (0 a 90): ", "Minimum elevation [°] (0 to 90): "), min_val=0.0, max_val=90.0)

tempo = input_float(_p("Tempo de simulação [dias]: ", "Simulation time [days]: "), min_val=0.01)
_data_str = input(_p(
    "Data de início (UTC) [DD/MM/AAAA, ex: 01/01/2025]: ",
    "Start date (UTC) [DD/MM/YYYY, e.g. 01/01/2025]: "
)).strip() or "01/01/2025"
_hora_str = input(_p(
    "Horário de início (UTC) [HH:MM, ex: 12:00]: ",
    "Start time (UTC) [HH:MM, e.g. 12:00]: "
)).strip() or "12:00"
epoch_gregorian_str = f"{_data_str} {_hora_str}"
_MESES_CONV = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
_EPOCH_MIN    = datetime(1957, 10, 4, 12, 0, 0)
_EPOCH_MAX    = datetime(2100, 2, 28, 0, 0, 0)
_j2000_dt     = datetime(2000, 1, 1, 12, 0, 0)

def _parse_epoch_ddmmyyyy(raw):
    raw = raw.strip()
    partes = raw.replace("T", " ").split()
    data_str = partes[0] if partes else ""
    hora_str = partes[1] if len(partes) > 1 else "12:00"
    campos_d = data_str.split("/")
    if len(campos_d) != 3:
        return None, None
    try:
        dd, mm, yyyy = int(campos_d[0]), int(campos_d[1]), int(campos_d[2])
        mes = _MESES_CONV.get(mm)
        if mes is None:
            return None, None
        campos_t = hora_str.split(":")
        hh = int(campos_t[0]) if campos_t else 0
        mn = int(campos_t[1]) if len(campos_t) > 1 else 0
        gmat_str = f"{dd:02d} {mes} {yyyy} {hh:02d}:{mn:02d}:00.000"
        dt = datetime(yyyy, mm, dd, hh, mn, 0)
        return dt, gmat_str
    except (ValueError, IndexError):
        return None, None

_epoch_dt, _epoch_gmat = _parse_epoch_ddmmyyyy(epoch_gregorian_str)
if _epoch_dt is None or _epoch_gmat is None:
    print(_p("AVISO: formato de data inválido. Usando 01/01/2025 12:00.",
             "WARNING: invalid date format. Using 01/01/2025 12:00."))
    _epoch_dt, _epoch_gmat = datetime(2025, 1, 1, 12, 0, 0), "01 Jan 2025 12:00:00.000"
if _epoch_dt < _EPOCH_MIN or _epoch_dt > _EPOCH_MAX:
    print(_p("AVISO: data fora do intervalo permitido. Usando 01/01/2025 12:00.",
             "WARNING: date out of allowed range. Using 01/01/2025 12:00."))
    _epoch_dt, _epoch_gmat = datetime(2025, 1, 1, 12, 0, 0), "01 Jan 2025 12:00:00.000"
epoch_gregorian_str = _epoch_gmat
initial_epoch = 21545.0 + (_epoch_dt - _j2000_dt).total_seconds() / 86400.0
final_epoch   = initial_epoch + tempo


# ---------------------------------------------- 3. CONFIGURAÇÃO DE ARQUIVOS -----------------------------------------------------------

BASE_DIR         = obter_base_dir()
if idioma_selecionado == "EN":
    pasta_scripts    = os.path.join(BASE_DIR, "Generated_Scripts_Pegasus")
    pasta_resultados = os.path.join(BASE_DIR, "Results_Pegasus")
else:
    pasta_scripts    = os.path.join(BASE_DIR, "Scripts_Gerados_Pegasus")
    pasta_resultados = os.path.join(BASE_DIR, "Resultados_Pegasus")

nome_arquivo_script  = f"Script_{inc:.2f}deg_{sma:.0f}km.script"
nome_arquivo_contato = f"Contato_INC{inc:.2f}_SMA{sma:.0f}.txt"
nome_arquivo_eclipse = f"Eclipse_INC{inc:.2f}_SMA{sma:.0f}.txt"

caminho_script_gerado     = os.path.join(pasta_scripts, nome_arquivo_script)
caminho_eclipse_resultado = os.path.join(pasta_resultados, nome_arquivo_eclipse).replace("\\", "/")
nome_arquivo_report       = f"Report_INC{inc:.2f}_SMA{sma:.0f}.txt"
caminho_report            = os.path.join(pasta_resultados, nome_arquivo_report).replace("\\", "/")
nome_arquivo_report2      = f"XYZ_Mag_INC{inc:.2f}_SMA{sma:.0f}.txt"
caminho_report2           = os.path.join(pasta_resultados, nome_arquivo_report2).replace("\\", "/")

align_vec      = eixo_nadir_vec
constraint_vec = eixo_vel_vec

_atit_tipo = dados_interface.get("atitude_tipo", "NadirPointing") if dados_interface else globals().get("_atit_modo", "NadirPointing")

if _atit_tipo == "Tumbling":
    _tipo_ci = dados_interface.get("tipo_ci", "EulerAngles") if dados_interface else globals().get("_tumb_tipo_ci", "EulerAngles")
    _ear1 = dados_interface.get("ear1", 0.0) if dados_interface else globals().get("_tumb_ear1", 0.0)
    _ear2 = dados_interface.get("ear2", 0.0) if dados_interface else globals().get("_tumb_ear2", 0.0)
    _ear3 = dados_interface.get("ear3", 0.0) if dados_interface else globals().get("_tumb_ear3", 0.0)
    if _tipo_ci == "Quaternion":
        _q1 = dados_interface.get("q1", 0.0) if dados_interface else globals().get("_tumb_q1", 0.0)
        _q2 = dados_interface.get("q2", 0.0) if dados_interface else globals().get("_tumb_q2", 0.0)
        _q3 = dados_interface.get("q3", 0.0) if dados_interface else globals().get("_tumb_q3", 0.0)
        _q4 = dados_interface.get("q4", 1.0) if dados_interface else globals().get("_tumb_q4", 1.0)
        _TUMB_Q0 = (float(_q1), float(_q2), float(_q3), float(_q4))
        try:
            from scipy.spatial.transform import Rotation as _RotInit
            _ea_ini = list(_RotInit.from_quat(_TUMB_Q0).as_euler('ZYX', degrees=True))
        except Exception:
            _ea_ini = [0.0, 0.0, 0.0]
    else:  
        _ea1 = dados_interface.get("ea1", 0.0) if dados_interface else globals().get("_tumb_ea1", 0.0)
        _ea2 = dados_interface.get("ea2", 0.0) if dados_interface else globals().get("_tumb_ea2", 0.0)
        _ea3 = dados_interface.get("ea3", 0.0) if dados_interface else globals().get("_tumb_ea3", 0.0)
        _ea_ini = [float(_ea1), float(_ea2), float(_ea3)]
        try:
            from scipy.spatial.transform import Rotation as _RotInit
            _TUMB_Q0 = tuple(_RotInit.from_euler('ZYX', _ea_ini, degrees=True).as_quat())
        except Exception:
            _TUMB_Q0 = (0.0, 0.0, 0.0, 1.0)

    bloco_atitude = """DefaultSC.Attitude = CoordinateSystemFixed;"""
    _ATITUDE_ANALITICA = True
    _TUMB_OMEGA = (float(_ear1), float(_ear2), float(_ear3))
    try:
        _TUMB_EPOCH_DT = datetime.strptime(str(epoch_gregorian_str), "%d %b %Y %H:%M:%S.%f")
    except Exception:
        _TUMB_EPOCH_DT = None
else:  
    _ATITUDE_ANALITICA = False
    bloco_atitude = f"""DefaultSC.Attitude = NadirPointing;
DefaultSC.AttitudeReferenceBody = Earth; 
DefaultSC.AttitudeConstraintType = Velocity;
DefaultSC.BodyAlignmentVectorX = {align_vec[0]};
DefaultSC.BodyAlignmentVectorY = {align_vec[1]};
DefaultSC.BodyAlignmentVectorZ = {align_vec[2]};
DefaultSC.BodyConstraintVectorX = {constraint_vec[0]};
DefaultSC.BodyConstraintVectorY = {constraint_vec[1]};
DefaultSC.BodyConstraintVectorZ = {constraint_vec[2]};"""

_att_display = 'Quaternion'
_att_rate_display = 'AngularVelocity'

print(f"  " + _p("Orbit", "Orbit") + f": SMA={sma:.3f} km | ECC={ecc:.6f} | INC={inc:.3f}° | RAAN={raan:.3f}° | AOP={aop:.3f}° | TA={ta:.3f}°")
print(f"  CubeSat: {tamanho_u}U | dx={dx:.4f} m | dy={dy:.4f} m | dz={dz:.4f} m")
print(f"  " + _p("Massa", "Mass") + f"={m_sat:.3f} kg | Cd={cd_sat:.3f} | Cr={cr_sat:.3f}")
if _atit_tipo == "Tumbling":
    _wx, _wy, _wz = _TUMB_OMEGA
    print(_p(f"  Atitude: Tumbling | velocidade angular ω = ({_wx:g}, {_wy:g}, {_wz:g}) °/s",
             f"  Attitude: Tumbling | angular velocity ω = ({_wx:g}, {_wy:g}, {_wz:g}) deg/s"))
else:
    print(_p(f"  Atitude: {face_nadir} -> Nadir | {face_vel} -> Velocidade",
             f"  Attitude: {face_nadir} -> Nadir | {face_vel} -> Velocity"))
print(_p(f"  Painéis solares: {faces_ativas if faces_ativas else 'nenhum'}",
         f"  Solar panels: {faces_ativas if faces_ativas else 'none'}"))
if gs == 's':
    print(_p(f"  Estação: lat={lat:.3f}° | lon={lon:.3f}° | alt={alt:.3f} km | elev={elev:.3f}°",
             f"  Station: lat={lat:.3f}° | lon={lon:.3f}° | alt={alt:.3f} km | elev={elev:.3f}°"))
else:
    print(_p("  Estação: não informada", "  Station: not provided"))
print(_p(f"  Simulação: {tempo:.3f} dia(s) | Epoch={epoch_gregorian_str}",
         f"  Simulation: {tempo:.3f} day(s) | Epoch={epoch_gregorian_str}"))
print(_p(f"  Script GMAT: {caminho_script_gerado}", f"  GMAT Script: {caminho_script_gerado}"))
print(_p(f"  Resultados esperados: {pasta_resultados}", f"  Expected results: {pasta_resultados}"))


# ---------------------------------------------- 4. GERAÇÃO DO SCRIPT GMAT -----------------------------------------------------------

conteudo_script_gmat = f"""% General Mission Analysis Tool(GMAT) Script

%----------------------------------------
%---------- Spacecraft
%----------------------------------------

Create Spacecraft DefaultSC;
DefaultSC.DateFormat = UTCGregorian;
DefaultSC.Epoch = '{epoch_gregorian_str}';
DefaultSC.CoordinateSystem = EarthMJ2000Eq;
DefaultSC.DisplayStateType = Keplerian;
DefaultSC.SMA = {sma};
DefaultSC.ECC = {ecc};
DefaultSC.INC = {inc};
DefaultSC.RAAN = {raan};
DefaultSC.AOP = {aop};
DefaultSC.TA = {ta};
DefaultSC.DryMass = {m_sat};
DefaultSC.Cd = {cd_sat};
DefaultSC.Cr = {cr_sat};
DefaultSC.DragArea = {drag_area};
DefaultSC.SRPArea = {srp_area};
DefaultSC.SPADDragScaleFactor = 1;
DefaultSC.SPADSRPScaleFactor = 1;
DefaultSC.AtmosDensityScaleFactor = 1;
DefaultSC.ExtendedMassPropertiesModel = 'None';
DefaultSC.NAIFId = -10000001;
DefaultSC.NAIFIdReferenceFrame = -9000001;
DefaultSC.OrbitColor = Red;
DefaultSC.TargetColor = Teal;
DefaultSC.OrbitErrorCovariance = [ 1e+70 0 0 0 0 0 ; 0 1e+70 0 0 0 0 ; 0 0 1e+70 0 0 0 ; 0 0 0 1e+70 0 0 ; 0 0 0 0 1e+70 0 ; 0 0 0 0 0 1e+70 ];
DefaultSC.CdSigma = 1e+70;
DefaultSC.CrSigma = 1e+70;
DefaultSC.Id = 'SatId';
{bloco_atitude}
DefaultSC.SPADSRPInterpolationMethod = Bilinear;
DefaultSC.SPADSRPScaleFactorSigma = 1e+70;
DefaultSC.SPADDragInterpolationMethod = Bilinear;
DefaultSC.SPADDragScaleFactorSigma = 1e+70;
DefaultSC.AtmosDensityScaleFactorSigma = 1e+70;
DefaultSC.ModelFile = 'aura.3ds';
DefaultSC.ModelOffsetX = 0;
DefaultSC.ModelOffsetY = 0;
DefaultSC.ModelOffsetZ = 0;
DefaultSC.ModelRotationX = 0;
DefaultSC.ModelRotationY = 0;
DefaultSC.ModelRotationZ = 0;
DefaultSC.ModelScale = 1;
DefaultSC.AttitudeDisplayStateType = '{_att_display}';
DefaultSC.AttitudeRateDisplayStateType = '{_att_rate_display}';
DefaultSC.AttitudeCoordinateSystem = EarthMJ2000Eq;
DefaultSC.EulerAngleSequence = '321';
"""

if gs == 's':
    caminho_contato_resultado = os.path.join(pasta_resultados, nome_arquivo_contato).replace("\\", "/")
    conteudo_script_gmat += f"""
%----------------------------------------
%---------- GroundStations
%----------------------------------------

Create GroundStation GroundStation1;
GroundStation1.OrbitColor = Thistle;
GroundStation1.TargetColor = DarkGray;
GroundStation1.CentralBody = Earth;
GroundStation1.StateType = Spherical;
GroundStation1.HorizonReference = Sphere;
GroundStation1.Location1 = {lat};
GroundStation1.Location2 = {lon};
GroundStation1.Location3 = {alt};
GroundStation1.Id = 'StationId';
GroundStation1.IonosphereModel = 'None';
GroundStation1.TroposphereModel = 'None';
GroundStation1.DataSource = 'Constant';
GroundStation1.Temperature = 295.1;
GroundStation1.Pressure = 1013.5;
GroundStation1.Humidity = 55;
GroundStation1.MinimumElevationAngle = {elev};
"""

conteudo_script_gmat += f"""
%----------------------------------------
%---------- ForceModels
%----------------------------------------

Create ForceModel DefaultProp_ForceModel;
DefaultProp_ForceModel.CentralBody = Earth;
DefaultProp_ForceModel.PrimaryBodies = {{Earth}};
DefaultProp_ForceModel.PointMasses = {{Luna, Sun}};
DefaultProp_ForceModel.SRP = On;
DefaultProp_ForceModel.RelativisticCorrection = Off;
DefaultProp_ForceModel.ErrorControl = RSSStep;
DefaultProp_ForceModel.GravityField.Earth.Degree = 10;
DefaultProp_ForceModel.GravityField.Earth.Order = 10;
DefaultProp_ForceModel.GravityField.Earth.StmLimit = 100;
DefaultProp_ForceModel.GravityField.Earth.PotentialFile = 'JGM2.cof';
DefaultProp_ForceModel.GravityField.Earth.TideModel = 'None';
DefaultProp_ForceModel.SRP.Flux = 1367;
DefaultProp_ForceModel.SRP.SRPModel = Spherical;
DefaultProp_ForceModel.SRP.Nominal_Sun = 149597870.691;
DefaultProp_ForceModel.Drag.AtmosphereModel = JacchiaRoberts;
DefaultProp_ForceModel.Drag.HistoricWeatherSource = 'ConstantFluxAndGeoMag';
DefaultProp_ForceModel.Drag.PredictedWeatherSource = 'ConstantFluxAndGeoMag';
DefaultProp_ForceModel.Drag.CSSISpaceWeatherFile = 'SpaceWeather-All-v1.2.txt';
DefaultProp_ForceModel.Drag.SchattenFile = 'SchattenPredict.txt';
DefaultProp_ForceModel.Drag.F107 = 150;
DefaultProp_ForceModel.Drag.F107A = 150;
DefaultProp_ForceModel.Drag.MagneticIndex = 3;
DefaultProp_ForceModel.Drag.SchattenErrorModel = 'Nominal';
DefaultProp_ForceModel.Drag.SchattenTimingModel = 'NominalCycle';
DefaultProp_ForceModel.Drag.DragModel = 'Spherical';

%----------------------------------------
%---------- Propagators
%----------------------------------------

Create Propagator DefaultProp;
DefaultProp.FM = DefaultProp_ForceModel;
DefaultProp.Type = RungeKutta89;
DefaultProp.InitialStepSize = 60;
DefaultProp.Accuracy = 9.999999999999999e-12;
DefaultProp.MinStep = 0.001;
DefaultProp.MaxStep = 2700;
DefaultProp.MaxStepAttempts = 50;
DefaultProp.StopIfAccuracyIsViolated = true;

%----------------------------------------
%---------- EventLocators
%----------------------------------------
"""

if gs == 's':
    conteudo_script_gmat += f"""
Create ContactLocator ContactLocator1;
ContactLocator1.Target = DefaultSC;
ContactLocator1.Filename = '{caminho_contato_resultado}';
ContactLocator1.InputEpochFormat = 'TAIModJulian';
ContactLocator1.InitialEpoch = '{initial_epoch}';
ContactLocator1.StepSize = 10;
ContactLocator1.FinalEpoch = '{final_epoch}';
ContactLocator1.UseLightTimeDelay = true;
ContactLocator1.UseStellarAberration = true;
ContactLocator1.WriteReport = true;
ContactLocator1.RunMode = Automatic;
ContactLocator1.UseEntireInterval = true;
ContactLocator1.Observers = {{GroundStation1}};
ContactLocator1.LightTimeDirection = Transmit;
ContactLocator1.LeftJustified = false;
ContactLocator1.ReportPrecision = 6;
ContactLocator1.ReportFormat = 'Legacy';
ContactLocator1.IntervalStepSize = 0;
ContactLocator1.ReportTimeFormat = 'UTCGregorian';
"""

conteudo_script_gmat += f"""
Create EclipseLocator EclipseLocator1;
EclipseLocator1.Spacecraft = DefaultSC;
EclipseLocator1.Filename = '{caminho_eclipse_resultado}';
EclipseLocator1.OccultingBodies = {{Earth}};
EclipseLocator1.InputEpochFormat = 'TAIModJulian';
EclipseLocator1.InitialEpoch = '{initial_epoch}';
EclipseLocator1.StepSize = 10;
EclipseLocator1.FinalEpoch = '{final_epoch}';
EclipseLocator1.UseLightTimeDelay = true;
EclipseLocator1.UseStellarAberration = true;
EclipseLocator1.WriteReport = true;
EclipseLocator1.RunMode = Automatic;
EclipseLocator1.UseEntireInterval = true;
EclipseLocator1.EclipseTypes = {{'Umbra', 'Penumbra', 'Antumbra'}};

%----------------------------------------
%---------- Subscribers
%----------------------------------------

Create ReportFile ReportFile1;
ReportFile1.Filename = '{caminho_report}';
ReportFile1.Precision = 16;
ReportFile1.Add = {{DefaultSC.TAIModJulian, DefaultSC.EarthMJ2000Eq.X, DefaultSC.EarthMJ2000Eq.Y, DefaultSC.EarthMJ2000Eq.Z, DefaultSC.EarthMJ2000Eq.VX, DefaultSC.EarthMJ2000Eq.VY, DefaultSC.EarthMJ2000Eq.VZ, Sun.EarthMJ2000Eq.X, Sun.EarthMJ2000Eq.Y, Sun.EarthMJ2000Eq.Z, DefaultSC.Q1, DefaultSC.Q2, DefaultSC.Q3, DefaultSC.Q4}};
ReportFile1.WriteHeaders = true;
ReportFile1.ColumnWidth = 23;
ReportFile1.WriteReport = true;

Create ReportFile ReportFile2;
ReportFile2.SolverIterations = Current;
ReportFile2.UpperLeft = [ 0 0 ];
ReportFile2.Size = [ 0 0 ];
ReportFile2.RelativeZOrder = 0;
ReportFile2.Maximized = false;
ReportFile2.Filename = '{caminho_report2}';
ReportFile2.Precision = 16;
ReportFile2.Add = {{DefaultSC.UTCGregorian, DefaultSC.Q1, DefaultSC.Q2, DefaultSC.Q3, DefaultSC.Q4, DefaultSC.EarthMJ2000Eq.X, DefaultSC.EarthMJ2000Eq.Y, DefaultSC.EarthMJ2000Eq.Z, Sun.EarthMJ2000Eq.X, Sun.EarthMJ2000Eq.Y, Sun.EarthMJ2000Eq.Z}};
ReportFile2.WriteHeaders = true;
ReportFile2.LeftJustify = On;
ReportFile2.ZeroFill = Off;
ReportFile2.FixedWidth = true;
ReportFile2.Delimiter = ' ';
ReportFile2.ColumnWidth = 23;
ReportFile2.WriteReport = true;
ReportFile2.AppendToExistingFile = false;
%----------------------------------------
%---------- Mission Sequence
%----------------------------------------

BeginMissionSequence;
Propagate DefaultProp(DefaultSC) {{DefaultSC.ElapsedDays = {tempo}, DefaultSC.Altitude = 200}};
"""


# ---------------------------------------------- 5. CRIAÇÃO DO SCRIPT -----------------------------------------------------------

etapa_interface("2. Script / GMAT")
try:
    os.makedirs(pasta_scripts, exist_ok=True)
    conteudo_script_gmat = remover_acentos(conteudo_script_gmat)
    with open(caminho_script_gerado, "w", encoding="utf-8") as f:
        f.write(conteudo_script_gmat.strip())
    print(_p(f"\nArquivo '{nome_arquivo_script}' criado em: {pasta_scripts}",
             f"\nFile '{nome_arquivo_script}' created in: {pasta_scripts}"))
except Exception as e:
    print(_p(f"\nERRO ao criar o arquivo '{nome_arquivo_script}': {e}",
             f"\nERROR creating file '{nome_arquivo_script}': {e}"))

# ---------------------------------------------- 6. EXECUÇÃO DO GMAT E ANÁLISE DOS RESULTADOS -----------------------------------------------------------

if gmat_disponivel:
    if dados_interface is not None:
        executar = dados_interface.get("executar", "n")
    else:
        executar = input_sn(_p("\nDeseja executar este script GMAT agora? (s/n): ", "\nRun this GMAT script now? (y/n): "))
    if executar == 's':
        print(_p("\n--- Executando o script GMAT ---", "\n--- Running GMAT script ---"))
        sucesso = False
        aviso_gmat = abrir_aviso_gmat_rodando(
            saida_interface["janela"] if saida_interface is not None else None,
            idioma=idioma_selecionado
        )
        try:
            import time
            os.makedirs(pasta_resultados, exist_ok=True)
            gmat.Clear()
            
            estado_execucao = {"sucesso": False}
            
            def tarefa_gmat():
                try:
                    if gmat.LoadScript(caminho_script_gerado):
                        if gmat.RunScript():
                            estado_execucao["sucesso"] = True
                        else:
                            print(_p("--- ERRO durante a execução do GMAT! ---", "--- ERROR during GMAT execution! ---"))
                            _gmat_bin = globals().get("GmatBinPath", "")
                            if _gmat_bin:
                                _log = os.path.normpath(os.path.join(_gmat_bin, "..", "output", "GmatLog.txt"))
                                print(_p(f"  Log GMAT: {_log}", f"  GMAT log: {_log}"))
                                if os.path.exists(_log):
                                    try:
                                        with open(_log, "r", encoding="utf-8", errors="replace") as _lf:
                                            _linhas = _lf.readlines()
                                        _inicio = 0
                                        for _i in range(len(_linhas) - 1, -1, -1):
                                            if "Interpreting scripts" in _linhas[_i]:
                                                _inicio = _i
                                                break
                                        _erros = [l.rstrip() for l in _linhas[_inicio:] if any(
                                            kw in l.upper() for kw in ("ERROR", "EXCEPTION", "ABORT", "FAILED", "UNABLE")
                                        ) and "libPythonInterface" not in l and "libMatlabInterface" not in l and "libFminconOptimizer" not in l][-6:]
                                        if _erros:
                                            print(_p("  Erros da execução atual:", "  Errors from current run:"))
                                            for _e in _erros:
                                                print(f"    {_e}")
                                    except Exception:
                                        pass
                    else:
                        print(_p("--- ERRO ao carregar o script GMAT! ---", "--- ERROR loading GMAT script! ---"))
                except Exception as e:
                    print(_p(f"--- ERRO inesperado no GMAT: {e} ---", f"--- Unexpected GMAT error: {e} ---"))
            
            thread_gmat = threading.Thread(target=tarefa_gmat, daemon=True)
            thread_gmat.start()
            
            while thread_gmat.is_alive():
                if saida_interface is not None:
                    try:
                        saida_interface["janela"].update()
                    except tk.TclError:
                        pass
                if aviso_gmat is not None:
                    try:
                        aviso_gmat.update()
                    except tk.TclError:
                        pass
                time.sleep(0.05)
                
            thread_gmat.join()
            
            if estado_execucao["sucesso"]:
                print(_p("--- Execução concluída com sucesso! ---", "--- Execution completed successfully! ---"))
                print(_p(f"Resultados em: {pasta_resultados}", f"Results in: {pasta_resultados}"))
                sucesso = True
        except Exception as e:
            print(_p(f"--- ERRO inesperado: {e} ---", f"--- Unexpected error: {e} ---"))
        finally:
            fechar_aviso(aviso_gmat)

        if sucesso:
            print(_p("\n--- Analisando Resultados ---", "\n--- Analyzing Results ---"))
            processar_report2(caminho_report2.replace("/", os.sep))

            dados_contato = None
            if gs == 's':
                dados_contato = analisar_contatos(caminho_contato_resultado.replace("/", os.sep))
                if dados_contato:
                    print(_p("\nResultados de Contato:", "\nContact Results:"))
                    print(_p(f"  - Tempo Total:      {dados_contato['total_s']:.2f} s",
                             f"  - Total Time:       {dados_contato['total_s']:.2f} s"))
                    print(_p(f"  - Menor Evento:     {dados_contato['menor_evento_s']:.2f} s",
                             f"  - Shortest Event:   {dados_contato['menor_evento_s']:.2f} s"))
                    print(f"  - " + _p("Nº de Eventos", "No. of Events") + f":    {dados_contato['num_eventos']}")
                    if dados_contato.get("por_dia"):
                        _dia_hdr = _p("Dia", "Day")
                        _nc_hdr  = _p("Nº contatos", "No. contacts")
                        _tt_hdr  = _p("Tempo total (s)", "Total time (s)")
                        print(_p("\n  Contatos por dia:", "\n  Contacts per day:"))
                        print(f"  {_dia_hdr:<14} {_nc_hdr:>12} {_tt_hdr:>16}")
                        print("  " + "-" * 46)
                        for _dia, _d in dados_contato["por_dia"].items():
                            print(f"  {_dia:<14} {_d['n']:>12} {_d['s']:>16.1f}")
                        print("  " + "-" * 46)
                else:
                    print(_p("\nNão foi possível analisar o arquivo de contato.",
                             "\nCould not analyze the contact file."))

            dados_eclipse = analisar_eclipses(caminho_eclipse_resultado.replace("/", os.sep))
            if dados_eclipse:
                print(_p("\nResultados de Eclipse:", "\nEclipse Results:"))
                print(_p(f"  - Tempo Total:      {dados_eclipse['total_s']:.2f} s",
                         f"  - Total Time:       {dados_eclipse['total_s']:.2f} s"))
                print(_p(f"  - Maior Evento:     {dados_eclipse['maior_evento_s']:.2f} s",
                         f"  - Longest Event:    {dados_eclipse['maior_evento_s']:.2f} s"))
                print(f"  - " + _p("Nº de Eventos", "No. of Events") + f":    {dados_eclipse['num_eventos']}")
            else:
                print(_p("\nNão foi possível analisar o arquivo de eclipse.",
                         "\nCould not analyze the eclipse file."))

            print(_p(
                "\n  [DISCLAIMER] Apenas o eclipse pela Terra é considerado. Eclipses de"
                "\n  terceiro corpo (ocultação lunar) são desconsiderados nesta etapa de"
                "\n  projeto preliminar, por não serem relevantes ao dimensionamento do EPS.",
                "\n  [DISCLAIMER] Only Earth eclipses are considered. Third-body (lunar)"
                "\n  occultations are disregarded at this preliminary design stage, as they"
                "\n  are not relevant to EPS sizing."))

            _tempo_real = tempo
            _ult_tai, _ult_alt = _ultimo_ponto_report(caminho_report.replace("/", os.sep))
            if _ult_tai is not None:
                _td = _ult_tai - initial_epoch
                _parou_antes = 0.0 < _td < tempo - (1.0 / 1440.0)  
                _reentrou = _parou_antes and (_ult_alt is None or _ult_alt <= 250.0)
                if _parou_antes:
                    _tempo_real = _td
                if _reentrou:
                    print(_p(f"\n  {'='*64}", f"\n  {'='*64}"))
                    print(_p(f"  ⚠ AVISO: O SATÉLITE REENTROU NA ATMOSFERA após {_td:.1f} dias.",
                             f"  ⚠ WARNING: THE SATELLITE REENTERED THE ATMOSPHERE after {_td:.1f} days."))
                    print(_p(f"  A altitude atingiu ≤ 200 km; os resultados foram cortados na reentrada",
                             f"  Altitude reached ≤ 200 km; results were cut at reentry"))
                    print(_p(f"  (não nos {tempo:.0f} dias solicitados). Esta é a vida útil real da órbita.",
                             f"  (not at the {tempo:.0f} requested days). This is the real orbit lifetime."))
                    print(_p(f"  {'='*64}", f"  {'='*64}"))
                elif _parou_antes:
                    print(_p(f"\n  [NOTA] A simulação terminou em {_td:.2f} dias (de {tempo:.0f} pedidos); análise usa a duração real.",
                             f"\n  [NOTE] Simulation ended at {_td:.2f} days (of {tempo:.0f} requested); analysis uses the real duration."))
            dados_sol = analisar_luz_solar(caminho_eclipse_resultado.replace("/", os.sep), epoch_gregorian_str, _tempo_real)
            if dados_sol:
                print(_p("\nResultados de Luz Solar:", "\nSunlight Results:"))
                print(_p(f"  - Tempo Total:      {dados_sol['total_s']:.2f} s",
                         f"  - Total Time:       {dados_sol['total_s']:.2f} s"))
                print(_p(f"  - Menor Evento*:    {dados_sol['menor_evento_s']:.2f} s",
                         f"  - Shortest Event*:  {dados_sol['menor_evento_s']:.2f} s"))
                print(f"  - " + _p("Nº de Eventos", "No. of Events") + f":    {dados_sol['num_eventos']}")
                print(_p("  (*) Terceiro menor — descarta bordas da simulação.",
                         "  (*) Third shortest — discards simulation boundary periods."))
            else:
                print(_p("\nNão foi possível analisar os dados de luz solar.",
                         "\nCould not analyze sunlight data."))

            if dados_eclipse is None or dados_sol is None:
                print(_p("\nAVISO: Dados insuficientes. Análises de placa e bateria indisponíveis.",
                         "\nWARNING: Insufficient data. Solar panel and battery analyses unavailable."))
            else:
                while True:

# ---------------------------------------------- 7. PLACA SOLAR -----------------------------------------------------------

                    etapa_interface("3. Painéis solares")
                    placa_concluida = False
                    Placa = input_sn(_p("\nDeseja executar a análise de placa solar? (s/n): ",
                                        "\nRun solar panel analysis? (y/n): "))
                    if Placa == 's':
                        if not faces_ativas:
                            print(_p("  AVISO: Nenhuma face com células solares foi configurada. Análise não necessária",
                                     "  WARNING: No face with solar cells configured. Analysis not needed."))
                        else:
                            Tm  = input_float(_p("Tempo de missão [anos]: ", "Mission time [years]: "), min_val=0.0)
                            Eff = input_float(_p("Eficiência da célula (Eff) [0 a 1] (padrão 0,30): ",
                                                 "Cell efficiency (Eff) [0 to 1] (default 0.30): "), min_val=0.0, max_val=1.0, default=0.30)
                            Deg = input_float(_p("Degradação anual (Deg) [%/ano] (padrão 2,75): ",
                                                 "Annual degradation (Deg) [%/yr] (default 2.75): "), min_val=0.0, default=2.75) / 100
                            Id  = input_float(_p("Degradação inerente (Id) [0 a 1] (padrão 0,77): ",
                                                 "Inherent degradation (Id) [0 to 1] (default 0.77): "), min_val=0.0, max_val=1.0, default=0.77)
                            _origem_consumo = input_int(
                                _p("\nConsumo — informar Pe e Pd diretamente (1) ou montar por modos de operação (2): ",
                                   "\nLoad — enter Pe and Pd directly (1) or build from operating modes (2): "),
                                opcoes_validas=[1, 2])
                            _det_modos = None
                            if _origem_consumo == 1:
                                Pe  = input_float(_p("Potência máxima requerida durante o eclipse (Pe) [W]: ",
                                                     "Max power required during eclipse (Pe) [W]: "), min_val=0.0)
                                Pd  = input_float(_p("Potência máxima requerida durante o sol (Pd) [W]: ",
                                                     "Max power required in sunlight (Pd) [W]: "), min_val=0.0)
                            FoS = input_float(_p("Fator de segurança da placa [adm] — aplica (1+FS)·Psa (ex.: 0,2 = +20%) (padrão 0): ",
                                                 "Panel safety factor [adm] — applies (1+FS)·Psa (e.g. 0.2 = +20%) (default 0): "), min_val=0.0, default=0.0)
                            Ld  = (1 - Deg) ** Tm

                            X = input_int(
                                _p("\nArquitetura de potência — DET (1), PPT (2), Outra (3): ",
                                   "\nPower architecture — DET (1), PPT (2), Other (3): "),
                                opcoes_validas=[1, 2, 3]
                            )
                            if X == 1:
                                Xe, Xd = 0.65, 0.85
                            elif X == 2:
                                Xe, Xd = 0.60, 0.80
                            elif X == 3:
                                Xe = input_float(_p("Eficiência de descarga (Xe) [0 a 1]: ",
                                                    "Discharge efficiency (Xe) [0 to 1]: "), min_val=0.0, max_val=1.0)
                                Xd = input_float(_p("Eficiência de carga (Xd) [0 a 1]: ",
                                                    "Charge efficiency (Xd) [0 to 1]: "), min_val=0.0, max_val=1.0)

                            _fill_mode = input_int(
                                _p("\nFator de preenchimento — por área [0 a 1] (1) ou por face 1U em células (2): ",
                                   "\nFill factor — by area [0 to 1] (1) or by 1U face in cells (2): "),
                                opcoes_validas=[1, 2])
                            AREA_1U_M2 = 0.01
                            if _fill_mode == 2:
                                _n_cel = input_float(_p("  Células por face 1U (padrão 2): ",
                                                        "  Cells per 1U face (default 2): "), min_val=0.0, default=2.0)
                                _a_cel = input_float(_p("  Área de cada célula [cm²] (padrão 30,31): ",
                                                        "  Area of each cell [cm²] (default 30.31): "), min_val=0.0, default=30.31)
                                areas_celulas = {f: _n_cel * (_a_cel * 1e-4) * (areas[f] / AREA_1U_M2) for f in faces_ativas}
                                _fill_desc = _p(f"{_n_cel:g} célula(s)/1U × {_a_cel:g} cm², escalado por face",
                                                f"{_n_cel:g} cell(s)/1U × {_a_cel:g} cm², scaled per face")
                            else:
                                fill_factor_in = input_float(
                                    _p(f"Fator de preenchimento [0 a 1] (padrão {FILL_FACTOR:.4f}): ",
                                       f"Fill factor [0 to 1] (default {FILL_FACTOR:.4f}): "),
                                    min_val=0.0, max_val=1.0, default=FILL_FACTOR)
                                areas_celulas = {f: areas[f] * fill_factor_in for f in faces_ativas}
                                _fill_desc = _p(f"área de face × {fill_factor_in:.4f}",
                                                f"face area × {fill_factor_in:.4f}")

                            if _origem_consumo == 2:
                                etapa_interface("3b. Modos de operação")
                                _t_sol_tot = dados_sol['total_s']
                                _t_ecl_tot = dados_eclipse['total_s']
                                _t_cont    = dados_contato['total_s'] if dados_contato else 0.0
                                if _t_cont <= 0:
                                    print(_p("  (Sem dados de contato com estação terrena: o duty automático resultaria em 0.)",
                                             "  (No ground-station contact data: automatic duty would yield 0.)"))
                                _n_modos = input_int(_p("\nQuantos modos de operação? ",
                                                        "\nHow many operating modes? "), min_val=1)
                                _modos = []
                                for _i in range(_n_modos):
                                    print(_p(f"\n  -- Modo {_i+1} --", f"\n  -- Mode {_i+1} --"))
                                    _nome = input_texto(_p("   Nome: ", "   Name: "), default=f"Modo {_i+1}")
                                    _pw   = input_float(_p("   Potência [W]: ", "   Power [W]: "), min_val=0.0)
                                    _fase = FASES_MODO[input_int(
                                        _p("   Fase — sempre (1), só no Sol (2), só no eclipse (3): ",
                                           "   Phase — always (1), sunlight only (2), eclipse only (3): "),
                                        opcoes_validas=[1, 2, 3])]
                                    _auto = input_sn(_p("   Usar as janelas de contato para o duty? (s/n): ",
                                                        "   Use ground-station contact windows for the duty? (y/n): "))
                                    if _auto == 's':
                                        _duty = duty_por_contato(_fase, _t_sol_tot, _t_ecl_tot, _t_cont)
                                        print(_p(f"   -> duty = {_duty*100:.2f}% (das janelas de contato)",
                                                 f"   -> duty = {_duty*100:.2f}% (from contact windows)"))
                                    else:
                                        _duty = input_float(_p("   Duty [0 a 1]: ", "   Duty [0 to 1]: "),
                                                            min_val=0.0, max_val=1.0)
                                    _modos.append({"nome": _nome, "P_W": _pw, "fase": _fase,
                                                   "duty": _duty, "auto": _auto == 's'})
                                Pd, Pe, _det_modos = calcular_consumo_por_modos(_modos)
                                etapa_interface("3. Painéis solares")


                            Ld_eol = Ld
                            Ld_bol = 1.0
                            _perda_pct = (1.0 - Ld_eol) * 100.0

                            def _escalar_res_orbitas(res_list, fator):
                                return [
                                    {
                                        "duracao_s":   r["duracao_s"],
                                        "P_media":     r["P_media"] * fator,
                                        "P_por_face":  {f: v * fator for f, v in r["P_por_face"].items()},
                                        "n_timesteps": r["n_timesteps"],
                                    }
                                    for r in res_list
                                ]

                            def _computar_base():
                                res_pot = analisar_potencia_solar(
                                    caminho_report.replace("/", os.sep),
                                    faces_ativas, areas_celulas, Eff, Id, Ld_bol,
                                    dados_sol['tai_pior_start'], dados_sol['tai_pior_stop'],
                                )
                                if res_pot is None:
                                    return None
                                m = {
                                    "P_pior_bol":      res_pot['P_media_total'],
                                    "P_media_bol":     None,
                                    "pf_pior_bol":     res_pot['P_media_por_face'],
                                    "pf_media_bol":    None,
                                    "P_validos_bol":   None,
                                    "res_orbitas_bol": None,
                                    "n_excluidos":     0,
                                }
                                if dados_sol.get('periodos_tai'):
                                    res_orb = calcular_potencia_por_periodo(
                                        caminho_report.replace("/", os.sep),
                                        faces_ativas, areas_celulas, Eff, Id, Ld_bol,
                                        dados_sol['periodos_tai'],
                                    )
                                    if res_orb:
                                        n_per  = len(res_orb)
                                        D_vals = [r['duracao_s'] for r in res_orb]
                                        P_vals = [r['P_media']   for r in res_orb]
                                        _ordd  = sorted(range(n_per), key=lambda i: D_vals[i])
                                        _borda = set(_ordd[:2])
                                        _val   = [i for i in range(n_per) if i not in _borda]
                                        if _val:
                                            P_validos            = [P_vals[i] for i in _val]
                                            i_pior               = min(_val, key=lambda i: P_vals[i])
                                            m["P_pior_bol"]      = min(P_validos)
                                            m["P_media_bol"]     = sum(P_validos) / len(P_validos)
                                            m["pf_pior_bol"]     = res_orb[i_pior]["P_por_face"]
                                            m["pf_media_bol"]    = {f: sum(res_orb[i]["P_por_face"][f] for i in _val) / len(_val)
                                                                    for f in faces_ativas}
                                            m["P_validos_bol"]   = P_validos
                                            m["res_orbitas_bol"] = res_orb
                                            m["n_excluidos"]     = n_per - len(P_validos)
                                return m

                            var_std = _computar_base()

                            if var_std is None:
                                print(_p("  ERRO: Não foi possível ler o report do GMAT. Análise de placa abortada.",
                                         "  ERROR: Could not read GMAT report. Solar panel analysis aborted."))
                            else:
                                _Tmin = dados_sol['menor_evento_s']
                                if _Tmin <= 0:
                                    print(_p("  AVISO: período de sol zero, Psa não calculada.", "  WARNING: zero sunlight period, Psa not calculated."))
                                    Psa = 0.0
                                else:
                                    Psa = ((Pe * dados_eclipse['maior_evento_s']) / Xe
                                           + (Pd * _Tmin) / Xd) / _Tmin
                                Psa = Psa * (1 + FoS)

                                _face_hdr = _p("Face", "Face")
                                _fa_hdr   = _p("Área face (cm²)", "Face area (cm²)")
                                _ca_hdr   = _p("Área célula (cm²)", "Cell area (cm²)")
                                _pm_hdr   = _p("P_media (W)", "Avg_P (W)")
                                def _tabela_faces(titulo, p_por_face, total):
                                    print(titulo)
                                    print(f"  {_face_hdr:<6} {_fa_hdr:>16} {_ca_hdr:>18} {_pm_hdr:>12}")
                                    print("  " + "-" * 56)
                                    for _f in faces_ativas:
                                        print(f"  {_f:<6} {areas[_f]*1e4:>16.2f} {areas_celulas[_f]*1e4:>18.2f} {p_por_face[_f]:>12.4f}")
                                    print("  " + "-" * 56)
                                    print(f"  {'TOTAL':<6} {'':>16} {'':>18} {total:>12.4f}")

                                print(_p(f"\n  [NOTA] Área efetiva de células: {_fill_desc}",
                                         f"\n  [NOTE] Effective cell area: {_fill_desc}"))
                                print(_p(f"  [NOTA] Degradação em vida: Ld = (1-Deg)^Tm = (1-{Deg:.4f})^{Tm:g} = {Ld_eol:.4f}  (perda de {_perda_pct:.1f}% no EOL)",
                                         f"  [NOTE] Life degradation: Ld = (1-Deg)^Tm = (1-{Deg:.4f})^{Tm:g} = {Ld_eol:.4f}  ({_perda_pct:.1f}% loss at EOL)"))
                                print(_p(f"  [NOTA] Degradação inerente Id = {Id:.4f}",
                                         f"  [NOTE] Inherent degradation Id = {Id:.4f}"))
                                print(_p("         Fonte: SMAD. Refere-se ao fator de perda associado a temperatura de operação, fiação e montagem",
                                         "         Source: SMAD. Refers to the loss factor associated with operating temperature, wiring and assembly"))
                                if FoS != 0.0:
                                    print(_p(f"  [NOTA] A Psa inclui fator de segurança da placa de {FoS*100:.0f}%.",
                                             f"  [NOTE] Psa includes a {FoS*100:.0f}% panel safety factor."))
                                if var_std.get("n_excluidos"):
                                    print(_p(f"  ({var_std['n_excluidos']} períodos excluídos: primeiro e último evento, pois há possibilidade de serem cortados)",
                                             f"  ({var_std['n_excluidos']} periods excluded: first and last event, possibly truncated)"))

                                if _det_modos:
                                    print("\n  " + "=" * 70)
                                    print("  " + _p("ORÇAMENTO DE CONSUMO POR MODO DE OPERAÇÃO",
                                                    "LOAD BUDGET BY OPERATING MODE"))
                                    print("  " + "=" * 70)
                                    _fase_lbl = {"sempre":  _p("sempre",  "always"),
                                                 "sol":     _p("só sol",  "sun only"),
                                                 "eclipse": _p("só ecl.", "ecl. only")}
                                    print(f"  {_p('Modo', 'Mode'):<18}{'P (W)':>9}{_p('Fase', 'Phase'):>10}"
                                          f"{'Duty':>9}{_p('No Sol (W)', 'In sun (W)'):>12}{_p('No ecl (W)', 'In ecl (W)'):>12}")
                                    print("  " + "-" * 70)
                                    for _d in _det_modos:
                                        _duty_str = f"{_d['duty']*100:.1f}%" + ("*" if _d.get("auto") else "")
                                        print(f"  {_d['nome'][:18]:<18}{_d['P_W']:>9.4f}{_fase_lbl[_d['fase']]:>10}"
                                              f"{_duty_str:>9}{_d['c_sol']:>12.4f}{_d['c_ecl']:>12.4f}")
                                    print("  " + "-" * 70)
                                    print(f"  {'TOTAL':<18}{'':>9}{'':>10}{'':>9}{Pd:>12.4f}{Pe:>12.4f}")
                                    if any(_d.get("auto") for _d in _det_modos):
                                        print(_p("  (*) duty derivado das janelas de contato com a estação terrena.",
                                                 "  (*) duty derived from ground-station contact windows."))
                                    print(_p(f"  Pd (média no Sol) = {Pd:.4f} W   |   Pe (média no eclipse) = {Pe:.4f} W",
                                             f"  Pd (avg in sun) = {Pd:.4f} W   |   Pe (avg in eclipse) = {Pe:.4f} W"))
                                    print(_p("  Fonte: SMAD — Pd e Pe são as médias ponderadas pelo duty cycle de cada carga.",
                                             "  Source: SMAD — Pd and Pe are the duty-cycle-weighted averages of each load."))

                                def _cenario(rot_pt, rot_en, variante, fator):
                                    P_pior  = variante["P_pior_bol"] * fator
                                    P_media = None if variante["P_media_bol"] is None else variante["P_media_bol"] * fator
                                    margem  = ((P_pior - Psa) / Psa * 100.0) if Psa > 0 else None
                                    return {"rot_pt": rot_pt, "rot_en": rot_en, "variante": variante, "fator": fator,
                                            "P_pior": P_pior, "P_media": P_media, "margem": margem,
                                            "suficiente": P_pior >= Psa}

                                cenarios = [
                                    _cenario("BOL", "BOL", var_std, Ld_bol),
                                    _cenario("EOL", "EOL", var_std, Ld_eol),
                                ]

                                _crit = min(cenarios, key=lambda c: c["P_pior"])

                                if _crit["variante"]["res_orbitas_bol"] is not None:
                                    _res_crit = _escalar_res_orbitas(_crit["variante"]["res_orbitas_bol"], _crit["fator"])
                                    globals()["_res_orbitas_periodos"] = _res_crit
                                    if "telas_analises" in globals():
                                        globals()["telas_analises"]["res_orbitas"] = _res_crit

                                _fator_c = _crit["fator"]
                                print("\n  " + "=" * 64)
                                print("  " + _p(f"GERAÇÃO POR FACE — CENÁRIO CRÍTICO ({_crit['rot_pt']})",
                                                f"GENERATION PER FACE — CRITICAL SCENARIO ({_crit['rot_en']})"))
                                print("  " + "=" * 64)
                                if _crit["variante"]["pf_media_bol"] is not None:
                                    _tabela_faces(_p("\n  Geração no PIOR CASO por face:", "\n  WORST-CASE generation per face:"),
                                                  {f: v * _fator_c for f, v in _crit["variante"]["pf_pior_bol"].items()}, _crit["P_pior"])
                                    _tabela_faces(_p("\n  Geração MÉDIA por face:", "\n  AVERAGE generation per face:"),
                                                  {f: v * _fator_c for f, v in _crit["variante"]["pf_media_bol"].items()},
                                                  _crit["variante"]["P_media_bol"] * _fator_c)
                                else:
                                    _tabela_faces(_p("\n  Potência média no pior período de sol por face:",
                                                     "\n  Average power in worst sunlight period per face:"),
                                                  {f: v * _fator_c for f, v in _crit["variante"]["pf_pior_bol"].items()}, _crit["P_pior"])

                                print("\n  " + "=" * 64)
                                print("  " + _p("BALANÇO DE POTÊNCIA — COMPARAÇÃO DE CENÁRIOS",
                                                "POWER BUDGET — SCENARIO COMPARISON"))
                                print("  " + "=" * 64)
                                _c_h = _p("Cenário",   "Scenario")
                                _pp  = _p("Pior (W)",  "Worst (W)")
                                _md  = _p("Média (W)", "Avg (W)")
                                _ps  = "Psa (W)"
                                _mg  = _p("Margem",    "Margin")
                                _rs  = _p("Resultado", "Result")
                                print(f"  {_c_h:<13}{_pp:>10}{_md:>11}{_ps:>10}{_mg:>10}  {_rs}")
                                print("  " + "-" * 64)
                                for c in cenarios:
                                    _rot     = _p(c["rot_pt"], c["rot_en"])
                                    _md_str  = f"{c['P_media']:.4f}" if c["P_media"] is not None else "-"
                                    _mg_str  = f"{c['margem']:+.1f}%" if c["margem"] is not None else "-"
                                    _res_str = _p("SUFICIENTE", "SUFFICIENT") if c["suficiente"] else _p("INSUFICIENTE", "INSUFFICIENT")
                                    _mark    = (_p("  <- crítico", "  <- critical") if c is _crit else "")
                                    print(f"  {_rot:<13}{c['P_pior']:>10.4f}{_md_str:>11}{Psa:>10.4f}{_mg_str:>10}  {_res_str}{_mark}")
                                print("  " + "-" * 64)

                                if _crit["suficiente"]:
                                    print(_p(f"\n  RESULTADO: Geração SUFICIENTE mesmo no pior cenário ({_crit['rot_pt']}).",
                                             f"\n  RESULT: Generation SUFFICIENT even in the worst scenario ({_crit['rot_en']})."))
                                else:
                                    _defic = Psa - _crit["P_pior"]
                                    print(_p(f"\n  RESULTADO: Geração INSUFICIENTE no pior cenário ({_crit['rot_pt']}). Déficit de {_defic:.4f} W.",
                                             f"\n  RESULT: Generation INSUFFICIENT in the worst scenario ({_crit['rot_en']}). Deficit of {_defic:.4f} W."))
                                    print(_p("             Considere aumentar a área de painéis, reduzir o consumo ou alterar a órbita.",
                                             "             Consider increasing panel area, reducing consumption or changing orbit."))

                                _perda_deg = cenarios[0]["P_pior"] - cenarios[1]["P_pior"]
                                print(_p(f"  Perda por degradação em vida (pior caso): {_perda_deg:.4f} W ({_perda_pct:.1f}% em {Tm:g} anos)",
                                         f"  Life-degradation loss (worst case): {_perda_deg:.4f} W ({_perda_pct:.1f}% over {Tm:g} yr)"))
                                print(_p("\n  Observação: o dimensionamento deve atender ao CENÁRIO CRÍTICO destacado acima.",
                                         "\n  Note: sizing must satisfy the CRITICAL SCENARIO highlighted above."))
                                placa_concluida = True

# ---------------------------------------------- 8. BATERIA -----------------------------------------------------------

                    if placa_concluida:
                        etapa_interface("4. Baterias")
                        Bateria = input_sn(_p("\nDeseja executar a análise de bateria? (s/n): ",
                                              "\nRun battery analysis? (y/n): "))
                    else:
                        Bateria = 'n'
                        print(_p("\nAnálise de bateria indisponível: execute e conclua primeiro a análise de painéis solares.",
                                 "\nBattery analysis unavailable: complete solar panel analysis first."))
                    if Bateria == 's':
                        Fe  = dados_eclipse['num_eventos'] / tempo
                        Te  = dados_eclipse['maior_evento_s']
                        if 'Tm' not in globals():
                            Tm = input_float(_p("Tempo de missão [anos]: ", "Mission time [years]: "), min_val=0.0)
                        Cdc = Fe * Tm * 365.25

                        Dod      = input_float(_p("DoD (Depth of Discharge) [0.001 a 1]: ",
                                                  "DoD (Depth of Discharge) [0.001 to 1]: "), min_val=0.001, max_val=1.0)
                        tipo_bat = input_int(
                            _p("Tipo de bateria — NiCd (1), NiH2 (2), Li-ion (3), Outra (4): ",
                               "Battery type — NiCd (1), NiH2 (2), Li-ion (3), Other (4): "),
                            opcoes_validas=[1, 2, 3, 4]
                        )
                        if tipo_bat == 1:
                            densidade = 40.0
                        elif tipo_bat == 2:
                            densidade = 55.0
                        elif tipo_bat == 3:
                            densidade = 150.0
                        elif tipo_bat == 4:
                            densidade = input_float(_p("Densidade de energia [Wh/kg]: ",
                                                       "Energy density [Wh/kg]: "), min_val=0.001)

                        N = input_int(_p("Número de bancos de bateria independentes (N): ",
                                         "Number of independent battery banks (N): "), min_val=1)
                        n = input_float(_p("Eficiência de transmissão da bateria (n) [0.001 a 1]: ",
                                           "Battery transmission efficiency (n) [0.001 to 1]: "), min_val=0.001, max_val=1.0)
                        FoS_bat = input_float(_p("Fator de segurança da bateria [adm] — aplica (1+FS)·C (ex.: 0,2 = +20%) (padrão 0): ",
                                                 "Battery safety factor [adm] — applies (1+FS)·C (e.g. 0.2 = +20%) (default 0): "),
                                              min_val=0.0, default=0.0)

                        Ctotal = Pe * Te / (Dod * N * n * 3600) * (1 + FoS_bat)
                        Mbat   = Ctotal / densidade

                        print(_p(f"\n  Ciclos de carga/descarga durante a missão: {Cdc:.0f}",
                                 f"\n  Charge/discharge cycles during mission: {Cdc:.0f}"))
                        if FoS_bat != 0.0:
                            print(_p(f"  A capacidade inclui fator de segurança da bateria de {FoS_bat*100:.0f}%.",
                                     f"  The capacity includes a {FoS_bat*100:.0f}% battery safety factor."))
                        print(_p(f"  Capacidade total requerida: {Ctotal:.2f} Wh",
                                 f"  Total required capacity: {Ctotal:.2f} Wh"))
                        print(_p(f"  Massa da bateria estimada:  {Mbat:.4f} kg",
                                 f"  Estimated battery mass:  {Mbat:.4f} kg"))

# ---------------------------------------------- 9. RECÁLCULO -----------------------------------------------------------

                    if saida_interface is not None:
                        try:
                            print(_p("\nFluxo de análise concluído. Esta janela permanecerá aberta para consulta e você pode recalcular os dados de placa e bateria.",
                                     "\nAnalysis flow completed. This window will remain open for reference and you can recalculate panel and battery data."))
                            saida_interface["btn_recalcular"].config(state=tk.NORMAL)
                            saida_interface["janela"].wait_variable(saida_interface["acao_var"])
                            acao = saida_interface["acao_var"].get()
                            saida_interface["btn_recalcular"].config(state=tk.DISABLED)
                            if acao == "recalcular":
                                print("\n" + "=" * 70 + "\n")
                                print(_p("--- RECALCULANDO PLACA SOLAR E BATERIA ---", "--- RECALCULATING SOLAR PANEL AND BATTERY ---"))
                                print("\n" + "=" * 70 + "\n")
                                continue
                            else:
                                break
                        except tk.TclError:
                            break
                    else:
                        refazer = input_sn(_p("\nDeseja alterar os dados de placa/bateria e refazer a análise? (s/n): ",
                                              "\nDo you want to alter panel/battery data and redo the analysis? (y/n): "))
                        if refazer != 's':
                            break
                        print("\n" + "=" * 70 + "\n")

if saida_interface is not None:
    try:
        try:
            saida_interface["janela"].mainloop()
        except tk.TclError:
            pass
    except Exception:
        pass
