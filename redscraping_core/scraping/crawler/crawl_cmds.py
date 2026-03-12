# redscraping_core/scraping/crawl_cmds.py

import click
from .urls import run_urls_crawler
# Add to imports at the top:
from .broken import run_broken_crawler
from .emails import run_emails_crawler
from .assets import run_assets_crawler
from .orphans import run_orphans_crawler



@click.command()
@click.argument('domain')
@click.option('--limit', type=int, default=0, help="Max pages to crawl (0 = unlimited)")
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv']), default='excel')
@click.option('--restart', is_flag=True, help="Start fresh")
def urls(domain, limit, output_format, restart):
    """Crawls a domain and maps all internal URLs."""
    run_urls_crawler(domain, limit, output_format, restart)



@click.command()
@click.argument('domain')
@click.option('--limit', type=int, default=0, help="Max pages to crawl (0 = unlimited)")
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv']), default='excel')
@click.option('--restart', is_flag=True, help="Start fresh")
def broken(domain, limit, output_format, restart):
    """Crawls a domain and finds all 404/Broken links."""
    run_broken_crawler(domain, limit, output_format, restart)



@click.command()
@click.argument('domain')
@click.option('--limit', type=int, default=0, help="Max pages to crawl (0 = unlimited)")
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv']), default='excel')
@click.option('--restart', is_flag=True, help="Start fresh")
def emails(domain, limit, output_format, restart):
    """Crawls a domain and extracts all email addresses."""
    run_emails_crawler(domain, limit, output_format, restart)



@click.command()
@click.argument('domain')
@click.option('--limit', type=int, default=0)
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv']), default='excel')
@click.option('--restart', is_flag=True)
def assets(domain, limit, output_format, restart):
    """Crawls a domain and catalogs all Images, CSS, JS, and Videos."""
    run_assets_crawler(domain, limit, output_format, restart)

@click.command()
@click.argument('domain')
@click.option('--limit', type=int, default=0)
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv']), default='excel')
@click.option('--restart', is_flag=True)
def orphans(domain, limit, output_format, restart):
    """Finds Orphan pages by comparing the site to its sitemap."""
    run_orphans_crawler(domain, limit, output_format, restart)