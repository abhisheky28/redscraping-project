# redscraping_core/cli.py
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# --- IMPORT FEATURE COMMANDS ---
from .utils.setup_cmds import info, setup_chrome, init, context
# Update your import line:
from .scraping.scrape_cmds import headings, clean, titles
from .scraping.scrape_cmds import headings, clean, titles, description
from .scraping.scrape_cmds import headings, clean, titles, description, meta
from .scraping.scrape_cmds import headings, clean, titles, description, meta, href
from .scraping.scrape_cmds import headings, clean, titles, description, meta, href, elements
from .scraping.scrape_cmds import headings, clean, titles, description, meta, href, elements, text



console = Console()

@click.group(invoke_without_command=True)
@click.pass_context
def main_cli(ctx):
    """🚀 RedScraping - The Ultimate SEO Spider & Automation Framework"""
    
    # INTERACTIVE APP MODE
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(
            "[bold red]🕸️ Welcome to RedScraping[/bold red]\n"
            "[cyan]The Open-Source SEO Spider & Automation Framework[/cyan]"
        ))
        
        # PRINT OPTIONS FIRST!
        console.print("\n[1] 🕷️ Crawl & Extract (Coming in v2!)")
        console.print("[2] 🏗️ Generate Boilerplate Project (Init)")
        console.print("[3] 🤖 Generate AI Scraper Context")
        console.print("[4] ❌ Exit\n")
        
        # THEN ASK FOR INPUT
        action = Prompt.ask(
            "Enter the number of your choice",
            choices=["1", "2", "3", "4"],
            default="1",
            show_choices=False
        )
        
        if action == "1":
            console.print("\n[yellow]👉 Scraping engine is currently being built! Soon you will be able to run 'redscrape heading urls.txt'[/yellow]")
        elif action == "2":
            console.print("\n[yellow]👉 To do this via CLI, run: redscrape init --type sheets[/yellow]")
            # We can actually trigger the function directly here in the future!
        elif action == "3":
            console.print("\n[yellow]👉 To do this via CLI, run: redscrape context[/yellow]")
        elif action == "4":
            console.print("Goodbye! 👋")

# --- REGISTER UTILS (v1) COMMANDS ---
main_cli.add_command(info)
main_cli.add_command(setup_chrome, name="setup-chrome")
main_cli.add_command(init)
main_cli.add_command(context)
from .scraping.scrape_cmds import headings, clean

# ...
main_cli.add_command(headings)
main_cli.add_command(titles)
main_cli.add_command(description)
main_cli.add_command(meta)
main_cli.add_command(href)
main_cli.add_command(elements)
main_cli.add_command(text)
main_cli.add_command(clean)

if __name__ == "__main__":
    main_cli()