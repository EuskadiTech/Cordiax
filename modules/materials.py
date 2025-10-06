# -*- coding: utf-8 -*-
"""
Módulo de Materiales Escolares
Gestión CRUD de materiales con control de inventario
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules import database


class MaterialsModule:
    """Módulo de gestión de materiales escolares"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_materials()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Materiales Escolares", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de botones
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Nuevo Material", 
                  command=self.new_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", 
                  command=self.edit_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.delete_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", 
                  command=self.load_materials).pack(side=tk.LEFT, padx=5)
        
        # Frame de tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("ID", "Nombre", "Categoría", "Cantidad", "Mínimo", "Unidad", "Estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=200)
        self.tree.column("Categoría", width=120)
        self.tree.column("Cantidad", width=80)
        self.tree.column("Mínimo", width=80)
        self.tree.column("Unidad", width=80)
        self.tree.column("Estado", width=120)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configurar colores para estado
        self.tree.tag_configure("bajo", background="#ffcccc")
        self.tree.tag_configure("normal", background="#ccffcc")
        
    def load_materials(self):
        """Cargar materiales desde la base de datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener materiales
        materials = database.fetch_all("""
            SELECT id, nombre, categoria, cantidad, cantidad_minima, unidad 
            FROM materiales 
            ORDER BY nombre
        """)
        
        # Agregar a tabla
        for material in materials:
            cantidad = material['cantidad'] or 0
            minimo = material['cantidad_minima'] or 0
            
            if cantidad <= minimo:
                estado = "⚠️ Bajo mínimo"
                tag = "bajo"
            else:
                estado = "✓ Normal"
                tag = "normal"
            
            self.tree.insert("", tk.END, values=(
                material['id'],
                material['nombre'],
                material['categoria'] or "",
                cantidad,
                minimo,
                material['unidad'] or "",
                estado
            ), tags=(tag,))
    
    def new_material(self):
        """Crear nuevo material"""
        MaterialDialog(self.parent, self.load_materials)
    
    def edit_material(self):
        """Editar material seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un material")
            return
        
        item = self.tree.item(selection[0])
        material_id = item['values'][0]
        
        MaterialDialog(self.parent, self.load_materials, material_id)
    
    def delete_material(self):
        """Eliminar material seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un material")
            return
        
        item = self.tree.item(selection[0])
        material_id = item['values'][0]
        material_name = item['values'][1]
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro de eliminar {material_name}?"):
            database.execute_query("DELETE FROM materiales WHERE id = ?", (material_id,))
            self.load_materials()
            messagebox.showinfo("Éxito", "Material eliminado correctamente")


class MaterialDialog:
    """Diálogo para crear/editar material"""
    
    def __init__(self, parent, callback, material_id=None):
        self.callback = callback
        self.material_id = material_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Material" if material_id is None else "Editar Material")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        if material_id:
            self.load_material_data()
    
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        ttk.Label(main_frame, text="Nombre:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.nombre_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Categoría:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.categoria_var = tk.StringVar()
        categorias = ["Papelería", "Útiles", "Limpieza", "Didáctico", "Tecnología", "Otro"]
        ttk.Combobox(main_frame, textvariable=self.categoria_var, values=categorias, 
                    width=37).grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Cantidad:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cantidad_var = tk.IntVar(value=0)
        ttk.Spinbox(main_frame, from_=0, to=10000, textvariable=self.cantidad_var, 
                   width=38).grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Cantidad Mínima:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.minimo_var = tk.IntVar(value=0)
        ttk.Spinbox(main_frame, from_=0, to=1000, textvariable=self.minimo_var, 
                   width=38).grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        ttk.Label(main_frame, text="Unidad:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.unidad_var = tk.StringVar()
        unidades = ["Unidades", "Cajas", "Paquetes", "Litros", "Kilogramos", "Metros"]
        ttk.Combobox(main_frame, textvariable=self.unidad_var, values=unidades, 
                    width=37).grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
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
    
    def load_material_data(self):
        """Cargar datos del material"""
        material = database.fetch_one(
            "SELECT * FROM materiales WHERE id = ?", (self.material_id,)
        )
        
        if material:
            self.nombre_var.set(material['nombre'])
            self.categoria_var.set(material['categoria'] or "")
            self.cantidad_var.set(material['cantidad'] or 0)
            self.minimo_var.set(material['cantidad_minima'] or 0)
            self.unidad_var.set(material['unidad'] or "")
            self.notas_text.insert("1.0", material['notas'] or "")
    
    def save(self):
        """Guardar material"""
        if not self.nombre_var.get():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            if self.material_id:
                # Actualizar
                database.execute_query("""
                    UPDATE materiales 
                    SET nombre=?, categoria=?, cantidad=?, cantidad_minima=?, 
                        unidad=?, notas=?
                    WHERE id=?
                """, (self.nombre_var.get(), self.categoria_var.get() or None,
                     self.cantidad_var.get(), self.minimo_var.get(),
                     self.unidad_var.get() or None,
                     self.notas_text.get("1.0", tk.END).strip() or None,
                     self.material_id))
            else:
                # Crear nuevo
                database.execute_query("""
                    INSERT INTO materiales 
                    (nombre, categoria, cantidad, cantidad_minima, unidad, notas)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.nombre_var.get(), self.categoria_var.get() or None,
                     self.cantidad_var.get(), self.minimo_var.get(),
                     self.unidad_var.get() or None,
                     self.notas_text.get("1.0", tk.END).strip() or None))
            
            messagebox.showinfo("Éxito", "Material guardado correctamente")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
