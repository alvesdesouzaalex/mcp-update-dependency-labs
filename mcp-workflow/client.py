import subprocess
import json

# sobe o MCP server
process = subprocess.Popen(
    ["python", "main.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

def send(msg):
    process.stdin.write(json.dumps(msg) + "\n")
    process.stdin.flush()
    return process.stdout.readline()


# =========================
# INIT MCP
# =========================
print("Initializing MCP session...")

send({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "demo-client", "version": "1.0"}
    }
})

process.stdin.write(json.dumps({
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}) + "\n")
process.stdin.flush()


# =========================
# SIMULAÇÃO DE LLM
# =========================
def interpret(prompt):
    prompt = prompt.lower()

    actions = []

    if "react" in prompt or "frontend" in prompt:
        actions.append(("update_react_project", {"path": "../mcp-frontend"}))

    if "kotlin" in prompt or "maven" in prompt or "backend" in prompt:
        actions.append(("update_maven_project", {"path": "../mcp-backend"}))

    if "pr" in prompt or "pull request" in prompt:
        actions.append(("create_pr", {
            "repo_path": "..",
            "branch_name": "chore/mcp-update-deps"
        }))

    return actions


# =========================
# EXECUÇÃO
# =========================

user_prompt = "Atualize todas dependências críticas e abra um PR"

print(f"\nUser prompt: {user_prompt}")

actions = interpret(user_prompt)

for i, (tool, args) in enumerate(actions, start=2):
    print(f"\nCalling tool: {tool}")

    response = send({
        "jsonrpc": "2.0",
        "id": i,
        "method": "tools/call",
        "params": {
            "name": tool,
            "arguments": args
        }
    })

    print("Response:", response)