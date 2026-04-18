import asyncio
import os
import json
import requests
import sys
from mcp_client import MCPClientHelper
from dependency_utils import (
    get_latest_maven_version, 
    get_latest_npm_version, 
    scan_maven_dependencies,
    scan_npm_dependencies,
    update_pom_xml, 
    update_package_json
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GITHUB_REPO = "alvesdesouzaalex/mcp-update-dependency-labs"

def parse_instruction(instruction: str) -> dict:
    """Parses user instruction to identify targets and PR requirement."""
    instr = instruction.lower()
    
    # Check for targets
    update_react = any(kw in instr for kw in ["react", "frontend", "tudo", "ambos", "projetos"])
    update_backend = any(kw in instr for kw in ["backend", "spring", "tudo", "ambos", "projetos"])
    
    # Check for PR
    create_pr_requested = any(kw in instr for kw in ["pull request", "pr", "abrir", "cria"])
    
    return {
        "react": update_react,
        "backend": update_backend,
        "pr": create_pr_requested
    }

async def run_workflow(instruction: str = "atualize tudo"):
    params = parse_instruction(instruction)
    print(f"Workflow params: {params} based on: '{instruction}'")
    
    # 1. CLEANUP
    if params["react"]:
        print("Step 1: Cleanup node_modules...")
        node_modules = os.path.join(ROOT_DIR, "mcp-frontend", "node_modules")
        if os.path.exists(node_modules):
            import shutil
            shutil.rmtree(node_modules)
            print("node_modules removed.")
    
    # 2. CONNECT TO MCP SERVERS
    print("Step 2: Connecting to MCP Servers...")
    # Using npx to run official servers
    fs_params = ["-y", "@modelcontextprotocol/server-filesystem", ROOT_DIR]
    git_params = ["-y", "@modelcontextprotocol/server-git", "--repository", ROOT_DIR]

    async with MCPClientHelper("npx", fs_params) as fs_client, \
               MCPClientHelper("npx", git_params) as git_client:
        
        print("Connected to MCP servers.")

        # 3. READ DEPENDENCIES
        print("Step 3: Reading dependencies...")
        
        pom_content = ""
        pom_path = os.path.join(ROOT_DIR, "mcp-backend", "pom.xml")
        if params["backend"]:
            pom_resp = await fs_client.call_tool("read_file", {"path": pom_path})
            pom_content = pom_resp.content[0].text
        
        pkg_content = ""
        pkg_path = os.path.join(ROOT_DIR, "mcp-frontend", "package.json")
        if params["react"]:
            pkg_resp = await fs_client.call_tool("read_file", {"path": pkg_path})
            pkg_content = pkg_resp.content[0].text

        # 4. FIND UPDATES
        print("Step 4: Finding updates dynamically...")
        
        # Backend Updates
        maven_updates = {}
        if params["backend"]:
            found_maven_deps = scan_maven_dependencies(pom_content)
            print(f"Found {len(found_maven_deps)} Maven dependencies with explicit versions.")
            for (g, a), v in found_maven_deps.items():
                latest = get_latest_maven_version(g, a)
                if latest and latest != v:
                    maven_updates[(g, a)] = latest
                    print(f"  [UPDATE] {g}:{a} -> {latest} (current: {v})")
        
        # Frontend Updates
        npm_updates = {}
        if params["react"]:
            found_npm_deps = scan_npm_dependencies(pkg_content)
            print(f"Found {len(found_npm_deps)} NPM dependencies.")
            for pkg, v in found_npm_deps.items():
                latest = get_latest_npm_version(pkg)
                if latest and latest != v:
                    npm_updates[pkg] = latest
                    print(f"  [UPDATE] {pkg} -> {latest} (current: {v})")

        # 5. APPLY UPDATES
        if maven_updates or npm_updates:
            print("Step 5: Applying updates...")
            if maven_updates:
                new_pom = update_pom_xml(pom_content, maven_updates)
                await fs_client.call_tool("write_file", {"path": pom_path, "content": new_pom})
            
            if npm_updates:
                new_pkg = update_package_json(pkg_content, npm_updates)
                await fs_client.call_tool("write_file", {"path": pkg_path, "content": new_pkg})
        else:
            print("No updates needed based on parameters.")

        # 6. GIT WORKFLOW
        print("Step 6: Git Workflow...")
        branch_name = f"update-deps-{os.urandom(2).hex()}"
        
        await git_client.call_tool("git_checkout", {"branch": branch_name, "create_branch": True})
        
        files_to_add = []
        if maven_updates: files_to_add.append("mcp-backend/pom.xml")
        if npm_updates: files_to_add.append("mcp-frontend/package.json")
        
        if files_to_add:
            await git_client.call_tool("git_add", {"files": files_to_add})
            await git_client.call_tool("git_commit", {"message": f"chore: dynamic update of {len(maven_updates) + len(npm_updates)} dependencies"})
            
            try:
                await git_client.call_tool("git_push", {"remote": "origin", "branch": branch_name})
            except Exception as e:
                print(f"Push skipped or failed: {e}")

        # 7. CREATE PULL REQUEST
        if params["pr"]:
            print("Step 7: Creating Pull Request...")
            pr_link = create_pull_request(branch_name)
            print(f"\n🚀 PR Link: {pr_link}")
            return pr_link

def create_pull_request(branch_name: str) -> str:
    manual_link = f"https://github.com/{GITHUB_REPO}/pull/new/{branch_name}"
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return manual_link

    url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "title": "chore: dynamic dependency update",
        "body": "Automated dependency update generated by mcp-workflow using dynamic scanning.",
        "head": branch_name,
        "base": "main"
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 201:
            return resp.json().get('html_url', manual_link)
    except:
        pass
        
    return manual_link

if __name__ == "__main__":
    asyncio.run(run_workflow(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else "atualize tudo"))
