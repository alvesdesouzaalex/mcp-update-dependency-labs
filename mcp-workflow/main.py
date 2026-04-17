from mcp.server.fastmcp import FastMCP
import subprocess
import json
import os
import shutil

mcp = FastMCP("dependency-automation")


# =========================
# HELPER
# =========================
def run(cmd, cwd=None):
    print(f"\n>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.stdout


# =========================
# REACT TOOL
# =========================
@mcp.tool()
def update_react_project(path: str) -> str:
    """
    Update React dependencies to latest version
    """

    print("\n===== REACT PROJECT =====")

    node_modules_path = os.path.join(path, "node_modules")
    package_lock_path = os.path.join(path, "package-lock.json")

    print("\nCleaning project...")

    if os.path.exists(node_modules_path):
        shutil.rmtree(node_modules_path)

    if os.path.exists(package_lock_path):
        os.remove(package_lock_path)

    run("npm install", cwd=path)

    output = run("npm outdated --json", cwd=path)

    if not output.strip():
        return "React deps already updated"

    deps = json.loads(output)

    deps_to_update = []

    for dep, info in deps.items():
        current = info.get("current", info.get("wanted", "unknown"))
        latest = info.get("latest", "unknown")

        if current != latest:
            deps_to_update.append(dep)

    if not deps_to_update:
        return "Nothing to update"

    install_cmd = "npm install " + " ".join([f"{dep}@latest" for dep in deps_to_update])
    run(install_cmd, cwd=path)

    run("npm install", cwd=path)
    run("npm audit fix", cwd=path)

    return f"Updated React deps: {deps_to_update}"


# =========================
# MAVEN TOOL
# =========================
@mcp.tool()
def update_maven_project(path: str) -> str:
    """
    Update Maven dependencies to latest versions
    """

    print("\n===== MAVEN PROJECT =====")

    run("mvn versions:display-dependency-updates", cwd=path)
    run("mvn versions:use-latest-releases", cwd=path)

    return "Maven dependencies updated"


# =========================
# GIT TOOL
# =========================
@mcp.tool()
def create_pr(repo_path: str, branch_name: str) -> str:
    """
    Create branch, commit changes and push
    """

    print("\n===== GIT FLOW =====")

    run(f"git checkout -b {branch_name}", cwd=repo_path)
    run("git add .", cwd=repo_path)
    run('git commit -m "chore: update dependencies via MCP"', cwd=repo_path)
    run(f"git push origin {branch_name}", cwd=repo_path)

    return f"Branch {branch_name} pushed. Run: gh pr create --fill"


# =========================
# SERVER
# =========================
if __name__ == "__main__":
    mcp.run(transport="stdio")