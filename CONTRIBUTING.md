# Contributing to PDF Colorizer

Thank you for interest in contributing! This guide will help you get set up for development.

## Getting Started

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/pdf-colorizer.git
cd pdf-colorizer
```

### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black isort flake8
```

### 3. Make Your Changes

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python -m pytest tests/ -v

# Format code
black pdf_colorizer.py
isort pdf_colorizer.py

# Check linting
flake8 pdf_colorizer.py
```

### 4. Commit and Push

```bash
git add .
git commit -m "Add: description of your changes"
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to https://github.com/YOUR_USERNAME/pdf-colorizer
2. Click "Compare & pull request"
3. Add description of changes
4. Submit!

## Development Guidelines

### Code Style

- Use Black for formatting: `black pdf_colorizer.py`
- Sort imports with isort: `isort pdf_colorizer.py`
- Maximum line length: 120 characters
- Follow PEP 8 conventions

### Testing

- Write tests for new features in `tests/test_pdf_colorizer.py`
- Ensure all tests pass: `python -m pytest tests/ -v`
- Aim for >80% code coverage: `python -m pytest tests/ --cov=./`

### Commit Messages

Use clear, descriptive commit messages:
- `Add: new feature description`
- `Fix: bug description`
- `Improve: enhancement description`
- `Docs: documentation update`

## Feature Development

### Adding a New Tool

1. Add tool option to UI in `initUI()`
2. Add handler method (e.g., `def new_tool(self, x, y)`)
3. Add tool selection logic in `on_image_click()`
4. Add corresponding tests
5. Update README with usage instructions

### Adding New Dependencies

```bash
# Install the package
pip install package-name

# Add to requirements.txt
pip freeze > requirements.txt

# Commit changes
git add requirements.txt
git commit -m "Add: package-name for feature X"
```

## Testing Checklist

Before submitting a PR, ensure:

- [ ] Code runs without errors
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Code is formatted: `black pdf_colorizer.py`
- [ ] Imports are sorted: `isort pdf_colorizer.py`
- [ ] No linting issues: `flake8 pdf_colorizer.py`
- [ ] New features have tests
- [ ] Documentation is updated

## Common Tasks

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test class
python -m pytest tests/test_pdf_colorizer.py::TestImageHandling -v

# Specific test
python -m pytest tests/test_pdf_colorizer.py::TestImageHandling::test_image_creation -v

# With coverage
python -m pytest tests/ --cov=./ --cov-report=html

# Stop on first failure
python -m pytest tests/ -x
```

### Debugging

```bash
# Run with verbose output
python -m pytest tests/ -vv

# Show print statements
python -m pytest tests/ -s

# Drop into debugger on failure
python -m pytest tests/ --pdb
```

### Building Executable

```bash
pip install pyinstaller
pyinstaller build_executable.spec
# Executable will be in dist/PDF_Colorizer.exe
```

## Code Review Process

When you submit a PR:

1. GitHub Actions runs tests automatically
2. Code is reviewed by maintainers
3. Changes may be requested
4. Once approved, PR is merged

## Questions?

- Check existing issues for similar questions
- Create a new issue to ask for help
- Look at similar code for examples

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing! 🎉
