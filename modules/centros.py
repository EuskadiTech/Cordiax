# -*- coding: utf-8 -*-
"""
Módulo de Centros
Gestión CRUD de centros escolares
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules import database
import os
import sys


class CentrosModule:
    """Módulo de gestión de centros"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_centros()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Gestión de Centros", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de botones
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Nuevo Centro", 
                  command=self.new_centro).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", 
                  command=self.edit_centro).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.delete_centro).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", 
                  command=self.load_centros).pack(side=tk.LEFT, padx=5)
        
        # Frame de tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("ID", "Nombre", "Dirección", "Teléfono", "Email")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Dirección", text="Dirección")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Email", text="Email")
        
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=200)
        self.tree.column("Dirección", width=250)
        self.tree.column("Teléfono", width=120)
        self.tree.column("Email", width=180)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def load_centros(self):
        """Cargar centros desde la base de datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener centros
        centros = database.fetch_all(
            "SELECT id, nombre, direccion, telefono, email FROM centros ORDER BY nombre"
        )
        
        # Agregar a tabla
        for centro in centros:
            self.tree.insert("", tk.END, values=(
                centro['id'],
                centro['nombre'],
                centro['direccion'] or "",
                centro['telefono'] or "",
                centro['email'] or ""
            ))
    
    def new_centro(self):
        """Crear nuevo centro"""
        CentroDialog(self.parent, self.load_centros)
    
    def edit_centro(self):
        """Editar centro seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un centro")
            return
        
        item = self.tree.item(selection[0])
        centro_id = item['values'][0]
        
        CentroDialog(self.parent, self.load_centros, centro_id)
    
    def delete_centro(self):
        """Eliminar centro seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un centro")
            return
        
        item = self.tree.item(selection[0])
        centro_id = item['values'][0]
        centro_name = item['values'][1]
        
        # Verificar si hay aulas asociadas
        aulas = database.fetch_all("SELECT COUNT(*) as count FROM aulas WHERE centro_id = ?", (centro_id,))
        if aulas and aulas[0]['count'] > 0:
            messagebox.showwarning("Advertencia", 
                                 f"No se puede eliminar el centro '{centro_name}' porque tiene aulas asociadas.")
            return
        
        # Verificar si hay estudiantes asociados
        estudiantes = database.fetch_all("SELECT COUNT(*) as count FROM estudiantes WHERE centro_id = ?", (centro_id,))
        if estudiantes and estudiantes[0]['count'] > 0:
            messagebox.showwarning("Advertencia", 
                                 f"No se puede eliminar el centro '{centro_name}' porque tiene estudiantes asociados.")
            return
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro de eliminar el centro '{centro_name}'?"):
            database.execute_query("DELETE FROM centros WHERE id = ?", (centro_id,))
            self.load_centros()
            messagebox.showinfo("Éxito", "Centro eliminado correctamente")


class CentroDialog:
    """Diálogo para crear/editar centro"""
    
    def __init__(self, parent, callback, centro_id=None):
        self.callback = callback
        self.centro_id = centro_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Centro" if centro_id is None else "Editar Centro")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set icon
        self._set_icon()
        
        self.setup_ui()
        
        if centro_id:
            self.load_centro_data()
    
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
        
        ttk.Label(main_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.email_var, width=40).grid(
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
    
    def load_centro_data(self):
        """Cargar datos del centro"""
        centro = database.fetch_one(
            "SELECT * FROM centros WHERE id = ?", (self.centro_id,)
        )
        
        if centro:
            self.nombre_var.set(centro['nombre'])
            self.direccion_var.set(centro['direccion'] or "")
            self.telefono_var.set(centro['telefono'] or "")
            self.email_var.set(centro['email'] or "")
            self.notas_text.insert("1.0", centro['notas'] or "")
    
    def save(self):
        """Guardar centro"""
        # Validar campos requeridos
        if not self.nombre_var.get():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        # Preparar datos
        data = {
            'nombre': self.nombre_var.get(),
            'direccion': self.direccion_var.get() or None,
            'telefono': self.telefono_var.get() or None,
            'email': self.email_var.get() or None,
            'notas': self.notas_text.get("1.0", tk.END).strip() or None
        }
        
        try:
            if self.centro_id:
                # Actualizar
                database.execute_query("""
                    UPDATE centros 
                    SET nombre=?, direccion=?, telefono=?, email=?, notas=?
                    WHERE id=?
                """, (data['nombre'], data['direccion'], data['telefono'],
                     data['email'], data['notas'], self.centro_id))
            else:
                # Crear nuevo
                database.execute_query("""
                    INSERT INTO centros 
                    (nombre, direccion, telefono, email, notas)
                    VALUES (?, ?, ?, ?, ?)
                """, (data['nombre'], data['direccion'], data['telefono'],
                     data['email'], data['notas']))
            
            messagebox.showinfo("Éxito", "Centro guardado correctamente")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
