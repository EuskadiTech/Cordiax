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
        
        ttk.Button(control_frame, text="Generar", 
                  command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Imprimir", 
                  command=self.print_report).pack(side=tk.LEFT, padx=5)
        
        # Frame de informe
        report_frame = ttk.Frame(self.parent)
        report_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto con scroll
        self.report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, 
                                                     font=("Courier", 10))
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
    def generate_report(self):
        """Generar informe diario"""
        self.report_text.delete("1.0", tk.END)
        
        fecha = self.date_var.get()
        
        # Encabezado
        report = "=" * 80 + "\n"
        report += f"INFORME DIARIO - {fecha}\n"
        report += "=" * 80 + "\n\n"
        
        # Materiales bajo mínimo
        report += "MATERIALES BAJO MÍNIMO:\n"
        report += "-" * 80 + "\n"
        
        materials = database.fetch_all("""
            SELECT nombre, categoria, cantidad, cantidad_minima, unidad
            FROM materiales
            WHERE cantidad <= cantidad_minima
            ORDER BY nombre
        """)
        
        if materials:
            for mat in materials:
                report += f"• {mat['nombre']}\n"
                report += f"  Categoría: {mat['categoria'] or 'N/A'}\n"
                report += f"  Cantidad actual: {mat['cantidad']} {mat['unidad'] or 'unidades'}\n"
                report += f"  Cantidad mínima: {mat['cantidad_minima']} {mat['unidad'] or 'unidades'}\n"
                report += f"  ⚠️ COMPRAR: {mat['cantidad_minima'] - mat['cantidad']} {mat['unidad'] or 'unidades'}\n\n"
        else:
            report += "  ✓ Todos los materiales están en niveles adecuados\n\n"
        
        # Menú del día
        report += "\nMENÚ DE CAFETERÍA DEL DÍA:\n"
        report += "-" * 80 + "\n"
        
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
            for item in menu_items:
                report += f"\n{item['tipo_comida'].upper()}:\n"
                report += f"  Plato: {item['plato']}\n"
                if item['descripcion']:
                    report += f"  Descripción: {item['descripcion']}\n"
                if item['alergenos']:
                    report += f"  ⚠️ Alérgenos: {item['alergenos']}\n"
        else:
            report += "  No hay menú registrado para este día\n"
        
        # Asistencia del día
        report += "\n\nRESUMEN DE ASISTENCIA:\n"
        report += "-" * 80 + "\n"
        
        asistencia = database.fetch_all("""
            SELECT estado, COUNT(*) as total
            FROM asistencia
            WHERE fecha = ?
            GROUP BY estado
        """, (fecha,))
        
        if asistencia:
            total_registros = sum(a['total'] for a in asistencia)
            report += f"Total de registros: {total_registros}\n\n"
            for a in asistencia:
                report += f"  {a['estado']}: {a['total']} estudiantes\n"
        else:
            report += "  No hay registros de asistencia para este día\n"
        
        report += "\n" + "=" * 80 + "\n"
        report += "Fin del informe\n"
        report += "=" * 80 + "\n"
        
        self.report_text.insert("1.0", report)
    
    def print_report(self):
        """Imprimir informe (copiar al portapapeles)"""
        report_content = self.report_text.get("1.0", tk.END)
        self.parent.clipboard_clear()
        self.parent.clipboard_append(report_content)
        messagebox.showinfo("Información", 
                           "Informe copiado al portapapeles. Puede pegarlo en un documento.")
