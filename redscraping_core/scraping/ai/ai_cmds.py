import click
import os
from rich.console import Console
from .ai_generator import generate_script
from .key_manager import save_key, delete_key, get_key

console = Console()

@click.command()
@click.argument('prompt')
@click.option('--name', default='custom_scraper.py', help="Name of the generated file")
def ai(prompt, name):
    """🤖 Generates a custom Selenium script using AI."""
    output_path = os.path.join(os.getcwd(), name)
    if os.path.exists(output_path):
        console.print(f"[yellow]⚠️ File '{name}' already exists. Overwriting...[/yellow]")
        
    success = generate_script(prompt, output_path)
    if success:
        console.print(f"[bold green]🎉 Success! Your custom script has been saved to: {name}[/bold green]")
        console.print(f"[cyan]👉 Run it using: python {name}[/cyan]")

# ==================================================================
# AI KEY MANAGEMENT COMMANDS
# ==================================================================
@click.group(name="ai-key")
def ai_key_group():
    """🔑 Manage your Gemini API Key."""
    pass

@ai_key_group.command(name="set")
@click.argument('api_key')
def set_key(api_key):
    """Saves your Gemini API Key."""
    save_key(api_key)

@ai_key_group.command(name="reset")
def reset_key():
    """Deletes your saved Gemini API Key."""
    delete_key()

@ai_key_group.command(name="show")
def show_key():
    """Shows if you have a key saved."""
    key = get_key()
    if key:
        masked_key = f"{key[:5]}...{key[-4:]}"
        console.print(f"[green]✅ Key is currently set: {masked_key}[/green]")
    else:
        console.print("[yellow]⚠️ No key is currently set.[/yellow]")