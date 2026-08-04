#!/bin/bash

# Navigate to project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CD_DIR="$PROJECT_DIR/pc-app"

echo "=================================================="
echo "   🚀 Menjalankan Aplikasi Absensi RFID ESP32-S3  "
echo "=================================================="

# Check virtual environment
if [ -d "$CD_DIR/.venv" ]; then
    source "$CD_DIR/.venv/bin/activate"
else
    echo "❌ Virtual environment .venv tidak ditemukan di $CD_DIR!"
    exit 1
fi

# Open browser automatically after 1.5s in background
(sleep 1.5 && xdg-open "http://localhost:8000" 2>/dev/null) &

# Run Uvicorn server
cd "$CD_DIR"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
