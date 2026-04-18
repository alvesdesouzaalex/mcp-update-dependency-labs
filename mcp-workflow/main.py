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
    
    # Check if we can run
    try:
        asyncio.run(run_workflow())
        print("\nWorkflow completed successfully!")
    except Exception as e:
        print(f"\nWorkflow failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
