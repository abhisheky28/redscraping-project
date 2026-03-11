import os
import click
import pandas as pd
import gspread
import traceback
from google.oauth2.credentials import Credentials
from .templates import CONFIG_TEMPLATE, SHEETS_SCRAPER_TEMPLATE, EXCEL_SCRAPER_TEMPLATE, AI_CONTEXT_TEMPLATE
from .gcp_setup import setup_gcp_auth

def setup_google_sheet():
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_authorized_user_file('token.json', scopes)
    gc = gspread.authorize(creds)
    
    sheet_name = "Redscraping"
    worksheet_name = "Scrape"
    
    try:
        sh = gc.open(sheet_name)
        click.secho(f"✅ Found existing Google Sheet: '{sheet_name}'", fg="green")
    except gspread.exceptions.SpreadsheetNotFound:
        click.secho(f"📝 Creating new Google Sheet: '{sheet_name}'...", fg="yellow")
        sh = gc.create(sheet_name)
        
    worksheet = sh.sheet1
    if worksheet.title != worksheet_name:
        worksheet.update_title(worksheet_name)
        
    if not worksheet.get_all_values():
        worksheet.append_row(["Keyword", "Company1", "Rankings", "Ranking URL"])
        click.secho("✅ Added default headers to the sheet.", fg="green")
        
    return sh.url

def generate_project(project_type):
    current_dir = os.getcwd()

    # --- NEW: CREATE FOLDERS ON INIT ---
    console = click.get_current_context().obj if hasattr(click.get_current_context(), 'obj') else None # A safe way to get console
    
    for folder in ["input", "output", ".cache"]:
        folder_path = os.path.join(current_dir, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            if console:
                click.secho(f"✅ Created '{folder}/' directory.", fg="green")
    # --- END OF NEW CODE ---

    
    config_path = os.path.join(current_dir, "config.py")
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(CONFIG_TEMPLATE)
        click.secho("✅ Created config.py", fg="green")
    else:
        click.secho("✅ config.py already exists (Skipped)", fg="yellow")

    base_scraper_path = os.path.join(current_dir, "scraper.py")
    if os.path.exists(base_scraper_path):
        script_name = f"scraper_{project_type}.py"
    else:
        script_name = "scraper.py"
    scraper_path = os.path.join(current_dir, script_name)
    
    if project_type == "sheets":
        setup_gcp_auth()
        try:
            sheet_url = setup_google_sheet()
        except Exception as e:
            click.secho(f"❌ Failed to setup Google Sheet. Error details:", fg="red")
            click.secho(traceback.format_exc(), fg="red")
            return
        
        with open(scraper_path, "w", encoding="utf-8") as f:
            f.write(SHEETS_SCRAPER_TEMPLATE)
        click.secho(f"✅ Created {script_name} (Google Sheets version)", fg="green")
        click.secho("\n🎉 Project ready!", fg="cyan", bold=True)
        click.secho(f"🔗 Your Google Sheet URL: {sheet_url}", fg="blue", bold=True)
        click.secho(f"👉 Add your keywords to the sheet, then run 'python {script_name}'.", fg="cyan")
        
    elif project_type == "excel":
        with open(scraper_path, "w", encoding="utf-8") as f:
            f.write(EXCEL_SCRAPER_TEMPLATE)
        click.secho(f"✅ Created {script_name} (Excel version)", fg="green")
        
        excel_path = os.path.join(current_dir, "data.xlsx")
        if not os.path.exists(excel_path):
            df = pd.DataFrame(columns=["Keyword", "Company1", "Rankings", "Ranking URL"])
            df.to_excel(excel_path, index=False)
            click.secho("✅ Created data.xlsx (Template)", fg="green")
        else:
            click.secho("✅ data.xlsx already exists (Skipped)", fg="yellow")
        
        click.secho(f"\n🎉 Project ready! Open data.xlsx, add keywords, then run 'python {script_name}'.", fg="cyan", bold=True)

def generate_ai_context():
    current_dir = os.getcwd()
    context_path = os.path.join(current_dir, "CONTEXT_FOR_AI.py")
    with open(context_path, "w", encoding="utf-8") as f:
        f.write(AI_CONTEXT_TEMPLATE)
    click.secho("✅ Created CONTEXT_FOR_AI.py", fg="green")
    click.secho("👉 Give this file to your AI assistant before giving it your scraper.py file.", fg="cyan")