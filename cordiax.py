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
from modules import database, encryption
from modules.unlock_dialog import UnlockDialog, EncryptionSetupDialog
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
from modules.manual import ManualModule

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
        
        # Manejar desbloqueo de base de datos encriptada
        if not self.handle_database_unlock():
            # Si el usuario cancela el desbloqueo, cerrar la aplicación
            self.root.destroy()
            return
        
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
    
    def handle_database_unlock(self):
        """Manejar el desbloqueo de la base de datos encriptada"""
        db_path = database.get_db_path()
        
        # Si la encriptación está habilitada
        if encryption.is_encryption_enabled(self.user_data_dir):
            if db_path.exists() and encryption.is_encrypted(db_path):
                # Solicitar contraseña para desbloquear
                max_attempts = 3
                for attempt in range(max_attempts):
                    dialog = UnlockDialog(self.root)
                    password = dialog.show()
                    
                    if password is None:
                        # Usuario canceló
                        return False
                    
                    # Intentar desencriptar
                    if encryption.decrypt_file(db_path, password):
                        database.set_password(password)
                        return True
                    else:
                        remaining = max_attempts - attempt - 1
                        if remaining > 0:
                            messagebox.showerror("Error", 
                                               f"Contraseña incorrecta.\n"
                                               f"Intentos restantes: {remaining}")
                        else:
                            messagebox.showerror("Error", 
                                               "Contraseña incorrecta. No se puede acceder a la base de datos.")
                            return False
        
        return True
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Configure style for buttons
        style = ttk.Style()
        style.configure('Nav.TButton', 
                       font=('Arial', 11, 'bold'),
                       padding=10)
        
        # macOS specific styling adjustments
        if sys.platform == "darwin":
            style.theme_use('aqua')
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de botones laterales with background color
        button_frame = tk.Frame(main_frame, width=280, bg='#2E86AB')
        button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0)
        button_frame.pack_propagate(False)
        
        # Header frame for logo and title
        header_frame = tk.Frame(button_frame, bg='#2E86AB')
        header_frame.pack(pady=(10, 20))
        
        # Logo
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                icon_path = os.path.join(sys._MEIPASS, 'logo.ico')
            else:
                # Running as script
                icon_path = os.path.join(os.path.dirname(__file__), 'logo.ico')
            
            if os.path.exists(icon_path):
                # Try to load and resize the icon for header display
                try:
                    from PIL import Image, ImageTk
                    logo_image = Image.open(icon_path)
                    logo_image = logo_image.resize((64, 64), Image.Resampling.LANCZOS)
                    self.logo_photo = ImageTk.PhotoImage(logo_image)
                    
                    logo_label = tk.Label(header_frame, image=self.logo_photo, bg='#2E86AB')
                    logo_label.pack(pady=(0, 5))
                except ImportError:
                    # Fallback: try to load as PhotoImage (works with some .ico files)
                    try:
                        self.logo_photo = tk.PhotoImage(file=icon_path)
                        # Scale down if needed (basic scaling)
                        self.logo_photo = self.logo_photo.subsample(2, 2)
                        
                        logo_label = tk.Label(header_frame, image=self.logo_photo, bg='#2E86AB')
                        logo_label.pack(pady=(0, 5))
                    except:
                        pass  # If all methods fail, continue without logo
        except Exception:
            pass  # If logo fails to load, just continue without it
        
        # Título
        title_label = tk.Label(header_frame, text="CORDIAX", 
                              font=("Arial", 20, "bold"),
                              bg='#2E86AB', fg='white')
        title_label.pack()
        
        # Create proper scrollable container
        scroll_container = tk.Frame(button_frame, bg='#2E86AB')
        scroll_container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbar
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create listbox for navigation items
        nav_listbox = tk.Listbox(scroll_container, 
                                bg='#2E86AB',
                                fg='white',
                                selectbackground='#F18F01',
                                selectforeground='white',
                                activestyle='none',
                                font=('Courier', 17, 'bold'),
                                relief=tk.FLAT,
                                highlightthickness=0,
                                bd=0,
                                height=12,
                                selectmode=tk.SINGLE,
                                exportselection=False,
                                yscrollcommand=scrollbar.set)
        nav_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=nav_listbox.yview)
        
        # Store reference for later use
        self.nav_listbox = nav_listbox
        
        # Navigation items and their commands
        self.nav_commands = {}
        modules = [
            ("@Inf. Diario", self.show_daily_report),
            ("", None),
            ("Datos Generales: ", None),
            ("  @Centros", self.show_centros),
            ("  @Aulas", self.show_aulas),
            ("", None),
            ("Alumnado: ", None),
            ("  @Lista", self.show_students),
            ("  @Asistencia", self.show_assistance),
            ("  @Notas Familiares", self.show_family_notes),
            ("", None),
            ("Datos temáticos: ", None),
            ("  @Almacen", self.show_materials),
            ("  @Comedor", self.show_cafeteria),
            ("", None),
            ("Otros Módulos: ", None),
            ("  @Autorizaciones", self.show_permissions),
            ("  @Documentos", self.show_documents),
            ("  @Mensajes y notas", self.show_messages),
            ("", None),
            ("@Respaldo", self.show_backup),
            ("@Manual", self.show_manual),
        ]
        
        # Add items to listbox and store commands
        for i, (text, command) in enumerate(modules):
            # Add some padding to make items look more like buttons
            padded_text = f"  {text}  "
            nav_listbox.insert(tk.END, padded_text)
            self.nav_commands[i] = command
        
        # Bind selection event
        def on_nav_select(event):
            selection = nav_listbox.curselection()
            if selection:
                index = selection[0]
                if index in self.nav_commands:
                    if self.nav_commands[index] != None:
                        self.nav_commands[index]()
                    else:
                        # If it's a non-clickable item, clear selection
                        nav_listbox.select_clear(0, tk.END)
        
        nav_listbox.bind('<<ListboxSelect>>', on_nav_select)
        
        # Set initial selection
        nav_listbox.selection_set(0)
        
        # Frame de contenido
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar el protocolo de cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Mostrar módulo inicial
        self.current_module = None
        self.show_daily_report()
    
    def on_closing(self):
        """Manejar el cierre de la aplicación"""
        try:
            # Encriptar la base de datos si es necesario
            if hasattr(database, 'get_password') and database.get_password():
                db_path = database.get_db_path()
                if db_path.exists():
                    password = database.get_password()
                    encryption.encrypt_file(db_path, password)
        except Exception as e:
            print(f"Error al encriptar la base de datos: {e}")
        finally:
            self.root.destroy()
        
    def clear_content(self):
        """Limpiar el frame de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_manual(self):
        """Mostrar módulo de manual"""
        self.clear_content()
        self.current_module = ManualModule(self.content_frame)

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
