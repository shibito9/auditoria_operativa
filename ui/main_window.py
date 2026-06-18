# -*- coding: utf-8 -*-
"""
Ventana Principal - Sistema de Auditoría Operativa
"""
import sys
import subprocess
from pathlib import Path

# Agregar directorio raíz al path para imports absolutos
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("Sistema de Auditoría Operativa")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Configuración de tema
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Sistema de Auditoría Operativa",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack(pady=(40, 60))
        
        # Subtítulo
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Selecciona el módulo de auditoría que deseas ejecutar",
            font=ctk.CTkFont(size=14)
        )
        self.subtitle_label.pack(pady=(0, 40))
        
        # Frame de botones
        self.buttons_frame = ctk.CTkFrame(self.main_frame)
        self.buttons_frame.pack(fill="x", pady=20)
        
        # Botones de navegación
        self._create_navigation_buttons()
        
        # Footer
        self.footer_label = ctk.CTkLabel(
            self.main_frame,
            text="Desarrollado por SANTIAGO AGUDELO - GAMAN -",
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color="gray"
        )
        self.footer_label.pack(side="bottom", pady=20)
        
        # Referencia a la ventana actual
        self.current_window: Optional[ctk.CTkToplevel] = None
    
    def _create_navigation_buttons(self):
        """Crea los botones de navegación principales"""
        
        # Botón Auditoría Caja Fuerte
        self.btn_caja_fuerte = ctk.CTkButton(
            self.buttons_frame,
            text="Auditoría Caja Fuerte",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=60,
            command=self._open_caja_fuerte
        )
        self.btn_caja_fuerte.pack(fill="x", pady=10, padx=100)
        
        # Botón Auditoría Facturas
        self.btn_facturas = ctk.CTkButton(
            self.buttons_frame,
            text="Auditoría Facturas",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=60,
            command=self._open_facturas
        )
        self.btn_facturas.pack(fill="x", pady=10, padx=100)
        
        # Botón Configuración de Reglas
        self.btn_config = ctk.CTkButton(
            self.buttons_frame,
            text="Configuración de Reglas",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=60,
            command=self._open_config
        )
        self.btn_config.pack(fill="x", pady=10, padx=100)
        
        # Botón Salir
        self.btn_salir = ctk.CTkButton(
            self.buttons_frame,
            text="Salir",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=60,
            fg_color="#C50F1F",
            hover_color="#A00D18",
            command=self._exit_app
        )
        self.btn_salir.pack(fill="x", pady=(30, 10), padx=100)
    
    def _open_caja_fuerte(self):
        """Abre el módulo de Auditoría Caja Fuerte como proceso independiente"""
        try:
            # Resolver ruta absoluta de gui.py desde la raíz del proyecto
            gui_path = ROOT_DIR / "gui.py"
            
            if not gui_path.exists():
                messagebox.showerror(
                    "Error",
                    f"No se encontró el archivo gui.py en: {gui_path}"
                )
                return
            
            # Lanzar gui.py como proceso independiente usando subprocess
            subprocess.Popen(
                [sys.executable, str(gui_path)],
                cwd=str(ROOT_DIR)
            )
            
            # Mostrar mensaje informativo
            messagebox.showinfo(
                "Módulo Caja Fuerte",
                "El módulo de Auditoría Caja Fuerte se ha abierto en una ventana independiente.\n"
                "La ventana principal permanecerá abierta como menú lanzador."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo lanzar el módulo de Caja Fuerte: {e}"
            )
    
    def _open_facturas(self):
        """Abre el módulo de Auditoría Facturas"""
        try:
            from ui.facturas_view import FacturasView
            self.withdraw()  # Ocultar ventana principal
            self.current_window = FacturasView(self)
            self.current_window.mainloop()
            self.deiconify()  # Mostrar ventana principal al cerrar
        except ImportError as e:
            messagebox.showerror(
                "Error",
                f"No se pudo cargar el módulo de Facturas: {e}"
            )
    
    def _open_config(self):
        """Abre el módulo de Gestión de Circulares"""
        try:
            from ui.gestion_circulares_view import GestionCircularesView
            self.withdraw()  # Ocultar ventana principal
            self.current_window = GestionCircularesView(self)
            self.current_window.mainloop()
            self.deiconify()  # Mostrar ventana principal al cerrar
        except ImportError as e:
            messagebox.showerror(
                "Error",
                f"No se pudo cargar el módulo de Gestión de Circulares: {e}"
            )
    
    def _exit_app(self):
        """Cierra la aplicación"""
        self.quit()
        self.destroy()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
