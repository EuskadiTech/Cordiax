# -*- coding: utf-8 -*-
"""
Módulo de Backup y Restauración
Gestión de copias de seguridad en formato .cordiax.zip
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from modules import database, encryption
from modules.unlock_dialog import EncryptionSetupDialog
from pathlib import Path
import zipfile
import shutil
from datetime import datetime


class BackupModule:
    """Módulo de backup y restauración"""
    
    def __init__(self, parent):
        self.parent = parent
        self.backup_dir = database.USER_DATA_DIR / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.setup_ui()
        self.load_backups()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Copia de Seguridad y Restauración", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de botones
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Crear Backup", 
                  command=self.create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Restaurar", 
                  command=self.restore_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportar Backup", 
                  command=self.export_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Importar Backup", 
                  command=self.import_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", 
                  command=self.delete_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", 
                  command=self.load_backups).pack(side=tk.LEFT, padx=5)
        
        # Frame de encriptación
        encryption_frame = ttk.LabelFrame(self.parent, text="Encriptación de Base de Datos", padding="10")
        encryption_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Estado de encriptación
        status_frame = ttk.Frame(encryption_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, text="Estado:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.encryption_status_label = ttk.Label(status_frame, text="", font=("Arial", 9, "bold"))
        self.encryption_status_label.pack(side=tk.LEFT)
        
        # Botones de encriptación
        enc_button_frame = ttk.Frame(encryption_frame)
        enc_button_frame.pack(fill=tk.X)
        
        ttk.Button(enc_button_frame, text="Habilitar Encriptación", 
                  command=self.enable_encryption).pack(side=tk.LEFT, padx=5)
        ttk.Button(enc_button_frame, text="Deshabilitar Encriptación", 
                  command=self.disable_encryption).pack(side=tk.LEFT, padx=5)
        
        # Actualizar estado de encriptación
        self.update_encryption_status()
        
        # Frame de tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("Nombre", "Fecha", "Tamaño")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("Nombre", width=400)
        self.tree.column("Fecha", width=180)
        self.tree.column("Tamaño", width=120)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Información
        info_frame = ttk.Frame(self.parent)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = ("Los backups incluyen: base de datos, documentos y archivos de configuración.\n"
                    "Se recomienda hacer backups regulares para proteger sus datos.")
        
        info_label = ttk.Label(info_frame, text=info_text, 
                              font=("Arial", 9, "italic"), justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
        
    def load_backups(self):
        """Cargar lista de backups"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Listar archivos de backup
        for backup_file in sorted(self.backup_dir.glob("*.cordiax.zip"), reverse=True):
            stat = backup_file.stat()
            size_mb = stat.st_size / (1024 * 1024)
            size_str = f"{size_mb:.2f} MB"
            
            fecha = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            self.tree.insert("", tk.END, values=(
                backup_file.name,
                fecha,
                size_str
            ))
    
    def create_backup(self):
        """Crear nuevo backup"""
        # Generar nombre de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"cordiax_backup_{timestamp}.cordiax.zip"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Crear archivo ZIP
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Agregar base de datos
                db_path = database.get_db_path()
                if db_path.exists():
                    zipf.write(str(db_path), "cordiax.db")
                
                # Agregar documentos
                docs_dir = database.USER_DATA_DIR / "documentos"
                if docs_dir.exists():
                    for file_path in docs_dir.rglob("*"):
                        if file_path.is_file():
                            arcname = f"documentos/{file_path.relative_to(docs_dir)}"
                            zipf.write(str(file_path), arcname)
                
                # Agregar PDFs
                pdfs_dir = database.USER_DATA_DIR / "pdfs"
                if pdfs_dir.exists():
                    for file_path in pdfs_dir.rglob("*"):
                        if file_path.is_file():
                            arcname = f"pdfs/{file_path.relative_to(pdfs_dir)}"
                            zipf.write(str(file_path), arcname)
            
            self.load_backups()
            messagebox.showinfo("Éxito", 
                               f"Backup creado correctamente:\n{backup_name}\n\n"
                               f"Ubicación: {backup_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear backup: {str(e)}")
    
    def restore_backup(self):
        """Restaurar desde backup seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un backup")
            return
        
        item = self.tree.item(selection[0])
        backup_name = item['values'][0]
        backup_path = self.backup_dir / backup_name
        
        # Confirmar restauración
        if not messagebox.askyesno("Confirmar Restauración", 
                                   f"¿Está seguro de restaurar desde {backup_name}?\n\n"
                                   "ADVERTENCIA: Esto reemplazará todos los datos actuales."):
            return
        
        try:
            # Extraer archivo ZIP
            with zipfile.ZipFile(str(backup_path), 'r') as zipf:
                # Restaurar base de datos
                if "cordiax.db" in zipf.namelist():
                    db_path = database.get_db_path()
                    zipf.extract("cordiax.db", str(database.USER_DATA_DIR))
                    # Mover al lugar correcto si es necesario
                    extracted = database.USER_DATA_DIR / "cordiax.db"
                    if extracted != db_path:
                        shutil.move(str(extracted), str(db_path))
                
                # Restaurar documentos
                docs_dir = database.USER_DATA_DIR / "documentos"
                for member in zipf.namelist():
                    if member.startswith("documentos/"):
                        zipf.extract(member, str(database.USER_DATA_DIR))
                
                # Restaurar PDFs
                pdfs_dir = database.USER_DATA_DIR / "pdfs"
                for member in zipf.namelist():
                    if member.startswith("pdfs/"):
                        zipf.extract(member, str(database.USER_DATA_DIR))
            
            messagebox.showinfo("Éxito", 
                               "Restauración completada correctamente.\n\n"
                               "Por favor, reinicie la aplicación para aplicar los cambios.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al restaurar backup: {str(e)}")
    
    def export_backup(self):
        """Exportar backup a una ubicación externa"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un backup")
            return
        
        item = self.tree.item(selection[0])
        backup_name = item['values'][0]
        backup_path = self.backup_dir / backup_name
        
        # Seleccionar ubicación de destino
        dest_path = filedialog.asksaveasfilename(
            defaultextension=".cordiax.zip",
            filetypes=[("Backup Cordiax", "*.cordiax.zip"), ("All files", "*.*")],
            initialfile=backup_name
        )
        
        if not dest_path:
            return
        
        try:
            shutil.copy2(str(backup_path), dest_path)
            messagebox.showinfo("Éxito", f"Backup exportado a:\n{dest_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar backup: {str(e)}")
    
    def import_backup(self):
        """Importar backup desde ubicación externa"""
        filename = filedialog.askopenfilename(
            title="Seleccionar backup",
            filetypes=[("Backup Cordiax", "*.cordiax.zip"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            source = Path(filename)
            # Generar nombre único si es necesario
            dest_name = source.name
            dest_path = self.backup_dir / dest_name
            
            counter = 1
            while dest_path.exists():
                name_parts = source.stem.split('.')
                dest_name = f"{name_parts[0]}_{counter}.cordiax.zip"
                dest_path = self.backup_dir / dest_name
                counter += 1
            
            shutil.copy2(filename, str(dest_path))
            self.load_backups()
            messagebox.showinfo("Éxito", f"Backup importado como:\n{dest_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar backup: {str(e)}")
    
    def delete_backup(self):
        """Eliminar backup seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un backup")
            return
        
        item = self.tree.item(selection[0])
        backup_name = item['values'][0]
        backup_path = self.backup_dir / backup_name
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro de eliminar el backup {backup_name}?"):
            try:
                backup_path.unlink()
                self.load_backups()
                messagebox.showinfo("Éxito", "Backup eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar backup: {str(e)}")
    
    def update_encryption_status(self):
        """Actualizar el estado de encriptación en la UI"""
        if encryption.is_encryption_enabled(database.USER_DATA_DIR):
            self.encryption_status_label.config(text="Habilitada", foreground="green")
        else:
            self.encryption_status_label.config(text="Deshabilitada", foreground="red")
    
    def enable_encryption(self):
        """Habilitar encriptación de la base de datos"""
        if encryption.is_encryption_enabled(database.USER_DATA_DIR):
            messagebox.showinfo("Información", "La encriptación ya está habilitada")
            return
        
        # Mostrar diálogo para configurar contraseña
        dialog = EncryptionSetupDialog(self.parent)
        password = dialog.show()
        
        if password is None:
            return
        
        try:
            # Marcar como habilitada
            encryption.enable_encryption(database.USER_DATA_DIR)
            
            # Establecer contraseña en la base de datos
            database.set_password(password)
            
            # Encriptar la base de datos actual
            db_path = database.get_db_path()
            if db_path.exists() and not encryption.is_encrypted(db_path):
                encryption.encrypt_file(db_path, password)
            
            self.update_encryption_status()
            messagebox.showinfo("Éxito", 
                               "Encriptación habilitada correctamente.\n\n"
                               "A partir de ahora, se solicitará la contraseña al iniciar la aplicación.")
        except Exception as e:
            encryption.disable_encryption(database.USER_DATA_DIR)
            messagebox.showerror("Error", f"Error al habilitar encriptación: {str(e)}")
    
    def disable_encryption(self):
        """Deshabilitar encriptación de la base de datos"""
        if not encryption.is_encryption_enabled(database.USER_DATA_DIR):
            messagebox.showinfo("Información", "La encriptación no está habilitada")
            return
        
        if not messagebox.askyesno("Confirmar", 
                                  "¿Está seguro de deshabilitar la encriptación?\n\n"
                                  "La base de datos quedará sin protección de contraseña."):
            return
        
        try:
            # Desencriptar la base de datos si está encriptada
            db_path = database.get_db_path()
            if encryption.is_encrypted(db_path):
                # La base de datos ya debería estar desencriptada en memoria
                # Solo necesitamos marcar como deshabilitada
                pass
            
            # Marcar como deshabilitada
            encryption.disable_encryption(database.USER_DATA_DIR)
            
            # Limpiar contraseña
            database.set_password(None)
            
            self.update_encryption_status()
            messagebox.showinfo("Éxito", 
                               "Encriptación deshabilitada correctamente.\n\n"
                               "Ya no se solicitará contraseña al iniciar la aplicación.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al deshabilitar encriptación: {str(e)}")
