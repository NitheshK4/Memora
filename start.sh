#!/bin/bash

# =============================================
# Memora - Native Startup Script
# =============================================
# Starts FastAPI backend + Streamlit frontend

BACKEND_PORT=8002
FRONTEND_PORT=8503

echo "===================================================="
echo "          🧠 Starting Memora Graph System           "
echo "===================================================="

# Seed the database if it doesn't exist yet
echo "📦 Checking database..."
python3 scripts/seed_db.py

echo ""
echo "🚀 Starting FastAPI Backend on port $BACKEND_PORT..."
python3 -m uvicorn app.api:app --host 127.0.0.1 --port $BACKEND_PORT --reload &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 3

echo "🎨 Starting Streamlit Frontend on port $FRONTEND_PORT..."
BACKEND_URL="http://localhost:$BACKEND_PORT" python3 -m streamlit run frontend/app.py --server.port $FRONTEND_PORT --server.headless true &
FRONTEND_PID=$!

echo ""
echo "===================================================="
echo "  ✅ Memora is running!"
echo "  📊 Dashboard:  http://localhost:$FRONTEND_PORT"
echo "  📖 API Docs:   http://localhost:$BACKEND_PORT/docs"
echo "  🔑 Login with: seed_user / password123"
echo "===================================================="
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""

# Wait and clean up on exit
trap "echo ''; echo 'Stopping Memora...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
