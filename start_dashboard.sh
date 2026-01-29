#!/bin/bash
# Quick start script for the GestureRating Dashboard

echo "======================================"
echo "GestureRating Dashboard Quick Start"
echo "======================================"
echo ""

# Check if React build exists
if [ ! -d "dashboard-frontend/dist" ]; then
    echo "ERROR: React build not found!"
    echo "Building frontend..."
    cd dashboard-frontend
    npm install
    npm run build
    cd ..
    echo "Build complete!"
    echo ""
fi

echo "Starting servers..."
echo ""
echo "Terminal 1: Main API + WebSocket (port 5000)"
echo "Terminal 2: Dashboard Server (port 5001)"
echo ""
echo "Starting main.py in background..."
python main.py &
MAIN_PID=$!

sleep 3

echo "Starting dashboard_app.py..."
python dashboard_app.py &
DASH_PID=$!

sleep 2

echo ""
echo "======================================"
echo "Dashboard is ready!"
echo "======================================"
echo "Main API: http://localhost:5000"
echo "Dashboard: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
trap "echo 'Stopping servers...'; kill $MAIN_PID $DASH_PID 2>/dev/null; exit" INT
wait
