#!/bin/bash

# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y python3 python3-pip tesseract-ocr libtesseract-dev libmagic-dev

# Install Python packages
pip3 install PyMuPDF pytesseract Pillow extract-msg mail-parser requests colorama dnspython python-whois

# Verify installations
echo "Verifying installations..."

# Check Python version
python3 --version

# Check if pip3 is installed
pip3 --version

# Check if Tesseract is installed
tesseract --version

# Check if PyMuPDF is installed
python3 -c "import fitz; print('PyMuPDF installed successfully')"

# Check if pytesseract is installed
python3 -c "import pytesseract; print('pytesseract installed successfully')"

# Check if Pillow is installed
python3 -c "from PIL import Image; print('Pillow installed successfully')"

# Check if extract-msg is installed
python3 -c "import extract_msg; print('extract-msg installed successfully')"

# Check if mail-parser is installed
python3 -c "import mailparser; print('mail-parser installed successfully')"

# Check if requests is installed
python3 -c "import requests; print('requests installed successfully')"

# Check if colorama is installed
python3 -c "import colorama; print('colorama installed successfully')"

# Check if dnspython is installed
python3 -c "import dns.resolver; print('dnspython installed successfully')"

# Check if python-whois is installed
python3 -c "import whois; print('python-whois installed successfully')"

echo "All dependencies installed successfully."
