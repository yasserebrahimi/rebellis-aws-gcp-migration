# Security
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256


# Storage
STORAGE_BACKEND=local
UPLOAD_DIR=./uploads


# ML Models
WHISPER_MODEL_SIZE=base
MOTION_MODEL_PATH=./models/motion


# API#!/bin/bash


# ============================================
# Rebellis Infrastructure Setup Script
# ============================================


set -euo pipefail


# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'


# Configuration
ENVIRONMENT=${1:-development}
PROJECT_NAME="rebellis"
PYTHON_VERSION="3.11"
NODE_VERSION="18"


# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }


# Header
echo "============================================"
echo " Rebellis Infrastructure Setup"
echo " Environment: $ENVIRONMENT"
echo "============================================"


# Detect OS
detect_os() {
if [[ "${OSTYPE:-}" == linux-gnu* ]]; then
OS="linux"
DISTRO=$(lsb_release -si 2>/dev/null || echo "unknown")
elif [[ "${OSTYPE:-}" == darwin* ]]; then
OS="macos"
else
log_error "Unsupported OS: ${OSTYPE:-unknown}"
fi
log_info "Detected OS: $OS ${DISTRO:-}"
}


# Install Python
install_python() {
log_info "Installing Python $PYTHON_VERSION..."


if command -v python$PYTHON_VERSION >/dev/null 2>&1; then
log_success "Python $PYTHON_VERSION already installed"
return
fi


if [[ "$OS" == "linux" ]]; then
if command -v apt-get >/dev/null 2>&1; then
sudo apt-get update
sudo apt-get install -y python$PYTHON_VERSION python$PYTHON_VERSION-venv python$PYTHON_VERSION-dev
else
log_warning "Non-Debian distro detected. Please install Python $PYTHON_VERSION manually."
fi
elif [[ "$OS" == "macos" ]]; then
main