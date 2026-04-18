import asyncio
import json
import os
from typing import Optional, Dict, Any

class MCPClientHelper:
    """
    A standalone JSON-RPC client for MCP servers that doesn't depend on the mcp library.
    Useful for environments with older Python versions.
    """
    def __init__(self, command: str, args: list[str]):
        self.command = command
        self.args = args
        self.process: Optional[asyncio.subprocess.Process] = None
        self._id_counter = 0

    async def __aenter__(self):
        self.process = await asyncio.create_subprocess_exec(
            self.command, *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        # Initialize MCP (minimal)
        init_resp = await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp-workflow", "version": "1.0.0"}
        })
        await self._send_notification("notifications/initialized", {})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.process:
            self.process.terminate()
            await self.process.wait()

    async def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self._id_counter += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._id_counter,
            "method": method,
            "params": params
        }
        line = json.dumps(request) + "\n"
        self.process.stdin.write(line.encode())
        await self.process.stdin.drain()
        
        # Read response
        resp_line = await self.process.stdout.readline()
        if not resp_line:
            # Check stderr for clues
            err = await self.process.stderr.read()
            raise RuntimeError(f"Server closed connection. Stderr: {err.decode()}")
            
        return json.loads(resp_line.decode())

    async def _send_notification(self, method: str, params: Dict[str, Any]):
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        line = json.dumps(notification) + "\n"
        self.process.stdin.write(line.encode())
        await self.process.stdin.drain()

    async def call_tool(self, name: str, arguments: dict):
        resp = await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        if "error" in resp:
            raise RuntimeError(f"Tool {name} failed: {resp['error']}")
        # The result of a tool call is in resp["result"]
        # Official servers return { "content": [{ "type": "text", "text": "..." }] }
        class MockResult:
            def __init__(self, data):
                self.content = [type('obj', (object,), {'text': c['text']}) for c in data.get('content', [])]
        
        return MockResult(resp["result"])
