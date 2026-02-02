#!/bin/bash
# Nordpuls - Start both backend and frontend

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=============================="
echo "  NORDPULS - Aktieanalys"
echo "=============================="
echo ""

# Check if venv exists
if [ ! -d "$SCRIPT_DIR/backend/.venv" ]; then
    echo "Skapar Python virtual environment..."
    uv venv "$SCRIPT_DIR/backend/.venv" 2>/dev/null || python3 -m venv "$SCRIPT_DIR/backend/.venv"
    echo "Installerar Python-beroenden..."
    uv pip install -r "$SCRIPT_DIR/backend/requirements.txt" -p "$SCRIPT_DIR/backend/.venv" 2>/dev/null || \
        "$SCRIPT_DIR/backend/.venv/bin/pip" install -r "$SCRIPT_DIR/backend/requirements.txt"
fi

# Check if node_modules exists
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo "Installerar Node.js-beroenden..."
    cd "$SCRIPT_DIR/frontend" && npm install
fi

echo ""
echo "Startar backend (port 8000)..."
cd "$SCRIPT_DIR/backend"
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Startar frontend (port 3000)..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Tryck Ctrl+C för att stoppa."

cleanup() {
    echo ""
    echo "Stoppar Nordpuls..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo "Klart."
}

trap cleanup INT TERM
wait
