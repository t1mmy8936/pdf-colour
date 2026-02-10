import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import io
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSpinBox, QPushButton, QColorDialog,
                             QFileDialog, QComboBox, QSlider, QMessageBox, QTextEdit)
from PyQt6.QtGui import QPixmap, QImage, QColor, QIcon, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import QScrollArea
import fitz  # PyMuPDF

class PDFColorizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Street Plan Colorizer")
        self.setGeometry(100, 100, 1400, 900)
        
        # State variables
        self.pdf_path = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.current_color = QColor(255, 0, 0)
        self.pdf_images = []
        self.colored_image = None
        self.original_image = None
        self.stroke_width = 5
        self.font_size = 20
        self.text_input = ""
        
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(250)
        
        # File selection
        file_label = QLabel("PDF File:")
        file_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(file_label)
        
        self.file_button = QPushButton("Open PDF")
        self.file_button.clicked.connect(self.open_pdf)
        left_layout.addWidget(self.file_button)
        
        # Page navigation
        page_label = QLabel("Page Navigation:")
        page_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(page_label)
        
        page_layout = QHBoxLayout()
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.valueChanged.connect(self.on_page_changed)
        page_layout.addWidget(self.page_spinbox)
        
        self.page_label = QLabel("of 0")
        page_layout.addWidget(self.page_label)
        left_layout.addLayout(page_layout)
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        zoom_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(zoom_label)
        
        zoom_layout = QHBoxLayout()
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(50)
        self.zoom_slider.setMaximum(300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.setTickInterval(50)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        zoom_layout.addWidget(self.zoom_label)
        left_layout.addLayout(zoom_layout)
        
        # Tool selection
        tool_label = QLabel("Tools:")
        tool_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(tool_label)
        
        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["Flood Fill (Smart)", "Brush Stroke", "Rectangle", "Text"])
        left_layout.addWidget(self.tool_combo)
        
        # Color selection
        color_label = QLabel("Color:")
        color_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(color_label)
        
        self.color_button = QPushButton()
        self.color_button.setFixedHeight(40)
        self.color_button.clicked.connect(self.choose_color)
        self.update_color_button()
        left_layout.addWidget(self.color_button)
        
        # Stroke width for brush
        width_label = QLabel("Stroke Width:")
        width_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(width_label)
        
        width_layout = QHBoxLayout()
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setMinimum(1)
        self.width_spinbox.setMaximum(100)
        self.width_spinbox.setValue(5)
        self.width_spinbox.valueChanged.connect(self.on_width_changed)
        width_layout.addWidget(self.width_spinbox)
        self.width_label = QLabel("5px")
        width_layout.addWidget(self.width_label)
        left_layout.addLayout(width_layout)
        
        # Tolerance for flood fill
        tolerance_label = QLabel("Fill Tolerance:")
        tolerance_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(tolerance_label)
        
        tolerance_layout = QHBoxLayout()
        self.tolerance_spinbox = QSpinBox()
        self.tolerance_spinbox.setMinimum(0)
        self.tolerance_spinbox.setMaximum(100)
        self.tolerance_spinbox.setValue(30)
        tolerance_layout.addWidget(self.tolerance_spinbox)
        self.tolerance_label = QLabel("30")
        tolerance_layout.addWidget(self.tolerance_label)
        left_layout.addLayout(tolerance_layout)
        
        # Text input for text tool
        text_label = QLabel("Text Content:")
        text_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(text_label)
        
        self.text_input_field = QTextEdit()
        self.text_input_field.setMaximumHeight(60)
        self.text_input_field.setPlaceholderText("Enter text to add...")
        left_layout.addWidget(self.text_input_field)
        
        # Font size for text
        font_size_label = QLabel("Font Size:")
        font_size_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(font_size_label)
        
        font_size_layout = QHBoxLayout()
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setMinimum(8)
        self.font_size_spinbox.setMaximum(200)
        self.font_size_spinbox.setValue(20)
        self.font_size_spinbox.valueChanged.connect(self.on_font_size_changed)
        font_size_layout.addWidget(self.font_size_spinbox)
        self.font_size_label = QLabel("20px")
        font_size_layout.addWidget(self.font_size_label)
        left_layout.addLayout(font_size_layout)
        
        # Action buttons
        action_label = QLabel("Actions:")
        action_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(action_label)
        
        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo)
        left_layout.addWidget(self.undo_button)
        
        self.reset_button = QPushButton("Reset Page")
        self.reset_button.clicked.connect(self.reset_page)
        left_layout.addWidget(self.reset_button)
        
        self.save_button = QPushButton("Save PDF")
        self.save_button.clicked.connect(self.save_pdf)
        left_layout.addWidget(self.save_button)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # Right panel - Image display
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: gray;")
        self.image_label.mousePressEvent = self.on_image_click
        self.image_label.mouseMoveEvent = self.on_mouse_move
        self.image_label.mouseReleaseEvent = self.on_mouse_release
        
        scroll_area.setWidget(self.image_label)
        main_layout.addWidget(scroll_area)
        
        # Mouse state tracking
        self.drawing = False
        self.last_x = 0
        self.last_y = 0
        self.undo_stack = []
        
    def open_pdf(self):
        """Open a PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.pdf_path = file_path
            self.load_pdf()
    
    def load_pdf(self):
        """Load PDF and convert to images"""
        try:
            pdf_document = fitz.open(self.pdf_path)
            self.total_pages = pdf_document.page_count
            self.page_spinbox.setMaximum(self.total_pages)
            self.page_label.setText(f"of {self.total_pages}")
            
            # Convert all pages to images
            self.pdf_images = []
            for page_num in range(self.total_pages):
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                ppm_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(ppm_data))
                self.pdf_images.append(img.convert("RGB"))
            
            pdf_document.close()
            self.current_page = 0
            self.undo_stack = []
            self.display_page()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {str(e)}")
    
    def display_page(self):
        """Display the current page"""
        if not self.pdf_images:
            return
        
        self.original_image = self.pdf_images[self.current_page].copy()
        self.colored_image = self.original_image.copy()
        self.update_display()
    
    def update_display(self):
        """Update the displayed image with current zoom"""
        if self.colored_image is None:
            return
        
        try:
            # Apply zoom
            new_width = int(self.colored_image.width * self.zoom_level)
            new_height = int(self.colored_image.height * self.zoom_level)
            display_image = self.colored_image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            
            # Save to bytes using PNG format
            from io import BytesIO
            buffer = BytesIO()
            display_image.save(buffer, format="PNG")
            buffer.seek(0)
            
            # Load directly into QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue(), "PNG")
            
            # Set the pixmap
            self.image_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Display error: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    def on_page_changed(self, value):
        """Handle page change"""
        self.current_page = value - 1
        self.undo_stack = []
        self.display_page()
    
    def on_zoom_changed(self, value):
        """Handle zoom change"""
        self.zoom_level = value / 100.0
        self.zoom_label.setText(f"{value}%")
        self.update_display()
    
    def on_width_changed(self, value):
        """Handle stroke width change"""
        self.stroke_width = value
        self.width_label.setText(f"{value}px")
    
    def on_font_size_changed(self, value):
        """Handle font size change"""
        self.font_size = value
        self.font_size_label.setText(f"{value}px")
    
    def choose_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor(self.current_color, self, "Choose Color")
        if color.isValid():
            self.current_color = color
            self.update_color_button()
    
    def update_color_button(self):
        """Update color button appearance"""
        style = f"background-color: rgb({self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()});"
        self.color_button.setStyleSheet(style)
    
    def on_image_click(self, event):
        """Handle mouse click on image"""
        if self.colored_image is None:
            return
        
        # Convert screen coordinates to image coordinates
        x = int(event.pos().x() / self.zoom_level)
        y = int(event.pos().y() / self.zoom_level)
        
        # Bounds checking
        if x < 0 or y < 0 or x >= self.colored_image.width or y >= self.colored_image.height:
            return
        
        tool = self.tool_combo.currentText()
        
        if tool == "Flood Fill (Smart)":
            self.smart_flood_fill(x, y)
        elif tool == "Brush Stroke":
            self.drawing = True
            self.last_x = x
            self.last_y = y
        elif tool == "Rectangle":
            # Start rectangle (to be implemented with drag)
            self.drawing = True
            self.last_x = x
            self.last_y = y
        elif tool == "Text":
            self.add_text(x, y)
    
    def on_mouse_move(self, event):
        """Handle mouse move for brush strokes"""
        if not self.drawing or self.colored_image is None:
            return
        
        x = int(event.pos().x() / self.zoom_level)
        y = int(event.pos().y() / self.zoom_level)
        
        if self.tool_combo.currentText() == "Brush Stroke":
            self.undo_stack.append(self.colored_image.copy())
            draw = ImageDraw.Draw(self.colored_image, 'RGBA')
            color = (self.current_color.red(), self.current_color.green(), 
                    self.current_color.blue(), 200)
            draw.line([(self.last_x, self.last_y), (x, y)], 
                     fill=color, width=self.stroke_width)
            self.last_x = x
            self.last_y = y
            self.update_display()
    
    def on_mouse_release(self, event):
        """Handle mouse release"""
        self.drawing = False
    
    def smart_flood_fill(self, x, y):
        """Perform simple flood fill with color blending"""
        try:
            self.undo_stack.append(self.colored_image.copy())
            
            # Use PIL's flood fill
            from PIL import ImageDraw
            color = (self.current_color.red(), self.current_color.green(), 
                    self.current_color.blue())
            
            ImageDraw.floodfill(self.colored_image, (x, y), color, 
                               thresh=self.tolerance_spinbox.value())
            self.update_display()
            
        except Exception as e:
            print(f"Fill error: {e}", flush=True)
            if self.undo_stack:
                self.colored_image = self.undo_stack.pop()
            QMessageBox.warning(self, "Fill Error", f"Flood fill failed: {str(e)}")
    
    def add_text(self, x, y):
        """Add text to the image at the specified coordinates"""
        try:
            text = self.text_input_field.toPlainText().strip()
            
            if not text:
                QMessageBox.warning(self, "Text Error", "Please enter some text first")
                return
            
            self.undo_stack.append(self.colored_image.copy())
            
            # Try to use a system font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size)
            except:
                try:
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", self.font_size)
                except:
                    # Use default font if Arial is not available
                    font = ImageFont.load_default()
            
            # Draw text on the image
            draw = ImageDraw.Draw(self.colored_image, 'RGBA')
            color = (self.current_color.red(), self.current_color.green(), 
                    self.current_color.blue(), 255)
            
            draw.text((x, y), text, fill=color, font=font)
            self.update_display()
            
        except Exception as e:
            print(f"Text error: {e}", flush=True)
            if self.undo_stack:
                self.colored_image = self.undo_stack.pop()
            QMessageBox.warning(self, "Text Error", f"Failed to add text: {str(e)}")
    
    def undo(self):
        """Undo last action"""
        if self.undo_stack:
            self.colored_image = self.undo_stack.pop()
            self.update_display()
    
    def reset_page(self):
        """Reset current page to original"""
        if self.original_image:
            self.colored_image = self.original_image.copy()
            self.undo_stack = []
            self.update_display()
    
    def save_pdf(self):
        """Save colored PDF"""
        if not self.pdf_images or not self.colored_image:
            QMessageBox.warning(self, "Save Error", "No PDF loaded")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", "", "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        try:
            # Convert all PIL images to PDF
            images = []
            for idx, img in enumerate(self.pdf_images):
                if idx == self.current_page:
                    images.append(self.colored_image.convert("RGB"))
                else:
                    images.append(img.convert("RGB"))
            
            # Save as PDF using PIL
            images[0].save(
                file_path,
                save_all=True,
                append_images=images[1:] if len(images) > 1 else []
            )
            QMessageBox.information(self, "Success", f"PDF saved to {file_path}")
            
        except Exception as e:
            print(f"Save error: {e}", flush=True)
            QMessageBox.critical(self, "Save Error", f"Failed to save PDF: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = PDFColorizer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
