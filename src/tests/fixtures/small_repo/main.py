"""Sample main module for test fixture."""
import os

def hello(name: str) -> str:
    return f"Hello, {name}!"

def get_config():
    return {
        "database_url": os.environ.get("DATABASE_URL", "sqlite:///test.db"),
        "debug": os.environ.get("DEBUG", "false").lower() == "true",
    }

if __name__ == "__main__":
    print(hello("World"))
