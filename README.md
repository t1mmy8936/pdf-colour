# PDF Street Plan Colorizer

A PyQt6-based application for viewing, annotating, and color-coding PDF street plans and architectural drawings. Features intelligent building boundary detection to prevent color bleeding and multiple annotation tools.

## Features

- **PDF Viewer**: Load and navigate multi-page PDF files
- **Smart Flood Fill**: Color areas while respecting building edges and boundaries
- **Brush Stroke Tool**: Draw freehand annotations with adjustable width
- **Rectangle Tool**: Create rectangular annotations
- **Text Tool**: Add text boxes with customizable font size and color
- **Zoom Control**: Zoom in/out for detailed work (50% - 300%)
- **Building Boundary Detection**: Uses edge detection to prevent colors from bleeding outside buildings
- **Undo/Reset**: Undo last action or reset the current page
- **Color Picker**: Select any color from the color palette
- **Tolerance Adjustment**: Fine-tune the flood fill sensitivity to respect different boundary types
- **Save Functionality**: Export the annotated PDF with all modifications

## Installation

1. Install Python 3.8 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python pdf_colorizer.py
   ```

2. Click "Open PDF" to load a PDF file (like "St Giles Circus - Estate Plan.pdf")

3. Select your tool from the Tools dropdown:
   - **Flood Fill (Smart)**: Click to fill an area while respecting building boundaries
   - **Brush Stroke**: Draw freehand lines
   - **Rectangle**: Draw rectangular shapes
   - **Text**: Add text at any location

4. For the **Text Tool**:
   - Type your text in the "Text Content" box
   - Adjust font size with the "Font Size" spinner (8-200px)
   - Click on the PDF to place the text at that location

5. Choose a color using the color button

5. Adjust settings as needed:
   - **Stroke Width**: Control brush/line thickness
   - **Fill Tolerance**: Adjust edge sensitivity for flood fill (lower = stricter boundaries)
   - **Zoom**: Use the slider to zoom in/out

6. Use action buttons:
   - **Undo**: Reverse the last action
   - **Reset Page**: Clear all modifications on current page
   - **Save PDF**: Export the annotated PDF

## How Smart Flood Fill Works

The smart flood fill uses edge detection to identify building boundaries:
1. Converts the image to grayscale
2. Applies Canny edge detection to find building outlines
3. Dilates the detected edges to create stronger barriers
4. Performs flood fill respecting these barriers
5. Blends the selected color with the existing image

The **Fill Tolerance** setting controls how strictly the algorithm respects boundaries:
- Lower values (0-20): Stricter boundaries, more color blocking at edges
- Medium values (20-40): Balanced approach (recommended)
- Higher values (40+): Looser boundaries, more color flexibility

## Keyboard Shortcuts

- Use the spinbox controls to navigate pages quickly
- Adjust zoom with the slider for better precision

## Tips for Best Results

1. Start with medium tolerance (30) and adjust based on your PDF's quality
2. Use zoom to see details and avoid accidentally filling large areas
3. Let multiple colors blend - they mix naturally for a better visual effect
4. For text labels, increase font size for visibility on zoomed-out views
5. Use contrasting colors for text to ensure readability on the PDF
6. Save frequently by exporting to a new file name until you're happy with results
7. For complex boundary areas, use the brush stroke tool instead of flood fill

## File Structure

- `pdf_colorizer.py`: Main application
- `requirements.txt`: Python dependencies
- PDF files to be processed

## Dependencies

- **PyQt6**: GUI framework
- **pdf2image**: PDF rendering
- **Pillow**: Image manipulation
- **OpenCV (cv2)**: Edge detection and image processing
- **PyMuPDF (fitz)**: PDF handling
- **NumPy**: Array operations
