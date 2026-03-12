# redscraping_core/ai/key_manager.py

import os
from rich.console import Console

console = Console()
ENV_FILE = os.path.join(os.getcwd(), ".env")

def save_key(api_key):
    """Saves the Gemini API key to a local .env file."""
    with open(ENV_FILE, "w") as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
    console.print("[bold green]✅ Gemini API Key saved successfully![/bold green]")

def get_key():
    """Reads the Gemini API key from the .env file."""
    if not os.path.exists(ENV_FILE):
        return None
        
    with open(ENV_FILE, "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                return line.strip().split("=")[1]
    return None

def delete_key():
    """Deletes the .env file to reset the key."""
    if os.path.exists(ENV_FILE):
        os.remove(ENV_FILE)
        console.print("[bold green]🗑️ Gemini API Key has been reset/deleted.[/bold green]")
    else:
        console.print("[yellow]⚠️ No API key found to delete.[/yellow]")