# -*- coding: utf-8 -*-
"""
Módulo de Aulas
Gestión CRUD de aulas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules import database
import os
import sys


class AulasModule:
    """Módulo de gestión de aulas"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_aulas()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Gestión de Aulas", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de botones
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Nueva Aula", 
                  command=self.new_aula).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", 
                  command=self.edit_aula).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.delete_aula).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", 
                  command=self.load_aulas).pack(side=tk.LEFT, padx=5)
        
        # Frame de tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("ID", "Nombre", "Centro", "Capacidad")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Centro", text="Centro")
        self.tree.heading("Capacidad", text="Capacidad")
        
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=200)
        self.tree.column("Centro", width=300)
        self.tree.column("Capacidad", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def load_aulas(self):
        """Cargar aulas desde la base de datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener aulas con información del centro
        aulas = database.fetch_all("""
            SELECT a.id, a.nombre, a.capacidad, c.nombre as centro_nombre
            FROM aulas a
            LEFT JOIN centros c ON a.centro_id = c.id
            ORDER BY c.nombre, a.nombre
        """)
        
        # Agregar a tabla
        for aula in aulas:
            self.tree.insert("", tk.END, values=(
                aula['id'],
                aula['nombre'],
                aula['centro_nombre'] or "Sin centro",
                aula['capacidad'] or ""
            ))
    
    def new_aula(self):
        """Crear nueva aula"""
        AulaDialog(self.parent, self.load_aulas)
    
    def edit_aula(self):
        """Editar aula seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un aula")
            return
        
        item = self.tree.item(selection[0])
        aula_id = item['values'][0]
        
        AulaDialog(self.parent, self.load_aulas, aula_id)
    
    def delete_aula(self):
        """Eliminar aula seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un aula")
            return
        
        item = self.tree.item(selection[0])
        aula_id = item['values'][0]
        aula_name = item['values'][1]
        
        # Verificar si hay estudiantes asociados
        estudiantes = database.fetch_all("SELECT COUNT(*) as count FROM estudiantes WHERE aula_id = ?", (aula_id,))
        if estudiantes and estudiantes[0]['count'] > 0:
            messagebox.showwarning("Advertencia", 
                                 f"No se puede eliminar el aula '{aula_name}' porque tiene estudiantes asociados.")
            return
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro de eliminar el aula '{aula_name}'?"):
            database.execute_query("DELETE FROM aulas WHERE id = ?", (aula_id,))
            self.load_aulas()
            messagebox.showinfo("Éxito", "Aula eliminada correctamente")


class AulaDialog:
    """Diálogo para crear/editar aula"""
    
    def __init__(self, parent, callback, aula_id=None):
        self.callback = callback
        self.aula_id = aula_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nueva Aula" if aula_id is None else "Editar Aula")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set icon
        self._set_icon()
        
        self.setup_ui()
        
        if aula_id:
            self.load_aula_data()
    
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
        
        ttk.Label(main_frame, text="Capacidad:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.capacidad_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.capacidad_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Notas:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.notas_text = tk.Text(main_frame, width=40, height=8)
        self.notas_text.grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
    
    def load_aula_data(self):
        """Cargar datos del aula"""
        aula = database.fetch_one(
            "SELECT * FROM aulas WHERE id = ?", (self.aula_id,)
        )
        
        if aula:
            self.nombre_var.set(aula['nombre'])
            self.capacidad_var.set(aula['capacidad'] or "")
            self.notas_text.insert("1.0", aula['notas'] or "")
            
            # Seleccionar centro
            if aula['centro_id']:
                centro = database.fetch_one("SELECT nombre FROM centros WHERE id = ?", (aula['centro_id'],))
                if centro:
                    self.centro_var.set(centro['nombre'])
    
    def save(self):
        """Guardar aula"""
        # Validar campos requeridos
        if not self.nombre_var.get():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        # Obtener centro_id
        centro_id = None
        if self.centro_var.get():
            centro_id = self.centros_dict.get(self.centro_var.get())
        
        # Preparar datos
        capacidad = None
        if self.capacidad_var.get():
            try:
                capacidad = int(self.capacidad_var.get())
            except ValueError:
                messagebox.showerror("Error", "La capacidad debe ser un número")
                return
        
        data = {
            'nombre': self.nombre_var.get(),
            'centro_id': centro_id,
            'capacidad': capacidad,
            'notas': self.notas_text.get("1.0", tk.END).strip() or None
        }
        
        try:
            if self.aula_id:
                # Actualizar
                database.execute_query("""
                    UPDATE aulas 
                    SET nombre=?, centro_id=?, capacidad=?, notas=?
                    WHERE id=?
                """, (data['nombre'], data['centro_id'], data['capacidad'],
                     data['notas'], self.aula_id))
            else:
                # Crear nueva
                database.execute_query("""
                    INSERT INTO aulas 
                    (nombre, centro_id, capacidad, notas)
                    VALUES (?, ?, ?, ?)
                """, (data['nombre'], data['centro_id'], data['capacidad'],
                     data['notas']))
            
            messagebox.showinfo("Éxito", "Aula guardada correctamente")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
