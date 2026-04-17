#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$ROOT_DIR/.pids"

# ─── Cores ───────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

p()  { printf "%b\n" "$*"; }

p "${CYAN}================================================${NC}"
p "${CYAN}   MCP Apps — Stopping...${NC}"
p "${CYAN}================================================${NC}"

kill_by_pid_file() {
  local NAME=$1
  local PID_FILE="$PID_DIR/$2.pid"

  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
      kill "$PID" 2>/dev/null
      sleep 1
      if kill -0 "$PID" 2>/dev/null; then
        kill -9 "$PID" 2>/dev/null
      fi
      p "   ${GREEN}✔ $NAME stopped (PID $PID)${NC}"
    else
      p "   ${YELLOW}⚠  $NAME was not running (stale PID $PID)${NC}"
    fi
    rm -f "$PID_FILE"
  else
    p "   ${YELLOW}⚠  No PID file for $NAME${NC}"
  fi
}

kill_by_port() {
  local NAME=$1
  local PORT=$2
  local PIDS
  PIDS=$(lsof -ti tcp:"$PORT" 2>/dev/null)
  if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill -9 2>/dev/null
    p "   ${GREEN}✔ $NAME killed via port $PORT${NC}"
  fi
}

p ""
p "${YELLOW}[1/2] Stopping mcp-backend...${NC}"
kill_by_pid_file "mcp-backend" "backend"
kill_by_port     "mcp-backend (port fallback)" "8080"

p ""
p "${YELLOW}[2/2] Stopping mcp-frontend...${NC}"
kill_by_pid_file "mcp-frontend" "frontend"
kill_by_port     "mcp-frontend (port fallback)" "5173"

p ""
p "${GREEN}================================================${NC}"
p "${GREEN}   ✅ All apps stopped!${NC}"
p "${GREEN}================================================${NC}"
p "   Run ${YELLOW}./start.sh${NC} to start again."
p "${GREEN}================================================${NC}\n"
