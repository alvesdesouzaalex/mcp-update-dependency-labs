#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$ROOT_DIR/.pids"
LOG_DIR="$ROOT_DIR/.logs"

mkdir -p "$PID_DIR" "$LOG_DIR"

# ─── Cores ───────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   MCP Apps — Starting...${NC}"
echo -e "${CYAN}================================================${NC}"

# ─── Backend ─────────────────────────────────────────────
echo -e "\n${YELLOW}[1/2] Starting mcp-backend (Spring Boot)...${NC}"

cd "$ROOT_DIR/mcp-backend"
mvn spring-boot:run > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PID_DIR/backend.pid"

echo -e "      PID: $BACKEND_PID"
echo -e "      Log: $LOG_DIR/backend.log"

# ─── Aguarda backend subir ────────────────────────────────
echo -ne "      Waiting for backend (port 8080)"
for i in $(seq 1 30); do
  sleep 2
  if curl -s "http://localhost:8080/hello?name=ping" > /dev/null 2>&1; then
    echo -e " ${GREEN}✔ UP${NC}"
    break
  fi
  echo -n "."
done

# ─── Frontend ────────────────────────────────────────────
echo -e "\n${YELLOW}[2/2] Starting mcp-frontend (Vite/React)...${NC}"

cd "$ROOT_DIR/mcp-frontend"
npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$PID_DIR/frontend.pid"

echo -e "      PID: $FRONTEND_PID"
echo -e "      Log: $LOG_DIR/frontend.log"

# ─── Aguarda frontend subir ───────────────────────────────
echo -ne "      Waiting for frontend (port 5173)"
for i in $(seq 1 15); do
  sleep 1
  if curl -s "http://localhost:5173" > /dev/null 2>&1; then
    echo -e " ${GREEN}✔ UP${NC}"
    break
  fi
  echo -n "."
done

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}   ✅ Both apps are running!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "   Backend  → http://localhost:8080"
echo -e "   Frontend → http://localhost:5173"
echo -e ""
echo -e "   Run ${YELLOW}./stop.sh${NC} to stop everything."
echo -e "${GREEN}================================================${NC}\n"
