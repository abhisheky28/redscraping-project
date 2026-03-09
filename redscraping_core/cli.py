import click
from .chrome_setup import setup_master_profile
from .project_generator import generate_project, generate_ai_context

@click.group()
def main_cli():
    """🚀 RedScraping CLI - Your Ultimate Automation Setup Tool"""
    pass

@main_cli.command()
def info():
    """Displays instructions on how to use the setups."""
    click.secho("\n=== RedScraping Setup Guide ===", fg="cyan", bold=True)
    click.echo("1. Run 'redscrape setup-chrome' to prime your browser.")
    click.echo("2. Run 'redscrape init --type sheets' (or --type excel) to generate your project.")
    click.echo("3. (Optional) Run 'redscrape context' to generate a helper file for AI assistants.")
    click.echo("4. Open your 'scraper.py' file, add your logic, and run it!\n")

@main_cli.command()
@click.option('--refresh', is_flag=True, help="Deletes the old profile and creates a new one.")
@click.option('--timeout', default=90, help="Time in seconds to wait for manual login.")
def setup_chrome(refresh, timeout):
    """Creates and logs into the Master Chrome Profile."""
    setup_master_profile(refresh=refresh, timeout=timeout)

@main_cli.command()
@click.option('--type', 'project_type', type=click.Choice(['sheets', 'excel']), required=True, help="Choose 'sheets' or 'excel'")
def init(project_type):
    """Generates the boilerplate code for your scraper."""
    click.secho(f"🏗️ Generating {project_type.upper()} project boilerplate...", fg="cyan")
    generate_project(project_type)

@main_cli.command()
def context():
    """Generates a context file for AI assistants."""
    generate_ai_context()