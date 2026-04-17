import subprocess
import json
import os


def run(cmd, cwd=None):
    print(f"\n>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.stdout


# =========================
# REACT PROJECT
# =========================

def update_react_project(path):
    print("\n===== REACT PROJECT =====")

    output = run("npm outdated --json", cwd=path)

    if not output.strip():
        print("React deps already updated")
        return

    deps = json.loads(output)

    print("\nOutdated React dependencies:")
    deps_to_update = []

    for dep, info in deps.items():
        current = info.get("current", info.get("wanted", "unknown"))
        latest = info.get("latest", "unknown")

        if current != latest:
            print(f"{dep}: {current} → {latest}")
            deps_to_update.append(dep)

    if not deps_to_update:
        print("Nothing to update")
        return

    print("\nUpdating dependencies to latest...")

    # monta comando
    install_cmd = "npm install " + " ".join([f"{dep}@latest" for dep in deps_to_update])

    run(install_cmd, cwd=path)

    print("\nFinal install...")
    run("npm install", cwd=path)


# =========================
# MAVEN PROJECT
# =========================

def update_maven_project(path):
    print("\n===== MAVEN PROJECT =====")

    # usa plugin versions
    run("mvn versions:display-dependency-updates", cwd=path)

    # atualizar automaticamente
    run("mvn versions:use-latest-releases", cwd=path)


# =========================
# GIT
# =========================

def create_pr_flow(repo_path, branch_name):
    print("\n===== GIT FLOW =====")

    run(f"git checkout -b {branch_name}", cwd=repo_path)
    run("git add .", cwd=repo_path)
    run('git commit -m "chore: update dependencies via automation"', cwd=repo_path)
    run(f"git push origin {branch_name}", cwd=repo_path)

    print("\nBranch criada. Para abrir PR:")
    print("gh pr create --fill")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    BASE_PATH = os.getcwd()
    BASE_PATH = BASE_PATH.replace("mcp-workflow", "")

    react_path = os.path.join(BASE_PATH, "mcp-frontend")  # ajuste nome
    maven_path = os.path.join(BASE_PATH, "mcp-backend")  # ajuste nome

    update_react_project(react_path)
    update_maven_project(maven_path)

    create_pr_flow(BASE_PATH, "chore/update-deps")
