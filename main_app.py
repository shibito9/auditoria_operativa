# -*- coding: utf-8 -*-
"""
Punto de entrada principal - Sistema de Auditoría Operativa
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports absolutos
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

import customtkinter as ctk

from ui.main_window import MainWindow


def main():
    """Función principal de la aplicación"""
    # Configuración de tema
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    # Crear y ejecutar la ventana principal
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
