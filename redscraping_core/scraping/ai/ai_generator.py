import os
import re
import time
from google import genai
from google.genai import types
from rich.console import Console
from .key_manager import get_key

console = Console()

BOILERPLATE_TEMPLATE = """import time
import gspread
import config
from google.oauth2.credentials import Credentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 🛑 USER SETTINGS: GOOGLE SHEET INFO
# ==========================================
SHEET_NAME = "Redscraping" 
WORKSHEET_NAME = "Scrape"
# ==========================================

def connect_to_sheets():
    print("Connecting to Google Sheets...")
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_authorized_user_file('token.json', scopes)
    gc = gspread.authorize(creds)
    return gc

def get_driver():
    print("Initializing Chrome...")
    options = Options()
    options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
    options.add_argument("--no-first-run")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

if __name__ == "__main__":
    # 1. Connect to Sheets
    gc = connect_to_sheets()
    try:
        sheet = gc.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
        data = sheet.get_all_records()
        print(f"✅ Successfully loaded {len(data)} rows from Google Sheets!")
    except Exception as e:
        print(f"❌ Error opening sheet: {e}")
        print(f"Make sure a sheet named '{SHEET_NAME}' exists on your Google account!")
        exit()

    # 2. Start Browser
    driver = get_driver()
    
    # ==========================================
    # 🤖 AI GENERATED LOGIC STARTS HERE
    # ==========================================
    
    # ==========================================
    # 🤖 AI GENERATED LOGIC ENDS HERE
    # ==========================================
    
    print("🏁 Done.")
    driver.quit()
"""

SYSTEM_PROMPT = f"""You are an expert Python and Selenium automation engineer.
Your job is to write custom web scraping and automation scripts based on user requests.

You MUST use the following boilerplate code exactly as it is. 
DO NOT change the imports, the setup functions, or the Google Sheets connection.
You must ONLY insert your custom logic inside the `if __name__ == "__main__":` block, exactly where it says "AI GENERATED LOGIC STARTS HERE".

The variable `data` is a list of dictionaries representing the Google Sheet rows.
The variable `sheet` is the gspread worksheet object (use this to update cells).
The variable `driver` is the active Selenium webdriver.

Here is the boilerplate:
{BOILERPLATE_TEMPLATE}

Return ONLY the complete, final Python code. Do not include markdown formatting like ```python. Just the raw code.
"""

def generate_with_retries(client, prompt, max_retries=4):
    """Handles API limits and errors using the new google-genai SDK."""
    for attempt in range(max_retries):
        try:
            # Using the newest, fastest model available in the new SDK
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                )
            )
            return response.text
            
        except Exception as e:
            error_str = str(e).lower()
            # Check if it's a rate limit (429) or quota error
            if "429" in error_str or "exhausted" in error_str or "quota" in error_str:
                wait_time = (2 ** attempt) * 5
                console.print(f"[yellow]⏳ Gemini API is busy. Waiting {wait_time}s before retrying... ({attempt + 1}/{max_retries})[/yellow]")
                time.sleep(wait_time)
            else:
                console.print(f"[red]❌ API Error: {e}[/red]")
                return None
                
    console.print("[red]❌ Failed to generate code after maximum retries.[/red]")
    return None

def generate_script(user_prompt, output_filename):
    api_key = get_key()
    
    if not api_key:
        console.print("[red]❌ Gemini API Key not found![/red]")
        console.print("[yellow]1. Get a free key here: https://aistudio.google.com/app/apikey[/yellow]")
        console.print("[yellow]2. Run this command to save it: redscrape ai-key set <YOUR_KEY>[/yellow]")
        return False

    # Initialize the new SDK client
    client = genai.Client(api_key=api_key)
    
    console.print("[cyan]🤖 Gemini 2.5 Flash is thinking and writing your code...[/cyan]")
    
    raw_code = generate_with_retries(client, user_prompt)
    
    if raw_code:
        clean_code = re.sub(r'^```python\n', '', raw_code)
        clean_code = re.sub(r'^```\n', '', clean_code)
        clean_code = re.sub(r'```$', '', clean_code)
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(clean_code.strip())
            
        return True
        
    return False