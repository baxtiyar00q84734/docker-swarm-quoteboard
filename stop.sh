#!/usr/bin/env bash
# Quote Board - remove everything from this computer (Mac / Linux)
# Usage:  bash stop.sh
docker stack rm quotes
sleep 10
docker volume rm quotes_redis-data 2>/dev/null
docker image rm quoteboard-web:1.0 2>/dev/null
docker swarm leave --force
echo "Cleaned up. The computer is back to how it was."
