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
        columns = ("ID", "Nombre", "Apellidos", "F. Nacimiento", "Teléfono", "Estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Apellidos", text="Apellidos")
        self.tree.heading("F. Nacimiento", text="F. Nacimiento")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Estado", text="Estado")
        
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=150)
        self.tree.column("Apellidos", width=150)
        self.tree.column("F. Nacimiento", width=100)
        self.tree.column("Teléfono", width=100)
        self.tree.column("Estado", width=80)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def load_students(self):
        """Cargar estudiantes desde la base de datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener estudiantes
        students = database.fetch_all(
            "SELECT id, nombre, apellidos, fecha_nacimiento, telefono, activo FROM estudiantes ORDER BY apellidos, nombre"
        )
        
        # Agregar a tabla
        for student in students:
            estado = "Activo" if student['activo'] else "Inactivo"
            self.tree.insert("", tk.END, values=(
                student['id'],
                student['nombre'],
                student['apellidos'],
                student['fecha_nacimiento'] or "",
                student['telefono'] or "",
                estado
            ))
    
    def new_student(self):
        """Crear nuevo estudiante"""
        StudentDialog(self.parent, self.load_students)
    
    def edit_student(self):
        """Editar estudiante seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un estudiante")
            return
        
        item = self.tree.item(selection[0])
        student_id = item['values'][0]
        
        StudentDialog(self.parent, self.load_students, student_id)
    
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
        self.dialog.geometry("500x450")
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
    
    def save(self):
        """Guardar estudiante"""
        # Validar campos requeridos
        if not self.nombre_var.get() or not self.apellidos_var.get():
            messagebox.showerror("Error", "Nombre y apellidos son obligatorios")
            return
        
        # Preparar datos
        data = {
            'nombre': self.nombre_var.get(),
            'apellidos': self.apellidos_var.get(),
            'fecha_nacimiento': self.fecha_nac_var.get() or None,
            'direccion': self.direccion_var.get() or None,
            'telefono': self.telefono_var.get() or None,
            'email_familia': self.email_var.get() or None,
            'notas': self.notas_text.get("1.0", tk.END).strip() or None,
            'activo': 1 if self.activo_var.get() else 0
        }
        
        try:
            if self.student_id:
                # Actualizar
                database.execute_query("""
                    UPDATE estudiantes 
                    SET nombre=?, apellidos=?, fecha_nacimiento=?, direccion=?, 
                        telefono=?, email_familia=?, notas=?, activo=?
                    WHERE id=?
                """, (data['nombre'], data['apellidos'], data['fecha_nacimiento'],
                     data['direccion'], data['telefono'], data['email_familia'],
                     data['notas'], data['activo'], self.student_id))
            else:
                # Crear nuevo
                database.execute_query("""
                    INSERT INTO estudiantes 
                    (nombre, apellidos, fecha_nacimiento, direccion, telefono, email_familia, notas, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['nombre'], data['apellidos'], data['fecha_nacimiento'],
                     data['direccion'], data['telefono'], data['email_familia'],
                     data['notas'], data['activo']))
            
            messagebox.showinfo("Éxito", "Estudiante guardado correctamente")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
