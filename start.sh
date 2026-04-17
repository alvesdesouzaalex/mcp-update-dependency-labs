#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$ROOT_DIR/.pids"
LOG_DIR="$ROOT_DIR/.logs"

mkdir -p "$PID_DIR" "$LOG_DIR"

# ─── Cores ───────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

p()  { printf "%b\n" "$*"; }
pn() { printf "%b"   "$*"; }

p "${CYAN}================================================${NC}"
p "${CYAN}   MCP Apps — Starting...${NC}"
p "${CYAN}================================================${NC}"

# ─── Backend ─────────────────────────────────────────────
p "\n${YELLOW}[1/2] Starting mcp-backend (Spring Boot)...${NC}"
p "      Building + starting (this may take ~30s on first run)..."

cd "$ROOT_DIR/mcp-backend"
mvn -q clean spring-boot:run > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PID_DIR/backend.pid"

p "      PID : $BACKEND_PID"
p "      Log : $LOG_DIR/backend.log"
pn "      Health: "

BACKEND_UP=false
for i in $(seq 1 60); do
  sleep 2

  # Se o processo Maven morreu, logo o backend crashou
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    printf "\n"
    p "\n${RED}✖ Backend crashed on startup!${NC}"
    p "  Last lines of $LOG_DIR/backend.log:"
    p "  ${RED}─────────────────────────────────────────${NC}"
    tail -20 "$LOG_DIR/backend.log" | while IFS= read -r line; do
      printf "  %s\n" "$line"
    done
    p "  ${RED}─────────────────────────────────────────${NC}"
    p "\n${RED}Aborting — fix the backend before starting.${NC}"
    rm -f "$PID_DIR/backend.pid"
    exit 1
  fi

  if curl -s "http://localhost:8080/hello?name=ping" > /dev/null 2>&1; then
    printf " ${GREEN}✔ UP (${i}x2s)${NC}\n"
    BACKEND_UP=true
    break
  fi
  pn "."
done

if [ "$BACKEND_UP" = false ]; then
  printf "\n"
  p "${RED}✖ Backend did not respond in 120s. Check: $LOG_DIR/backend.log${NC}"
  exit 1
fi

# ─── Frontend ────────────────────────────────────────────
p "\n${YELLOW}[2/2] Starting mcp-frontend (Vite/React)...${NC}"

cd "$ROOT_DIR/mcp-frontend"
npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$PID_DIR/frontend.pid"

p "      PID : $FRONTEND_PID"
p "      Log : $LOG_DIR/frontend.log"
pn "      Health: "

FRONTEND_UP=false
for i in $(seq 1 15); do
  sleep 1
  if curl -s "http://localhost:5173" > /dev/null 2>&1; then
    printf " ${GREEN}✔ UP (${i}s)${NC}\n"
    FRONTEND_UP=true
    break
  fi
  pn "."
done

if [ "$FRONTEND_UP" = false ]; then
  printf "\n"
  p "${RED}✖ Frontend did not respond in 15s. Check: $LOG_DIR/frontend.log${NC}"
  exit 1
fi

p "\n${GREEN}================================================${NC}"
p "${GREEN}   ✅ Both apps are running!${NC}"
p "${GREEN}================================================${NC}"
p "   Backend  → http://localhost:8080"
p "   Frontend → http://localhost:5173"
p ""
p "   Run ${YELLOW}./stop.sh${NC} to stop everything."
p "${GREEN}================================================${NC}\n"
