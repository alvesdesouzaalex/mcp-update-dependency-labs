# MCP Update Dependency Labs

# Structure
mcp-update-dependency-labs/
├── mcp-backend/                    ← Kotlin + Spring Boot 3 + Maven
│   ├── pom.xml
│   └── src/main/kotlin/com/example/mcpbackend/
│       ├── McpBackendApplication.kt
│       └── HelloController.kt     ← GET /hello?name=... + CORS habilitado
│
└── mcp-frontend/                   ← React + Vite
|    └── src/
|        ├── App.jsx                 ← Formulário + fetch + exibe resposta
|        └── App.css                 ← Design escuro glassmorphism
│ 
└── mcp-workflow/                   ← python MCPs server
    ├── main.py


# How to run

```bash
./start.sh
```

# How to stop

```bash
./stop.sh
```
