#!/bin/bash

# AI Refinement Dashboard Setup Script
# This script sets up the entire development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to create directory if it doesn't exist
create_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        print_status "Created directory: $1"
    fi
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status "Python version: $PYTHON_VERSION"
        
        # Check if version is 3.8 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python version is compatible (3.8+)"
        else
            print_error "Python 3.8 or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Function to check Node.js version
check_node_version() {
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_status "Node.js version: $NODE_VERSION"
        
        # Check if version is 16 or higher
        if node -e "const v=process.version.slice(1).split('.'); exit(v[0]>=16?0:1)"; then
            print_success "Node.js version is compatible (16+)"
        else
            print_error "Node.js 16 or higher is required"
            exit 1
        fi
    else
        print_error "Node.js is not installed"
        exit 1
    fi
}

# Function to check Ollama
check_ollama() {
    if command_exists ollama; then
        print_success "Ollama is installed"
        
        # Check if Ollama is running
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            print_success "Ollama is running"
        else
            print_warning "Ollama is not running. Please start it with: ollama serve"
        fi
    else
        print_warning "Ollama is not installed. Please install it from https://ollama.ai"
    fi
}

# Function to setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Python environment setup completed"
}

# Function to setup Node.js environment
setup_node_env() {
    print_status "Setting up Node.js environment..."
    
    # Install Node.js dependencies
    if [ -f "frontend/package.json" ]; then
        cd frontend
        print_status "Installing Node.js dependencies..."
        npm install
        cd ..
        print_success "Node.js environment setup completed"
    else
        print_error "frontend/package.json not found"
        exit 1
    fi
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    # Create necessary directories
    create_dir "backend"
    create_dir "backend/migrations"
    create_dir "backend/chromadb_data"
    create_dir "backend/avatars"
    create_dir "backend/training_scripts"
    
    # Run database setup
    cd backend
    python3 setup_db.py --action setup
    cd ..
    
    print_success "Database setup completed"
}

# Function to setup environment file
setup_env_file() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success "Created .env file from env.example"
            print_warning "Please review and modify .env file as needed"
        else
            print_warning "env.example not found, skipping .env setup"
        fi
    else
        print_status ".env file already exists"
    fi
}

# Function to check ports
check_ports() {
    print_status "Checking required ports..."
    
    if port_in_use 5000; then
        print_warning "Port 5000 is already in use (backend)"
    else
        print_success "Port 5000 is available (backend)"
    fi
    
    if port_in_use 5173; then
        print_warning "Port 5173 is already in use (frontend)"
    else
        print_success "Port 5173 is available (frontend)"
    fi
    
    if port_in_use 11434; then
        print_success "Port 11434 is in use (Ollama)"
    else
        print_warning "Port 11434 is not in use (Ollama)"
    fi
}

# Function to run tests
run_tests() {
    print_status "Running basic tests..."
    
    # Test Python imports
    source venv/bin/activate
    python3 -c "
import sys
sys.path.append('backend')
try:
    from database import db
    from api_server import app
    print('✅ Python imports successful')
except Exception as e:
    print(f'❌ Python import error: {e}')
    sys.exit(1)
"
    
    # Test Node.js build
    cd frontend
    if npm run build >/dev/null 2>&1; then
        print_success "Frontend build test passed"
    else
        print_warning "Frontend build test failed"
    fi
    cd ..
}

# Function to show final status
show_final_status() {
    echo ""
    echo "🎉 AI Refinement Dashboard Setup Complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Review .env file configuration"
    echo "  2. Start Ollama: ollama serve"
    echo "  3. Start the application: ./start_services.sh"
    echo ""
    echo "🌐 Access URLs:"
    echo "  Frontend: http://localhost:5173"
    echo "  Backend API: http://localhost:5000"
    echo "  Health Check: http://localhost:5000/api/health"
    echo ""
    echo "📚 Documentation:"
    echo "  Database migrations: python3 backend/setup_db.py --help"
    echo "  Service management: ./start_services.sh --help"
    echo ""
}

# Main setup function
main() {
    echo "🚀 AI Refinement Dashboard Setup"
    echo "================================="
    echo ""
    
    # Check system requirements
    print_status "Checking system requirements..."
    check_python_version
    check_node_version
    check_ollama
    check_ports
    echo ""
    
    # Setup environments
    setup_python_env
    echo ""
    setup_node_env
    echo ""
    
    # Setup database and configuration
    setup_database
    echo ""
    setup_env_file
    echo ""
    
    # Run tests
    run_tests
    echo ""
    
    # Show final status
    show_final_status
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "AI Refinement Dashboard Setup Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --quick        Skip tests and port checks"
        echo "  --no-tests     Skip tests"
        echo ""
        echo "This script will:"
        echo "  - Check system requirements (Python 3.8+, Node.js 16+)"
        echo "  - Create Python virtual environment"
        echo "  - Install Python dependencies"
        echo "  - Install Node.js dependencies"
        echo "  - Setup database with migrations"
        echo "  - Create environment configuration"
        echo "  - Run basic tests"
        echo ""
        exit 0
        ;;
    --quick)
        print_status "Running quick setup (skipping tests and port checks)..."
        check_python_version
        check_node_version
        setup_python_env
        setup_node_env
        setup_database
        setup_env_file
        show_final_status
        ;;
    --no-tests)
        print_status "Running setup without tests..."
        check_python_version
        check_node_version
        check_ollama
        check_ports
        setup_python_env
        setup_node_env
        setup_database
        setup_env_file
        show_final_status
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
