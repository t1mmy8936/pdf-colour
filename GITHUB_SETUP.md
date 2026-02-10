# GitHub Setup & Deployment Guide

This guide explains how to set up the PDF Colorizer repository on GitHub and configure CI/CD.

## Prerequisites

- A GitHub account
- Git installed locally
- The working project directory with all files

## Step 1: Set Up Git Locally

```bash
cd c:\Users\TimothyOgden\Desktop\RandomPRoject
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"
git add .
git commit -m "Initial commit: PDF Colorizer with text tools and test suite"
```

## Step 2: Create Repository on GitHub

1. Go to https://github.com/new
2. Enter repository name: `pdf-colorizer`
3. Choose "Public" or "Private" (recommendation: Public for open source)
4. **Do NOT** initialize with README, .gitignore, or license (we have these)
5. Click "Create repository"
6. Copy the HTTPS URL (format: `https://github.com/YOUR_USERNAME/pdf-colorizer.git`)

## Step 3: Connect Local Repository to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/pdf-colorizer.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 4: Verify GitHub Actions Setup

1. Go to https://github.com/YOUR_USERNAME/pdf-colorizer
2. Click on "Actions" tab
3. You should see workflow files:
   - **tests.yml** - Runs tests on push and pull requests
   - **release.yml** - Creates releases when you tag commits

## Step 5: Enable GitHub Actions (if needed)

1. Go to Settings → Actions → General
2. Ensure "Allow all actions and reusable workflows" is selected
3. Save changes

## Running Tests Locally

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage report
python -m pytest tests/ --cov=./ --cov-report=html

# Run specific test class
python -m pytest tests/test_pdf_colorizer.py::TestImageHandling -v
```

## Creating a Release

1. Create a tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. GitHub Actions will automatically:
   - Build the Windows executable
   - Create a release on GitHub
   - Upload the executable as an artifact
   - Make it available for download

3. View releases at: https://github.com/YOUR_USERNAME/pdf-colorizer/releases

## Project Structure

```
pdf-colorizer/
├── .github/
│   └── workflows/
│       ├── tests.yml        # CI/CD pipeline
│       └── release.yml      # Release automation
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_pdf_colorizer.py
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
├── pytest.ini
├── build_executable.spec
├── pdf_colorizer.py
└── pdf_colorizer_debug.py
```

## CI/CD Pipeline Details

### Tests Workflow (tests.yml)

**Triggers:** Push to main/develop or pull requests

**Jobs:**
1. **test** - Runs on Windows, macOS, and Ubuntu with Python 3.9-3.12
   - Installs dependencies
   - Runs pytest with coverage
   - Uploads coverage to Codecov
   - Archives HTML coverage reports

2. **linting** - Code style checks
   - Black (code formatter)
   - isort (import sorter)
   - flake8 (linter)

3. **build** - Creates Windows executable
   - Requires tests to pass first
   - Uses PyInstaller
   - Uploads PDF_Colorizer.exe artifact

## Troubleshooting

### Tests failing in CI/CD but passing locally

- Check Python versions: CI uses 3.9, 3.10, 3.11, 3.12
- Ensure requirements.txt is up to date
- Run tests with different Python versions locally

### GitHub Actions not running

- Check that workflows are in `.github/workflows/`
- Verify GitHub Actions is enabled in Settings
- Check workflow syntax (YAML formatting)

### Release build fails

- Ensure PyInstaller spec file exists: `build_executable.spec`
- Check that all dependencies are in `requirements.txt`
- Verify Windows SDK is available (usually automatic)

## Next Steps

1. Add codecov badge to README (optional):
   ```markdown
   [![codecov](https://codecov.io/gh/YOUR_USERNAME/pdf-colorizer/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/pdf-colorizer)
   ```

2. Set up branch protection rules (optional):
   - Settings → Branches → Add rule
   - Branch name pattern: `main`
   - Require status checks to pass before merging

3. Add collaborators:
   - Settings → Collaborators → Add people

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
