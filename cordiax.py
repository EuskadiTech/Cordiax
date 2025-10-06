#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cordiax - Sistema de Gestión de Aula
Aplicación de gestión para aulas escolares
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from pathlib import Path

# Importar módulos de la aplicación
from modules import database
from modules.students import StudentListModule
from modules.assistance import AssistanceModule
from modules.materials import MaterialsModule
from modules.cafeteria import CafeteriaModule
from modules.daily_report import DailyReportModule
from modules.family_notes import FamilyNotesModule
from modules.permissions import PermissionsModule
from modules.documents import DocumentsModule
from modules.messages import MessagesModule
from modules.backup import BackupModule
from modules.centros import CentrosModule
from modules.aulas import AulasModule


class CordiaxApp:
    """Aplicación principal de Cordiax"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Cordiax - Gestión de Aula")
        self.root.geometry("1200x700")
        
        # Set icon for main window
        self.set_window_icon(self.root)
        
        # Configurar el directorio de datos del usuario
        self.setup_user_directory()
        
        # Inicializar la base de datos
        database.initialize_database()
        
        # Configurar la interfaz
        self.setup_ui()
    
    def set_window_icon(self, window):
        """Set icon for a window"""
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                icon_path = os.path.join(sys._MEIPASS, 'logo.ico')
            else:
                # Running as script
                icon_path = os.path.join(os.path.dirname(__file__), 'logo.ico')
            
            if os.path.exists(icon_path):
                window.iconbitmap(icon_path)
        except Exception:
            pass  # If icon fails to load, just continue
        
    def setup_user_directory(self):
        """Configurar el directorio de datos del usuario"""
        user_home = Path.home()
        self.user_data_dir = user_home / "_SuperCordiax"
        self.user_data_dir.mkdir(exist_ok=True)
        
        # Crear subdirectorios
        (self.user_data_dir / "documentos").mkdir(exist_ok=True)
        (self.user_data_dir / "backups").mkdir(exist_ok=True)
        (self.user_data_dir / "pdfs").mkdir(exist_ok=True)
        
        # Establecer rutas en el módulo de base de datos
        database.USER_DATA_DIR = self.user_data_dir
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Configure style for buttons
        style = ttk.Style()
        style.configure('Nav.TButton', 
                       font=('Arial', 11, 'bold'),
                       padding=10)
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de botones laterales with background color
        button_frame = tk.Frame(main_frame, width=220, bg='#2E86AB')
        button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        button_frame.pack_propagate(False)
        
        # Título
        title_label = tk.Label(button_frame, text="CORDIAX", 
                              font=("Arial", 20, "bold"),
                              bg='#2E86AB', fg='white')
        title_label.pack(pady=(10, 20))
        
        # Canvas y scrollbar para hacer la lista de botones scrollable
        canvas = tk.Canvas(button_frame, bg='#2E86AB', highlightthickness=0)
        scrollbar = tk.Scrollbar(button_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2E86AB')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas y scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de navegación
        self.nav_buttons = []
        modules = [
            ("Lista de Estudiantes", self.show_students),
            ("Asistencia", self.show_assistance),
            ("Materiales Escolares", self.show_materials),
            ("Menú Cafetería", self.show_cafeteria),
            ("Informe Diario", self.show_daily_report),
            ("Notas Familiares", self.show_family_notes),
            ("Permisos", self.show_permissions),
            ("Documentos", self.show_documents),
            ("Mensajes", self.show_messages),
            ("Centros", self.show_centros),
            ("Aulas", self.show_aulas),
            ("Copia de Seguridad", self.show_backup),
        ]
        
        for text, command in modules:
            btn = tk.Button(scrollable_frame, text=text, command=command, 
                          width=22, height=2,
                          font=('Arial', 10, 'bold'),
                          bg='#A23B72', fg='white',
                          activebackground='#F18F01',
                          activeforeground='white',
                          cursor='hand2',
                          relief=tk.RAISED,
                          bd=2)
            btn.pack(pady=5, padx=10, fill=tk.X)
            self.nav_buttons.append(btn)
        
        # Habilitar scroll con la rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Frame de contenido
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Mostrar módulo inicial
        self.current_module = None
        self.show_students()
        
    def clear_content(self):
        """Limpiar el frame de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_students(self):
        """Mostrar módulo de estudiantes"""
        self.clear_content()
        self.current_module = StudentListModule(self.content_frame)
        
    def show_assistance(self):
        """Mostrar módulo de asistencia"""
        self.clear_content()
        self.current_module = AssistanceModule(self.content_frame)
        
    def show_materials(self):
        """Mostrar módulo de materiales"""
        self.clear_content()
        self.current_module = MaterialsModule(self.content_frame)
        
    def show_cafeteria(self):
        """Mostrar módulo de cafetería"""
        self.clear_content()
        self.current_module = CafeteriaModule(self.content_frame)
        
    def show_daily_report(self):
        """Mostrar módulo de informe diario"""
        self.clear_content()
        self.current_module = DailyReportModule(self.content_frame)
        
    def show_family_notes(self):
        """Mostrar módulo de notas familiares"""
        self.clear_content()
        self.current_module = FamilyNotesModule(self.content_frame)
        
    def show_permissions(self):
        """Mostrar módulo de permisos"""
        self.clear_content()
        self.current_module = PermissionsModule(self.content_frame)
        
    def show_documents(self):
        """Mostrar módulo de documentos"""
        self.clear_content()
        self.current_module = DocumentsModule(self.content_frame)
        
    def show_messages(self):
        """Mostrar módulo de mensajes"""
        self.clear_content()
        self.current_module = MessagesModule(self.content_frame)
        
    def show_backup(self):
        """Mostrar módulo de copia de seguridad"""
        self.clear_content()
        self.current_module = BackupModule(self.content_frame)
    
    def show_centros(self):
        """Mostrar módulo de centros"""
        self.clear_content()
        self.current_module = CentrosModule(self.content_frame)
    
    def show_aulas(self):
        """Mostrar módulo de aulas"""
        self.clear_content()
        self.current_module = AulasModule(self.content_frame)


def main():
    """Función principal"""
    root = tk.Tk()
    app = CordiaxApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
