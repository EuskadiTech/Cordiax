# -*- coding: utf-8 -*-
"""
Módulo de diálogo de desbloqueo
Maneja el diálogo de contraseña al arranque
"""

import tkinter as tk
from tkinter import ttk, messagebox


class UnlockDialog:
    """Diálogo para desbloquear la base de datos encriptada"""
    
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Desbloquear Cordiax")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        
        # Centrar ventana
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Hacer modal
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        self.dialog.focus_set()
        
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="Base de datos encriptada",
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Mensaje
        msg_label = ttk.Label(main_frame,
                             text="Ingrese la contraseña para desbloquear:",
                             font=("Arial", 10))
        msg_label.pack(pady=(0, 15))
        
        # Campo de contraseña
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(password_frame, text="Contraseña:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.password_entry = ttk.Entry(password_frame, show="*", width=30)
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.password_entry.focus()
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.ok())
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Aceptar", command=self.ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.cancel).pack(side=tk.RIGHT)
        
    def ok(self):
        """Manejar botón OK"""
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Advertencia", "Por favor, ingrese una contraseña")
            return
        
        self.result = password
        self.dialog.destroy()
        
    def cancel(self):
        """Manejar botón Cancelar"""
        self.result = None
        self.dialog.destroy()
        
    def show(self):
        """Mostrar diálogo y esperar resultado"""
        self.dialog.wait_window()
        return self.result


class EncryptionSetupDialog:
    """Diálogo para configurar la encriptación por primera vez"""
    
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configurar Encriptación")
        self.dialog.geometry("450x250")
        self.dialog.resizable(False, False)
        
        # Centrar ventana
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Hacer modal
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        self.dialog.focus_set()
        
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame,
                               text="Configurar Encriptación de Base de Datos",
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Mensaje
        msg_label = ttk.Label(main_frame,
                             text="Configure una contraseña para proteger su base de datos.\n"
                                  "Esta contraseña se solicitará cada vez que inicie la aplicación.",
                             font=("Arial", 9),
                             justify=tk.LEFT)
        msg_label.pack(pady=(0, 15))
        
        # Campo de contraseña
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(password_frame, text="Contraseña:").pack(side=tk.LEFT, padx=(0, 10))
        self.password_entry = ttk.Entry(password_frame, show="*", width=30)
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Campo de confirmación
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(confirm_frame, text="Confirmar:").pack(side=tk.LEFT, padx=(0, 10))
        self.confirm_entry = ttk.Entry(confirm_frame, show="*", width=30)
        self.confirm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind Enter key
        self.confirm_entry.bind("<Return>", lambda e: self.ok())
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Habilitar Encriptación", 
                  command=self.ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side=tk.RIGHT)
        
    def ok(self):
        """Manejar botón OK"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password:
            messagebox.showwarning("Advertencia", "Por favor, ingrese una contraseña")
            return
        
        if len(password) < 4:
            messagebox.showwarning("Advertencia", 
                                 "La contraseña debe tener al menos 4 caracteres")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        self.result = password
        self.dialog.destroy()
        
    def cancel(self):
        """Manejar botón Cancelar"""
        self.result = None
        self.dialog.destroy()
        
    def show(self):
        """Mostrar diálogo y esperar resultado"""
        self.dialog.wait_window()
        return self.result
