# -*- coding: utf-8 -*-
"""
Vista de Auditoría Facturas - Sistema de Auditoría Operativa
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path para imports absolutos
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional, Dict, Any
import pandas as pd


class FacturasView(ctk.CTkToplevel):
    def __init__(self, parent_window):
        super().__init__()
        
        self.parent_window = parent_window
        self.title("Auditoría Facturas - Sistema de Auditoría Operativa")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Configuración de tema
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Variables de estado
        self.excel_path: Optional[Path] = None
        self.df_facturas: Optional[pd.DataFrame] = None
        self.facturas_procesadas: Dict[str, Any] = {}
        
        # Configuración de la ventana
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._create_header()
        
        # Panel de selección de archivo
        self._create_file_selection_panel()
        
        # Panel resumen
        self._create_summary_panel()
        
        # Tabla de resultados
        self._create_results_table()
        
        # Botones de acción
        self._create_action_buttons()
    
    def _create_header(self):
        """Crea el encabezado de la ventana"""
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Auditoría de Facturas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Validación de facturas con agrupación por Secuencia Factura",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(side="left", padx=10, pady=10)
    
    def _create_file_selection_panel(self):
        """Crea el panel de selección de archivo Excel"""
        file_frame = ctk.CTkFrame(self.main_frame)
        file_frame.pack(fill="x", pady=(0, 20))
        
        # Label
        file_label = ctk.CTkLabel(
            file_frame,
            text="Archivo Excel de Facturas:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        file_label.pack(side="left", padx=10, pady=10)
        
        # Entry para mostrar la ruta
        self.file_path_var = ctk.StringVar()
        file_entry = ctk.CTkEntry(
            file_frame,
            textvariable=self.file_path_var,
            width=400,
            font=ctk.CTkFont(size=12)
        )
        file_entry.pack(side="left", padx=10, pady=10)
        
        # Botón de búsqueda
        browse_button = ctk.CTkButton(
            file_frame,
            text="Buscar Excel",
            width=120,
            command=self._browse_excel
        )
        browse_button.pack(side="left", padx=10, pady=10)
        
        # Botón de carga
        load_button = ctk.CTkButton(
            file_frame,
            text="Cargar y Validar",
            width=140,
            fg_color="#107C10",
            hover_color="#0B5A0A",
            command=self._load_and_validate_excel
        )
        load_button.pack(side="left", padx=10, pady=10)
    
    def _create_summary_panel(self):
        """Crea el panel resumen con estadísticas"""
        summary_frame = ctk.CTkFrame(self.main_frame)
        summary_frame.pack(fill="x", pady=(0, 20))
        
        # Título del panel
        summary_title = ctk.CTkLabel(
            summary_frame,
            text="Resumen de Auditoría",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        summary_title.pack(pady=10)
        
        # Frame de métricas
        metrics_frame = ctk.CTkFrame(summary_frame)
        metrics_frame.pack(fill="x", padx=10, pady=10)
        
        # Métricas
        self._create_metric_card(
            metrics_frame, 
            "Total Facturas", 
            "0", 
            "total_facturas",
            "#1F4E78"
        )
        
        self._create_metric_card(
            metrics_frame, 
            "Correctas", 
            "0", 
            "correctas",
            "#107C10"
        )
        
        self._create_metric_card(
            metrics_frame, 
            "Errores", 
            "0", 
            "errores",
            "#C50F1F"
        )
        
        self._create_metric_card(
            metrics_frame, 
            "Revisión Manual", 
            "0", 
            "revision_manual",
            "#9A6700"
        )
        
        self._create_metric_card(
            metrics_frame, 
            "Excluidas", 
            "0", 
            "excluidas",
            "#555555"
        )
    
    def _create_metric_card(self, parent: ctk.CTkFrame, title: str, value: str, 
                           var_name: str, color: str):
        """Crea una tarjeta de métrica individual"""
        card_frame = ctk.CTkFrame(parent, fg_color=color)
        card_frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        
        label_title = ctk.CTkLabel(
            card_frame,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white"
        )
        label_title.pack(pady=5)
        
        # Variable para el valor
        setattr(self, f"{var_name}_var", ctk.StringVar(value=value))
        
        label_value = ctk.CTkLabel(
            card_frame,
            textvariable=getattr(self, f"{var_name}_var"),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        label_value.pack(pady=5)
    
    def _create_results_table(self):
        """Crea la tabla de resultados"""
        table_frame = ctk.CTkFrame(self.main_frame)
        table_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Título
        table_title = ctk.CTkLabel(
            table_frame,
            text="Resultados de Auditoría por Factura",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        table_title.pack(pady=10)
        
        # Scrollable frame para la tabla
        self.table_scroll = ctk.CTkScrollableFrame(table_frame, height=400)
        self.table_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Mensaje inicial
        self.empty_message = ctk.CTkLabel(
            self.table_scroll,
            text="Carga un archivo Excel para ver los resultados de auditoría",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.empty_message.pack(pady=50)
    
    def _create_action_buttons(self):
        """Crea los botones de acción"""
        buttons_frame = ctk.CTkFrame(self.main_frame)
        buttons_frame.pack(fill="x", pady=(0, 10))
        
        # Botón exportar
        export_button = ctk.CTkButton(
            buttons_frame,
            text="Exportar Resultados",
            width=150,
            command=self._export_results
        )
        export_button.pack(side="right", padx=10, pady=10)
        
        # Botón volver
        back_button = ctk.CTkButton(
            buttons_frame,
            text="Volver al Menú Principal",
            width=180,
            fg_color="#555555",
            hover_color="#444444",
            command=self._back_to_main
        )
        back_button.pack(side="right", padx=10, pady=10)
    
    def _browse_excel(self):
        """Abre el diálogo para seleccionar archivo Excel"""
        file_path = filedialog.askopenfilename(
            title="Selecciona el archivo Excel de Facturas",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.excel_path = Path(file_path)
            self.file_path_var.set(str(self.excel_path))
    
    def _load_and_validate_excel(self):
        """Carga y valida el archivo Excel"""
        if not self.excel_path or not self.excel_path.exists():
            messagebox.showerror(
                "Error",
                "Por favor selecciona un archivo Excel válido."
            )
            return
        
        try:
            # Cargar el Excel con pandas
            self.df_facturas = pd.read_excel(self.excel_path)
            
            # Validar columnas requeridas
            self._validate_required_columns()
            
            # Procesar facturas (agrupación por Secuencia Factura)
            self._process_facturas()
            
            # Actualizar interfaz
            self._update_summary()
            self._populate_results_table()
            
            messagebox.showinfo(
                "Éxito",
                f"Archivo cargado correctamente.\nTotal de filas: {len(self.df_facturas)}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error al cargar Excel",
                f"No se pudo cargar el archivo: {str(e)}"
            )
    
    def _validate_required_columns(self):
        """Valida que el Excel tenga las columnas requeridas con alias de encabezado"""
        # Definir columnas requeridas con sus alias permitidos
        required_columns_with_aliases = {
            "Secuencia Factura": ["Secuencia Factura", "Numero Factura", "Número Factura"],
            "Fecha Factura": ["Fecha Factura", "Fecha", "Fecha Factura"],
            "Factura Gramos": ["Factura Gramos", "Gramos Factura", "Peso Factura"],
            "Subtotal": ["Subtotal", "Sub Total"],
            "Descuento": ["Descuento", "Descuentos"],
            "Valor Total": ["Valor Total", "Total", "Valor Total"],
            "Producto Categoria": ["Producto Categoria", "Categoría Producto", "Categoria"],
            "Producto Sku": ["Producto Sku", "SKU", "Sku"],
            "Producto Gramos": ["Producto Gramos", "Gramos Producto", "Peso Producto"],
            "Producto Descripcion": ["Producto Descripcion", "Descripción Producto", "Descripcion"],
            "Linea Nombre": ["Linea Nombre", "Línea", "Linea"],
        }
        
        # Mapeo de columnas encontradas en el Excel
        self.column_mapping = {}
        missing_columns = []
        
        for main_col, aliases in required_columns_with_aliases.items():
            found = False
            for df_col in self.df_facturas.columns:
                # Buscar coincidencia con cualquier alias (case-insensitive)
                for alias in aliases:
                    if alias.lower() in str(df_col).lower():
                        self.column_mapping[main_col] = df_col
                        found = True
                        break
                if found:
                    break
            
            if not found:
                missing_columns.append(f"{main_col} (alias: {', '.join(aliases)})")
        
        if missing_columns:
            raise ValueError(
                f"Faltan columnas requeridas en el Excel:\n{chr(10).join(missing_columns)}"
            )
        
        # Definir columna identificadora principal de factura
        self.factura_id_column = self.column_mapping["Secuencia Factura"]
    
    def _process_facturas(self):
        """Procesa las facturas agrupando por Secuencia Factura"""
        # Esta función se implementará con el servicio de parser
        # Por ahora, solo contamos las filas
        self.facturas_procesadas = {
            "total_filas": len(self.df_facturas),
            "total_facturas": 0,  # Se calculará después de agrupar
            "correctas": 0,
            "errores": 0,
            "revision_manual": 0,
            "excluidas": 0,
        }
        
        # Placeholder: actualizar métricas temporales
        self.total_facturas_var.set(str(len(self.df_facturas)))
    
    def _update_summary(self):
        """Actualiza el panel resumen con las estadísticas"""
        # Esta función se actualizará cuando se implemente el servicio de auditor
        pass
    
    def _populate_results_table(self):
        """Pobla la tabla de resultados con las facturas procesadas"""
        # Limpiar mensaje vacío
        if hasattr(self, 'empty_message'):
            self.empty_message.destroy()
        
        # Esta función se implementará cuando se procesen las facturas
        placeholder_label = ctk.CTkLabel(
            self.table_scroll,
            text="La tabla se poblará con los resultados de auditoría",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        placeholder_label.pack(pady=50)
    
    def _export_results(self):
        """Exporta los resultados a un archivo Excel"""
        messagebox.showinfo(
            "En desarrollo",
            "La función de exportación está en desarrollo."
        )
    
    def _back_to_main(self):
        """Vuelve a la ventana principal"""
        self.destroy()
        if self.parent_window:
            self.parent_window.deiconify()
