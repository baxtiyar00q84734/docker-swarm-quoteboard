#!/usr/bin/env bash
# Quote Board - start everything (Mac / Linux)
# Usage:  bash start.sh
set -e
cd "$(dirname "$0")"

echo "1/4 Checking Docker..."
docker version --format 'Docker {{.Server.Version}}' || { echo "Docker is not running. Start Docker and try again."; exit 1; }

echo "2/4 Enabling Swarm mode (if needed)..."
if [ "$(docker info --format '{{.Swarm.LocalNodeState}}')" != "active" ]; then
  docker swarm init 2>/dev/null || docker swarm init --advertise-addr 127.0.0.1
fi
docker node ls

echo "3/4 Building the web image..."
docker build -t quoteboard-web:1.0 ./web

echo "4/4 Deploying the stack..."
docker stack deploy -c docker-compose.yml quotes
sleep 15
docker stack services quotes

echo
echo "App:        http://localhost:8000"
echo "Visualizer: http://localhost:8080"
