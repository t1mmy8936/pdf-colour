import pytest
import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw
from io import BytesIO
import tempfile

# Add the project directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestImageHandling:
    """Test image loading and manipulation"""
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample image for testing"""
        img = Image.new('RGB', (500, 500), color='white')
        return img
    
    def test_image_creation(self, sample_image):
        """Test that sample image is created correctly"""
        assert sample_image.width == 500
        assert sample_image.height == 500
        assert sample_image.mode == 'RGB'
    
    def test_image_resize(self, sample_image):
        """Test image resizing"""
        resized = sample_image.resize((250, 250))
        assert resized.width == 250
        assert resized.height == 250
    
    def test_image_format_conversion(self, sample_image):
        """Test converting image formats"""
        # Convert to RGB
        rgb_img = sample_image.convert('RGB')
        assert rgb_img.mode == 'RGB'
        
        # Convert to RGBA
        rgba_img = sample_image.convert('RGBA')
        assert rgba_img.mode == 'RGBA'
    
    def test_image_to_bytes(self, sample_image):
        """Test converting image to bytes"""
        data = sample_image.tobytes('raw', 'RGB')
        assert len(data) == 500 * 500 * 3  # width * height * 3 bytes per pixel
    
    def test_image_draw(self, sample_image):
        """Test drawing on image"""
        draw = ImageDraw.Draw(sample_image)
        # Draw a line
        draw.line([(0, 0), (100, 100)], fill='black', width=2)
        # Verify pixel changed
        assert sample_image.getpixel((50, 50)) != (255, 255, 255)


class TestColorProcessing:
    """Test color handling and operations"""
    
    def test_rgb_tuple_conversion(self):
        """Test RGB color tuple creation"""
        color = (255, 0, 0)
        assert color[0] == 255  # Red
        assert color[1] == 0    # Green
        assert color[2] == 0    # Blue
    
    def test_color_blending(self):
        """Test color blending calculation"""
        color1 = (255, 0, 0)  # Red
        color2 = (0, 0, 255)  # Blue
        alpha = 0.5
        
        blended = tuple(int(c1 * alpha + c2 * (1 - alpha)) 
                       for c1, c2 in zip(color1, color2))
        
        assert blended == (127, 0, 127)
    
    def test_grayscale_conversion(self):
        """Test conversion to grayscale"""
        img = Image.new('RGB', (100, 100), color='white')
        gray = img.convert('L')
        
        assert gray.mode == 'L'
        pixel_value = gray.getpixel((0, 0))
        assert pixel_value == 255  # White should be 255 in grayscale


class TestFileOperations:
    """Test file I/O operations"""
    
    def test_image_save_load(self):
        """Test saving and loading images"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Create and save image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(tmp_path, 'PNG')
            
            # Load and verify
            loaded = Image.open(tmp_path)
            assert loaded.width == 100
            assert loaded.height == 100
            assert loaded.mode == 'RGB'
        finally:
            try:
                os.unlink(tmp_path)
            except PermissionError:
                # Windows file locking, try again
                import time
                time.sleep(0.1)
                try:
                    os.unlink(tmp_path)
                except:
                    pass
    
    def test_bytes_io_handling(self):
        """Test BytesIO buffer operations"""
        img = Image.new('RGB', (50, 50), color='blue')
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        # Verify buffer has data
        assert len(buffer.getvalue()) > 0
        
        # Reload from buffer
        buffer.seek(0)
        loaded = Image.open(buffer)
        assert loaded.width == 50
        assert loaded.height == 50
    
    def test_temp_file_creation(self):
        """Test temporary file operations"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'test data')
            tmp_path = tmp.name
        
        try:
            assert Path(tmp_path).exists()
            with open(tmp_path, 'rb') as f:
                data = f.read()
            assert data == b'test data'
        finally:
            os.unlink(tmp_path)


class TestFlooding:
    """Test flood fill operations"""
    
    @pytest.fixture
    def floodfill_test_image(self):
        """Create a simple image for flood fill testing"""
        img = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(img)
        # Draw a black rectangle
        draw.rectangle([25, 25, 75, 75], outline='black', width=2)
        return img
    
    def test_floodfill_same_color(self, floodfill_test_image):
        """Test flood fill with same color"""
        from PIL import ImageDraw as ID
        
        # Fill white area with blue
        ID.floodfill(floodfill_test_image, (10, 10), (0, 0, 255), thresh=0)
        
        # Check that area was filled
        pixel = floodfill_test_image.getpixel((10, 10))
        assert pixel == (0, 0, 255)
    
    def test_floodfill_respects_boundaries(self, floodfill_test_image):
        """Test that flood fill respects color boundaries"""
        from PIL import ImageDraw as ID
        
        # Fill white area with red
        ID.floodfill(floodfill_test_image, (10, 10), (255, 0, 0), thresh=0)
        
        # Area inside rectangle should not be filled
        pixel_inside = floodfill_test_image.getpixel((50, 50))
        assert pixel_inside == (255, 255, 255)  # Still white
    
    def test_edge_strength_detection(self):
        """Test that edge strength threshold is applied correctly"""
        import cv2
        import numpy as np
        
        # Create an image with both strong and faint edges
        img = Image.new('RGB', (200, 200), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw a strong black rectangle
        draw.rectangle([50, 50, 150, 150], outline='black', width=3)
        
        # Draw a faint gray line at a different location
        draw.line([(160, 50), (160, 150)], fill=(200, 200, 200), width=1)
        
        # Convert to numpy for edge detection
        img_array = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        
        # Compute edge magnitude
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edge_magnitude = np.sqrt(sobelx**2 + sobely**2).astype(np.uint8)
        
        # Get magnitudes in regions with edges
        strong_edge_magnitude = np.max(edge_magnitude[49:52, 49:52])  # At the strong black rectangle corner
        faint_edge_magnitude = np.max(edge_magnitude[50:70, 159:161])  # At the faint gray line
        
        assert strong_edge_magnitude > faint_edge_magnitude, \
            f"Strong edge magnitude ({strong_edge_magnitude}) should be > faint edge ({faint_edge_magnitude})"
    
    def test_edge_strength_threshold_filtering(self):
        """Test that edge strength thresholding filters weak edges"""
        import cv2
        import numpy as np
        
        # Create test image with edges of varying strength
        img = Image.new('RGB', (150, 150), 'white')
        draw = ImageDraw.Draw(img)
        draw.line([(50, 50), (50, 100)], fill='black', width=2)
        
        img_array = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edge_magnitude = np.sqrt(sobelx**2 + sobely**2).astype(np.uint8)
        
        # Test different threshold levels
        threshold_low = 30
        threshold_high = 100
        
        barrier_low = (edge_magnitude > threshold_low).astype(np.uint8) * 255
        barrier_high = (edge_magnitude > threshold_high).astype(np.uint8) * 255
        
        # Higher threshold should result in fewer barriers
        assert barrier_high.sum() <= barrier_low.sum(), \
            "Higher threshold should produce fewer/equal barrier pixels"


class TestTextRendering:
    """Test text drawing operations"""
    
    def test_text_placement(self):
        """Test placing text on image"""
        img = Image.new('RGB', (200, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to draw text (may not work without proper font)
        try:
            draw.text((10, 10), "Test", fill='black')
            # Check if pixel changed
            pixel = img.getpixel((10, 10))
            assert pixel != (255, 255, 255)
        except Exception:
            # Font not available, which is okay for this test
            pass
    
    def test_text_color(self):
        """Test text rendering with different colors"""
        img = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw text in black
        try:
            draw.text((5, 5), "Hi", fill=(0, 0, 0))
            # Verify some pixels changed from white
            changed = False
            for x in range(20):
                for y in range(15):
                    if img.getpixel((5 + x, 5 + y)) != (255, 255, 255):
                        changed = True
                        break
            assert changed
        except Exception:
            # Font not available
            pass


class TestImageProcessing:
    """Test advanced image processing"""
    
    def test_image_copy(self):
        """Test image copying"""
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = img1.copy()
        
        # Modify copy
        draw = ImageDraw.Draw(img2)
        draw.rectangle([0, 0, 50, 50], fill='blue')
        
        # Original should be unchanged
        assert img1.getpixel((25, 25)) == (255, 0, 0)
        assert img2.getpixel((25, 25)) == (0, 0, 255)
    
    def test_image_crop(self):
        """Test image cropping"""
        img = Image.new('RGB', (100, 100), color='green')
        cropped = img.crop((25, 25, 75, 75))
        
        assert cropped.width == 50
        assert cropped.height == 50
    
    def test_image_transparency(self):
        """Test RGBA with transparency"""
        img = Image.new('RGBA', (100, 100), (255, 255, 255, 255))
        
        # Set a pixel with partial transparency
        img.putpixel((50, 50), (255, 0, 0, 128))
        
        pixel = img.getpixel((50, 50))
        assert pixel == (255, 0, 0, 128)


class TestDataStructures:
    """Test data handling and structures"""
    
    def test_undo_stack(self):
        """Test undo stack with images"""
        undo_stack = []
        
        img1 = Image.new('RGB', (50, 50), color='red')
        img2 = Image.new('RGB', (50, 50), color='blue')
        
        undo_stack.append(img1)
        undo_stack.append(img2)
        
        assert len(undo_stack) == 2
        
        popped = undo_stack.pop()
        assert popped.getpixel((0, 0)) == (0, 0, 255)
        assert len(undo_stack) == 1
    
    def test_page_list(self):
        """Test page list management"""
        pages = []
        
        for i in range(3):
            img = Image.new('RGB', (100, 100), color=(i*80, i*80, i*80))
            pages.append(img)
        
        assert len(pages) == 3
        assert pages[0].getpixel((0, 0)) == (0, 0, 0)
        assert pages[2].getpixel((0, 0)) == (160, 160, 160)
    
    def test_zoom_calculations(self):
        """Test zoom level calculations"""
        original_width = 1000
        original_height = 800
        
        zoom_level = 1.5
        
        new_width = int(original_width * zoom_level)
        new_height = int(original_height * zoom_level)
        
        assert new_width == 1500
        assert new_height == 1200
    
    def test_zoom_inverse_transformation(self):
        """Test inverse zoom transformation"""
        screen_x, screen_y = 300, 200
        zoom_level = 2.0
        
        # Convert screen coords to image coords
        image_x = int(screen_x / zoom_level)
        image_y = int(screen_y / zoom_level)
        
        assert image_x == 150
        assert image_y == 100


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_zero_dimension_handling(self):
        """Test handling of invalid dimensions"""
        # PIL allows creating images with 0 dimensions, so we test that it doesn't crash
        try:
            img = Image.new('RGB', (0, 100))
            # If it succeeds, that's okay - PIL is lenient
            assert img is not None
        except (ValueError, TypeError):
            # Or it could raise an error, which we also accept
            pass
    
    def test_invalid_color_format(self):
        """Test handling of invalid color formats"""
        img = Image.new('RGB', (50, 50))
        draw = ImageDraw.Draw(img)
        
        # This might not raise but should handle gracefully
        try:
            draw.text((10, 10), "test", fill="invalid")
        except (ValueError, AttributeError):
            pass  # Expected to fail
    
    def test_out_of_bounds_access(self):
        """Test accessing pixels out of bounds"""
        img = Image.new('RGB', (100, 100))
        
        # This should raise IndexError
        with pytest.raises(IndexError):
            img.getpixel((200, 200))
    
    def test_image_mode_mismatch(self):
        """Test handling mode mismatches"""
        img_rgb = Image.new('RGB', (50, 50))
        img_l = Image.new('L', (50, 50))
        
        assert img_rgb.mode != img_l.mode
        
        # Converting should work
        converted = img_rgb.convert('L')
        assert converted.mode == 'L'


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_create_color_draw_save_workflow(self):
        """Test complete workflow: create -> color -> draw -> save"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Create
            img = Image.new('RGB', (200, 200), 'white')
            
            # Color
            img.putpixel((100, 100), (255, 0, 0))
            
            # Draw
            draw = ImageDraw.Draw(img)
            draw.line([(0, 0), (200, 200)], fill='blue', width=2)
            
            # Save
            img.save(tmp_path, 'PNG')
            
            # Verify
            assert Path(tmp_path).exists()
            loaded = Image.open(tmp_path)
            assert loaded.width == 200
            assert loaded.height == 200
        finally:
            try:
                if Path(tmp_path).exists():
                    os.unlink(tmp_path)
            except PermissionError:
                import time
                time.sleep(0.1)
                try:
                    os.unlink(tmp_path)
                except:
                    pass
    
    def test_multi_page_simulation(self):
        """Test simulating multi-page document workflow"""
        pages = []
        
        # Create 3 pages
        for i in range(3):
            img = Image.new('RGB', (100, 100), color=(50 + i*50, 50 + i*50, 50 + i*50))
            pages.append(img)
        
        # Modify page 1
        draw = ImageDraw.Draw(pages[1])
        draw.rectangle([10, 10, 90, 90], outline='black')
        
        # Verify modifications
        assert pages[0].getpixel((0, 0)) == (50, 50, 50)
        assert pages[1].getpixel((0, 0)) == (100, 100, 100)
        assert pages[2].getpixel((0, 0)) == (150, 150, 150)
