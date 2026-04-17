#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$ROOT_DIR/.pids"

# ─── Cores ───────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   MCP Apps — Stopping...${NC}"
echo -e "${CYAN}================================================${NC}"

kill_by_pid_file() {
  local NAME=$1
  local PID_FILE="$PID_DIR/$2.pid"

  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
      kill "$PID" 2>/dev/null
      sleep 1
      # Force kill if still alive
      if kill -0 "$PID" 2>/dev/null; then
        kill -9 "$PID" 2>/dev/null
      fi
      echo -e "   ${GREEN}✔ $NAME stopped (PID $PID)${NC}"
    else
      echo -e "   ${YELLOW}⚠  $NAME was not running (stale PID $PID)${NC}"
    fi
    rm -f "$PID_FILE"
  else
    echo -e "   ${YELLOW}⚠  No PID file for $NAME${NC}"
  fi
}

kill_by_port() {
  local NAME=$1
  local PORT=$2
  local PIDS
  PIDS=$(lsof -ti tcp:"$PORT" 2>/dev/null)
  if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill -9 2>/dev/null
    echo -e "   ${GREEN}✔ $NAME killed on port $PORT${NC}"
  fi
}

echo ""
echo -e "${YELLOW}[1/2] Stopping mcp-backend...${NC}"
kill_by_pid_file "mcp-backend" "backend"
kill_by_port "mcp-backend (fallback)" "8080"

echo ""
echo -e "${YELLOW}[2/2] Stopping mcp-frontend...${NC}"
kill_by_pid_file "mcp-frontend" "frontend"
kill_by_port "mcp-frontend (fallback)" "5173"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   ✅ All apps stopped!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "   Run ${YELLOW}./start.sh${NC} to start again."
echo -e "${GREEN}================================================${NC}\n"
