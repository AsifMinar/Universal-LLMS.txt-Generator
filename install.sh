#!/bin/bash
# Universal LLMs.txt Generator Installation Script
# Updated: 2025-06-06
# Author: AsifMinar

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emojis for better UX
ROCKET="🚀"
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
GEAR="⚙️"

echo -e "${BLUE}${ROCKET} Universal LLMs.txt Generator Installation${NC}"
echo "=================================================="
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}${WARNING} $1${NC}"
}

print_info() {
    echo -e "${BLUE}${INFO} $1${NC}"
}

# Check if running as root (not recommended)
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root is not recommended. Consider using a virtual environment."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
fi

print_info "Detected OS: $OS"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
    echo ""
    print_info "Installation instructions:"
    case $OS in
        "linux")
            echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
            echo "  CentOS/RHEL:   sudo dnf install python3 python3-pip"
            echo "  Arch Linux:    sudo pacman -S python python-pip"
            ;;
        "macos")
            echo "  macOS: brew install python3"
            echo "  Or download from: https://python.org"
            ;;
        "windows")
            echo "  Windows: Download from https://python.org"
            echo "  Or use Microsoft Store: python3"
            ;;
        *)
            echo "  Visit: https://python.org/downloads"
            ;;
    esac
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

version_check() {
    printf '%s\n%s\n' "$required_version" "$python_version" | sort -V | head -n1
}

if [ "$(version_check)" != "$required_version" ]; then
    print_error "Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

print_status "Python $python_version found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    print_info "Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Check if git is installed (for GitHub installation)
if ! command -v git &> /dev/null; then
    print_warning "Git is not installed. Will use alternative installation method."
    USE_GIT=false
else
    USE_GIT=true
fi

# Create virtual environment option
echo ""
print_info "Installation options:"
echo "1. System-wide installation (requires sudo/admin)"
echo "2. User installation (recommended)"
echo "3. Virtual environment (best practice)"
echo ""
read -p "Choose installation method (1/2/3): " -n 1 -r INSTALL_METHOD
echo ""

case $INSTALL_METHOD in
    1)
        INSTALL_CMD="sudo pip3 install"
        print_warning "Installing system-wide (requires admin privileges)"
        ;;
    2)
        INSTALL_CMD="pip3 install --user"
        print_info "Installing for current user only"
        ;;
    3)
        print_info "Creating virtual environment..."
        
        # Check if venv module is available
        if ! python3 -c "import venv" &> /dev/null; then
            print_error "Python venv module not available. Installing python3-venv..."
            case $OS in
                "linux")
                    sudo apt install python3-venv 2>/dev/null || sudo dnf install python3-venv 2>/dev/null || print_warning "Please install python3-venv manually"
                    ;;
                *)
                    print_warning "Please ensure python3-venv is installed"
                    ;;
            esac
        fi
        
        # Create and activate virtual environment
        python3 -m venv llms-txt-env
        source llms-txt-env/bin/activate 2>/dev/null || source llms-txt-env/Scripts/activate 2>/dev/null
        INSTALL_CMD="pip install"
        print_status "Virtual environment created and activated"
        ;;
    *)
        print_error "Invalid option. Using user installation."
        INSTALL_CMD="pip3 install --user"
        ;;
esac

# Upgrade pip
print_info "Upgrading pip..."
$INSTALL_CMD --upgrade pip

# Install the package
print_info "Installing Universal LLMs.txt Generator..."

if [ "$USE_GIT" = true ]; then
    # Install from GitHub
    if $INSTALL_CMD git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git; then
        print_status "Installation from GitHub successful!"
    else
        print_warning "GitHub installation failed. Trying alternative method..."
        # Fallback to pip install (when package is published)
        # $INSTALL_CMD universal-llms-txt-generator
        print_error "Installation failed. Please check your internet connection and try again."
        exit 1
    fi
else
    print_warning "Git not available. Manual installation required."
    echo ""
    print_info "Manual installation steps:"
    echo "1. Download: https://github.com/AsifMinar/Universal-LLMS.txt-Generator/archive/main.zip"
    echo "2. Extract the ZIP file"
    echo "3. Navigate to the extracted folder"
    echo "4. Run: pip install -r requirements.txt"
    echo "5. Run: chmod +x llms_txt_generator.py"
    exit 1
fi

# Verify installation
print_info "Verifying installation..."

# Check if the command is available
if command -v llms-txt-gen &> /dev/null; then
    print_status "Command-line tool installed successfully!"
    COMMAND="llms-txt-gen"
elif python3 -c "import llms_txt_generator" &> /dev/null; then
    print_status "Python module installed successfully!"
    COMMAND="python3 -m llms_txt_generator"
else
    print_warning "Installation completed but command not found in PATH"
    print_info "You can run the tool using: python3 llms_txt_generator.py"
    COMMAND="python3 llms_txt_generator.py"
fi

# Show success message and next steps
echo ""
echo "=================================================="
print_status "Installation Complete!"
echo "=================================================="
echo ""
print_info "Quick Start Guide:"
echo ""
echo "${GEAR} Initialize configuration:"
echo "   $COMMAND --init"
echo ""
echo "${GEAR} Generate llms.txt:"
echo "   $COMMAND --generate"
echo ""
echo "${GEAR} Set up auto-updates:"
echo "   $COMMAND --setup-cron --interval daily"
echo ""
echo "${GEAR} Start webhook server:"
echo "   $COMMAND --webhook --port 8080"
echo ""
print_info "Documentation: https://github.com/AsifMinar/Universal-LLMS.txt-Generator"
print_info "Issues: https://github.com/AsifMinar/Universal-LLMS.txt-Generator/issues"
echo ""

# Offer to run initialization
read -p "Would you like to initialize the configuration now? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    print_info "Initializing configuration..."
    
    # Ask for website type
    echo "What type of website do you have?"
    echo "1. WordPress"
    echo "2. Static Site (Hugo, Jekyll, Gatsby, etc.)"
    echo "3. Django"
    echo "4. Flask"
    echo "5. Other (will use sitemap.xml)"
    echo ""
    read -p "Choose your website type (1-5): " -n 1 -r SITE_TYPE
    echo ""
    
    case $SITE_TYPE in
        1) INIT_TYPE="wordpress" ;;
        2) INIT_TYPE="static" ;;
        3) INIT_TYPE="django" ;;
        4) INIT_TYPE="flask" ;;
        *) INIT_TYPE="sitemap" ;;
    esac
    
    if $COMMAND --init --type $INIT_TYPE; then
        print_status "Configuration initialized!"
        print_info "Edit llms_config.yaml to customize your settings"
        print_info "Then run: $COMMAND --generate"
    else
        print_warning "Initialization failed. You can run it manually later."
    fi
fi

echo ""
print_status "Setup complete! Happy generating! 🎉"

# If virtual environment was created, remind user
if [ "$INSTALL_METHOD" = "3" ]; then
    echo ""
    print_info "Remember to activate your virtual environment before using:"
    echo "   source llms-txt-env/bin/activate"
    echo "   # or on Windows: llms-txt-env\\Scripts\\activate"
fi
