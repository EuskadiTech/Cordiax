# -*- coding: utf-8 -*-
"""
Módulo de Manual
Muestra el manual de usuario
"""

MANUAL = """
Cordiax - Manual de Usuario
===========================

1. Introducción
----------------
Bienvenido a Cordiax, una aplicación diseñada para gestionar centros educativos de manera eficiente. Este manual te guiará a través de las funcionalidades principales de la aplicación.

2. Instalación
-----------------
Para instalar Cordiax, sigue estos pasos:
1. Inserta el DVD de ejecución en tu computadora.
2. Ejecuta el archivo "CORDIAX-DVD.exe".
3. ¡Ya esta!

3. Funcionalidades Principales
---------------------------------
- Gestión de Centros y Aulas: Añade, edita y elimina centros educativos y sus aulas.
- Gestión de Estudiantes: Registra y administra la información de los estudiantes.
- Registro de Asistencia: Lleva un control detallado de la asistencia diaria de los estudiantes.
- Menú del Comedor: Gestiona y visualiza el menú diario del comedor escolar.
- Reportes Diarios: Genera informes detallados sobre la asistencia y el menú del día.
- Mensajes y Notas: Envía y recibe mensajes importantes relacionados con la gestión escolar.
- Respaldo de Datos: Realiza copias de seguridad de la base de datos para prevenir pérdidas de información.

4. Uso de la Aplicación
------------------------------
- Navegación: Utiliza el menú lateral para acceder a las diferentes secciones de la aplicación.
- Páginas: Cada página está identificada con el símbolo "@" seguido del nombre de la sección.
- Formularios: Completa los formularios con la información requerida y utiliza los botones para guardar o cancelar.
- Reportes: Accede a la sección de reportes para generar y visualizar informes personalizados.

5. ¿Dónde se guardan los datos?
---------------------------------
Los datos de Cordiax se almacenan en una base de datos SQLite ubicada en el directorio de la cuenta de usuario, en la ruta:
C:\\Users\\TuUsuario\\_SuperCordiax\\

Este programa no requiere conexión a internet para funcionar, y todos los datos se guardan localmente en tu computadora. por lo que si quieres cambiar de computadora, debes hacer un respaldo de la carpeta "_SuperCordiax".

"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import os
class ManualModule:
    """Módulo para mostrar el manual de usuario"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_manual()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Manual de Usuario", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Área de texto con scroll
        self.text_area = scrolledtext.ScrolledText(self.parent, wrap=tk.WORD, font=("Courier", 18), padx=10, pady=10)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)  # Inicialmente deshabilitado
        
    def load_manual(self):
        """Cargar el contenido del manual desde la variable MANUAL"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, MANUAL)
        self.text_area.config(state=tk.DISABLED)