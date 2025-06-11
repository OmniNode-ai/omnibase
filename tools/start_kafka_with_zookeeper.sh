#!/bin/bash
# Start Zookeeper and Kafka in Docker with correct networking for ONEX/OmniBase development
# Idempotent: safe to run multiple times

set -e

# Step 1: Stop and remove existing containers if they exist
echo "[INFO] Stopping and removing existing kafka and zookeeper containers (if any)..."
docker rm -f kafka 2>/dev/null || true
docker rm -f zookeeper 2>/dev/null || true

# Step 2: Create Docker network if it doesn't exist
echo "[INFO] Ensuring docker network 'kafka-net' exists..."
docker network inspect kafka-net >/dev/null 2>&1 || docker network create kafka-net

# Step 3: Start Zookeeper on kafka-net
echo "[INFO] Starting Zookeeper on kafka-net..."
docker run -d --name zookeeper --network kafka-net -p 2181:2181 zookeeper:3.8

# Step 4: Start Kafka on kafka-net, referencing Zookeeper by container name
# Set internal topic replication factors to 1 for single-broker dev (prevents log clutter)
# Advertise localhost for host-based clients (ONEX daemon expects localhost:9092)
HOST_IP=192.168.86.101

echo "[INFO] Starting Kafka on kafka-net..."
docker run -d --name kafka --network kafka-net -p 9092:9092 \
  --env KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
  --env KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  --env KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092 \
  --env KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  --env KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1 \
  --env KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1 \
  confluentinc/cp-kafka:7.4.0

# Wait for Kafka to be ready
echo "[INFO] Waiting for Kafka to be ready..."
until docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list >/dev/null 2>&1; do
  sleep 2
done
echo "[INFO] Kafka is ready."

# Ensure the 'onex-default' topic exists
if ! docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list | grep -q '^onex-default$'; then
  echo "[INFO] Creating topic 'onex-default'..."
  docker exec kafka kafka-topics --bootstrap-server localhost:9092 --create --topic onex-default --partitions 1 --replication-factor 1
else
  echo "[INFO] Topic 'onex-default' already exists."
fi

nohup poetry run python src/omnibase/nodes/node_kafka_event_bus/v1_0_0/daemon.py > kafka_node.log 2>&1 &

# Step 5: Print status
echo "[INFO] Docker containers running:"
docker ps --filter name=kafka --filter name=zookeeper

echo "[INFO] Kafka and Zookeeper should now be running and networked." 