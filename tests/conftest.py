import pytest
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_image_dir(tmp_path):
    """Fixture providing a temporary directory for test images"""
    return tmp_path


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Fixture providing a temp path for PDF files"""
    return tmp_path / "test.pdf"


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
