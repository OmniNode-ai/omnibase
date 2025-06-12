#!/bin/bash

# ONEX Development Services Setup Script
# Provides one-command environment setup for ONEX development

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.dev.yml"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICES_TO_START="zookeeper kafka postgres redis"
OPTIONAL_SERVICES="kafka-ui pgadmin"
HEALTH_CHECK_TIMEOUT=120
HEALTH_CHECK_INTERVAL=5

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    log_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    log_info "Checking Docker Compose installation..."
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    log_success "Docker Compose is available"
}

# Check if compose file exists
check_compose_file() {
    log_info "Checking Docker Compose file..."
    
    if [ ! -f "$PROJECT_ROOT/$COMPOSE_FILE" ]; then
        log_error "Docker Compose file not found: $PROJECT_ROOT/$COMPOSE_FILE"
        exit 1
    fi
    
    log_success "Docker Compose file found"
}

# Check for port conflicts
check_port_conflicts() {
    log_info "Checking for port conflicts..."
    
    local ports=(2181 5432 6379 8080 8081 9092 9101)
    local conflicts=()
    
    for port in "${ports[@]}"; do
        if lsof -i :$port &> /dev/null; then
            conflicts+=($port)
        fi
    done
    
    if [ ${#conflicts[@]} -gt 0 ]; then
        log_warning "Port conflicts detected on: ${conflicts[*]}"
        log_warning "These services may fail to start. Consider stopping conflicting services."
        
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Setup cancelled by user"
            exit 0
        fi
    else
        log_success "No port conflicts detected"
    fi
}

# Pull Docker images
pull_images() {
    log_info "Pulling Docker images..."
    
    cd "$PROJECT_ROOT"
    if docker-compose -f "$COMPOSE_FILE" pull; then
        log_success "Docker images pulled successfully"
    else
        log_error "Failed to pull Docker images"
        exit 1
    fi
}

# Start services with dependency ordering
start_services() {
    log_info "Starting ONEX development services..."
    
    cd "$PROJECT_ROOT"
    
    # Start core services first
    for service in $SERVICES_TO_START; do
        log_info "Starting $service..."
        
        if docker-compose -f "$COMPOSE_FILE" up -d "$service"; then
            log_success "$service started"
        else
            log_error "Failed to start $service"
            exit 1
        fi
        
        # Wait a bit between services for dependency resolution
        sleep 2
    done
}

# Wait for services to be healthy
wait_for_health() {
    log_info "Waiting for services to be healthy..."
    
    local start_time=$(date +%s)
    local services_healthy=false
    
    while [ $(($(date +%s) - start_time)) -lt $HEALTH_CHECK_TIMEOUT ]; do
        local all_healthy=true
        
        # Check Zookeeper
        if ! docker exec onex-zookeeper bash -c "echo 'ruok' | nc localhost 2181" &> /dev/null; then
            all_healthy=false
        fi
        
        # Check Kafka
        if ! docker exec onex-kafka kafka-broker-api-versions --bootstrap-server localhost:9092 &> /dev/null; then
            all_healthy=false
        fi
        
        # Check PostgreSQL
        if ! docker exec onex-postgres pg_isready -U onex_user -d onex_dev &> /dev/null; then
            all_healthy=false
        fi
        
        # Check Redis
        if ! docker exec onex-redis redis-cli --raw incr ping &> /dev/null; then
            all_healthy=false
        fi
        
        if [ "$all_healthy" = true ]; then
            services_healthy=true
            break
        fi
        
        echo -n "."
        sleep $HEALTH_CHECK_INTERVAL
    done
    
    echo  # New line after dots
    
    if [ "$services_healthy" = true ]; then
        log_success "All core services are healthy"
    else
        log_warning "Some services may not be fully ready yet"
        log_info "You can check service status with: poetry run onex services status"
    fi
}

# Start optional services
start_optional_services() {
    log_info "Starting optional services..."
    
    cd "$PROJECT_ROOT"
    
    for service in $OPTIONAL_SERVICES; do
        log_info "Starting $service..."
        
        if docker-compose -f "$COMPOSE_FILE" up -d "$service"; then
            log_success "$service started"
        else
            log_warning "Failed to start $service (optional)"
        fi
    done
}

# Display service information
display_service_info() {
    log_success "ONEX Development Environment Setup Complete!"
    echo
    echo "Services started:"
    echo "  • Zookeeper:    localhost:2181"
    echo "  • Kafka:        localhost:9092"
    echo "  • PostgreSQL:   localhost:5432 (user: onex_user, db: onex_dev)"
    echo "  • Redis:        localhost:6379"
    echo
    echo "Optional services:"
    echo "  • Kafka UI:     http://localhost:8080"
    echo "  • pgAdmin:      http://localhost:8081 (admin@onex.dev / onex_admin_password)"
    echo
    echo "Environment variables for testing:"
    echo "  export ONEX_KAFKA_BOOTSTRAP_SERVERS=localhost:9092"
    echo "  export ONEX_DB_HOST=localhost"
    echo "  export ONEX_DB_PORT=5432"
    echo "  export ONEX_DB_USERNAME=onex_user"
    echo "  export ONEX_DB_PASSWORD=onex_password"
    echo "  export ONEX_DB_DATABASE=onex_dev"
    echo
    echo "Useful commands:"
    echo "  poetry run onex services status    # Check service status"
    echo "  poetry run onex services health    # Detailed health dashboard"
    echo "  poetry run onex services stop      # Stop all services"
    echo "  poetry run onex run node_kafka_event_bus --args='[\"--run-scenario\", \"scenario_kafka_real_basic\"]'"
    echo
}

# Cleanup function for script interruption
cleanup() {
    log_warning "Setup interrupted. Cleaning up..."
    cd "$PROJECT_ROOT"
    docker-compose -f "$COMPOSE_FILE" down &> /dev/null || true
    exit 1
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main setup function
main() {
    echo "🚀 ONEX Development Services Setup"
    echo "=================================="
    echo
    
    # Pre-flight checks
    check_docker
    check_docker_compose
    check_compose_file
    check_port_conflicts
    
    # Setup process
    pull_images
    start_services
    wait_for_health
    start_optional_services
    
    # Display results
    display_service_info
    
    log_success "Setup completed successfully! 🎉"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "ONEX Development Services Setup Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --stop         Stop all services"
        echo "  --status       Show service status"
        echo "  --clean        Stop and remove all containers and volumes"
        echo
        echo "This script sets up the complete ONEX development environment including:"
        echo "  • Kafka (with Zookeeper)"
        echo "  • PostgreSQL"
        echo "  • Redis"
        echo "  • Kafka UI (optional)"
        echo "  • pgAdmin (optional)"
        exit 0
        ;;
    --stop)
        log_info "Stopping ONEX development services..."
        cd "$PROJECT_ROOT"
        docker-compose -f "$COMPOSE_FILE" down
        log_success "Services stopped"
        exit 0
        ;;
    --status)
        log_info "Checking service status..."
        cd "$PROJECT_ROOT"
        docker-compose -f "$COMPOSE_FILE" ps
        exit 0
        ;;
    --clean)
        log_warning "This will stop and remove all containers and volumes!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cleaning up ONEX development environment..."
            cd "$PROJECT_ROOT"
            docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
            log_success "Environment cleaned"
        else
            log_info "Cleanup cancelled"
        fi
        exit 0
        ;;
    "")
        # No arguments, run main setup
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 