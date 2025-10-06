# -*- coding: utf-8 -*-
"""
Módulo de Sincronización para Cordiax
Gestión de sincronización de base de datos con diferentes protocolos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import time
import json
from datetime import datetime
from modules import database, encryption

try:
    from webdav3.client import Client as WebDAVClient
    WEBDAV_AVAILABLE = True
except ImportError:
    WEBDAV_AVAILABLE = False

try:
    from smb.SMBConnection import SMBConnection
    SMB_AVAILABLE = True
except ImportError:
    SMB_AVAILABLE = False

try:
    import socketio
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False


class SyncModule:
    """Módulo de sincronización de base de datos"""
    
    def __init__(self, parent):
        self.parent = parent
        # Check if sync_config.json exists in current directory first
        local_config = Path("./sync_config.json")
        if local_config.exists():
            self.config_path = local_config
        else:
            self.config_path = database.USER_DATA_DIR / "sync_config.json"
        self.sync_running = False
        self.sync_thread = None
        self.sio = None
        self.load_config()
        self.setup_ui()
        
    def load_config(self):
        """Cargar configuración de sincronización"""
        default_config = {
            "enabled": False,
            "protocol": "webdav",  # webdav, smb, socketio
            "polling_interval": 300,  # 5 minutos
            "webdav": {
                "url": "",
                "username": "",
                "password": "",
                "remote_path": "/cordiax_sync/"
            },
            "smb": {
                "server": "",
                "share_name": "",
                "username": "",
                "password": "",
                "domain": "",
                "remote_path": "/cordiax_sync/"
            },
            "socketio": {
                "server_url": "http://localhost:5000",
                "namespace": "/cordiax-sync/"
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key in default_config:
                        if key not in loaded_config:
                            loaded_config[key] = default_config[key]
                    self.config = loaded_config
            except Exception as e:
                print(f"Error cargando configuración: {e}")
                self.config = default_config
        else:
            self.config = default_config
            
    def save_config(self):
        """Guardar configuración de sincronización"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")
            return False
            
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Título
        title = ttk.Label(self.parent, text="Sincronización de Datos", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20))
        
        # Frame de estado
        status_frame = ttk.LabelFrame(self.parent, text="Estado de Sincronización", padding="10")
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.sync_status_label = ttk.Label(status_frame, text="Sincronización deshabilitada", 
                                           font=("Arial", 10))
        self.sync_status_label.pack(pady=5)
        
        self.last_sync_label = ttk.Label(status_frame, text="Última sincronización: Nunca", 
                                         font=("Arial", 9))
        self.last_sync_label.pack(pady=5)
        
        # Botones de control
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.start_button = ttk.Button(control_frame, text="Iniciar Sincronización", 
                                       command=self.start_sync)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Detener Sincronización", 
                                      command=self.stop_sync, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.manual_sync_button = ttk.Button(control_frame, text="Sincronizar Ahora", 
                                            command=self.manual_sync)
        self.manual_sync_button.pack(side=tk.LEFT, padx=5)
        
        # Configuración general
        general_frame = ttk.LabelFrame(self.parent, text="Configuración General", padding="10")
        general_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Habilitar sincronización
        self.enabled_var = tk.BooleanVar(value=self.config["enabled"])
        ttk.Checkbutton(general_frame, text="Habilitar sincronización automática", 
                       variable=self.enabled_var).pack(anchor=tk.W, pady=5)
        
        # Protocolo
        protocol_frame = ttk.Frame(general_frame)
        protocol_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(protocol_frame, text="Protocolo:").pack(side=tk.LEFT, padx=(0, 10))
        self.protocol_var = tk.StringVar(value=self.config["protocol"])
        
        protocols = []
        if WEBDAV_AVAILABLE:
            protocols.append(("WebDAV", "webdav"))
        if SMB_AVAILABLE:
            protocols.append(("SMB/CIFS", "smb"))
        if SOCKETIO_AVAILABLE:
            protocols.append(("Flask-SocketIO", "socketio"))
            
        if not protocols:
            ttk.Label(protocol_frame, text="No hay protocolos disponibles. Instale las dependencias.", 
                     foreground="red").pack(side=tk.LEFT)
        else:
            for text, value in protocols:
                ttk.Radiobutton(protocol_frame, text=text, value=value, 
                               variable=self.protocol_var, 
                               command=self.on_protocol_change).pack(side=tk.LEFT, padx=5)
        
        # Intervalo de polling
        interval_frame = ttk.Frame(general_frame)
        interval_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(interval_frame, text="Intervalo de sincronización (segundos):").pack(side=tk.LEFT, padx=(0, 10))
        self.interval_var = tk.StringVar(value=str(self.config["polling_interval"]))
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        interval_entry.pack(side=tk.LEFT)
        
        # Notebook para configuraciones específicas
        self.config_notebook = ttk.Notebook(self.parent)
        self.config_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # WebDAV config
        self.webdav_frame = self.create_webdav_config()
        self.config_notebook.add(self.webdav_frame, text="WebDAV")
        
        # SMB config
        self.smb_frame = self.create_smb_config()
        self.config_notebook.add(self.smb_frame, text="SMB/CIFS")
        
        # SocketIO config
        self.socketio_frame = self.create_socketio_config()
        self.config_notebook.add(self.socketio_frame, text="Flask-SocketIO")
        
        # Seleccionar la pestaña según el protocolo actual
        self.select_protocol_tab()
        
        # Botón de guardar
        save_button = ttk.Button(self.parent, text="Guardar Configuración", 
                                command=self.save_configuration)
        save_button.pack(pady=10)
        
        # Log de sincronización
        log_frame = ttk.LabelFrame(self.parent, text="Registro de Sincronización", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar para el log
        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=10, yscrollcommand=log_scroll.set, 
                               state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        log_scroll.config(command=self.log_text.yview)
        
    def create_webdav_config(self):
        """Crear configuración de WebDAV"""
        frame = ttk.Frame(self.config_notebook)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # URL
        ttk.Label(frame, text="URL del servidor WebDAV:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.webdav_url_var = tk.StringVar(value=self.config["webdav"]["url"])
        ttk.Entry(frame, textvariable=self.webdav_url_var, width=50).grid(row=0, column=1, pady=5)
        
        # Username
        ttk.Label(frame, text="Usuario:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.webdav_user_var = tk.StringVar(value=self.config["webdav"]["username"])
        ttk.Entry(frame, textvariable=self.webdav_user_var, width=50).grid(row=1, column=1, pady=5)
        
        # Password
        ttk.Label(frame, text="Contraseña:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.webdav_pass_var = tk.StringVar(value=self.config["webdav"]["password"])
        ttk.Entry(frame, textvariable=self.webdav_pass_var, width=50, show="*").grid(row=2, column=1, pady=5)
        
        # Remote path
        ttk.Label(frame, text="Ruta remota:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.webdav_path_var = tk.StringVar(value=self.config["webdav"]["remote_path"])
        ttk.Entry(frame, textvariable=self.webdav_path_var, width=50).grid(row=3, column=1, pady=5)
        
        # Test button
        ttk.Button(frame, text="Probar Conexión", command=self.test_webdav).grid(row=4, column=1, pady=10, sticky=tk.W)
        
        if not WEBDAV_AVAILABLE:
            ttk.Label(frame, text="WebDAV no está disponible. Instale 'webdavclient3'.", 
                     foreground="red").grid(row=5, column=0, columnspan=2, pady=5)
        
        return frame
        
    def create_smb_config(self):
        """Crear configuración de SMB"""
        frame = ttk.Frame(self.config_notebook)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Server
        ttk.Label(frame, text="Servidor:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.smb_server_var = tk.StringVar(value=self.config["smb"]["server"])
        ttk.Entry(frame, textvariable=self.smb_server_var, width=50).grid(row=0, column=1, pady=5)
        
        # Share name
        ttk.Label(frame, text="Nombre de recurso compartido:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.smb_share_var = tk.StringVar(value=self.config["smb"]["share_name"])
        ttk.Entry(frame, textvariable=self.smb_share_var, width=50).grid(row=1, column=1, pady=5)
        
        # Username
        ttk.Label(frame, text="Usuario:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.smb_user_var = tk.StringVar(value=self.config["smb"]["username"])
        ttk.Entry(frame, textvariable=self.smb_user_var, width=50).grid(row=2, column=1, pady=5)
        
        # Password
        ttk.Label(frame, text="Contraseña:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.smb_pass_var = tk.StringVar(value=self.config["smb"]["password"])
        ttk.Entry(frame, textvariable=self.smb_pass_var, width=50, show="*").grid(row=3, column=1, pady=5)
        
        # Domain
        ttk.Label(frame, text="Dominio (opcional):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.smb_domain_var = tk.StringVar(value=self.config["smb"]["domain"])
        ttk.Entry(frame, textvariable=self.smb_domain_var, width=50).grid(row=4, column=1, pady=5)
        
        # Remote path
        ttk.Label(frame, text="Ruta remota:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.smb_path_var = tk.StringVar(value=self.config["smb"]["remote_path"])
        ttk.Entry(frame, textvariable=self.smb_path_var, width=50).grid(row=5, column=1, pady=5)
        
        # Test button
        ttk.Button(frame, text="Probar Conexión", command=self.test_smb).grid(row=6, column=1, pady=10, sticky=tk.W)
        
        if not SMB_AVAILABLE:
            ttk.Label(frame, text="SMB no está disponible. Instale 'pysmb'.", 
                     foreground="red").grid(row=7, column=0, columnspan=2, pady=5)
        
        return frame
        
    def create_socketio_config(self):
        """Crear configuración de SocketIO"""
        frame = ttk.Frame(self.config_notebook)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Server URL
        ttk.Label(frame, text="URL del servidor:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.socketio_url_var = tk.StringVar(value=self.config["socketio"]["server_url"])
        ttk.Entry(frame, textvariable=self.socketio_url_var, width=50).grid(row=0, column=1, pady=5)
        
        # Namespace
        ttk.Label(frame, text="Namespace:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.socketio_namespace_var = tk.StringVar(value=self.config["socketio"]["namespace"])
        ttk.Entry(frame, textvariable=self.socketio_namespace_var, width=50).grid(row=1, column=1, pady=5)
        
        # Test button
        ttk.Button(frame, text="Probar Conexión", command=self.test_socketio).grid(row=2, column=1, pady=10, sticky=tk.W)
        
        if not SOCKETIO_AVAILABLE:
            ttk.Label(frame, text="SocketIO no está disponible. Instale 'python-socketio[client]'.", 
                     foreground="red").grid(row=3, column=0, columnspan=2, pady=5)
        
        return frame
        
    def on_protocol_change(self):
        """Manejar cambio de protocolo"""
        self.select_protocol_tab()
        
    def select_protocol_tab(self):
        """Seleccionar pestaña según protocolo"""
        protocol = self.protocol_var.get()
        if protocol == "webdav":
            self.config_notebook.select(0)
        elif protocol == "smb":
            self.config_notebook.select(1)
        elif protocol == "socketio":
            self.config_notebook.select(2)
            
    def save_configuration(self):
        """Guardar configuración actual"""
        try:
            # Validar intervalo
            interval = int(self.interval_var.get())
            if interval < 60:
                messagebox.showwarning("Advertencia", 
                                      "El intervalo mínimo es de 60 segundos")
                return
                
            # Actualizar configuración
            self.config["enabled"] = self.enabled_var.get()
            self.config["protocol"] = self.protocol_var.get()
            self.config["polling_interval"] = interval
            
            # WebDAV
            self.config["webdav"]["url"] = self.webdav_url_var.get()
            self.config["webdav"]["username"] = self.webdav_user_var.get()
            self.config["webdav"]["password"] = self.webdav_pass_var.get()
            self.config["webdav"]["remote_path"] = self.webdav_path_var.get()
            
            # SMB
            self.config["smb"]["server"] = self.smb_server_var.get()
            self.config["smb"]["share_name"] = self.smb_share_var.get()
            self.config["smb"]["username"] = self.smb_user_var.get()
            self.config["smb"]["password"] = self.smb_pass_var.get()
            self.config["smb"]["domain"] = self.smb_domain_var.get()
            self.config["smb"]["remote_path"] = self.smb_path_var.get()
            
            # SocketIO
            self.config["socketio"]["server_url"] = self.socketio_url_var.get()
            self.config["socketio"]["namespace"] = self.socketio_namespace_var.get()
            
            if self.save_config():
                messagebox.showinfo("Éxito", "Configuración guardada correctamente")
        except ValueError:
            messagebox.showerror("Error", "El intervalo debe ser un número entero")
            
    def log(self, message):
        """Agregar mensaje al log"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def get_db_file_to_sync(self):
        """Obtener el archivo de base de datos para sincronizar"""
        db_path = database.get_db_path()
        
        # Si la encriptación está habilitada, asegurarse de que esté encriptada
        if encryption.is_encryption_enabled(database.USER_DATA_DIR):
            if not encryption.is_encrypted(db_path):
                # Encriptar antes de sincronizar
                if database.DB_PASSWORD:
                    encryption.encrypt_file(db_path, database.DB_PASSWORD)
                else:
                    self.log("Error: Base de datos no encriptada y no hay contraseña disponible")
                    return None
        
        return db_path
    
    def get_files_to_sync(self):
        """Obtener todos los archivos y directorios a sincronizar"""
        import os
        import zipfile
        import tempfile
        
        # Crear un archivo ZIP temporal con todos los datos
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_zip.close()
        
        try:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Añadir base de datos
                db_file = self.get_db_file_to_sync()
                if db_file and db_file.exists():
                    zipf.write(db_file, 'cordiax.db')
                    self.log(f"Añadido: cordiax.db")
                
                # Añadir archivos de directorios
                dirs_to_sync = ['documentos', 'pdfs']
                
                for dir_name in dirs_to_sync:
                    dir_path = database.USER_DATA_DIR / dir_name
                    if dir_path.exists():
                        file_count = 0
                        for root, dirs, files in os.walk(dir_path):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = os.path.relpath(file_path, database.USER_DATA_DIR)
                                zipf.write(file_path, arcname)
                                file_count += 1
                        self.log(f"Añadidos {file_count} archivos de {dir_name}/")
                
                # Restaurar estado de encriptación de la BD si fue modificada
                if db_file and encryption.is_encryption_enabled(database.USER_DATA_DIR):
                    if not encryption.is_encrypted(db_file):
                        if database.DB_PASSWORD:
                            encryption.encrypt_file(db_file, database.DB_PASSWORD)
            
            return Path(temp_zip.name)
            
        except Exception as e:
            self.log(f"Error creando archivo de sincronización: {e}")
            if os.path.exists(temp_zip.name):
                os.unlink(temp_zip.name)
            return None
        
    def start_sync(self):
        """Iniciar sincronización automática"""
        if not self.config["enabled"]:
            messagebox.showwarning("Advertencia", 
                                  "La sincronización no está habilitada. Active la opción en la configuración.")
            return
            
        if self.sync_running:
            messagebox.showinfo("Información", "La sincronización ya está en ejecución")
            return
            
        protocol = self.config["protocol"]
        
        # Verificar disponibilidad del protocolo
        if protocol == "webdav" and not WEBDAV_AVAILABLE:
            messagebox.showerror("Error", "WebDAV no está disponible. Instale webdavclient3")
            return
        elif protocol == "smb" and not SMB_AVAILABLE:
            messagebox.showerror("Error", "SMB no está disponible. Instale pysmb")
            return
        elif protocol == "socketio" and not SOCKETIO_AVAILABLE:
            messagebox.showerror("Error", "SocketIO no está disponible. Instale python-socketio")
            return
            
        self.sync_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.sync_status_label.config(text=f"Sincronización activa ({protocol})")
        
        # Iniciar hilo de sincronización
        if protocol == "socketio":
            self.sync_thread = threading.Thread(target=self.socketio_sync_loop, daemon=True)
        else:
            self.sync_thread = threading.Thread(target=self.polling_sync_loop, daemon=True)
        self.sync_thread.start()
        
        self.log(f"Sincronización iniciada con protocolo {protocol}")
        
    def stop_sync(self):
        """Detener sincronización automática"""
        self.sync_running = False
        
        # Desconectar SocketIO si está activo
        if self.sio and self.sio.connected:
            self.sio.disconnect()
            
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.sync_status_label.config(text="Sincronización detenida")
        self.log("Sincronización detenida")
        
    def manual_sync(self):
        """Realizar sincronización manual"""
        protocol = self.config["protocol"]
        
        # Verificar disponibilidad del protocolo
        if protocol == "webdav" and not WEBDAV_AVAILABLE:
            messagebox.showerror("Error", "WebDAV no está disponible")
            return
        elif protocol == "smb" and not SMB_AVAILABLE:
            messagebox.showerror("Error", "SMB no está disponible")
            return
        elif protocol == "socketio" and not SOCKETIO_AVAILABLE:
            messagebox.showerror("Error", "SocketIO no está disponible")
            return
            
        self.log("Iniciando sincronización manual...")
        
        try:
            if protocol == "webdav":
                self.sync_webdav()
            elif protocol == "smb":
                self.sync_smb()
            elif protocol == "socketio":
                self.sync_socketio_manual()
                
            self.last_sync_label.config(text=f"Última sincronización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            messagebox.showinfo("Éxito", "Sincronización completada")
        except Exception as e:
            self.log(f"Error en sincronización manual: {e}")
            messagebox.showerror("Error", f"Error durante la sincronización: {e}")
            
    def polling_sync_loop(self):
        """Loop de sincronización con polling"""
        while self.sync_running:
            try:
                protocol = self.config["protocol"]
                
                if protocol == "webdav":
                    self.sync_webdav()
                elif protocol == "smb":
                    self.sync_smb()
                    
                self.last_sync_label.config(text=f"Última sincronización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                self.log(f"Error en sincronización: {e}")
                
            # Esperar intervalo
            time.sleep(self.config["polling_interval"])
            
    def socketio_sync_loop(self):
        """Loop de sincronización con SocketIO"""
        try:
            if not SOCKETIO_AVAILABLE:
                self.log("SocketIO no está disponible")
                return
                
            self.sio = socketio.Client()
            
            @self.sio.on('connect', namespace=self.config["socketio"]["namespace"])
            def on_connect():
                self.log("Conectado al servidor SocketIO")
                # Sincronizar al conectar
                self.sync_socketio_manual()
                
            @self.sio.on('sync_request', namespace=self.config["socketio"]["namespace"])
            def on_sync_request(data):
                self.log("Solicitud de sincronización recibida del servidor")
                self.sync_socketio_manual()
                
            @self.sio.on('disconnect', namespace=self.config["socketio"]["namespace"])
            def on_disconnect():
                self.log("Desconectado del servidor SocketIO")
                
            # Conectar al servidor
            self.sio.connect(self.config["socketio"]["server_url"])
            
            # Mantener la conexión
            while self.sync_running:
                time.sleep(1)
                
        except Exception as e:
            self.log(f"Error en SocketIO: {e}")
        finally:
            if self.sio and self.sio.connected:
                self.sio.disconnect()
                
    def sync_webdav(self):
        """Sincronizar con WebDAV"""
        if not WEBDAV_AVAILABLE:
            raise Exception("WebDAV no está disponible")
            
        config = self.config["webdav"]
        
        # Crear cliente WebDAV
        options = {
            'webdav_hostname': config["url"],
            'webdav_login': config["username"],
            'webdav_password': config["password"]
        }
        
        client = WebDAVClient(options)
        
        # Obtener archivo ZIP con todos los datos a sincronizar
        sync_file = self.get_files_to_sync()
        if not sync_file:
            raise Exception("No se pudo crear el archivo de sincronización")
            
        try:
            remote_path = config["remote_path"].rstrip('/') + '/cordiax_sync.zip'
            
            # Subir archivo
            self.log("Subiendo datos a WebDAV...")
            client.upload_sync(remote_path=remote_path, local_path=str(sync_file))
            self.log("Datos sincronizados con WebDAV")
        finally:
            # Eliminar archivo temporal
            if sync_file.exists():
                sync_file.unlink()
        
        
    def sync_smb(self):
        """Sincronizar con SMB"""
        if not SMB_AVAILABLE:
            raise Exception("SMB no está disponible")
            
        config = self.config["smb"]
        
        # Crear conexión SMB
        conn = SMBConnection(
            config["username"],
            config["password"],
            "cordiax-client",
            config["server"],
            domain=config["domain"],
            use_ntlm_v2=True
        )
        
        # Conectar
        self.log("Conectando a servidor SMB...")
        if not conn.connect(config["server"], 139):
            raise Exception("No se pudo conectar al servidor SMB")
            
        # Obtener archivo ZIP con todos los datos a sincronizar
        sync_file = self.get_files_to_sync()
        if not sync_file:
            raise Exception("No se pudo crear el archivo de sincronización")
            
        try:
            remote_path = config["remote_path"].rstrip('/') + '/cordiax_sync.zip'
            
            # Subir archivo
            self.log("Subiendo datos a SMB...")
            with open(sync_file, 'rb') as f:
                conn.storeFile(config["share_name"], remote_path, f)
            self.log("Datos sincronizados con SMB")
        finally:
            conn.close()
            # Eliminar archivo temporal
            if sync_file.exists():
                sync_file.unlink()
        
        
    def sync_socketio_manual(self):
        """Sincronizar manualmente con SocketIO"""
        if not SOCKETIO_AVAILABLE:
            raise Exception("SocketIO no está disponible")
            
        # Obtener archivo ZIP con todos los datos a sincronizar
        sync_file = self.get_files_to_sync()
        if not sync_file:
            raise Exception("No se pudo crear el archivo de sincronización")
            
        try:
            # Leer archivo
            with open(sync_file, 'rb') as f:
                data = f.read()
                
            # Enviar al servidor
            if self.sio and self.sio.connected:
                self.log("Enviando datos al servidor SocketIO...")
                self.sio.emit('sync_data', {'data': data.hex()}, 
                             namespace=self.config["socketio"]["namespace"])
                self.log("Datos sincronizados con SocketIO")
            else:
                raise Exception("No hay conexión SocketIO activa")
        finally:
            # Eliminar archivo temporal
            if sync_file.exists():
                sync_file.unlink()
        
        
    def test_webdav(self):
        """Probar conexión WebDAV"""
        if not WEBDAV_AVAILABLE:
            messagebox.showerror("Error", "WebDAV no está disponible")
            return
            
        try:
            config = {
                'webdav_hostname': self.webdav_url_var.get(),
                'webdav_login': self.webdav_user_var.get(),
                'webdav_password': self.webdav_pass_var.get()
            }
            
            client = WebDAVClient(config)
            
            # Verificar que se pueda listar el directorio raíz
            client.list()
            
            messagebox.showinfo("Éxito", "Conexión WebDAV exitosa")
            self.log("Prueba de conexión WebDAV exitosa")
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con WebDAV: {e}")
            self.log(f"Error en prueba WebDAV: {e}")
            
    def test_smb(self):
        """Probar conexión SMB"""
        if not SMB_AVAILABLE:
            messagebox.showerror("Error", "SMB no está disponible")
            return
            
        try:
            conn = SMBConnection(
                self.smb_user_var.get(),
                self.smb_pass_var.get(),
                "cordiax-client",
                self.smb_server_var.get(),
                domain=self.smb_domain_var.get(),
                use_ntlm_v2=True
            )
            
            if conn.connect(self.smb_server_var.get(), 139):
                messagebox.showinfo("Éxito", "Conexión SMB exitosa")
                self.log("Prueba de conexión SMB exitosa")
                conn.close()
            else:
                messagebox.showerror("Error", "No se pudo conectar al servidor SMB")
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con SMB: {e}")
            self.log(f"Error en prueba SMB: {e}")
            
    def test_socketio(self):
        """Probar conexión SocketIO"""
        if not SOCKETIO_AVAILABLE:
            messagebox.showerror("Error", "SocketIO no está disponible")
            return
            
        try:
            test_sio = socketio.Client()
            
            connected = False
            
            @test_sio.on('connect', namespace=self.socketio_namespace_var.get())
            def on_connect():
                nonlocal connected
                connected = True
                
            test_sio.connect(self.socketio_url_var.get(), 
                           namespaces=[self.socketio_namespace_var.get()])
            
            # Esperar un momento para la conexión
            time.sleep(2)
            
            if connected:
                messagebox.showinfo("Éxito", "Conexión SocketIO exitosa")
                self.log("Prueba de conexión SocketIO exitosa")
            else:
                messagebox.showwarning("Advertencia", "No se recibió confirmación de conexión")
                
            test_sio.disconnect()
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con SocketIO: {e}")
            self.log(f"Error en prueba SocketIO: {e}")
