# -*- coding: utf-8 -*-
"""
Módulo de Informe Diario
Muestra materiales bajo mínimo y menú del día
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from modules import database
from datetime import date


class DailyReportModule:
    """Módulo de informe diario"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.generate_report()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Informe Diario", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de controles
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Fecha:").pack(side=tk.LEFT, padx=5)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(control_frame, textvariable=self.date_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # Frame de filtros
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Centro:").pack(side=tk.LEFT, padx=5)
        self.centro_filter_var = tk.StringVar(value="")
        self.centro_filter_combo = ttk.Combobox(filter_frame, textvariable=self.centro_filter_var, 
                                                width=20, state="readonly")
        self.centro_filter_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Aula:").pack(side=tk.LEFT, padx=5)
        self.aula_filter_var = tk.StringVar(value="")
        self.aula_filter_combo = ttk.Combobox(filter_frame, textvariable=self.aula_filter_var, 
                                              width=20, state="readonly")
        self.aula_filter_combo.pack(side=tk.LEFT, padx=5)
        
        # Cargar filtros
        self.load_filters()
        
        ttk.Button(filter_frame, text="Generar", 
                  command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Imprimir", 
                  command=self.print_report).pack(side=tk.LEFT, padx=5)
        
        # Frame de informe
        report_frame = ttk.Frame(self.parent)
        report_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto con scroll
        self.report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, 
                                                     font=("Courier", 19), bg="#000000", fg="#00FF00", padx=10, pady=10)
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
    def load_filters(self):
        """Cargar opciones de filtro"""
        # Cargar centros
        centros = database.fetch_all("SELECT id, nombre FROM centros ORDER BY nombre")
        centro_names = ["Todos"] + [c['nombre'] for c in centros]
        self.centro_filter_combo['values'] = centro_names
        if not self.centro_filter_var.get():
            self.centro_filter_var.set("Todos")
        
        # Cargar aulas
        aulas = database.fetch_all("SELECT id, nombre FROM aulas ORDER BY nombre")
        aula_names = ["Todas"] + [a['nombre'] for a in aulas]
        self.aula_filter_combo['values'] = aula_names
        if not self.aula_filter_var.get():
            self.aula_filter_var.set("Todas")
        
    def generate_report(self):
        """Generar informe diario"""
        self.report_text.delete("1.0", tk.END)
        
        fecha = self.date_var.get()
        COLS = 70
        HAS_DATA = False
        # Encabezado
        report = "=" * COLS + "\n"
        report += f"INFORME DIARIO - {fecha}\n"
        
        # Agregar información de filtros
        if self.centro_filter_var.get() and self.centro_filter_var.get() != "Todos":
            report += f"Centro: {self.centro_filter_var.get()}\n"
        if self.aula_filter_var.get() and self.aula_filter_var.get() != "Todas":
            report += f"Aula: {self.aula_filter_var.get()}\n"
        
        report += "=" * COLS + "\n"
        
        # Materiales bajo mínimo
        materials = database.fetch_all("""
            SELECT nombre, categoria, cantidad, cantidad_minima, unidad
            FROM materiales
            WHERE cantidad <= cantidad_minima
            ORDER BY nombre
        """)
        
        if materials:
            HAS_DATA = True
            report += "\nMATERIALES BAJO MÍNIMO:\n"
            report += "-" * COLS + "\n"
            
            for mat in materials:
                report += f"• {mat['nombre']}\n"
                report += f"  Categoría: {mat['categoria'] or 'N/A'}\n"
                report += f"  Cantidad actual: {mat['cantidad']} {mat['unidad'] or 'unidades'}\n"
                report += f"  Cantidad mínima: {mat['cantidad_minima']} {mat['unidad'] or 'unidades'}\n"
                report += f"  ⚠️ COMPRAR: {mat['cantidad_minima'] - mat['cantidad']} {mat['unidad'] or 'unidades'}\n\n"
        
        
        # Menú del día
        menu_items = database.fetch_all("""
            SELECT tipo_comida, plato, descripcion, alergenos
            FROM menu_cafeteria
            WHERE fecha = ?
            ORDER BY CASE tipo_comida 
                WHEN 'Desayuno' THEN 1 
                WHEN 'Almuerzo' THEN 2 
                WHEN 'Merienda' THEN 3 
                WHEN 'Cena' THEN 4 
                ELSE 5 END
        """, (fecha,))
        
        if menu_items:
            HAS_DATA = True
            report += "\nMENÚ DEL COMEDOR DEL DÍA:\n"
            report += "-" * COLS + "\n"
            for item in menu_items:
                report += f"\n{item['tipo_comida'].upper()}:\n"
                report += f"  Plato: {item['plato']}\n"
                if item['descripcion']:
                    report += f"  Descripción: {item['descripcion']}\n"
                if item['alergenos']:
                    report += f"  ⚠️ Alérgenos: {item['alergenos']}\n"
        
        # Asistencia del día con filtros
        
        # Construir consulta con filtros
        query = """
            SELECT a.estado, COUNT(*) as total
            FROM asistencia a
            JOIN estudiantes e ON a.estudiante_id = e.id
            LEFT JOIN centros c ON e.centro_id = c.id
            LEFT JOIN aulas au ON e.aula_id = au.id
            WHERE a.fecha = ?
        """
        params = [fecha]
        
        # Filtro por centro
        if self.centro_filter_var.get() and self.centro_filter_var.get() != "Todos":
            query += " AND c.nombre = ?"
            params.append(self.centro_filter_var.get())
        
        # Filtro por aula
        if self.aula_filter_var.get() and self.aula_filter_var.get() != "Todas":
            query += " AND au.nombre = ?"
            params.append(self.aula_filter_var.get())
        
        query += " GROUP BY a.estado"
        
        asistencia = database.fetch_all(query, tuple(params))
        
        if asistencia:
            HAS_DATA = True
            report += "\n\nRESUMEN DE ASISTENCIA:\n"
            report += "-" * COLS + "\n"
            total_registros = sum(a['total'] for a in asistencia)
            report += f"Total de registros: {total_registros}\n\n"
            for a in asistencia:
                report += f"  {a['estado']}: {a['total']} estudiantes\n"
        
        if not HAS_DATA:
            report += "No hay datos disponibles para la fecha y filtros seleccionados.\n"


        report += "\n" + "=" * COLS + "\n"
        report += "Fin del informe\n"
        report += "=" * COLS + "\n"
        
        self.report_text.insert("1.0", report)
    
    def print_report(self):
        """Imprimir informe (copiar al portapapeles)"""
        report_content = self.report_text.get("1.0", tk.END)
        self.parent.clipboard_clear()
        self.parent.clipboard_append(report_content)
        messagebox.showinfo("Información", 
                           "Informe copiado al portapapeles. Puede pegarlo en un documento.")
