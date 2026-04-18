import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current directory to path to ensure local imports work
sys.path.append(os.path.dirname(__file__))

from workflow import run_workflow

def main():
    print("=== MCP Dependency Workflow CLI ===")
    
    # Load environment variables (GITHUB_TOKEN, etc.)
    load_dotenv()
    
    # Get instruction from args
    instruction = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "atualize tudo"
    
    # Check if we can run
    try:
        pr_link = asyncio.run(run_workflow(instruction))
        if pr_link:
            print(f"\n✅ Concluído! Para abrir o Pull Request, clique aqui:\n{pr_link}")
        else:
            print("\n✅ Fluxo concluído!")
    except Exception as e:
        print(f"\n❌ Erro no workflow: {e}")
        # sys.exit(1) # Removed for flexibility in internal tool run

if __name__ == "__main__":
    main()
