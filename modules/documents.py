# -*- coding: utf-8 -*-
"""
Módulo de Documentos
Gestión de archivos Word, Excel, PowerPoint
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from modules import database
import shutil
import os
from pathlib import Path


class DocumentsModule:
    """Módulo de gestión de documentos"""
    
    def __init__(self, parent):
        self.parent = parent
        self.documents_dir = database.USER_DATA_DIR / "documentos"
        self.setup_ui()
        self.load_documents()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Documentos", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de botones
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Importar Documento", 
                  command=self.import_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Abrir", 
                  command=self.open_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.delete_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", 
                  command=self.load_documents).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Abrir Carpeta", 
                  command=self.open_folder).pack(side=tk.LEFT, padx=5)
        
        # Frame de tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("Nombre", "Tipo", "Tamaño", "Fecha Modificación")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("Nombre", width=300)
        self.tree.column("Tipo", width=120)
        self.tree.column("Tamaño", width=100)
        self.tree.column("Fecha Modificación", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Instrucciones
        info_frame = ttk.Frame(self.parent)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_label = ttk.Label(info_frame, 
                              text="Tipos soportados: Word (.docx), Excel (.xlsx), PowerPoint (.pptx)",
                              font=("Arial", 9, "italic"))
        info_label.pack(anchor=tk.W)
        
    def load_documents(self):
        """Cargar documentos desde la carpeta"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Listar archivos en el directorio de documentos
        if not self.documents_dir.exists():
            return
        
        supported_extensions = ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt', '.pdf']
        
        for file_path in sorted(self.documents_dir.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                # Obtener información del archivo
                stat = file_path.stat()
                size_kb = stat.st_size / 1024
                
                if size_kb < 1024:
                    size_str = f"{size_kb:.1f} KB"
                else:
                    size_str = f"{size_kb/1024:.1f} MB"
                
                # Tipo de archivo
                tipo_dict = {
                    '.docx': 'Word', '.doc': 'Word',
                    '.xlsx': 'Excel', '.xls': 'Excel',
                    '.pptx': 'PowerPoint', '.ppt': 'PowerPoint',
                    '.pdf': 'PDF'
                }
                tipo = tipo_dict.get(file_path.suffix.lower(), 'Otro')
                
                # Fecha de modificación
                from datetime import datetime
                mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                
                self.tree.insert("", tk.END, values=(
                    file_path.name,
                    tipo,
                    size_str,
                    mod_time
                ))
    
    def import_document(self):
        """Importar un documento"""
        filetypes = [
            ("Documentos", "*.docx *.xlsx *.pptx *.doc *.xls *.ppt *.pdf"),
            ("Word", "*.docx *.doc"),
            ("Excel", "*.xlsx *.xls"),
            ("PowerPoint", "*.pptx *.ppt"),
            ("PDF", "*.pdf"),
            ("Todos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Seleccionar documento",
            filetypes=filetypes
        )
        
        if not filename:
            return
        
        try:
            source = Path(filename)
            destination = self.documents_dir / source.name
            
            # Si ya existe, preguntar
            if destination.exists():
                if not messagebox.askyesno("Confirmar", 
                                          f"El archivo {source.name} ya existe. ¿Reemplazar?"):
                    return
            
            shutil.copy2(filename, destination)
            self.load_documents()
            messagebox.showinfo("Éxito", "Documento importado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar documento: {str(e)}")
    
    def open_document(self):
        """Abrir documento seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un documento")
            return
        
        item = self.tree.item(selection[0])
        filename = item['values'][0]
        file_path = self.documents_dir / filename
        
        try:
            # Abrir con la aplicación predeterminada del sistema
            import platform
            if platform.system() == 'Windows':
                os.startfile(str(file_path))
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{file_path}"')
            else:  # Linux
                os.system(f'xdg-open "{file_path}"')
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir documento: {str(e)}")
    
    def delete_document(self):
        """Eliminar documento seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un documento")
            return
        
        item = self.tree.item(selection[0])
        filename = item['values'][0]
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro de eliminar {filename}?"):
            file_path = self.documents_dir / filename
            try:
                file_path.unlink()
                self.load_documents()
                messagebox.showinfo("Éxito", "Documento eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def open_folder(self):
        """Abrir carpeta de documentos"""
        try:
            import platform
            if platform.system() == 'Windows':
                os.startfile(str(self.documents_dir))
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{self.documents_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{self.documents_dir}"')
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir carpeta: {str(e)}")
