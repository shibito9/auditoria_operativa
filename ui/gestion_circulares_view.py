# -*- coding: utf-8 -*-
"""
Vista de Gestión de Circulares - Sistema de Auditoría Operativa
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path para imports absolutos
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional, Dict, Any, List
from datetime import date, datetime

from services.circulares_db_service import CircularesDbService


class GestionCircularesView(ctk.CTkToplevel):
    def __init__(self, parent_window):
        super().__init__()
        
        self.parent_window = parent_window
        self.title("Gestión de Circulares - Sistema de Auditoría Operativa")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Configuración de tema
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        
        # Variables de estado
        self.db_service = CircularesDbService()
        self.circulares: List[Dict[str, Any]] = []
        self.circular_seleccionada: Optional[Dict[str, Any]] = None
        
        # Configuración de la ventana
        self._setup_ui()
        self._cargar_circulares()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._create_header()
        
        # Panel de lista de circulares
        self._create_circulares_list_panel()
        
        # Panel de detalles de circular
        self._create_circular_details_panel()
        
        # Panel de botones de acción (siempre visible)
        self._create_action_buttons_panel()
    
    def _create_header(self):
        """Crea el encabezado de la ventana"""
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Gestión de Circulares",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Administrar circulares comerciales, reglas y exclusiones",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(side="left", padx=10, pady=10)
        
        # Botón nueva circular
        nueva_button = ctk.CTkButton(
            header_frame,
            text="+ Nueva Circular",
            width=150,
            fg_color="#107C10",
            hover_color="#0B5A0A",
            command=self._nueva_circular
        )
        nueva_button.pack(side="right", padx=10, pady=10)
        
        # Botón refrescar
        refrescar_button = ctk.CTkButton(
            header_frame,
            text="Refrescar",
            width=120,
            command=self._cargar_circulares
        )
        refrescar_button.pack(side="right", padx=10, pady=10)
        
        # Botón cerrar
        cerrar_button = ctk.CTkButton(
            header_frame,
            text="Cerrar",
            width=100,
            fg_color="#555555",
            hover_color="#444444",
            command=self._back_to_main
        )
        cerrar_button.pack(side="right", padx=10, pady=10)
    
    def _create_circulares_list_panel(self):
        """Crea el panel de lista de circulares"""
        list_frame = ctk.CTkFrame(self.main_frame)
        list_frame.pack(fill="x", pady=(0, 20))
        
        # Título
        list_title = ctk.CTkLabel(
            list_frame,
            text="Circulares Registradas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_title.pack(pady=10)
        
        # Scrollable frame para la lista con altura fija
        self.list_scroll = ctk.CTkScrollableFrame(list_frame, height=250)
        self.list_scroll.pack(fill="x", padx=10, pady=10)
    
    def _create_circular_details_panel(self):
        """Crea el panel de detalles de circular"""
        details_frame = ctk.CTkFrame(self.main_frame)
        details_frame.pack(fill="both", expand=True)
        
        # Título
        details_title = ctk.CTkLabel(
            details_frame,
            text="Detalles de Circular",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        details_title.pack(pady=10)
        
        # Notebook para tabs
        self.notebook = ctk.CTkTabview(details_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab de información general
        self.tab_info = self.notebook.add("Información General")
        self._create_info_tab()
        
        # Tab de reglas
        self.tab_reglas = self.notebook.add("Reglas")
        self._create_reglas_tab()
        
        # Tab de exclusiones
        self.tab_exclusiones = self.notebook.add("Exclusiones")
        self._create_exclusiones_tab()
    
    def _create_action_buttons_panel(self):
        """Crea el panel de botones de acción (siempre visible)"""
        buttons_frame = ctk.CTkFrame(self.main_frame, height=80)
        buttons_frame.pack(fill="x", pady=(20, 0))
        buttons_frame.pack_propagate(False)  # Mantener altura fija
        
        # Botón limpiar
        limpiar_button = ctk.CTkButton(
            buttons_frame,
            text="Limpiar Formulario",
            width=150,
            fg_color="#FF9900",
            hover_color="#E68A00",
            command=self._nueva_circular
        )
        limpiar_button.pack(side="left", padx=10, pady=10)
        
        # Botón guardar
        guardar_button = ctk.CTkButton(
            buttons_frame,
            text="Guardar/Actualizar",
            width=150,
            fg_color="#107C10",
            hover_color="#0B5A0A",
            command=self._guardar_circular
        )
        guardar_button.pack(side="left", padx=10, pady=10)
        
        # Botón eliminar
        eliminar_button = ctk.CTkButton(
            buttons_frame,
            text="Eliminar Circular",
            width=150,
            fg_color="#C50F1F",
            hover_color="#A00D1A",
            command=self._eliminar_circular
        )
        eliminar_button.pack(side="left", padx=10, pady=10)
    
    def _create_info_tab(self):
        """Crea el tab de información general"""
        info_frame = ctk.CTkFrame(self.tab_info)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Grid de campos
        self.codigo_var = ctk.StringVar()
        self.nombre_var = ctk.StringVar()
        self.fecha_inicio_var = ctk.StringVar()
        self.fecha_fin_var = ctk.StringVar()
        self.descuento_var = ctk.StringVar()
        self.activa_var = ctk.BooleanVar(value=True)
        self.observaciones_var = ctk.StringVar()
        
        # Código
        ctk.CTkLabel(info_frame, text="Código:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        codigo_entry = ctk.CTkEntry(info_frame, textvariable=self.codigo_var, width=200)
        codigo_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Nombre
        ctk.CTkLabel(info_frame, text="Nombre:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        nombre_entry = ctk.CTkEntry(info_frame, textvariable=self.nombre_var, width=400)
        nombre_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Fecha inicio
        ctk.CTkLabel(info_frame, text="Fecha Inicio:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        fecha_inicio_entry = ctk.CTkEntry(info_frame, textvariable=self.fecha_inicio_var, width=200)
        fecha_inicio_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Fecha fin
        ctk.CTkLabel(info_frame, text="Fecha Fin:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        fecha_fin_entry = ctk.CTkEntry(info_frame, textvariable=self.fecha_fin_var, width=200)
        fecha_fin_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Descuento
        ctk.CTkLabel(info_frame, text="Descuento %:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        descuento_entry = ctk.CTkEntry(info_frame, textvariable=self.descuento_var, width=200)
        descuento_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        # Activa
        ctk.CTkLabel(info_frame, text="Activa:").grid(row=5, column=0, padx=10, pady=10, sticky="e")
        activa_switch = ctk.CTkSwitch(info_frame, text="", variable=self.activa_var)
        activa_switch.grid(row=5, column=1, padx=10, pady=10, sticky="w")
        
        # Observaciones
        ctk.CTkLabel(info_frame, text="Observaciones:").grid(row=6, column=0, padx=10, pady=10, sticky="ne")
        observaciones_text = ctk.CTkTextbox(info_frame, width=400, height=100)
        observaciones_text.grid(row=6, column=1, padx=10, pady=10, sticky="w")
        self.observaciones_text = observaciones_text
    
    def _create_reglas_tab(self):
        """Crea el tab de reglas"""
        reglas_frame = ctk.CTkFrame(self.tab_reglas)
        reglas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botón agregar regla
        agregar_regla_button = ctk.CTkButton(
            reglas_frame,
            text="+ Agregar Regla",
            width=150,
            command=self._agregar_regla
        )
        agregar_regla_button.pack(pady=10)
        
        # Scrollable frame para lista de reglas
        self.reglas_scroll = ctk.CTkScrollableFrame(reglas_frame, height=400)
        self.reglas_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_exclusiones_tab(self):
        """Crea el tab de exclusiones"""
        exclusiones_frame = ctk.CTkFrame(self.tab_exclusiones)
        exclusiones_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botón agregar exclusión
        agregar_exclusion_button = ctk.CTkButton(
            exclusiones_frame,
            text="+ Agregar Exclusión",
            width=150,
            command=self._agregar_exclusion
        )
        agregar_exclusion_button.pack(pady=10)
        
        # Scrollable frame para lista de exclusiones
        self.exclusiones_scroll = ctk.CTkScrollableFrame(exclusiones_frame, height=400)
        self.exclusiones_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _cargar_circulares(self):
        """Carga la lista de circulares desde la base de datos"""
        try:
            self.circulares = self.db_service.obtener_todas_circulares()
            self._populate_circulares_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las circulares: {str(e)}")
    
    def _populate_circulares_list(self):
        """Pobla la lista de circulares"""
        # Limpiar contenido anterior
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        if not self.circulares:
            empty_label = ctk.CTkLabel(
                self.list_scroll,
                text="No hay circulares registradas",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
        
        # Crear encabezado
        header_frame = ctk.CTkFrame(self.list_scroll)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        headers = ["Código", "Nombre", "Fecha Inicio", "Fecha Fin", "Estado"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=11, weight="bold"),
                width=150,
                anchor="w"
            )
            label.grid(row=0, column=i, padx=5, pady=5)
        
        # Poblar filas
        for circular in self.circulares:
            row_frame = ctk.CTkFrame(self.list_scroll)
            row_frame.pack(fill="x", padx=5, pady=2)
            
            # Color según estado
            bg_color = "#C6EFCE" if circular["activa"] else "#F2F2F2"
            
            # Código
            ctk.CTkLabel(
                row_frame,
                text=circular["codigo"],
                width=150,
                anchor="w"
            ).grid(row=0, column=0, padx=5, pady=5)
            
            # Nombre
            ctk.CTkLabel(
                row_frame,
                text=circular["nombre"][:30] + "..." if len(circular["nombre"]) > 30 else circular["nombre"],
                width=150,
                anchor="w"
            ).grid(row=0, column=1, padx=5, pady=5)
            
            # Fecha inicio
            ctk.CTkLabel(
                row_frame,
                text=circular["fecha_inicio"],
                width=150,
                anchor="w"
            ).grid(row=0, column=2, padx=5, pady=5)
            
            # Fecha fin
            ctk.CTkLabel(
                row_frame,
                text=circular["fecha_fin"],
                width=150,
                anchor="w"
            ).grid(row=0, column=3, padx=5, pady=5)
            
            # Estado
            estado_label = ctk.CTkLabel(
                row_frame,
                text="Activa" if circular["activa"] else "Inactiva",
                width=150,
                anchor="w",
                fg_color=bg_color,
                corner_radius=4
            )
            estado_label.grid(row=0, column=4, padx=5, pady=5)
            
            # Botón seleccionar
            seleccionar_button = ctk.CTkButton(
                row_frame,
                text="Seleccionar",
                width=100,
                command=lambda c=circular: self._seleccionar_circular(c)
            )
            seleccionar_button.grid(row=0, column=5, padx=5, pady=5)
    
    def _seleccionar_circular(self, circular: Dict[str, Any]):
        """Selecciona una circular y muestra sus detalles"""
        self.circular_seleccionada = circular
        
        # Cargar datos en campos
        self.codigo_var.set(circular["codigo"])
        self.nombre_var.set(circular["nombre"])
        self.fecha_inicio_var.set(circular["fecha_inicio"])
        self.fecha_fin_var.set(circular["fecha_fin"])
        self.descuento_var.set(str(circular.get("descuento_porcentaje", "")))
        self.activa_var.set(circular["activa"])
        
        # Observaciones
        self.observaciones_text.delete("1.0", "end")
        self.observaciones_text.insert("1.0", circular.get("observaciones", ""))
        
        # Cargar reglas
        self._cargar_reglas(circular["id"])
        
        # Cargar exclusiones
        self._cargar_exclusiones(circular["id"])
    
    def _cargar_reglas(self, circular_id: int):
        """Carga las reglas de una circular"""
        try:
            reglas = self.db_service.obtener_reglas(circular_id)
            self._populate_reglas_list(reglas)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las reglas: {str(e)}")
    
    def _populate_reglas_list(self, reglas: List[Dict[str, Any]]):
        """Pobla la lista de reglas"""
        # Limpiar contenido anterior
        for widget in self.reglas_scroll.winfo_children():
            widget.destroy()
        
        if not reglas:
            empty_label = ctk.CTkLabel(
                self.reglas_scroll,
                text="No hay reglas registradas",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
        
        for regla in reglas:
            regla_frame = ctk.CTkFrame(self.reglas_scroll)
            regla_frame.pack(fill="x", padx=5, pady=2)
            
            # Categoría
            ctk.CTkLabel(
                regla_frame,
                text=f"Categoría: {regla['categoria']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w"
            ).pack(side="left", padx=10, pady=5)
            
            # Procedencia
            if regla.get("criterios_procedencia"):
                ctk.CTkLabel(
                    regla_frame,
                    text=f"Procedencia: {', '.join(regla['criterios_procedencia'])}",
                    anchor="w"
                ).pack(side="left", padx=10, pady=5)
            
            # Descuento
            if regla.get("descuento_porcentaje"):
                ctk.CTkLabel(
                    regla_frame,
                    text=f"Descuento: {regla['descuento_porcentaje']}%",
                    anchor="w"
                ).pack(side="left", padx=10, pady=5)
            
            # Botón eliminar
            eliminar_button = ctk.CTkButton(
                regla_frame,
                text="Eliminar",
                width=80,
                fg_color="#C50F1F",
                hover_color="#A00D1A",
                command=lambda r=regla: self._eliminar_regla(r["id"])
            )
            eliminar_button.pack(side="right", padx=5, pady=5)
    
    def _cargar_exclusiones(self, circular_id: int):
        """Carga las exclusiones de una circular"""
        try:
            exclusiones = self.db_service.obtener_exclusiones(circular_id)
            self._populate_exclusiones_list(exclusiones)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las exclusiones: {str(e)}")
    
    def _populate_exclusiones_list(self, exclusiones: List[Dict[str, Any]]):
        """Pobla la lista de exclusiones"""
        # Limpiar contenido anterior
        for widget in self.exclusiones_scroll.winfo_children():
            widget.destroy()
        
        if not exclusiones:
            empty_label = ctk.CTkLabel(
                self.exclusiones_scroll,
                text="No hay exclusiones registradas",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
        
        for exclusion in exclusiones:
            exclusion_frame = ctk.CTkFrame(self.exclusiones_scroll)
            exclusion_frame.pack(fill="x", padx=5, pady=2)
            
            # Patrón
            ctk.CTkLabel(
                exclusion_frame,
                text=f"Patrón: {exclusion['patron']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w"
            ).pack(side="left", padx=10, pady=5)
            
            # Tipo
            ctk.CTkLabel(
                exclusion_frame,
                text=f"Tipo: {exclusion['tipo']}",
                anchor="w"
            ).pack(side="left", padx=10, pady=5)
            
            # Botón eliminar
            eliminar_button = ctk.CTkButton(
                exclusion_frame,
                text="Eliminar",
                width=80,
                fg_color="#C50F1F",
                hover_color="#A00D1A",
                command=lambda e=exclusion: self._eliminar_exclusion(e["id"])
            )
            eliminar_button.pack(side="right", padx=5, pady=5)
    
    def _nueva_circular(self):
        """Prepara el formulario para una nueva circular"""
        self.circular_seleccionada = None
        
        # Limpiar campos
        self.codigo_var.set("")
        self.nombre_var.set("")
        self.fecha_inicio_var.set("")
        self.fecha_fin_var.set("")
        self.descuento_var.set("")
        self.activa_var.set(True)
        self.observaciones_text.delete("1.0", "end")
        
        # Limpiar listas
        for widget in self.reglas_scroll.winfo_children():
            widget.destroy()
        for widget in self.exclusiones_scroll.winfo_children():
            widget.destroy()
    
    def _guardar_circular(self):
        """Guarda los cambios de la circular"""
        try:
            # Validar campos requeridos
            codigo = self.codigo_var.get().strip()
            nombre = self.nombre_var.get().strip()
            fecha_inicio = self.fecha_inicio_var.get().strip()
            fecha_fin = self.fecha_fin_var.get().strip()
            
            if not codigo or not nombre or not fecha_inicio or not fecha_fin:
                messagebox.showerror("Error", "Los campos Código, Nombre, Fecha Inicio y Fecha Fin son obligatorios")
                return
            
            # Preparar datos
            circular_data = {
                "codigo": codigo,
                "nombre": nombre,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "descuento_porcentaje": float(self.descuento_var.get()) if self.descuento_var.get() else None,
                "activa": self.activa_var.get(),
                "observaciones": self.observaciones_text.get("1.0", "end").strip()
            }
            
            if self.circular_seleccionada:
                # Actualizar circular existente
                self.db_service.actualizar_circular(self.circular_seleccionada["id"], circular_data)
                messagebox.showinfo("Éxito", "Circular actualizada correctamente")
            else:
                # Crear nueva circular
                self.db_service.crear_circular(circular_data)
                messagebox.showinfo("Éxito", "Circular creada correctamente")
            
            # Recargar lista
            self._cargar_circulares()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la circular: {str(e)}")
    
    def _eliminar_circular(self):
        """Elimina la circular seleccionada"""
        if not self.circular_seleccionada:
            messagebox.showwarning("Advertencia", "No hay ninguna circular seleccionada")
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la circular {self.circular_seleccionada['codigo']}?\n\n"
            "Esta acción también eliminará todas sus reglas y exclusiones."
        )
        
        if respuesta:
            try:
                self.db_service.eliminar_circular(self.circular_seleccionada["id"])
                messagebox.showinfo("Éxito", "Circular eliminada correctamente")
                self._cargar_circulares()
                self._nueva_circular()  # Limpiar formulario
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la circular: {str(e)}")
    
    def _agregar_regla(self):
        """Abre un diálogo para agregar una nueva regla"""
        if not self.circular_seleccionada:
            messagebox.showwarning("Advertencia", "Debe seleccionar una circular primero")
            return
        
        # Crear diálogo simple para agregar regla
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Regla")
        dialog.geometry("500x400")
        
        # Campos
        categoria_var = ctk.StringVar()
        procedencia_var = ctk.StringVar()
        descuento_var = ctk.StringVar()
        
        ctk.CTkLabel(dialog, text="Categoría:").pack(pady=5)
        ctk.CTkEntry(dialog, textvariable=categoria_var, width=300).pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Procedencia (separada por comas):").pack(pady=5)
        ctk.CTkEntry(dialog, textvariable=procedencia_var, width=300).pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Descuento %:").pack(pady=5)
        ctk.CTkEntry(dialog, textvariable=descuento_var, width=300).pack(pady=5)
        
        def guardar():
            try:
                categoria = categoria_var.get().strip()
                if not categoria:
                    messagebox.showerror("Error", "La categoría es obligatoria")
                    return
                
                procedencia_list = [p.strip() for p in procedencia_var.get().split(",") if p.strip()]
                descuento = float(descuento_var.get()) if descuento_var.get() else None
                
                regla_data = {
                    "categoria": categoria,
                    "criterios_procedencia": procedencia_list,
                    "descuento_porcentaje": descuento
                }
                
                self.db_service.agregar_regla(self.circular_seleccionada["id"], regla_data)
                self._cargar_reglas(self.circular_seleccionada["id"])
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar la regla: {str(e)}")
        
        ctk.CTkButton(dialog, text="Guardar", command=guardar).pack(pady=20)
    
    def _eliminar_regla(self, regla_id: int):
        """Elimina una regla"""
        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta regla?")
        if respuesta:
            try:
                self.db_service.eliminar_regla(regla_id)
                if self.circular_seleccionada:
                    self._cargar_reglas(self.circular_seleccionada["id"])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la regla: {str(e)}")
    
    def _agregar_exclusion(self):
        """Abre un diálogo para agregar una nueva exclusión"""
        if not self.circular_seleccionada:
            messagebox.showwarning("Advertencia", "Debe seleccionar una circular primero")
            return
        
        # Crear diálogo simple para agregar exclusión
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Exclusión")
        dialog.geometry("400x200")
        
        patron_var = ctk.StringVar()
        
        ctk.CTkLabel(dialog, text="Patrón de exclusión:").pack(pady=5)
        ctk.CTkEntry(dialog, textvariable=patron_var, width=300).pack(pady=5)
        
        def guardar():
            try:
                patron = patron_var.get().strip()
                if not patron:
                    messagebox.showerror("Error", "El patrón es obligatorio")
                    return
                
                self.db_service.agregar_exclusion(self.circular_seleccionada["id"], patron, "descripcion")
                self._cargar_exclusiones(self.circular_seleccionada["id"])
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar la exclusión: {str(e)}")
        
        ctk.CTkButton(dialog, text="Guardar", command=guardar).pack(pady=20)
    
    def _eliminar_exclusion(self, exclusion_id: int):
        """Elimina una exclusión"""
        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta exclusión?")
        if respuesta:
            try:
                self.db_service.eliminar_exclusion(exclusion_id)
                if self.circular_seleccionada:
                    self._cargar_exclusiones(self.circular_seleccionada["id"])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la exclusión: {str(e)}")
    
    def _back_to_main(self):
        """Vuelve a la ventana principal"""
        self.destroy()
        if self.parent_window:
            self.parent_window.deiconify()
