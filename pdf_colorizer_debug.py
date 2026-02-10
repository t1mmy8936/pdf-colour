import sys
import traceback
import cv2
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
import io
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSpinBox, QPushButton, QColorDialog,
                             QFileDialog, QComboBox, QSlider, QMessageBox)
from PyQt6.QtGui import QPixmap, QImage, QColor, QIcon, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import QScrollArea
import fitz  # PyMuPDF

print("All imports successful", flush=True)

class PDFColorizer(QMainWindow):
    def __init__(self):
        super().__init__()
        print("Initializing PDFColorizer", flush=True)
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
        self.edge_strength_threshold = 50  # Controls which lines are considered boundaries
        
        print("About to initUI", flush=True)
        self.initUI()
        print("PDFColorizer initialized successfully", flush=True)
        
    def initUI(self):
        """Initialize the user interface"""
        print("Starting initUI", flush=True)
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
        self.tool_combo.addItems(["Flood Fill (Smart)", "Brush Stroke", "Rectangle"])
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
        
        print("initUI completed successfully", flush=True)
        
    def open_pdf(self):
        """Open a PDF file"""
        print("open_pdf called", flush=True)
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            print(f"Loading PDF: {file_path}", flush=True)
            self.pdf_path = file_path
            self.load_pdf()
    
    def load_pdf(self):
        """Load PDF and convert to images"""
        try:
            print("load_pdf started", flush=True)
            pdf_document = fitz.open(self.pdf_path)
            self.total_pages = pdf_document.page_count
            print(f"PDF has {self.total_pages} pages", flush=True)
            
            self.page_spinbox.setMaximum(self.total_pages)
            self.page_label.setText(f"of {self.total_pages}")
            
            # Convert all pages to images
            self.pdf_images = []
            for page_num in range(self.total_pages):
                print(f"Converting page {page_num + 1}/{self.total_pages}", flush=True)
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                ppm_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(ppm_data))
                self.pdf_images.append(img.convert("RGB"))
            
            pdf_document.close()
            self.current_page = 0
            self.undo_stack = []
            print("About to display page", flush=True)
            self.display_page()
            print("PDF loaded successfully", flush=True)
            
        except Exception as e:
            print(f"Error in load_pdf: {str(e)}", flush=True)
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {str(e)}")
    
    def display_page(self):
        """Display the current page"""
        print("display_page called", flush=True)
        if not self.pdf_images:
            return
        
        self.original_image = self.pdf_images[self.current_page].copy()
        self.colored_image = self.original_image.copy()
        self.update_display()
    
    def update_display(self):
        """Update the displayed image with current zoom"""
        print("update_display called", flush=True)
        if self.colored_image is None:
            print("colored_image is None", flush=True)
            return
        
        try:
            # Apply zoom
            new_width = int(self.colored_image.width * self.zoom_level)
            new_height = int(self.colored_image.height * self.zoom_level)
            print(f"Resizing to {new_width}x{new_height}", flush=True)
            display_image = self.colored_image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            
            # Save to bytes using PNG format
            from io import BytesIO
            print("Creating BytesIO buffer", flush=True)
            buffer = BytesIO()
            print("Saving image to buffer", flush=True)
            display_image.save(buffer, format="PNG")
            print(f"Buffer size: {len(buffer.getvalue())}", flush=True)
            buffer.seek(0)
            
            # Load directly into QPixmap
            print("Loading QPixmap from PNG data", flush=True)
            pixmap = QPixmap()
            success = pixmap.loadFromData(buffer.getvalue(), "PNG")
            print(f"QPixmap load success: {success}, size: {pixmap.width()}x{pixmap.height()}", flush=True)
            
            # Set the pixmap
            print("Setting pixmap on label", flush=True)
            self.image_label.setPixmap(pixmap)
            print("update_display completed successfully", flush=True)
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
        if self.colored_image is None or self.image_label.pixmap() is None:
            return
        
        # Get the pixmap from the label
        pixmap = self.image_label.pixmap()
        
        # Calculate the position of the pixmap within the label (accounts for centering)
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()
        
        # Calculate offsets due to centering alignment
        x_offset = (label_width - pixmap_width) / 2
        y_offset = (label_height - pixmap_height) / 2
        
        # Get click position relative to the label
        click_x = event.pos().x()
        click_y = event.pos().y()
        
        # Subtract the pixmap offset to get position relative to pixmap
        pixmap_relative_x = click_x - x_offset
        pixmap_relative_y = click_y - y_offset
        
        print(f"Click at label ({click_x}, {click_y}), pixmap offset ({x_offset}, {y_offset}), relative ({pixmap_relative_x}, {pixmap_relative_y})", flush=True)
        
        # Check if click is actually on the pixmap
        if pixmap_relative_x < 0 or pixmap_relative_y < 0 or \
           pixmap_relative_x >= pixmap_width or pixmap_relative_y >= pixmap_height:
            return
        
        # Convert from zoomed image coordinates to original image coordinates
        x = int(pixmap_relative_x / self.zoom_level)
        y = int(pixmap_relative_y / self.zoom_level)
        
        print(f"Converted to image coords: ({x}, {y})", flush=True)
        
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
    
    def on_mouse_move(self, event):
        """Handle mouse move for brush strokes"""
        if not self.drawing or self.colored_image is None or self.image_label.pixmap() is None:
            return
        
        # Get the pixmap from the label
        pixmap = self.image_label.pixmap()
        
        # Calculate the position of the pixmap within the label (accounts for centering)
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()
        
        # Calculate offsets due to centering alignment
        x_offset = (label_width - pixmap_width) / 2
        y_offset = (label_height - pixmap_height) / 2
        
        # Get mouse position relative to the label
        mouse_x = event.pos().x()
        mouse_y = event.pos().y()
        
        # Subtract the pixmap offset to get position relative to pixmap
        pixmap_relative_x = mouse_x - x_offset
        pixmap_relative_y = mouse_y - y_offset
        
        # Check if mouse is on the pixmap
        if pixmap_relative_x < 0 or pixmap_relative_y < 0 or \
           pixmap_relative_x >= pixmap_width or pixmap_relative_y >= pixmap_height:
            return
        
        # Convert from zoomed image coordinates to original image coordinates
        x = int(pixmap_relative_x / self.zoom_level)
        y = int(pixmap_relative_y / self.zoom_level)
        
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
        """Perform intelligent flood fill that respects edge strength"""
        try:
            print(f"smart_flood_fill called at ({x}, {y})", flush=True)
            self.undo_stack.append(self.colored_image.copy())
            
            # Convert image to numpy array for edge detection
            colored_array = cv2.cvtColor(np.array(self.colored_image), cv2.COLOR_RGBA2BGR)
            gray = cv2.cvtColor(colored_array, cv2.COLOR_BGR2GRAY)
            print(f"Converted to grayscale: {gray.shape}", flush=True)
            
            # Detect edges using Sobel for edge magnitude
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edge_magnitude = np.sqrt(sobelx**2 + sobely**2).astype(np.uint8)
            print(f"Edge magnitude computed: min={edge_magnitude.min()}, max={edge_magnitude.max()}", flush=True)
            
            # Create a barrier mask: edges stronger than threshold act as barriers
            edge_threshold = self.edge_strength_threshold
            barrier_mask = (edge_magnitude > edge_threshold).astype(np.uint8) * 255
            print(f"Barrier mask created with threshold={edge_threshold}", flush=True)
            
            # Convert colored image to BGR for OpenCV flood fill
            colored_bgr = cv2.cvtColor(np.array(self.colored_image), cv2.COLOR_RGBA2BGR)
            
            # Prepare the seed point
            if 0 <= x < colored_bgr.shape[1] and 0 <= y < colored_bgr.shape[0]:
                # Check if starting point is on a barrier - if so, don't fill
                if barrier_mask[y, x] > 200:
                    print(f"Starting point is on a strong edge, skip fill", flush=True)
                    return  # Starting point is on a strong edge, don't fill
                
                # Use OpenCV's flood fill with mask to respect barriers
                color = (self.current_color.blue(), self.current_color.green(), 
                        self.current_color.red())  # BGR format
                print(f"Using color (BGR): {color}", flush=True)
                
                # Create a mask for flood fill (must be 1 pixel larger)
                mask = np.zeros((colored_bgr.shape[0] + 2, colored_bgr.shape[1] + 2), 
                               dtype=np.uint8)
                
                # Add barrier information to mask
                mask[1:-1, 1:-1] = barrier_mask
                print(f"Mask prepared for flood fill", flush=True)
                
                tolerance = self.tolerance_spinbox.value()
                cv2.floodFill(colored_bgr, mask, (x, y), color, 
                            (tolerance,) * 3, (tolerance,) * 3)
                print(f"Flood fill completed with tolerance={tolerance}", flush=True)
                
                # Convert back to RGBA and update
                result_rgba = cv2.cvtColor(colored_bgr, cv2.COLOR_BGR2RGBA)
                self.colored_image = Image.fromarray(result_rgba, 'RGBA')
                self.update_display()
            
        except Exception as e:
            print(f"Smart fill error: {e}", flush=True)
            if self.undo_stack:
                self.colored_image = self.undo_stack.pop()
            QMessageBox.warning(self, "Fill Error", f"Flood fill failed: {str(e)}")
    
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
            
            # Save as PDF
            images[0].save(
                file_path,
                save_all=True,
                append_images=images[1:] if len(images) > 1 else []
            )
            QMessageBox.information(self, "Success", f"PDF saved to {file_path}")
            
        except Exception as e:
            print(f"Error in save_pdf: {str(e)}", flush=True)
            traceback.print_exc()
            QMessageBox.critical(self, "Save Error", f"Failed to save PDF: {str(e)}")


def main():
    print("Starting application", flush=True)
    app = QApplication(sys.argv)
    print("QApplication created", flush=True)
    window = PDFColorizer()
    print("PDFColorizer window created", flush=True)
    window.show()
    print("Window shown", flush=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {str(e)}", flush=True)
        traceback.print_exc()
