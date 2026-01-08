#!/usr/bin/env bash
# Local development startup script
# Starts both backend and frontend services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting Azure Service Catalog development environment..."

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Install dependencies if needed
echo "📦 Installing backend dependencies..."
cd "$PROJECT_ROOT/backend"
uv sync --all-extras

echo "📦 Installing frontend dependencies..."
cd "$PROJECT_ROOT/frontend"
uv sync --all-extras

# Start backend
echo "🔧 Starting backend on http://localhost:8000..."
cd "$PROJECT_ROOT/backend"
uv run uvicorn src.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start frontend
echo "🎨 Starting frontend on http://localhost:8501..."
cd "$PROJECT_ROOT/frontend"
uv run streamlit run src/app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "✅ Development environment is running!"
echo ""
echo "   Frontend:  http://localhost:8501"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services."
echo ""

# Wait for processes
wait
