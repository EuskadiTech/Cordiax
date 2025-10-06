# -*- coding: utf-8 -*-
"""
Módulo de Asistencia
Gestión de asistencia de estudiantes con check-in y notas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules import database
from datetime import datetime, date
import os
import sys


class AssistanceModule:
    """Módulo de gestión de asistencia"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_assistance()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Asistencia de Estudiantes", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de controles
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Selector de fecha
        ttk.Label(control_frame, text="Fecha:").pack(side=tk.LEFT, padx=5)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(control_frame, textvariable=self.date_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Hoy", 
                  command=lambda: self.date_var.set(date.today().strftime("%Y-%m-%d"))).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Buscar", 
                  command=self.load_assistance).pack(side=tk.LEFT, padx=5)
        
        # Frame de filtros
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Centro:").pack(side=tk.LEFT, padx=5)
        self.centro_filter_var = tk.StringVar(value="")
        self.centro_filter_combo = ttk.Combobox(filter_frame, textvariable=self.centro_filter_var, 
                                                width=20, state="readonly")
        self.centro_filter_combo.pack(side=tk.LEFT, padx=5)
        self.centro_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_assistance())
        
        ttk.Label(filter_frame, text="Aula:").pack(side=tk.LEFT, padx=5)
        self.aula_filter_var = tk.StringVar(value="")
        self.aula_filter_combo = ttk.Combobox(filter_frame, textvariable=self.aula_filter_var, 
                                              width=20, state="readonly")
        self.aula_filter_combo.pack(side=tk.LEFT, padx=5)
        self.aula_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_assistance())
        
        # Cargar filtros
        self.load_filters()
        
        # Frame de botones
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Registrar Asistencia", 
                  command=self.new_assistance).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", 
                  command=self.edit_assistance).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.delete_assistance).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Check-in Rápido", 
                  command=self.quick_checkin).pack(side=tk.LEFT, padx=5)
        
        # Frame de tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("ID", "Estudiante", "Centro", "Aula", "Fecha", "Estado", "Entrada", "Salida", "Notas")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("ID", width=40)
        self.tree.column("Estudiante", width=150)
        self.tree.column("Centro", width=120)
        self.tree.column("Aula", width=80)
        self.tree.column("Fecha", width=90)
        self.tree.column("Estado", width=80)
        self.tree.column("Entrada", width=70)
        self.tree.column("Salida", width=70)
        self.tree.column("Notas", width=150)
        
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
        
    def load_assistance(self):
        """Cargar asistencia de la fecha seleccionada"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener asistencia
        fecha = self.date_var.get()
        
        # Construir consulta con filtros
        query = """
            SELECT a.id, e.nombre, e.apellidos, a.fecha, a.estado, 
                   a.hora_entrada, a.hora_salida, a.notas,
                   c.nombre as centro_nombre, au.nombre as aula_nombre
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
        
        query += " ORDER BY e.apellidos, e.nombre"
        
        records = database.fetch_all(query, tuple(params))
        
        # Agregar a tabla
        for record in records:
            self.tree.insert("", tk.END, values=(
                record['id'],
                f"{record['nombre']} {record['apellidos']}",
                record['centro_nombre'] or "",
                record['aula_nombre'] or "",
                record['fecha'],
                record['estado'],
                record['hora_entrada'] or "",
                record['hora_salida'] or "",
                record['notas'] or ""
            ))
    
    def new_assistance(self):
        """Registrar nueva asistencia"""
        AssistanceDialog(self.parent, self.load_assistance, self.date_var.get())
    
    def edit_assistance(self):
        """Editar asistencia seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro")
            return
        
        item = self.tree.item(selection[0])
        assistance_id = item['values'][0]
        
        AssistanceDialog(self.parent, self.load_assistance, self.date_var.get(), assistance_id)
    
    def delete_assistance(self):
        """Eliminar asistencia seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro")
            return
        
        item = self.tree.item(selection[0])
        assistance_id = item['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este registro?"):
            database.execute_query("DELETE FROM asistencia WHERE id = ?", (assistance_id,))
            self.load_assistance()
            messagebox.showinfo("Éxito", "Registro eliminado correctamente")
    
    def quick_checkin(self):
        """Check-in rápido para todos los estudiantes activos"""
        fecha = self.date_var.get()
        hora_actual = datetime.now().strftime("%H:%M:%S")
        
        # Construir consulta con filtros
        query = """
            SELECT e.id, e.nombre, e.apellidos 
            FROM estudiantes e
            LEFT JOIN centros c ON e.centro_id = c.id
            LEFT JOIN aulas au ON e.aula_id = au.id
            WHERE e.activo = 1
            AND e.id NOT IN (
                SELECT estudiante_id FROM asistencia WHERE fecha = ?
            )
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
        
        students = database.fetch_all(query, tuple(params))
        
        if not students:
            messagebox.showinfo("Información", "Todos los estudiantes ya tienen registro de asistencia")
            return
        
        # Registrar asistencia para todos
        for student in students:
            database.execute_query("""
                INSERT INTO asistencia (estudiante_id, fecha, estado, hora_entrada)
                VALUES (?, ?, ?, ?)
            """, (student['id'], fecha, "Presente", hora_actual))
        
        self.load_assistance()
        messagebox.showinfo("Éxito", f"Check-in completado para {len(students)} estudiantes")


class AssistanceDialog:
    """Diálogo para registrar/editar asistencia"""
    
    def __init__(self, parent, callback, fecha, assistance_id=None):
        self.callback = callback
        self.fecha = fecha
        self.assistance_id = assistance_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Registrar Asistencia" if assistance_id is None else "Editar Asistencia")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set icon
        self._set_icon()
        
        self.setup_ui()
        
        if assistance_id:
            self.load_assistance_data()
    
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
        
        # Fecha
        ttk.Label(main_frame, text="Fecha:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.fecha_var = tk.StringVar(value=self.fecha)
        ttk.Entry(main_frame, textvariable=self.fecha_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        # Estado
        ttk.Label(main_frame, text="Estado:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.estado_var = tk.StringVar(value="Presente")
        estados = ["Presente", "Ausente", "Tardanza", "Permiso"]
        ttk.Combobox(main_frame, textvariable=self.estado_var, values=estados,
                    width=37, state="readonly").grid(row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        # Hora entrada
        ttk.Label(main_frame, text="Hora Entrada:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entrada_var = tk.StringVar(value=datetime.now().strftime("%H:%M:%S"))
        ttk.Entry(main_frame, textvariable=self.entrada_var, width=40).grid(
            row=row, column=1, pady=5, sticky=tk.EW)
        row += 1
        
        # Hora salida
        ttk.Label(main_frame, text="Hora Salida:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.salida_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.salida_var, width=40).grid(
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
    
    def load_assistance_data(self):
        """Cargar datos de asistencia"""
        record = database.fetch_one("""
            SELECT a.*, e.nombre, e.apellidos
            FROM asistencia a
            JOIN estudiantes e ON a.estudiante_id = e.id
            WHERE a.id = ?
        """, (self.assistance_id,))
        
        if record:
            # Buscar y seleccionar estudiante
            student_name = f"{record['nombre']} {record['apellidos']}"
            for i, (sid, sname) in enumerate(self.student_list):
                if sid == record['estudiante_id']:
                    self.student_combo.current(i)
                    break
            
            self.fecha_var.set(record['fecha'])
            self.estado_var.set(record['estado'])
            self.entrada_var.set(record['hora_entrada'] or "")
            self.salida_var.set(record['hora_salida'] or "")
            self.notas_text.insert("1.0", record['notas'] or "")
    
    def save(self):
        """Guardar asistencia"""
        if not self.student_var.get():
            messagebox.showerror("Error", "Por favor, seleccione un estudiante")
            return
        
        # Obtener ID del estudiante seleccionado
        student_index = self.student_combo.current()
        student_id = self.student_list[student_index][0]
        
        try:
            if self.assistance_id:
                # Actualizar
                database.execute_query("""
                    UPDATE asistencia 
                    SET estudiante_id=?, fecha=?, estado=?, hora_entrada=?, 
                        hora_salida=?, notas=?
                    WHERE id=?
                """, (student_id, self.fecha_var.get(), self.estado_var.get(),
                     self.entrada_var.get() or None, self.salida_var.get() or None,
                     self.notas_text.get("1.0", tk.END).strip() or None,
                     self.assistance_id))
            else:
                # Crear nuevo
                database.execute_query("""
                    INSERT INTO asistencia 
                    (estudiante_id, fecha, estado, hora_entrada, hora_salida, notas)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (student_id, self.fecha_var.get(), self.estado_var.get(),
                     self.entrada_var.get() or None, self.salida_var.get() or None,
                     self.notas_text.get("1.0", tk.END).strip() or None))
            
            messagebox.showinfo("Éxito", "Asistencia guardada correctamente")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
