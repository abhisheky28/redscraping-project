# redscraping_core/scraping/scrape_cmds.py

import click
import os
import glob
from rich.console import Console
# We no longer need preflight here
from .url_features.headings import run_headings_scraper
from .url_features.titles import run_titles_scraper
from .url_features.description import run_description_scraper
from .url_features.meta import run_meta_scraper
from .url_features.href import run_href_scraper
from .url_features.elements import run_elements_scraper
# Add to imports at the top:
from .url_features.all_text import run_all_text_scraper


console = Console()

@click.command()
@click.argument('input_file')
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv', 'json', 'txt']), default='excel')
@click.option('--restart', is_flag=True, help="Ignore cache and start from scratch")
def headings(input_file, output_format, restart):
    """Scrapes H1-H6 from URLs in the 'input' folder."""
    
    # --- THIS IS THE FIX ---
    # We now call the function with only the 3 arguments it expects.
    run_headings_scraper(input_file, output_format, restart)
    # -----------------------


@click.command()
@click.argument('input_file')
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv', 'json', 'txt']), default='excel')
@click.option('--restart', is_flag=True, help="Ignore cache and start from scratch")
def titles(input_file, output_format, restart):
    """Scrapes <title> tags from URLs."""
    run_titles_scraper(input_file, output_format, restart)



@click.command()
@click.argument('input_file')
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv', 'json', 'txt']), default='excel')
@click.option('--restart', is_flag=True)
def description(input_file, output_format, restart):
    """Scrapes meta descriptions from URLs."""
    run_description_scraper(input_file, output_format, restart)



@click.command()
@click.argument('input_file')
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv', 'json', 'txt']), default='excel')
@click.option('--restart', is_flag=True, help="Ignore cache and start from scratch")
def meta(input_file, output_format, restart):
    """Scrapes ALL meta tags from URLs."""
    run_meta_scraper(input_file, output_format, restart)



# Add this command below your others:
@click.command()
@click.argument('input_file')
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv', 'json', 'txt']), default='excel')
@click.option('--restart', is_flag=True, help="Ignore cache and start from scratch")
def href(input_file, output_format, restart):
    """Scrapes all links (href) from URLs."""
    run_href_scraper(input_file, output_format, restart)



@click.command()
@click.argument('selector')
@click.argument('input_file')
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv', 'json', 'txt']), default='excel')
@click.option('--restart', is_flag=True, help="Ignore cache and start from scratch")
def elements(selector, input_file, output_format, restart):
    """Scrapes specific CSS elements. (e.g., redscrape elements ".price" urls.txt)"""
    run_elements_scraper(input_file, selector, output_format, restart)




# Add this command below your others:
@click.command()
@click.argument('input_file')
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv', 'json', 'txt']), default='excel')
@click.option('--restart', is_flag=True, help="Ignore cache and start from scratch")
def text(input_file, output_format, restart):
    """Scrapes all visible, readable text from URLs."""
    run_all_text_scraper(input_file, output_format, restart)




@click.command()
@click.argument('feature', type=click.Choice(['headings', 'titles', 'description', 'meta', 'href', 'all']))
def clean(feature):
    """Cleans the internal cache. (e.g., redscrape clean headings)"""
    cache_dir = os.path.join(os.getcwd(), ".cache")
    
    if not os.path.exists(cache_dir):
        console.print("[yellow]No cache folder found.[/yellow]")
        return

    if feature == 'all':
        files = glob.glob(os.path.join(cache_dir, "*.json"))
    else:
        files = glob.glob(os.path.join(cache_dir, f"{feature}_*.json"))

    if not files:
        console.print(f"[green]✨ Cache is already clean for '{feature}'.[/green]")
        return

    for f in files:
        os.remove(f)
    
    console.print(f"[bold green]🧹 Successfully cleaned {len(files)} cache file(s) for '{feature}'.[/bold green]")