# -*- coding: utf-8 -*-
"""
Módulo de Lista de Estudiantes
Gestión CRUD de estudiantes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules import database
from datetime import datetime
import os
import sys


class StudentListModule:
    """Módulo de gestión de estudiantes"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_students()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Lista de Estudiantes", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de filtros
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Centro:").pack(side=tk.LEFT, padx=5)
        self.centro_filter_var = tk.StringVar(value="")
        self.centro_filter_combo = ttk.Combobox(filter_frame, textvariable=self.centro_filter_var, 
                                                width=20, state="readonly")
        self.centro_filter_combo.pack(side=tk.LEFT, padx=5)
        self.centro_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_students())
        
        ttk.Label(filter_frame, text="Aula:").pack(side=tk.LEFT, padx=5)
        self.aula_filter_var = tk.StringVar(value="")
        self.aula_filter_combo = ttk.Combobox(filter_frame, textvariable=self.aula_filter_var, 
                                              width=20, state="readonly")
        self.aula_filter_combo.pack(side=tk.LEFT, padx=5)
        self.aula_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_students())
        
        # Cargar filtros
        self.load_filters()
        
        # Frame de botones
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Nuevo Estudiante", 
                  command=self.new_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", 
                  command=self.edit_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.delete_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", 
                  command=self.load_students).pack(side=tk.LEFT, padx=5)
        
        # Frame de tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("ID", "Nombre", "Apellidos", "Centro", "Aula", "F. Nacimiento", "Teléfono", "Estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Apellidos", text="Apellidos")
        self.tree.heading("Centro", text="Centro")
        self.tree.heading("Aula", text="Aula")
        self.tree.heading("F. Nacimiento", text="F. Nacimiento")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Estado", text="Estado")
        
        self.tree.column("ID", width=40)
        self.tree.column("Nombre", width=120)
        self.tree.column("Apellidos", width=120)
        self.tree.column("Centro", width=150)
        self.tree.column("Aula", width=100)
        self.tree.column("F. Nacimiento", width=100)
        self.tree.column("Teléfono", width=100)
        self.tree.column("Estado", width=80)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
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
        
    def load_students(self):
        """Cargar estudiantes desde la base de datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Construir consulta con filtros
        query = """
            SELECT e.id, e.nombre, e.apellidos, e.fecha_nacimiento, e.telefono, e.activo,
                   c.nombre as centro_nombre, a.nombre as aula_nombre
            FROM estudiantes e
            LEFT JOIN centros c ON e.centro_id = c.id
            LEFT JOIN aulas a ON e.aula_id = a.id
            WHERE 1=1
        """
        params = []
        
        # Filtro por centro
        if self.centro_filter_var.get() and self.centro_filter_var.get() != "Todos":
            query += " AND c.nombre = ?"
            params.append(self.centro_filter_var.get())
        
        # Filtro por aula
        if self.aula_filter_var.get() and self.aula_filter_var.get() != "Todas":
            query += " AND a.nombre = ?"
            params.append(self.aula_filter_var.get())
        
        query += " ORDER BY e.apellidos, e.nombre"
        
        # Obtener estudiantes
        students = database.fetch_all(query, tuple(params) if params else None)
        
        # Agregar a tabla
        for student in students:
            estado = "Activo" if student['activo'] else "Inactivo"
            self.tree.insert("", tk.END, values=(
                student['id'],
                student['nombre'],
                student['apellidos'],
                student['centro_nombre'] or "",
                student['aula_nombre'] or "",
                student['fecha_nacimiento'] or "",
                student['telefono'] or "",
                estado
            ))
    
    def new_student(self):
        """Crear nuevo estudiante"""
        StudentDialog(self.parent, self.reload_data)
    
    def reload_data(self):
        """Recargar filtros y estudiantes"""
        self.load_filters()
        self.load_students()
    
    def edit_student(self):
        """Editar estudiante seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un estudiante")
            return
        
        item = self.tree.item(selection[0])
        student_id = item['values'][0]
        
        StudentDialog(self.parent, self.reload_data, student_id)
    
    def delete_student(self):
        """Eliminar estudiante seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un estudiante")
            return
        
        item = self.tree.item(selection[0])
        student_id = item['values'][0]
        student_name = f"{item['values'][1]} {item['values'][2]}"
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro de eliminar a {student_name}?"):
            database.execute_query("DELETE FROM estudiantes WHERE id = ?", (student_id,))
            self.load_students()
            messagebox.showinfo("Éxito", "Estudiante eliminado correctamente")


class StudentDialog:
    """Diálogo para crear/editar estudiante"""
    
    def __init__(self, parent, callback, student_id=None):
        self.callback = callback
        self.student_id = student_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Estudiante" if student_id is None else "Editar Estudiante")
        self.dialog.geometry("500x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set icon
        self._set_icon()
        
        self.setup_ui()
        
        if student_id:
            self.load_student_data()
    
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
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        row = 0
        
        ttk.Label(main_frame, text="Nombre:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.nombre_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Apellidos:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.apellidos_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.apellidos_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Centro:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.centro_var = tk.StringVar()
        self.centro_combo = ttk.Combobox(main_frame, textvariable=self.centro_var, 
                                        width=38, state="readonly")
        self.centro_combo.grid(row=row, column=1, pady=5, sticky=tk.EW)
        
        # Cargar centros
        centros = database.fetch_all("SELECT id, nombre FROM centros ORDER BY nombre")
        self.centros_dict = {f"{c['nombre']}": c['id'] for c in centros}
        self.centro_combo['values'] = [""] + list(self.centros_dict.keys())
        row += 1
        
        ttk.Label(main_frame, text="Aula:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.aula_var = tk.StringVar()
        self.aula_combo = ttk.Combobox(main_frame, textvariable=self.aula_var, 
                                      width=38, state="readonly")
        self.aula_combo.grid(row=row, column=1, pady=5, sticky=tk.EW)
        
        # Cargar aulas
        aulas = database.fetch_all("SELECT id, nombre FROM aulas ORDER BY nombre")
        self.aulas_dict = {f"{a['nombre']}": a['id'] for a in aulas}
        self.aula_combo['values'] = [""] + list(self.aulas_dict.keys())
        row += 1
        
        ttk.Label(main_frame, text="F. Nacimiento:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.fecha_nac_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.fecha_nac_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=("Arial", 8)).grid(
            row=row, column=2, sticky=tk.W, padx=5)
        row += 1
        
        ttk.Label(main_frame, text="Dirección:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.direccion_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.direccion_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Teléfono:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.telefono_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.telefono_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Email Familia:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.email_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Notas:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.notas_text = tk.Text(main_frame, width=40, height=5)
        self.notas_text.grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Estado:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.activo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Activo", variable=self.activo_var).grid(
            row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
    
    def load_student_data(self):
        """Cargar datos del estudiante"""
        student = database.fetch_one(
            "SELECT * FROM estudiantes WHERE id = ?", (self.student_id,)
        )
        
        if student:
            self.nombre_var.set(student['nombre'])
            self.apellidos_var.set(student['apellidos'])
            self.fecha_nac_var.set(student['fecha_nacimiento'] or "")
            self.direccion_var.set(student['direccion'] or "")
            self.telefono_var.set(student['telefono'] or "")
            self.email_var.set(student['email_familia'] or "")
            self.notas_text.insert("1.0", student['notas'] or "")
            self.activo_var.set(bool(student['activo']))
            
            # Seleccionar centro
            if student['centro_id']:
                centro = database.fetch_one("SELECT nombre FROM centros WHERE id = ?", (student['centro_id'],))
                if centro:
                    self.centro_var.set(centro['nombre'])
            
            # Seleccionar aula
            if student['aula_id']:
                aula = database.fetch_one("SELECT nombre FROM aulas WHERE id = ?", (student['aula_id'],))
                if aula:
                    self.aula_var.set(aula['nombre'])
    
    def save(self):
        """Guardar estudiante"""
        # Validar campos requeridos
        if not self.nombre_var.get() or not self.apellidos_var.get():
            messagebox.showerror("Error", "Nombre y apellidos son obligatorios")
            return
        
        # Obtener centro_id y aula_id
        centro_id = None
        if self.centro_var.get():
            centro_id = self.centros_dict.get(self.centro_var.get())
        
        aula_id = None
        if self.aula_var.get():
            aula_id = self.aulas_dict.get(self.aula_var.get())
        
        # Preparar datos
        data = {
            'nombre': self.nombre_var.get(),
            'apellidos': self.apellidos_var.get(),
            'fecha_nacimiento': self.fecha_nac_var.get() or None,
            'direccion': self.direccion_var.get() or None,
            'telefono': self.telefono_var.get() or None,
            'email_familia': self.email_var.get() or None,
            'notas': self.notas_text.get("1.0", tk.END).strip() or None,
            'activo': 1 if self.activo_var.get() else 0,
            'centro_id': centro_id,
            'aula_id': aula_id
        }
        
        try:
            if self.student_id:
                # Actualizar
                database.execute_query("""
                    UPDATE estudiantes 
                    SET nombre=?, apellidos=?, fecha_nacimiento=?, direccion=?, 
                        telefono=?, email_familia=?, notas=?, activo=?, centro_id=?, aula_id=?
                    WHERE id=?
                """, (data['nombre'], data['apellidos'], data['fecha_nacimiento'],
                     data['direccion'], data['telefono'], data['email_familia'],
                     data['notas'], data['activo'], data['centro_id'], data['aula_id'], 
                     self.student_id))
            else:
                # Crear nuevo
                database.execute_query("""
                    INSERT INTO estudiantes 
                    (nombre, apellidos, fecha_nacimiento, direccion, telefono, email_familia, notas, activo, centro_id, aula_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['nombre'], data['apellidos'], data['fecha_nacimiento'],
                     data['direccion'], data['telefono'], data['email_familia'],
                     data['notas'], data['activo'], data['centro_id'], data['aula_id']))
            
            messagebox.showinfo("Éxito", "Estudiante guardado correctamente")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
