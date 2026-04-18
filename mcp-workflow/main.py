import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current directory to path to ensure local imports work
sys.path.append(os.path.dirname(__file__))

from workflow import run_workflow

def main():
    # Load environment variables (GITHUB_TOKEN, etc.)
    load_dotenv()
    
    print("=== MCP Dependency Workflow CLI ===")
    print("Type 'sair', 'exit' or 'quit' to stop.")
    
    while True:
        try:
            # Prompt the user
            print("\n" + "="*40)
            instruction = input("O que você deseja fazer? > ")
            
            if not instruction.strip():
                continue
                
            if instruction.lower() in ["sair", "exit", "quit"]:
                print("Encerrando workflow. Até logo!")
                break
            
            # Execute workflow
            pr_link = asyncio.run(run_workflow(instruction))
            
            if pr_link:
                print(f"\n✅ Concluído! Para abrir o Pull Request, clique aqui:\n{pr_link}")
            else:
                print("\n✅ Fluxo concluído!")
                
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except Exception as e:
            print(f"\n❌ Erro no workflow: {e}")

if __name__ == "__main__":
    main()
