import os
import shutil
import time
import click
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_master_profile(profile_dir="Chrome-Profile", refresh=False, timeout=90):
    current_dir = os.getcwd()
    profile_path = os.path.join(current_dir, profile_dir)

    if refresh and os.path.exists(profile_path):
        click.secho(f"🗑️ Removing existing profile at: {profile_path}", fg="yellow")
        try:
            shutil.rmtree(profile_path)
            time.sleep(2)
        except OSError as e:
            click.secho(f"❌ Error removing profile: {e}. Make sure Chrome is closed!", fg="red")
            return

    click.secho(f"🚀 Initializing Chrome Profile at: {profile_path}", fg="green")
    
    options = Options()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--no-first-run")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    os.environ['WDM_LOG'] = '0' 
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    click.secho("\n" + "="*60, fg="cyan", bold=True)
    click.secho("!!! ACTION REQUIRED !!!", fg="red", bold=True)
    click.secho(f"A new Chrome browser has opened. You have {timeout} seconds.", fg="cyan")
    click.secho("1. Go to google.com and sign in to your Google account.", fg="cyan")
    click.secho("2. Close the browser MANUALLY when you are done.", fg="cyan")
    click.secho("="*60 + "\n", fg="cyan", bold=True)

    time.sleep(timeout)
    
    try:
        driver.quit()
    except:
        pass
        
    click.secho("✅ Master profile setup complete!", fg="green", bold=True)