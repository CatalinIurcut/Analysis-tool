#!/bin/bash

# Function to check if a package is installed and install it if not
check_and_install() {
    package=$1
    if ! dpkg -s $package > /dev/null 2>&1; then
        echo "$package is not installed. Installing..."
        sudo apt-get install -y $package
    else
        echo "$package is already installed."
    fi
}

# Function to check if a Python package is installed and install it if not
check_and_install_pip_package() {
    package=$1
    if ! python3 -m pip show $package > /dev/null 2>&1; then
        echo "$package is not installed. Installing..."
        python3 -m pip install $package
    else
        echo "$package is already installed."
    fi
}

# Update package list
echo "Updating package list..."
sudo apt-get update

# List of required Ubuntu packages
ubuntu_packages=(
    "python3"
    "python3-pip"
    "tesseract-ocr"
    "poppler-utils"
    "libtiff5-dev"
    "libjpeg8-dev"
    "zlib1g-dev"
    "libfreetype6-dev"
    "liblcms2-dev"
    "libopenjp2-7"
    "libopenjp2-7-dev"
    "libwebp-dev"
    "libharfbuzz-dev"
    "libfribidi-dev"
    "whois"
)

# List of required Python packages
python_packages=(
    "PyMuPDF"
    "extract-msg"
    "mail-parser"
    "requests"
    "colorama"
)

# Install required Ubuntu packages
for package in "${ubuntu_packages[@]}"; do
    check_and_install $package
done

# Install required Python packages
for package in "${python_packages[@]}"; do
    check_and_install_pip_package $package
done

echo "All dependencies installed."
