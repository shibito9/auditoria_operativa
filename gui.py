# -*- coding: utf-8 -*-
"""
GUI para auditoría de contratos en caja fuerte - GAMAN V7.

Ejecutar:
    py gui.py

Requiere:
    pip install openpyxl
"""

from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from caja_fuerte_backend import (
    CajaFuerteBackend,
    MODO_PARCIAL,
    MODO_TOTAL,
    PESO_BOLSA_SEGURIDAD_GR,
    PESO_TOLERANCIA_GR,
    get_default_output_dir,
    get_last_run_date,
    get_last_run_text,
    parse_user_date,
)



APP_VERSION = "V7"
DEVELOPER_SIGNATURE = "Desarrollado por SANTIAGO AGUDELO - GAMAN -"

NOVEDADES = [
    "OK",
    "DIFERENCIA_PESO_TOTAL",
    "DIFERENCIA_CANTIDAD",
    "BOLSA_ILEGIBLE",
    "BOLSA_ROTA",
    "BOLSA_SIN_ETIQUETA",
    "BOLSA_NO_COINCIDE",
    "BOLSA_MANIPULADA",
    "INFORMACION_NO_COINCIDE",
    "CONTRATO_DETERIORADO",
    "DOCUMENTO_ILEGIBLE",
    "CODIGO_BARRAS_NO_LEE",
    "OTRA",
]


class AuditoriaCajaFuerteGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GAMAN - Auditoría de Caja Fuerte")
        self.geometry("1280x820")
        self.minsize(1180, 740)

        self.backend = CajaFuerteBackend()
        self.current_contract = None
        self.current_raw = ""
        self.last_loaded_record = None
        self.auto_after_id = None
        self.last_processed_raw = ""

        self._configure_style()
        self._bind_global_shortcuts()
        self._build_start_view()

    # =====================================================
    # ESTILO
    # =====================================================
    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 19, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("KPI.TLabel", font=("Segoe UI", 12, "bold"), padding=6)
        style.configure("StatusOk.TLabel", foreground="#107C10", font=("Segoe UI", 12, "bold"))
        style.configure("StatusWarn.TLabel", foreground="#9A6700", font=("Segoe UI", 12, "bold"))
        style.configure("StatusError.TLabel", foreground="#C50F1F", font=("Segoe UI", 12, "bold"))
        style.configure("Big.TButton", font=("Segoe UI", 11, "bold"), padding=8)
        style.configure("InfoName.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("InfoValue.TLabel", font=("Segoe UI", 12))
        style.configure("ImportantValue.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Signature.TLabel", font=("Segoe UI", 9, "italic"), foreground="#555555")

    def _bind_global_shortcuts(self):
        self.bind("<F1>", lambda event: self._mark_ok())
        self.bind("<F2>", lambda event: self._mark_novedad())
        self.bind("<F3>", lambda event: self._clear_current())
        self.bind("<F4>", lambda event: self._repeat_last_contract())
        self.bind("<Escape>", lambda event: self._clear_current())

    def _clear_root(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _add_signature_footer(self, parent):
        footer = ttk.Frame(parent)
        footer.pack(fill="x", side="bottom", pady=(10, 0))
        ttk.Label(footer, text=f"{DEVELOPER_SIGNATURE}  |  {APP_VERSION}", style="Signature.TLabel").pack(side="right")

    def _add_signature_footer_grid(self, parent, row: int):
        footer = ttk.Frame(parent)
        footer.grid(row=row, column=0, sticky="ew", pady=(6, 0))
        ttk.Label(footer, text=f"{DEVELOPER_SIGNATURE}  |  {APP_VERSION}", style="Signature.TLabel").pack(side="right")


    # =====================================================
    # VISTA INICIAL
    # =====================================================
    def _build_start_view(self):
        self._clear_root()
        self.current_contract = None
        self.current_raw = ""
        self.last_loaded_record = None

        container = ttk.Frame(self, padding=24)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Auditoría de contratos en caja fuerte", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            container,
            text="Carga el reporte Excel, define el alcance y trabaja con pistola de códigos sin manipular manualmente el archivo.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 18))

        form = ttk.Frame(container)
        form.pack(fill="x", pady=10)
        form.columnconfigure(1, weight=1)

        self.excel_var = tk.StringVar()
        ttk.Label(form, text="Archivo Excel:").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.excel_var).grid(row=0, column=1, sticky="ew", padx=8, pady=6)
        ttk.Button(form, text="Buscar...", command=self._browse_excel).grid(row=0, column=2, pady=6)

        self.output_dir_var = tk.StringVar(value=get_default_output_dir())
        ttk.Label(form, text="Carpeta resultados:").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.output_dir_var).grid(row=1, column=1, sticky="ew", padx=8, pady=6)
        ttk.Button(form, text="Cambiar...", command=self._browse_output_dir).grid(row=1, column=2, pady=6)

        self.mode_var = tk.StringVar(value=MODO_PARCIAL)
        ttk.Label(form, text="Tipo de auditoría:").grid(row=2, column=0, sticky="w", pady=6)
        mode_frame = ttk.Frame(form)
        mode_frame.grid(row=2, column=1, sticky="w", padx=8, pady=6)
        ttk.Radiobutton(mode_frame, text="Parcial", value=MODO_PARCIAL, variable=self.mode_var, command=self._on_mode_change).pack(side="left", padx=(0, 12))
        ttk.Radiobutton(mode_frame, text="Total", value=MODO_TOTAL, variable=self.mode_var, command=self._on_mode_change).pack(side="left")

        last_run = get_last_run_text()
        last_date = get_last_run_date()
        default_fecha = last_date.strftime("%d/%m/%Y") if last_date else ""
        self.fecha_desde_var = tk.StringVar(value=default_fecha)
        ttk.Label(form, text="Fecha desde:").grid(row=3, column=0, sticky="w", pady=6)
        self.fecha_entry = ttk.Entry(form, textvariable=self.fecha_desde_var, width=18)
        self.fecha_entry.grid(row=3, column=1, sticky="w", padx=8, pady=6)
        ttk.Label(form, text="Formato: dd/mm/aaaa. En parcial se audita desde esta fecha hasta hoy.").grid(row=3, column=1, sticky="w", padx=(160, 8))

        ttk.Label(form, text="Última ejecución:").grid(row=4, column=0, sticky="w", pady=6)
        ttk.Label(form, text=last_run or "Sin registro anterior").grid(row=4, column=1, sticky="w", padx=8, pady=6)

        self.usuario_var = tk.StringVar(value=os.environ.get("USERNAME") or "AUDITOR")
        ttk.Label(form, text="Auditor/usuario:").grid(row=5, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.usuario_var, width=30).grid(row=5, column=1, sticky="w", padx=8, pady=6)

        info = ttk.LabelFrame(container, text="Funcionamiento operativo V7", padding=12)
        info.pack(fill="x", pady=16)
        ttk.Label(
            info,
            text=(
                f"Bolsa de seguridad fija: {PESO_BOLSA_SEGURIDAD_GR:.2f} g. "
                f"Novedad por peso si la diferencia neta supera ±{PESO_TOLERANCIA_GR:.2f} g.\n"
                "TOTAL: toma todos los contratos del Excel sin excluir por estado. PARCIAL: filtra por fecha y conserva el estado del reporte.\n"
                "Flujo rápido: escaneas un contrato, revisas la información y, si escaneas el siguiente código, "
                "el sistema guarda automáticamente el contrato actual como OK antes de cargar el nuevo."
            ),
            justify="left",
        ).pack(anchor="w")

        ttk.Button(container, text="Iniciar auditoría", style="Big.TButton", command=self._start_audit).pack(anchor="e", pady=20)
        self._add_signature_footer(container)
        self._on_mode_change()

    def _browse_excel(self):
        path = filedialog.askopenfilename(
            title="Selecciona el reporte Excel",
            filetypes=[("Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
        )
        if path:
            self.excel_var.set(path)

    def _browse_output_dir(self):
        path = filedialog.askdirectory(title="Selecciona carpeta base de resultados")
        if path:
            self.output_dir_var.set(path)

    def _on_mode_change(self):
        if hasattr(self, "fecha_entry"):
            if self.mode_var.get() == MODO_TOTAL:
                self.fecha_entry.configure(state="disabled")
            else:
                self.fecha_entry.configure(state="normal")

    def _start_audit(self):
        excel_path = self.excel_var.get().strip().strip('"')
        if not excel_path:
            messagebox.showwarning("Falta archivo", "Selecciona el Excel del inventario de contratos.")
            return
        if not Path(excel_path).exists():
            messagebox.showerror("Archivo no existe", f"No existe el archivo:\n{excel_path}")
            return

        output_dir = self.output_dir_var.get().strip().strip('"')
        if not output_dir:
            messagebox.showwarning("Falta carpeta", "Selecciona la carpeta base donde se guardarán los resultados.")
            return

        mode = self.mode_var.get()
        fecha_desde = None
        if mode == MODO_PARCIAL:
            fecha_desde = parse_user_date(self.fecha_desde_var.get())
            if not fecha_desde:
                messagebox.showwarning("Fecha requerida", "Para auditoría parcial indica la fecha desde en formato dd/mm/aaaa.")
                return

        try:
            progress = self.backend.start(
                excel_path=excel_path,
                modo=mode,
                fecha_desde=fecha_desde,
                usuario=self.usuario_var.get(),
                output_dir=output_dir,
            )
        except Exception as exc:
            messagebox.showerror("Error al iniciar", str(exc))
            return

        if progress["total_objetivo"] == 0:
            messagebox.showwarning(
                "Sin contratos objetivo",
                "No se encontraron contratos dentro del alcance seleccionado. Revisa el modo, la fecha o el Excel.",
            )
        self._build_audit_view(progress)

    # =====================================================
    # VISTA DE AUDITORÍA
    # =====================================================
    def _build_audit_view(self, progress):
        self._clear_root()

        main = ttk.Frame(self, padding=14)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(4, weight=1)

        header = ttk.Frame(main)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Auditoría en ejecución", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(header, text="Finalizar y generar resumen", style="Big.TButton", command=self._finalize).grid(row=0, column=1, sticky="e")

        self.kpi_frame = ttk.Frame(main)
        self.kpi_frame.grid(row=1, column=0, sticky="ew", pady=(12, 8))
        self._update_kpis(progress)

        scan_box = ttk.LabelFrame(main, text="Escaneo", padding=12)
        scan_box.grid(row=2, column=0, sticky="ew", pady=8)
        scan_box.columnconfigure(1, weight=1)

        ttk.Label(scan_box, text="Código / contrato:").grid(row=0, column=0, sticky="w")
        self.scan_var = tk.StringVar()
        self.scan_entry = ttk.Entry(scan_box, textvariable=self.scan_var, font=("Segoe UI", 17))
        self.scan_entry.grid(row=0, column=1, sticky="ew", padx=8)
        self.scan_entry.bind("<Return>", lambda event: self._process_scan())
        self.scan_var.trace_add("write", self._schedule_auto_scan)
        ttk.Button(scan_box, text="Buscar", command=self._process_scan).grid(row=0, column=2)

        self.status_label = ttk.Label(scan_box, text="Escanea un contrato para iniciar.", style="StatusWarn.TLabel")
        self.status_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(10, 0))

        data_area = ttk.Frame(main)
        data_area.grid(row=3, column=0, sticky="ew", pady=8)
        data_area.columnconfigure(0, weight=3)
        data_area.columnconfigure(1, weight=2)

        self.info_box = ttk.LabelFrame(data_area, text="Información del contrato", padding=12)
        self.info_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.info_box.columnconfigure(1, weight=1)
        self.info_box.columnconfigure(3, weight=1)

        self.info_vars = {}
        left_labels = [
            ("contrato", "Contrato"),
            ("cliente", "Cliente"),
            ("documento", "Cédula"),
            ("joyeria", "Joyería"),
            ("estado", "Estado"),
            ("valor", "Valor"),
            ("fecha_operacion", "Fecha operación"),
            ("cantidad_esperada", "Cantidad artículos"),
        ]
        right_labels = [
            ("peso_libre_esperado", "Peso libre / oro"),
            ("peso_total_esperado", "Peso total joya"),
            ("peso_bolsa_seguridad", "Bolsa seguridad fija"),
            ("peso_con_bolsa_esperado", "Peso total + bolsa"),
            ("peso_productos_libre", "Suma libre detalle"),
            ("peso_productos_total", "Suma total detalle"),
            ("siguiente_contrato", "Siguiente esperado"),
            ("audit_estado", "Auditoría actual"),
        ]
        for i, (key, label) in enumerate(left_labels):
            ttk.Label(self.info_box, text=f"{label}:", style="InfoName.TLabel").grid(row=i, column=0, sticky="nw", pady=3)
            var = tk.StringVar(value="")
            self.info_vars[key] = var
            ttk.Label(self.info_box, textvariable=var, style="ImportantValue.TLabel" if key in ("contrato", "cliente") else "InfoValue.TLabel", wraplength=320).grid(row=i, column=1, sticky="nw", pady=3)
        for i, (key, label) in enumerate(right_labels):
            ttk.Label(self.info_box, text=f"{label}:", style="InfoName.TLabel").grid(row=i, column=2, sticky="nw", padx=(20, 0), pady=3)
            var = tk.StringVar(value="")
            self.info_vars[key] = var
            ttk.Label(self.info_box, textvariable=var, style="ImportantValue.TLabel" if key == "peso_con_bolsa_esperado" else "InfoValue.TLabel", wraplength=260).grid(row=i, column=3, sticky="nw", pady=3)

        verify_box = ttk.LabelFrame(data_area, text="Registro de verificación", padding=12)
        verify_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        verify_box.columnconfigure(1, weight=1)

        self.cantidad_var = tk.StringVar()
        self.peso_bruto_bolsa_var = tk.StringVar()
        self.novedad_var = tk.StringVar(value="OK")
        self.obs_var = tk.StringVar()
        self.calc_result_var = tk.StringVar(value="")

        ttk.Label(verify_box, text="Cantidad evidenciada:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(verify_box, textvariable=self.cantidad_var).grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(verify_box, text="Peso real con bolsa (opcional):").grid(row=1, column=0, sticky="w", pady=4)
        peso_entry = ttk.Entry(verify_box, textvariable=self.peso_bruto_bolsa_var)
        peso_entry.grid(row=1, column=1, sticky="ew", pady=4)
        self.peso_bruto_bolsa_var.trace_add("write", self._update_weight_preview)

        ttk.Label(verify_box, text="Cálculo:").grid(row=2, column=0, sticky="nw", pady=4)
        ttk.Label(verify_box, textvariable=self.calc_result_var, wraplength=430, style="InfoValue.TLabel").grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(verify_box, text="Tipo novedad:").grid(row=3, column=0, sticky="w", pady=4)
        self.novedad_combo = ttk.Combobox(verify_box, textvariable=self.novedad_var, values=NOVEDADES, state="readonly")
        self.novedad_combo.grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(verify_box, text="Observación:").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(verify_box, textvariable=self.obs_var).grid(row=4, column=1, sticky="ew", pady=4)

        btns = ttk.Frame(verify_box)
        btns.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self.ok_btn = ttk.Button(btns, text="Marcar OK  (F1 / Enter sin texto)", style="Big.TButton", command=self._mark_ok, state="disabled")
        self.ok_btn.pack(side="left", padx=(0, 8))
        self.nov_btn = ttk.Button(btns, text="Guardar novedad  (F2)", command=self._mark_novedad, state="disabled")
        self.nov_btn.pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Limpiar  (F3)", command=self._clear_current).pack(side="left")

        help_text = (
            "Velocidad: si hay un contrato cargado y escaneas otro código, "
            "el sistema guarda el contrato actual y carga el nuevo automáticamente."
        )
        ttk.Label(verify_box, text=help_text, foreground="#555555", wraplength=500).grid(row=6, column=0, columnspan=2, sticky="w", pady=(12, 0))

        bottom_area = ttk.Frame(main)
        bottom_area.grid(row=4, column=0, sticky="nsew", pady=(8, 0))
        bottom_area.rowconfigure(0, weight=1)
        bottom_area.columnconfigure(0, weight=3)
        bottom_area.columnconfigure(1, weight=2)

        product_box = ttk.LabelFrame(bottom_area, text="Detalle de artículos del contrato", padding=8)
        product_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        product_box.rowconfigure(0, weight=1)
        product_box.columnconfigure(0, weight=1)

        columns = ("numero", "familia", "calidad", "peso_estimado", "peso_total", "valor_compra", "descripcion")
        self.product_tree = ttk.Treeview(product_box, columns=columns, show="headings")
        headings = {
            "numero": "N°",
            "familia": "Familia",
            "calidad": "Calidad",
            "peso_estimado": "Peso Libre",
            "peso_total": "Peso Total",
            "valor_compra": "Valor Compra",
            "descripcion": "Descripción",
        }
        widths = {
            "numero": 55,
            "familia": 150,
            "calidad": 75,
            "peso_estimado": 92,
            "peso_total": 92,
            "valor_compra": 120,
            "descripcion": 420,
        }
        for col in columns:
            self.product_tree.heading(col, text=headings[col])
            self.product_tree.column(col, width=widths[col], anchor="w")
        self.product_tree.tag_configure("total", background="#E2F0D9")

        yscroll = ttk.Scrollbar(product_box, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=yscroll.set)
        self.product_tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")

        pending_box = ttk.LabelFrame(bottom_area, text="Contratos pendientes por escanear", padding=8)
        pending_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        pending_box.rowconfigure(1, weight=1)
        pending_box.columnconfigure(0, weight=1)

        self.pending_count_var = tk.StringVar(value="Pendientes: 0")
        ttk.Label(
            pending_box,
            textvariable=self.pending_count_var,
            style="StatusWarn.TLabel",
            wraplength=420,
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        pending_columns = ("contrato", "estado", "cliente", "peso_bolsa")
        self.pending_tree = ttk.Treeview(pending_box, columns=pending_columns, show="headings", height=8)
        pending_headings = {
            "contrato": "Contrato",
            "estado": "Estado",
            "cliente": "Cliente",
            "peso_bolsa": "Peso + bolsa",
        }
        pending_widths = {
            "contrato": 125,
            "estado": 95,
            "cliente": 190,
            "peso_bolsa": 90,
        }
        for col in pending_columns:
            self.pending_tree.heading(col, text=pending_headings[col])
            self.pending_tree.column(col, width=pending_widths[col], anchor="w")
        self.pending_tree.tag_configure("pendiente", background="#FFF2CC")

        pscroll = ttk.Scrollbar(pending_box, orient="vertical", command=self.pending_tree.yview)
        self.pending_tree.configure(yscrollcommand=pscroll.set)
        self.pending_tree.grid(row=1, column=0, sticky="nsew")
        pscroll.grid(row=1, column=1, sticky="ns")

        self._update_pending_table()
        self.scan_entry.focus_set()

    def _update_kpis(self, progress=None):
        if progress is None:
            progress = self.backend.get_progress()
        for w in self.kpi_frame.winfo_children():
            w.destroy()

        items = [
            ("Modo", progress.get("modo", "")),
            ("Objetivo", progress.get("total_objetivo", 0)),
            ("Verificados", progress.get("verificados", 0)),
            ("Novedades", progress.get("novedades", 0)),
            ("Faltantes", progress.get("faltantes", 0)),
            ("No encontrados", progress.get("no_encontrados", 0)),
        ]
        for i, (label, value) in enumerate(items):
            frame = ttk.Frame(self.kpi_frame, padding=6, relief="groove")
            frame.grid(row=0, column=i, sticky="ew", padx=3)
            self.kpi_frame.columnconfigure(i, weight=1)
            ttk.Label(frame, text=label, font=("Segoe UI", 9)).pack(anchor="center")
            ttk.Label(frame, text=str(value), style="KPI.TLabel").pack(anchor="center")

        if hasattr(self, "pending_tree"):
            self._update_pending_table()

    def _update_pending_table(self):
        if not hasattr(self, "pending_tree"):
            return
        for item in self.pending_tree.get_children():
            self.pending_tree.delete(item)

        pending = self.backend.get_pending_contracts(limit=500)
        total_pending = self.backend.get_progress().get("faltantes", len(pending))
        extra = "" if len(pending) == total_pending else f"  (mostrando {len(pending)})"
        self.pending_count_var.set(f"Pendientes por escanear/verificar: {total_pending}{extra}")

        for row in pending:
            peso_bolsa = row.get("peso_con_bolsa", "")
            if peso_bolsa:
                peso_bolsa = f"{peso_bolsa} g"
            self.pending_tree.insert(
                "",
                "end",
                values=(
                    row.get("contrato", ""),
                    row.get("estado", ""),
                    row.get("cliente", ""),
                    peso_bolsa,
                ),
                tags=("pendiente",),
            )

    def _is_complete_scan(self, text: str) -> bool:
        """
        Función auxiliar para determinar si un texto es un escaneo completo válido.
        Devuelve True solo en estos casos:
        - Exactamente 5 dígitos -> contrato viejo (ej: 35265)
        - Exactamente 11 dígitos -> contrato nuevo pegado (ej: 43401003162)
        - Formato completo con separadores (ej: 434-01-003162, 434 01 003162, 434'01'003162)
        """
        import re
        text = text.strip()
        
        # Caso 1: Exactamente 5 dígitos -> contrato viejo
        if re.fullmatch(r"\d{5}", text):
            return True
        
        # Caso 2: Exactamente 11 dígitos -> contrato nuevo pegado
        if re.fullmatch(r"\d{11}", text):
            return True
        
        # Caso 3: Formato completo con separadores (guion, espacio, apostrofe)
        # Patrones: 434-01-003162, 434 01 003162, 434'01'003162
        if re.fullmatch(r"\d{3}[- '\s]\d{2}[- '\s]\d{6}", text):
            return True
        
        return False

    def _schedule_auto_scan(self, *_):
        value = self.scan_var.get().strip()
        if self.auto_after_id:
            self.after_cancel(self.auto_after_id)
            self.auto_after_id = None
        if self._is_complete_scan(value):
            self.auto_after_id = self.after(400, self._auto_scan_if_stable)

    def _auto_scan_if_stable(self):
        value = self.scan_var.get().strip()
        if value and self._is_complete_scan(value):
            self._process_scan()

    def _process_scan(self):
        raw = self.scan_var.get().strip()

        # Enter con campo vacío: guardar contrato actual como OK.
        if not raw:
            if self.current_contract:
                self._mark_ok()
            return

        # Flujo rápido: si ya hay contrato en pantalla, el siguiente escaneo guarda el actual primero.
        if self.current_contract:
            saved = self._save_verification(clear_after=True, silent=True)
            if not saved:
                return

        self.current_raw = raw
        result = self.backend.scan_contract(raw)
        self.scan_var.set("")
        self.last_processed_raw = raw

        if result.status in ("ENCONTRADO", "YA_AUDITADO"):
            self._load_contract(result.record)
            if result.status == "YA_AUDITADO":
                self._set_status(result.message, "warn")
            else:
                self._set_status(result.message, "ok")
            self.ok_btn.configure(state="normal")
            self.nov_btn.configure(state="normal")
        elif result.status in ("FUERA_ALCANCE", "NO_AUDITABLE_ESTADO"):
            if result.record:
                self._load_contract(result.record)
            else:
                self._clear_current(keep_status=True)
            self._set_status(result.message, "warn")
            self.ok_btn.configure(state="disabled")
            self.nov_btn.configure(state="disabled")
        else:
            self._clear_current(keep_status=True)
            self._set_status(f"{result.status}: {result.message} ({result.contrato or raw})", "error")
            self.ok_btn.configure(state="disabled")
            self.nov_btn.configure(state="disabled")

        self._update_kpis()
        self.scan_entry.focus_set()

    def _load_contract(self, record):
        self.current_contract = record.get("contrato")
        self.last_loaded_record = record
        for key, var in self.info_vars.items():
            value = record.get(key, "")
            if key == "audit_estado" and not value:
                value = "SIN AUDITAR"
            if key in ("peso_libre_esperado", "peso_total_esperado", "peso_bolsa_seguridad", "peso_con_bolsa_esperado", "peso_productos_libre", "peso_productos_total") and value:
                value = f"{value} g"
            var.set(str(value))

        self.cantidad_var.set(str(record.get("cantidad_esperada", "")))
        self.peso_bruto_bolsa_var.set("")
        self.novedad_var.set("OK")
        self.obs_var.set("")
        self._update_weight_preview()

        for item in self.product_tree.get_children():
            self.product_tree.delete(item)

        for p in record.get("productos", []):
            self.product_tree.insert(
                "",
                "end",
                values=(
                    p.get("numero", ""),
                    p.get("familia", ""),
                    p.get("calidad", ""),
                    p.get("peso_estimado", ""),
                    p.get("peso_total", ""),
                    p.get("valor_compra", ""),
                    p.get("descripcion", ""),
                ),
            )

        self.product_tree.insert(
            "",
            "end",
            values=(
                "",
                "TOTALES DEL CONTRATO",
                "",
                f"{record.get('peso_productos_libre', '')} g" if record.get("peso_productos_libre") else "",
                f"{record.get('peso_productos_total', '')} g" if record.get("peso_productos_total") else "",
                record.get("valor_productos_total", ""),
                f"Peso total + bolsa esperada: {record.get('peso_con_bolsa_esperado', '')} g",
            ),
            tags=("total",),
        )

    def _parse_float_ui(self, value: str):
        value = (value or "").strip().replace(",", ".")
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    def _update_weight_preview(self, *_):
        if not self.last_loaded_record:
            self.calc_result_var.set("")
            return
        peso_total_txt = str(self.last_loaded_record.get("peso_total_esperado", "")).replace(",", ".")
        peso_con_bolsa_txt = str(self.last_loaded_record.get("peso_con_bolsa_esperado", "")).replace(",", ".")
        peso_total = self._parse_float_ui(peso_total_txt)
        peso_con_bolsa = self._parse_float_ui(peso_con_bolsa_txt)
        bruto = self._parse_float_ui(self.peso_bruto_bolsa_var.get())

        base = ""
        if peso_total is not None and peso_con_bolsa is not None:
            base = f"Esperado con bolsa: {peso_con_bolsa:.2f} g = {peso_total:.2f} g joya + {PESO_BOLSA_SEGURIDAD_GR:.2f} g bolsa"
        if bruto is None:
            self.calc_result_var.set(base)
            return
        neto = bruto - PESO_BOLSA_SEGURIDAD_GR
        diff = ""
        if peso_total is not None:
            diferencia = neto - peso_total
            resultado = "OK" if abs(diferencia) <= PESO_TOLERANCIA_GR else "NOVEDAD"
            diff = f"\nReal neto: {neto:.2f} g | Diferencia: {diferencia:+.2f} g | {resultado}"
        self.calc_result_var.set(base + diff)

    def _set_status(self, message, kind):
        style = {
            "ok": "StatusOk.TLabel",
            "warn": "StatusWarn.TLabel",
            "error": "StatusError.TLabel",
        }.get(kind, "StatusWarn.TLabel")
        self.status_label.configure(text=message, style=style)

    def _mark_ok(self):
        if not self.current_contract:
            return
        self.novedad_var.set("OK")
        self.obs_var.set("")
        self._save_verification()

    def _mark_novedad(self):
        if not self.current_contract:
            return
        if self.novedad_var.get() == "OK" and not self.obs_var.get().strip():
            if not messagebox.askyesno(
                "Confirmar",
                "No seleccionaste una novedad ni escribiste observación. ¿Deseas registrar como OK?",
            ):
                return
        self._save_verification()

    def _save_verification(self, clear_after=True, silent=False):
        try:
            result = self.backend.register_verification(
                contrato=self.current_contract,
                raw_scan=self.current_raw,
                cantidad_evidenciada=self.cantidad_var.get(),
                peso_bruto_bolsa_evidenciado=self.peso_bruto_bolsa_var.get(),
                novedad_tipo=self.novedad_var.get(),
                observacion=self.obs_var.get(),
            )
        except Exception as exc:
            if not silent:
                messagebox.showerror("Error al guardar", str(exc))
            else:
                self._set_status(f"No se pudo guardar {self.current_contract}: {exc}", "error")
            return False

        saved_contract = self.current_contract
        if not silent:
            if result["resultado"] == "OK":
                self._set_status(f"OK guardado para {saved_contract}.", "ok")
            else:
                self._set_status(f"NOVEDAD guardada para {saved_contract}: {result['novedad_tipo']}", "warn")

        self._update_kpis(result.get("progress"))
        if clear_after:
            self._clear_current(keep_status=True)
        self.scan_entry.focus_set()
        return True

    def _repeat_last_contract(self):
        if self.last_processed_raw:
            self.scan_var.set(self.last_processed_raw)
            self._process_scan()

    def _clear_current(self, keep_status=False):
        self.current_contract = None
        self.current_raw = ""
        self.last_loaded_record = None
        for var in getattr(self, "info_vars", {}).values():
            var.set("")
        if hasattr(self, "product_tree"):
            for item in self.product_tree.get_children():
                self.product_tree.delete(item)
        if hasattr(self, "cantidad_var"):
            self.cantidad_var.set("")
            self.peso_bruto_bolsa_var.set("")
            self.novedad_var.set("OK")
            self.obs_var.set("")
            self.calc_result_var.set("")
        if hasattr(self, "ok_btn"):
            self.ok_btn.configure(state="disabled")
            self.nov_btn.configure(state="disabled")
        if not keep_status and hasattr(self, "status_label"):
            self._set_status("Escanea un contrato para continuar.", "warn")
        if hasattr(self, "scan_entry"):
            self.scan_entry.focus_set()

    def _finalize(self):
        progress = self.backend.get_progress()
        if progress.get("faltantes", 0) > 0:
            proceed = messagebox.askyesno(
                "Hay faltantes",
                f"Quedan {progress['faltantes']} contratos sin verificar.\n\n¿Deseas finalizar de todas formas y generar el reporte?",
            )
            if not proceed:
                return

        try:
            final = self.backend.finalize()
        except Exception as exc:
            messagebox.showerror("Error al finalizar", str(exc))
            return

        self._open_path(final.get("carpeta_salida"))
        self._show_final_dialog(final)

    def _open_path(self, path: str | None):
        if not path:
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception:
            pass

    def _show_final_dialog(self, final):
        dialog = tk.Toplevel(self)
        dialog.title("Auditoría finalizada")
        dialog.geometry("620x360")
        dialog.transient(self)
        dialog.grab_set()
        dialog.columnconfigure(0, weight=1)

        body = ttk.Frame(dialog, padding=20)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)

        ttk.Label(body, text="Se generó el Excel de auditoría", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        summary = (
            f"Verificados: {final['verificados']}\n"
            f"Novedades: {final['novedades']}\n"
            f"Faltantes: {final['faltantes']}\n"
            f"No encontrados: {final['no_encontrados']}\n\n"
            f"Archivo:\n{final['archivo_salida']}"
        )
        ttk.Label(body, text=summary, justify="left", wraplength=560, style="InfoValue.TLabel").grid(row=1, column=0, sticky="w", pady=(12, 18))

        btns = ttk.Frame(body)
        btns.grid(row=2, column=0, sticky="ew")

        ttk.Button(btns, text="Abrir Excel generado", command=lambda: self._open_path(final.get("archivo_salida"))).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Abrir carpeta", command=lambda: self._open_path(final.get("carpeta_salida"))).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Nueva auditoría", command=lambda: [dialog.destroy(), self._build_start_view()]).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Salir", command=self.destroy).pack(side="right")

        ttk.Label(body, text=DEVELOPER_SIGNATURE, style="Signature.TLabel").grid(row=3, column=0, sticky="e", pady=(18, 0))



def main():
    app = AuditoriaCajaFuerteGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
