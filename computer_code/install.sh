#!/bin/bash

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
    if ! command -v "$pkg" &> /dev/null; then
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
install_if_missing ffmpeg


# install v4l2
install_if_missing v4l-utils

# Upgrade pip and install numpy
pip install --upgrade pip
pip install numpy scipy opencv-python flask Flask-SocketIO Ruckig flask-cors

echo "Virtual environment ready and numpy installed."  

