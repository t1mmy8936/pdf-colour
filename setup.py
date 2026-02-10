from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pdf-colorizer",
    version="1.0.0",
    author="Timothy Ogden",
    description="A tool for color-coding PDF street plans and architectural drawings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TimothyOgden/pdf-colorizer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.9",
    install_requires=[
        "PyQt6>=6.7.0",
        "Pillow>=10.2.0",
        "opencv-python>=4.9.0",
        "numpy>=2.0.0",
        "pymupdf>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "pdf-colorizer=pdf_colorizer:main",
        ],
    },
)
