# -*- coding: utf-8 -*-
"""
Módulo de Permisos
Gestión de permisos con plantilla de 3 filas y sí/no
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from modules import database
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import sys


class PermissionsModule:
    """Módulo de gestión de permisos"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_permissions()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Permisos", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de botones
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Nuevo Permiso", 
                  command=self.new_permission).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", 
                  command=self.edit_permission).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.delete_permission).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generar Plantilla PDF", 
                  command=self.generate_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", 
                  command=self.load_permissions).pack(side=tk.LEFT, padx=5)
        
        # Frame de tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("ID", "Estudiante", "Tipo", "Respuesta", "Fecha", "Notas")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("ID", width=50)
        self.tree.column("Estudiante", width=200)
        self.tree.column("Tipo", width=150)
        self.tree.column("Respuesta", width=80)
        self.tree.column("Fecha", width=100)
        self.tree.column("Notas", width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def load_permissions(self):
        """Cargar permisos desde la base de datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener permisos
        permissions = database.fetch_all("""
            SELECT p.id, e.nombre, e.apellidos, p.tipo_permiso, p.respuesta, 
                   p.fecha, p.notas
            FROM permisos p
            JOIN estudiantes e ON p.estudiante_id = e.id
            ORDER BY p.fecha DESC, e.apellidos
        """)
        
        # Agregar a tabla
        for perm in permissions:
            self.tree.insert("", tk.END, values=(
                perm['id'],
                f"{perm['nombre']} {perm['apellidos']}",
                perm['tipo_permiso'],
                perm['respuesta'] or "",
                perm['fecha'] or "",
                perm['notas'] or ""
            ))
    
    def new_permission(self):
        """Crear nuevo permiso"""
        PermissionDialog(self.parent, self.load_permissions)
    
    def edit_permission(self):
        """Editar permiso seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un permiso")
            return
        
        item = self.tree.item(selection[0])
        permission_id = item['values'][0]
        
        PermissionDialog(self.parent, self.load_permissions, permission_id)
    
    def delete_permission(self):
        """Eliminar permiso seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un permiso")
            return
        
        item = self.tree.item(selection[0])
        permission_id = item['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este permiso?"):
            database.execute_query("DELETE FROM permisos WHERE id = ?", (permission_id,))
            self.load_permissions()
            messagebox.showinfo("Éxito", "Permiso eliminado correctamente")
    
    def generate_template(self):
        """Generar plantilla PDF de permisos"""
        # Diálogo para seleccionar tipo de permiso
        dialog = tk.Toplevel(self.parent)
        dialog.title("Generar Plantilla de Permisos")
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Set icon
        try:
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(sys._MEIPASS, 'logo.ico')
            else:
                icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo.ico')
            if os.path.exists(icon_path):
                dialog.iconbitmap(icon_path)
        except Exception:
            pass
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Tipo de Permiso:").pack(pady=5)
        tipo_var = tk.StringVar()
        ttk.Entry(frame, textvariable=tipo_var, width=40).pack(pady=5)
        
        ttk.Label(frame, text="(Ej: Permiso de Fotografía, Excursión, etc.)").pack(pady=5)
        
        def generar():
            tipo = tipo_var.get()
            if not tipo:
                messagebox.showerror("Error", "Por favor, ingrese el tipo de permiso")
                return
            
            self.create_permission_pdf(tipo)
            dialog.destroy()
        
        ttk.Button(frame, text="Generar", command=generar).pack(pady=10)
        
    def create_permission_pdf(self, tipo_permiso):
        """Crear PDF de plantilla de permisos"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"permisos_{tipo_permiso.lower().replace(' ', '_')}.pdf"
        )
        
        if not filename:
            return
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=20,
                alignment=1
            )
            
            story.append(Paragraph(f"PLANTILLA DE {tipo_permiso.upper()}", title_style))
            story.append(Spacer(1, 0.2 * inch))
            
            # Obtener estudiantes activos
            students = database.fetch_all("""
                SELECT nombre, apellidos 
                FROM estudiantes 
                WHERE activo = 1 
                ORDER BY apellidos, nombre
            """)
            
            # Crear tabla con 3 columnas
            data = [["Estudiante", "SÍ", "NO"]]
            
            for student in students:
                nombre_completo = f"{student['nombre']} {student['apellidos']}"
                data.append([nombre_completo, "☐", "☐"])
            
            # Crear tabla
            t = Table(data, colWidths=[4*inch, 0.75*inch, 0.75*inch])
            t.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Contenido
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                
                # Bordes
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(t)
            story.append(Spacer(1, 0.3 * inch))
            
            # Nota al pie
            nota = Paragraph(
                "<i>Por favor, marque con una X en la casilla correspondiente.</i>",
                styles['Normal']
            )
            story.append(nota)
            
            # Generar PDF
            doc.build(story)
            
            messagebox.showinfo("Éxito", f"Plantilla generada correctamente:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar plantilla: {str(e)}")


class PermissionDialog:
    """Diálogo para crear/editar permiso"""
    
    def __init__(self, parent, callback, permission_id=None):
        self.callback = callback
        self.permission_id = permission_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Permiso" if permission_id is None else "Editar Permiso")
        self.dialog.geometry("450x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set icon
        self._set_icon()
        
        self.setup_ui()
        
        if permission_id:
            self.load_permission_data()
    
    def _set_icon(self):
        """Set window icon"""
        try:
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(sys._MEIPASS, 'logo.ico')
            else:
                icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo.ico')
            if os.path.exists(icon_path):
                self.dialog.iconbitmap(icon_path)
        except Exception:
            pass
    
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Estudiante
        ttk.Label(main_frame, text="Estudiante:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(main_frame, textvariable=self.student_var, 
                                         width=37, state="readonly")
        self.student_combo.grid(row=row, column=1, pady=5, sticky=tk.EW)
        
        # Cargar estudiantes
        students = database.fetch_all(
            "SELECT id, nombre, apellidos FROM estudiantes WHERE activo = 1 ORDER BY apellidos, nombre"
        )
        self.student_list = [(s['id'], f"{s['nombre']} {s['apellidos']}") for s in students]
        self.student_combo['values'] = [s[1] for s in self.student_list]
        row += 1
        
        # Tipo de permiso
        ttk.Label(main_frame, text="Tipo de Permiso:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tipo_var = tk.StringVar()
        tipos = ["Permiso de Fotografía", "Excursión", "Actividad Deportiva", "Uso de Internet", "Otro"]
        ttk.Combobox(main_frame, textvariable=self.tipo_var, values=tipos, 
                    width=37).grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        # Respuesta
        ttk.Label(main_frame, text="Respuesta:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.respuesta_var = tk.StringVar()
        respuestas = ["SÍ", "NO", "Pendiente"]
        ttk.Combobox(main_frame, textvariable=self.respuesta_var, values=respuestas, 
                    width=37, state="readonly").grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        # Fecha
        ttk.Label(main_frame, text="Fecha:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.fecha_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(main_frame, textvariable=self.fecha_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        # Notas
        ttk.Label(main_frame, text="Notas:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.notas_text = tk.Text(main_frame, width=40, height=5)
        self.notas_text.grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
    
    def load_permission_data(self):
        """Cargar datos del permiso"""
        perm = database.fetch_one("""
            SELECT p.*, e.nombre, e.apellidos
            FROM permisos p
            JOIN estudiantes e ON p.estudiante_id = e.id
            WHERE p.id = ?
        """, (self.permission_id,))
        
        if perm:
            # Buscar y seleccionar estudiante
            for i, (sid, sname) in enumerate(self.student_list):
                if sid == perm['estudiante_id']:
                    self.student_combo.current(i)
                    break
            
            self.tipo_var.set(perm['tipo_permiso'])
            self.respuesta_var.set(perm['respuesta'] or "")
            self.fecha_var.set(perm['fecha'] or "")
            self.notas_text.insert("1.0", perm['notas'] or "")
    
    def save(self):
        """Guardar permiso"""
        if not self.student_var.get() or not self.tipo_var.get():
            messagebox.showerror("Error", "Estudiante y tipo de permiso son obligatorios")
            return
        
        # Obtener ID del estudiante seleccionado
        student_index = self.student_combo.current()
        student_id = self.student_list[student_index][0]
        
        try:
            if self.permission_id:
                # Actualizar
                database.execute_query("""
                    UPDATE permisos 
                    SET estudiante_id=?, tipo_permiso=?, respuesta=?, fecha=?, notas=?
                    WHERE id=?
                """, (student_id, self.tipo_var.get(), self.respuesta_var.get() or None,
                     self.fecha_var.get() or None,
                     self.notas_text.get("1.0", tk.END).strip() or None,
                     self.permission_id))
            else:
                # Crear nuevo
                database.execute_query("""
                    INSERT INTO permisos 
                    (estudiante_id, tipo_permiso, respuesta, fecha, notas)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, self.tipo_var.get(), self.respuesta_var.get() or None,
                     self.fecha_var.get() or None,
                     self.notas_text.get("1.0", tk.END).strip() or None))
            
            messagebox.showinfo("Éxito", "Permiso guardado correctamente")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
