#!/usr/bin/env bash
# DriveForge Web Landing Page - Deployment Script (Linux/macOS)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-preview}"
ARG2="${2:-}"

echo "=================================================="
echo "  DriveForge Web Landing Page Deployment Helper   "
echo "=================================================="

case "$TARGET" in
  preview)
    PORT="${ARG2:-8080}"
    echo "[Preview] Launching Python static server on port $PORT..."
    echo "Visit: http://localhost:$PORT"
    cd "$SCRIPT_DIR" && python3 -m http.server "$PORT"
    ;;
  
  pocketbase)
    PB_DIR="$ARG2"
    if [ -z "$PB_DIR" ]; then
      echo "Error: Please provide PocketBase root directory."
      echo "Usage: ./deploy.sh pocketbase /path/to/pocketbase"
      exit 1
    fi
    PB_PUBLIC="$PB_DIR/pb_public"
    echo "[PocketBase] Syncing assets to $PB_PUBLIC..."
    mkdir -p "$PB_PUBLIC"
    rsync -av --exclude="*.sh" --exclude="*.ps1" --exclude="Dockerfile" --exclude="docker-compose.yml" --exclude="nginx.conf" "$SCRIPT_DIR/" "$PB_PUBLIC/"
    echo "✓ Successfully deployed to PocketBase pb_public!"
    echo "Access via PocketBase: http://your-domain-or-ip:8090/"
    ;;

  docker)
    echo "[Docker] Building and starting container..."
    cd "$SCRIPT_DIR" && docker compose up -d --build
    echo "✓ Web container is up and running on port 8080!"
    ;;

  custom)
    DEST_DIR="$ARG2"
    if [ -z "$DEST_DIR" ]; then
      echo "Error: Please provide destination directory."
      echo "Usage: ./deploy.sh custom /var/www/driveforge"
      exit 1
    fi
    echo "[Custom Deploy] Deploying to $DEST_DIR..."
    mkdir -p "$DEST_DIR"
    rsync -av --exclude="*.sh" --exclude="*.ps1" --exclude="Dockerfile" --exclude="docker-compose.yml" --exclude="nginx.conf" "$SCRIPT_DIR/" "$DEST_DIR/"
    echo "✓ Assets copied to $DEST_DIR successfully!"
    ;;

  *)
    echo "Unknown command: $TARGET"
    echo "Supported targets: preview, pocketbase, docker, custom"
    exit 1
    ;;
esac
