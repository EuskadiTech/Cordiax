# -*- coding: utf-8 -*-
"""
Módulo de Mensajes
Sistema de mensajes internos para estudiantes
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from modules import database
from datetime import datetime
import os
import sys


class MessagesModule:
    """Módulo de mensajes internos"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_messages()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Mensajes de Estudiantes", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de botones
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Nuevo Mensaje", 
                  command=self.new_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Ver", 
                  command=self.view_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Marcar como Leído", 
                  command=self.mark_read).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.delete_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", 
                  command=self.load_messages).pack(side=tk.LEFT, padx=5)
        
        # Frame de filtros
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filtrar:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar(value="Todos")
        ttk.Radiobutton(filter_frame, text="Todos", variable=self.filter_var, 
                       value="Todos", command=self.load_messages).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="No Leídos", variable=self.filter_var, 
                       value="No Leídos", command=self.load_messages).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Leídos", variable=self.filter_var, 
                       value="Leídos", command=self.load_messages).pack(side=tk.LEFT, padx=5)
        
        # Frame de tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("ID", "Estudiante", "Asunto", "Fecha", "Leído")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("ID", width=50)
        self.tree.column("Estudiante", width=200)
        self.tree.column("Asunto", width=300)
        self.tree.column("Fecha", width=150)
        self.tree.column("Leído", width=80)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configurar etiquetas para mensajes no leídos
        self.tree.tag_configure("unread", background="#ffffcc", font=("Arial", 10, "bold"))
        
        # Doble clic para ver mensaje
        self.tree.bind("<Double-1>", lambda e: self.view_message())
        
    def load_messages(self):
        """Cargar mensajes desde la base de datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Construir query según filtro
        filter_type = self.filter_var.get()
        
        if filter_type == "No Leídos":
            where_clause = "WHERE m.leido = 0"
        elif filter_type == "Leídos":
            where_clause = "WHERE m.leido = 1"
        else:
            where_clause = ""
        
        # Obtener mensajes
        messages = database.fetch_all(f"""
            SELECT m.id, e.nombre, e.apellidos, m.asunto, m.fecha, m.leido
            FROM mensajes m
            JOIN estudiantes e ON m.estudiante_id = e.id
            {where_clause}
            ORDER BY m.fecha DESC
        """)
        
        # Agregar a tabla
        for msg in messages:
            leido_str = "Sí" if msg['leido'] else "No"
            tag = "" if msg['leido'] else "unread"
            
            self.tree.insert("", tk.END, values=(
                msg['id'],
                f"{msg['nombre']} {msg['apellidos']}",
                msg['asunto'],
                msg['fecha'],
                leido_str
            ), tags=(tag,))
    
    def new_message(self):
        """Crear nuevo mensaje"""
        MessageDialog(self.parent, self.load_messages)
    
    def view_message(self):
        """Ver mensaje seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un mensaje")
            return
        
        item = self.tree.item(selection[0])
        message_id = item['values'][0]
        
        ViewMessageDialog(self.parent, message_id)
        
        # Marcar como leído
        database.execute_query("UPDATE mensajes SET leido = 1 WHERE id = ?", (message_id,))
        self.load_messages()
    
    def mark_read(self):
        """Marcar mensaje como leído"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un mensaje")
            return
        
        item = self.tree.item(selection[0])
        message_id = item['values'][0]
        
        database.execute_query("UPDATE mensajes SET leido = 1 WHERE id = ?", (message_id,))
        self.load_messages()
    
    def delete_message(self):
        """Eliminar mensaje seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un mensaje")
            return
        
        item = self.tree.item(selection[0])
        message_id = item['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este mensaje?"):
            database.execute_query("DELETE FROM mensajes WHERE id = ?", (message_id,))
            self.load_messages()
            messagebox.showinfo("Éxito", "Mensaje eliminado correctamente")


class MessageDialog:
    """Diálogo para crear mensaje"""
    
    def __init__(self, parent, callback):
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Mensaje")
        self.dialog.geometry("550x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set icon
        self._set_icon()
        
        self.setup_ui()
    
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
                                         width=47, state="readonly")
        self.student_combo.grid(row=row, column=1, pady=5, sticky=tk.EW)
        
        # Cargar estudiantes
        students = database.fetch_all(
            "SELECT id, nombre, apellidos FROM estudiantes WHERE activo = 1 ORDER BY apellidos, nombre"
        )
        self.student_list = [(s['id'], f"{s['nombre']} {s['apellidos']}") for s in students]
        self.student_combo['values'] = [s[1] for s in self.student_list]
        row += 1
        
        # Asunto
        ttk.Label(main_frame, text="Asunto:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.asunto_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.asunto_var, width=50).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        # Mensaje
        ttk.Label(main_frame, text="Mensaje:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.mensaje_text = scrolledtext.ScrolledText(main_frame, width=50, height=15, wrap=tk.WORD)
        self.mensaje_text.grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
    
    def save(self):
        """Guardar mensaje"""
        if not self.student_var.get() or not self.asunto_var.get():
            messagebox.showerror("Error", "Estudiante y asunto son obligatorios")
            return
        
        mensaje = self.mensaje_text.get("1.0", tk.END).strip()
        if not mensaje:
            messagebox.showerror("Error", "El mensaje no puede estar vacío")
            return
        
        # Obtener ID del estudiante seleccionado
        student_index = self.student_combo.current()
        student_id = self.student_list[student_index][0]
        
        try:
            database.execute_query("""
                INSERT INTO mensajes 
                (estudiante_id, asunto, mensaje, leido)
                VALUES (?, ?, ?, 0)
            """, (student_id, self.asunto_var.get(), mensaje))
            
            messagebox.showinfo("Éxito", "Mensaje guardado correctamente")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")


class ViewMessageDialog:
    """Diálogo para ver mensaje"""
    
    def __init__(self, parent, message_id):
        self.message_id = message_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Ver Mensaje")
        self.dialog.geometry("550x450")
        self.dialog.transient(parent)
        
        # Set icon
        self._set_icon()
        
        self.setup_ui()
        self.load_message()
    
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
        
        # Estudiante
        self.student_label = ttk.Label(main_frame, text="", font=("Arial", 12, "bold"))
        self.student_label.pack(anchor=tk.W, pady=5)
        
        # Asunto
        self.asunto_label = ttk.Label(main_frame, text="", font=("Arial", 10, "bold"))
        self.asunto_label.pack(anchor=tk.W, pady=5)
        
        # Fecha
        self.fecha_label = ttk.Label(main_frame, text="", font=("Arial", 9))
        self.fecha_label.pack(anchor=tk.W, pady=5)
        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Mensaje
        self.mensaje_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                                      font=("Arial", 10), state=tk.DISABLED)
        self.mensaje_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=self.dialog.destroy).pack(pady=10)
    
    def load_message(self):
        """Cargar datos del mensaje"""
        msg = database.fetch_one("""
            SELECT m.*, e.nombre, e.apellidos
            FROM mensajes m
            JOIN estudiantes e ON m.estudiante_id = e.id
            WHERE m.id = ?
        """, (self.message_id,))
        
        if msg:
            self.student_label.config(text=f"Estudiante: {msg['nombre']} {msg['apellidos']}")
            self.asunto_label.config(text=f"Asunto: {msg['asunto']}")
            self.fecha_label.config(text=f"Fecha: {msg['fecha']}")
            
            self.mensaje_text.config(state=tk.NORMAL)
            self.mensaje_text.insert("1.0", msg['mensaje'])
            self.mensaje_text.config(state=tk.DISABLED)
