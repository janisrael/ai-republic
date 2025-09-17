#!/bin/bash

# AI Refinement Dashboard - Service Management Script
# This script manages the frontend and backend services

PROJECT_ROOT="/run/media/swordfish/New Volume2/development/hasaan/ai-refinement-dashboard"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

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

# Function to stop all services
stop_services() {
    print_status "Stopping all services..."
    
    # Kill processes by port
    for port in 5000 5001 5173 6001 6002; do
        PID=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$PID" ]; then
            print_status "Killing process on port $port (PID: $PID)"
            kill -9 $PID 2>/dev/null
        fi
    done
    
    # Kill by process name
    pkill -f "api_server.py" 2>/dev/null
    pkill -f "npm run dev" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    pkill -f "python3.*api_server" 2>/dev/null
    
    sleep 2
    print_success "All services stopped"
}

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start after $max_attempts seconds"
    return 1
}

# Function to start backend service
start_backend() {
    print_status "Starting backend API server..."
    
    if ! check_port 5000; then
        print_warning "Port 5000 is already in use"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Check if required files exist
    if [ ! -f "api_server.py" ]; then
        print_error "api_server.py not found in $BACKEND_DIR"
        return 1
    fi
    
    # Start backend in background
    nohup python3 api_server.py > api_server.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    
    # Wait for backend to be ready
    if wait_for_service "http://localhost:5000/api/health" "Backend API"; then
        print_success "Backend API server started (PID: $BACKEND_PID)"
        return 0
    else
        print_error "Failed to start backend API server"
        return 1
    fi
}

# Function to start frontend service
start_frontend() {
    print_status "Starting frontend development server..."
    
    if ! check_port 5173; then
        print_warning "Port 5173 is already in use"
        return 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in $FRONTEND_DIR"
        return 1
    fi
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend in background
    nohup npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid
    
    # Wait for frontend to be ready
    if wait_for_service "http://localhost:5173" "Frontend"; then
        print_success "Frontend development server started (PID: $FRONTEND_PID)"
        return 0
    else
        print_error "Failed to start frontend development server"
        return 1
    fi
}

# Function to start all services
start_all() {
    print_status "Starting AI Refinement Dashboard services..."
    
    # Stop any existing services first
    stop_services
    
    # Start backend
    if start_backend; then
        # Start frontend
        if start_frontend; then
            print_success "All services started successfully!"
            echo ""
            echo "🌐 Frontend: http://localhost:5173"
            echo "🔧 Backend API: http://localhost:5000"
            echo "📊 Health Check: http://localhost:5000/api/health"
            echo ""
            echo "📋 Available API endpoints:"
            echo "  GET  /api/datasets - List all datasets"
            echo "  GET  /api/datasets/<name> - Get dataset samples"
            echo "  POST /api/load-dataset - Load new dataset"
            echo "  GET  /api/training-jobs - Get training jobs"
            echo "  POST /api/start-training - Start training"
            echo "  GET  /api/health - Health check"
            echo ""
            echo "📝 Logs:"
            echo "  Backend: $BACKEND_DIR/api_server.log"
            echo "  Frontend: $FRONTEND_DIR/frontend.log"
            echo ""
            echo "🛑 To stop all services: ./start_services.sh stop"
        else
            print_error "Failed to start frontend"
            stop_services
            return 1
        fi
    else
        print_error "Failed to start backend"
        return 1
    fi
}

# Function to show status
show_status() {
    print_status "Service Status:"
    echo ""
    
    # Check backend
    if check_port 5000; then
        echo -e "Backend API: ${RED}STOPPED${NC}"
    else
        echo -e "Backend API: ${GREEN}RUNNING${NC} (http://localhost:5000)"
    fi
    
    # Check frontend
    if check_port 5173; then
        echo -e "Frontend: ${RED}STOPPED${NC}"
    else
        echo -e "Frontend: ${GREEN}RUNNING${NC} (http://localhost:5173)"
    fi
    
    echo ""
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        "backend"|"api")
            if [ -f "$BACKEND_DIR/api_server.log" ]; then
                tail -f "$BACKEND_DIR/api_server.log"
            else
                print_error "Backend log file not found"
            fi
            ;;
        "frontend"|"web")
            if [ -f "$FRONTEND_DIR/frontend.log" ]; then
                tail -f "$FRONTEND_DIR/frontend.log"
            else
                print_error "Frontend log file not found"
            fi
            ;;
        *)
            print_error "Usage: $0 logs [backend|frontend]"
            ;;
    esac
}

# Main script logic
case "$1" in
    "start")
        start_all
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 2
        start_all
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs $2
        ;;
    *)
        echo "AI Refinement Dashboard - Service Management"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services (backend + frontend)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show service status"
        echo "  logs     - Show logs (backend|frontend)"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 stop"
        echo "  $0 restart"
        echo "  $0 status"
        echo "  $0 logs backend"
        echo "  $0 logs frontend"
        ;;
esac
