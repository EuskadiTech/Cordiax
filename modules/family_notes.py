# -*- coding: utf-8 -*-
"""
Módulo de Notas Familiares
Generación de PDFs con encabezado y logo
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from modules import database
from datetime import date
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas


class FamilyNotesModule:
    """Módulo de notas familiares"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Título
        title = ttk.Label(self.parent, text="Notas Familiares", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Frame de controles
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Asunto:").pack(side=tk.LEFT, padx=5)
        self.asunto_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.asunto_var, width=40).pack(
            side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Generar PDF", 
                  command=self.generate_pdf).pack(side=tk.LEFT, padx=5)
        
        # Frame de contenido
        content_frame = ttk.Frame(self.parent)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(content_frame, text="Contenido de la nota:").pack(anchor=tk.W, pady=(0, 5))
        
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                                      font=("Arial", 11), height=20)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Instrucciones
        info_frame = ttk.Frame(self.parent)
        info_frame.pack(fill=tk.X)
        
        info_label = ttk.Label(info_frame, 
                              text="El PDF incluirá encabezado con el nombre de la institución y la fecha.",
                              font=("Arial", 9, "italic"))
        info_label.pack(anchor=tk.W)
        
    def generate_pdf(self):
        """Generar PDF de la nota familiar"""
        asunto = self.asunto_var.get()
        contenido = self.content_text.get("1.0", tk.END).strip()
        
        if not asunto or not contenido:
            messagebox.showerror("Error", "Por favor, ingrese asunto y contenido")
            return
        
        # Seleccionar ubicación del archivo
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"nota_familiar_{date.today().strftime('%Y%m%d')}.pdf"
        )
        
        if not filename:
            return
        
        try:
            # Crear PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Estilo personalizado para el título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=30,
                alignment=1  # Centrado
            )
            
            # Estilo para el contenido
            content_style = ParagraphStyle(
                'CustomContent',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                leading=16
            )
            
            # Encabezado
            story.append(Paragraph("NOTA FAMILIAR", title_style))
            story.append(Spacer(1, 0.2 * inch))
            
            # Información de la nota
            fecha_actual = date.today().strftime("%d de %B de %Y")
            
            # Tabla de información
            data = [
                ["Fecha:", fecha_actual],
                ["Asunto:", asunto]
            ]
            
            t = Table(data, colWidths=[1.5*inch, 4.5*inch])
            t.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a237e')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(t)
            story.append(Spacer(1, 0.3 * inch))
            
            # Contenido
            for parrafo in contenido.split('\n'):
                if parrafo.strip():
                    p = Paragraph(parrafo, content_style)
                    story.append(p)
            
            story.append(Spacer(1, 0.5 * inch))
            
            # Línea de firma
            story.append(Spacer(1, 0.5 * inch))
            firma_data = [
                ["_" * 40],
                ["Firma del Responsable"]
            ]
            
            firma_table = Table(firma_data, colWidths=[3*inch])
            firma_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(firma_table)
            
            # Generar PDF
            doc.build(story)
            
            messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")
