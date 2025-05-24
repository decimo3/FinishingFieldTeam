from src.solvelib import provider
from src import webhandler

if __name__ == "__main__":
    print("=" * 50)
    print("🏁 Running Finishing Field Team...")
    print("=" * 50)
    
    print("\n➡️ Running Provider Module...")
    provider.main()

    print("\n➡️ Running WebHandler Module...")
    webhandler.main()

    print("\n✅ All modules executed successfully.")
