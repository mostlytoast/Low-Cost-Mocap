#!/bin/bash

# Ensure script is run from the 'computer_code' directory
if [ "$(basename "$PWD")" != "computer_code" ]; then
    echo "Error: Please run this script from the 'computer_code' directory."
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Using existing virtual environment."
else
    echo "Creating new virtual environment."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate
# Function to check and install a package if not present
install_if_missing() {
    local pkg="$1"
    local trg_pkg="$2" #name of package as used in command line
    if ! command -v "$trg_pkg" &> /dev/null; then
        echo "$pkg not found, attempting to install..."
        if [ "$(uname)" == "Darwin" ]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew install "$pkg"
            else
                echo "Homebrew not found. Please install $pkg manually."
                exit 1
            fi
        elif [ -f /etc/debian_version ]; then
            # Debian/Ubuntu
            sudo apt-get update
            sudo apt-get install -y "$pkg"
        elif [ -f /etc/redhat-release ]; then
            # RHEL/CentOS/Fedora
            sudo dnf install -y "$pkg" || sudo yum install -y "$pkg"
        else
            echo "Unsupported OS. Please install $pkg manually."
            exit 1
        fi
    else
        echo "$pkg is already installed."
    fi
}

# install ffmpeg
install_if_missing ffmpeg ffmpeg


# install v4l2
#TODO install mac/windows alternatives based on system version 
install_if_missing v4l-utils  v4l2-ctl 

# Upgrade pip and install numpy
pip install --upgrade pip
pip install numpy scipy flask Flask-SocketIO Ruckig flask-cors scikit-spatial line-profiler PyQt5 opencv-python-headless imutils pyvirtualcam pyinstaller moderngl pyrr

echo "Virtual environment ready and numpy installed."  

echo "Run 'source venv/bin/activate' to activate the virtual environment in your terminal."