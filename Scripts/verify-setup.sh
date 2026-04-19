#!/bin/bash

echo "Risk Analytics - Health Check"
echo "=============================="

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "✗ Docker is not running"
    exit 1
fi
echo "✓ Docker running"

# Check containers
CONTAINERS=(kafka zookeeper spark-master spark-worker timescaledb)
for container in "${CONTAINERS[@]}"; do
    if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        echo "✓ $container running"
    else
        echo "✗ $container NOT running"
    fi
done

# Check Spark Web UI
if curl -s http://localhost:8080 > /dev/null; then
    echo "✓ Spark Master UI accessible (http://localhost:8080)"
else
    echo "✗ Spark Master UI not accessible"
fi

# Check Kafka connectivity
if docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo "✓ Kafka broker responding"
else
    echo "✗ Kafka broker not responding"
fi

# Check database
if docker exec timescaledb psql -U riskengine -d riskmetrics -c "\dt" > /dev/null 2>&1; then
    echo "✓ Database accessible"
else
    echo "✗ Database not accessible"
fi

echo ""
echo "Health check complete!"