# -*- coding: utf-8 -*-
"""
Módulo de Menú de Cafetería
Gestión CRUD del menú diario de la cafetería
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules import database
from datetime import date, timedelta


class CafeteriaModule:
    """Módulo de gestión de menú de cafetería"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_menus()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Menú de Cafetería", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de controles
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Desde:").pack(side=tk.LEFT, padx=5)
        self.date_from_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(control_frame, textvariable=self.date_from_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Hasta:").pack(side=tk.LEFT, padx=5)
        fecha_hasta = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.date_to_var = tk.StringVar(value=fecha_hasta)
        ttk.Entry(control_frame, textvariable=self.date_to_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Buscar", 
                  command=self.load_menus).pack(side=tk.LEFT, padx=5)
        
        # Frame de botones
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Nuevo Plato", 
                  command=self.new_menu).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", 
                  command=self.edit_menu).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.delete_menu).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", 
                  command=self.load_menus).pack(side=tk.LEFT, padx=5)
        
        # Frame de tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("ID", "Fecha", "Tipo", "Plato", "Descripción", "Alérgenos")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("ID", width=50)
        self.tree.column("Fecha", width=100)
        self.tree.column("Tipo", width=100)
        self.tree.column("Plato", width=200)
        self.tree.column("Descripción", width=250)
        self.tree.column("Alérgenos", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def load_menus(self):
        """Cargar menús del rango de fechas"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener menús
        menus = database.fetch_all("""
            SELECT id, fecha, tipo_comida, plato, descripcion, alergenos
            FROM menu_cafeteria
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha, tipo_comida
        """, (self.date_from_var.get(), self.date_to_var.get()))
        
        # Agregar a tabla
        for menu in menus:
            self.tree.insert("", tk.END, values=(
                menu['id'],
                menu['fecha'],
                menu['tipo_comida'],
                menu['plato'],
                menu['descripcion'] or "",
                menu['alergenos'] or ""
            ))
    
    def new_menu(self):
        """Crear nuevo menú"""
        MenuDialog(self.parent, self.load_menus)
    
    def edit_menu(self):
        """Editar menú seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un plato")
            return
        
        item = self.tree.item(selection[0])
        menu_id = item['values'][0]
        
        MenuDialog(self.parent, self.load_menus, menu_id)
    
    def delete_menu(self):
        """Eliminar menú seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un plato")
            return
        
        item = self.tree.item(selection[0])
        menu_id = item['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este plato?"):
            database.execute_query("DELETE FROM menu_cafeteria WHERE id = ?", (menu_id,))
            self.load_menus()
            messagebox.showinfo("Éxito", "Plato eliminado correctamente")


class MenuDialog:
    """Diálogo para crear/editar menú"""
    
    def __init__(self, parent, callback, menu_id=None):
        self.callback = callback
        self.menu_id = menu_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Plato" if menu_id is None else "Editar Plato")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        if menu_id:
            self.load_menu_data()
    
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        ttk.Label(main_frame, text="Fecha:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.fecha_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(main_frame, textvariable=self.fecha_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Tipo de Comida:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tipo_var = tk.StringVar()
        tipos = ["Desayuno", "Almuerzo", "Merienda", "Cena"]
        ttk.Combobox(main_frame, textvariable=self.tipo_var, values=tipos, 
                    width=37, state="readonly").grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Plato:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.plato_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.plato_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.descripcion_text = tk.Text(main_frame, width=40, height=4)
        self.descripcion_text.grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Alérgenos:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.alergenos_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.alergenos_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        ttk.Label(main_frame, text="(gluten, lácteos, frutos secos...)", 
                 font=("Arial", 8)).grid(row=row, column=2, sticky=tk.W, padx=5)
        row += 1
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
    
    def load_menu_data(self):
        """Cargar datos del menú"""
        menu = database.fetch_one(
            "SELECT * FROM menu_cafeteria WHERE id = ?", (self.menu_id,)
        )
        
        if menu:
            self.fecha_var.set(menu['fecha'])
            self.tipo_var.set(menu['tipo_comida'])
            self.plato_var.set(menu['plato'])
            self.descripcion_text.insert("1.0", menu['descripcion'] or "")
            self.alergenos_var.set(menu['alergenos'] or "")
    
    def save(self):
        """Guardar menú"""
        if not self.tipo_var.get() or not self.plato_var.get():
            messagebox.showerror("Error", "Tipo de comida y plato son obligatorios")
            return
        
        try:
            if self.menu_id:
                # Actualizar
                database.execute_query("""
                    UPDATE menu_cafeteria 
                    SET fecha=?, tipo_comida=?, plato=?, descripcion=?, alergenos=?
                    WHERE id=?
                """, (self.fecha_var.get(), self.tipo_var.get(), self.plato_var.get(),
                     self.descripcion_text.get("1.0", tk.END).strip() or None,
                     self.alergenos_var.get() or None, self.menu_id))
            else:
                # Crear nuevo
                database.execute_query("""
                    INSERT INTO menu_cafeteria 
                    (fecha, tipo_comida, plato, descripcion, alergenos)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.fecha_var.get(), self.tipo_var.get(), self.plato_var.get(),
                     self.descripcion_text.get("1.0", tk.END).strip() or None,
                     self.alergenos_var.get() or None))
            
            messagebox.showinfo("Éxito", "Menú guardado correctamente")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
