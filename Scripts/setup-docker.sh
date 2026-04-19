#!/bin/bash

echo "=================================================="
echo "Risk Analytics - Docker Environment Setup"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Start Docker services
echo -e "\n${YELLOW}Step 1: Starting Docker Compose...${NC}"
cd ../producer-module
docker-compose down
docker-compose up -d
print_status "Docker services started"

# Step 2: Wait for services to be ready
echo -e "\n${YELLOW}Step 2: Waiting for services to initialize...${NC}"
sleep 10
print_status "Services initialized"

# Step 3: Fix Spark permissions (one-time setup)
echo -e "\n${YELLOW}Step 3: Setting up Spark permissions...${NC}"
docker exec -it -u root spark-master bash -c "
    mkdir -p /home/spark/.ivy2/cache
    chown -R spark:spark /home/spark/.ivy2
    chmod -R 755 /home/spark/.ivy2
"
print_status "Spark permissions configured"

# Step 4: Install Python dependencies on Spark containers
echo -e "\n${YELLOW}Step 4: Installing Python dependencies...${NC}"
docker exec -it -u root spark-master pip3 install --quiet numpy pandas psycopg2-binary setuptools wheel
docker exec -it -u root spark-worker pip3 install --quiet numpy pandas psycopg2-binary setuptools wheel
print_status "Python dependencies installed"

# Step 5: Build and install risk_package
echo -e "\n${YELLOW}Step 5: Building risk_package...${NC}"
cd ../simulation-module

# Build package if setup.py exists
if [ -f "setup.py" ]; then
    # Clean old builds
    # rm -rf build dist *.egg-info 2>/dev/null
    
    # python3 setup.py sdist bdist_wheel > /dev/null 2>&1
    # print_status "Package built"
    
    # Find the built package (handles version automatically)
    PACKAGE_FILE=$(ls dist/*.tar.gz | head -n 1)
    
    if [ -z "$PACKAGE_FILE" ]; then
        print_error "Package file not found in dist/"
        exit 1
    fi
    
    print_status "Found package: $PACKAGE_FILE"
    
    # Copy to containers
    docker cp dist/risk_package-0.1.0.tar.gz spark-master:/tmp/
    docker cp dist/risk_package-0.1.0.tar.gz spark-worker:/tmp/
    
    # Install on both containers (using the fixed path)
   docker exec -it -u root spark-master pip3 install /tmp/risk_package-0.1.0.tar.gz
    docker exec -it -u root spark-worker pip3 install /tmp/risk_package-0.1.0.tar.gz    
    print_status "risk_package installed on all nodes"
else
    print_warning "setup.py not found, skipping package installation"
fi

# Step 6: Initialize database schema
echo -e "\n${YELLOW}Step 6: Setting up database...${NC}"
if [ -f "init_db.sql" ]; then
    docker cp init_db.sql timescaledb:/tmp/
    # user name is
    docker exec -it timescaledb psql -U riskengine -d riskmetrics -f /tmp/init_db.sql > /dev/null 2>&1
    print_status "Database schema initialized"
else
    print_warning "init_db.sql not found, skipping database setup"
fi

# Step 7: Copy application files
echo -e "\n${YELLOW}Step 7: Deploying application files...${NC}"
docker cp risk_engine_stream.py spark-master:/opt/spark/work-dir/
print_status "Application files deployed"

# Step 8: Configure Spark logging
echo -e "\n${YELLOW}Step 8: Configuring Spark logging...${NC}"
docker exec -it spark-master bash -c "
cat > /opt/spark/conf/log4j2.properties <<'EOF'
# Set root logger to WARN
rootLogger.level = warn
rootLogger.appenderRef.stdout.ref = console

# Console appender
appender.console.type = Console
appender.console.name = console
appender.console.target = SYSTEM_ERR
appender.console.layout.type = PatternLayout
appender.console.layout.pattern = %d{yy/MM/dd HH:mm:ss} %p %c{1}: %m%n

# Suppress verbose Kafka logs
logger.kafka.name = org.apache.kafka
logger.kafka.level = error

# Suppress verbose Spark logs
logger.spark.name = org.apache.spark
logger.spark.level = warn

# Show only errors from network components
logger.netty.name = io.netty
logger.netty.level = error

# Your application logs (INFO level)
logger.app.name = com.riskengine
logger.app.level = info
EOF
"
print_status "Logging configured"

# Step 9: Verify setup
echo -e "\n${YELLOW}Step 9: Verifying setup...${NC}"

# Check containers
RUNNING=$(docker ps --filter "name=kafka|zookeeper|spark|timescaledb" --format "{{.Names}}" | wc -l)
if [ "$RUNNING" -eq 5 ]; then
    print_status "All 5 containers running"
else
    print_error "Expected 5 containers, found $RUNNING"
fi

# Check Kafka topic
TOPIC=$(docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | grep raw-market-data)
if [ ! -z "$TOPIC" ]; then
    print_status "Kafka topic 'raw-market-data' exists"
else
    print_status "Creating Kafka topic 'raw-market-data'..."
    docker exec -it kafka kafka-topics --create --topic raw-market-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 > /dev/null 2>&1
fi

# Check database
DB_READY=$(docker exec -it timescaledb psql -U riskengine -d riskmetrics -c "\dt" 2>/dev/null | grep risk_metrics)
if [ ! -z "$DB_READY" ]; then
    print_status "Database table 'risk_metrics' exists"
else
    print_warning "Database table not found"
fi

echo -e "\n${GREEN}=================================================="
echo "Setup Complete!"
echo "==================================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Start Java producer: cd producer-module/market-data-producer && ./mvnw spring-boot:run"
echo "  2. Start Spark job: ./scripts/run-spark-job.sh"
echo "  3. View results: docker exec -it timescaledb psql -U riskengine -d riskmetrics -c 'SELECT * FROM risk_metrics ORDER BY timestamp DESC LIMIT 5;'"
echo ""