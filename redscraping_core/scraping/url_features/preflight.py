import os
from rich.console import Console
from ...utils.chrome_setup import setup_master_profile

console = Console()

def run_preflight():
    """Ensures input, output, cache folders, and Chrome profile exist."""
    base_dir = os.getcwd()
    input_dir = os.path.join(base_dir, "input")
    output_dir = os.path.join(base_dir, "output")
    cache_dir = os.path.join(base_dir, ".cache") # Centralized Cache

    # 1. Create Folders
    for directory in [input_dir, output_dir, cache_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            # Don't print creation of hidden cache folder to keep UI clean
            if not directory.endswith('.cache'):
                console.print(f"[dim]📁 Created '{os.path.basename(directory)}/' folder.[/dim]")

    # 2. Check Chrome Profile
    profile_dir = os.path.join(base_dir, "Chrome-Profile")
    if not os.path.exists(profile_dir):
        console.print("[yellow]⚠️ Chrome Profile not found. Setting it up now...[/yellow]")
        setup_master_profile()
        
    return input_dir, output_dir, cache_dir