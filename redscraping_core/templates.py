# Redscraping_core/templates.py

CONFIG_TEMPLATE = """# config.py
import os

# --- Project Paths ---
PROJECT_ROOT = os.getcwd()
CHROME_PROFILE_PATH = os.path.join(PROJECT_ROOT, "Chrome-Profile")

# --- Scraping Config ---
SEARCH_URL = "https://www.google.com"

# List of user agents to rotate for stealth
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
]
"""

SHEETS_SCRAPER_TEMPLATE = """# scraper.py
import time
import gspread
import config
from google.oauth2.credentials import Credentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
    driver.get(config.SEARCH_URL)
    
    print("🌐 Browser opened successfully! Ready to scrape.")
    time.sleep(5)
    
    driver.quit()
    print("🏁 Done.")
"""

EXCEL_SCRAPER_TEMPLATE = """# scraper.py
import time
import pandas as pd
import config
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 🛑 USER SETTINGS: PUT YOUR EXCEL NAME HERE
# ==========================================
EXCEL_FILE = "data.xlsx"
# ==========================================

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
    # 1. Read Excel
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"✅ Successfully loaded {len(df)} rows from {EXCEL_FILE}!")
    except Exception as e:
        print(f"❌ Error reading Excel: {e}")
        exit()

    # 2. Start Browser
    driver = get_driver()
    driver.get(config.SEARCH_URL)
    
    print("🌐 Browser opened successfully! Ready to scrape.")
    time.sleep(5)
    
    driver.quit()
    print("🏁 Done.")
"""



AI_CONTEXT_TEMPLATE = """# ==============================================================================
# == CONTEXT FOR AI ASSISTANT (RedScraping Library) - v1.0
# ==============================================================================
#
# INSTRUCTIONS FOR THE HUMAN:
# 1. Give this ENTIRE file to your AI assistant (like ChatGPT) FIRST.
# 2. THEN, give it your 'scraper.py' file.
# 3. FINALLY, give it your prompt.
#
# --- EXAMPLE PROMPT ---
# "Using the context provided, please modify my scraper.py file. I need it to:
#  - Loop through each keyword in my Google Sheet.
#  - Search for the keyword on Google.
#  - Find the top 3 organic search result URLs.
#  - Save the URLs back to the sheet in the 'Ranking URL' column, separated by commas.
#  - If there's a major crash, send me an email notification."
#

# ==============================================================================
# == SECTION 1: PROJECT OVERVIEW & FILE STRUCTURE
# ==============================================================================
#
# When a user runs `Redscrape init`, the following files are created:
#
# - `scraper.py`: The main script where you (the AI) will write the custom logic.
# - `config.py`: A file containing shared variables.
# - `Chrome-Profile/`: A dedicated Chrome profile for stealthy scraping.
# - `token.json`: The user's Google OAuth token (DO NOT READ/WRITE THIS).
# - `data.xlsx` (Excel only): A template Excel file for input.
#

# ==============================================================================
# == SECTION 2: THE CORE LIBRARY FUNCTIONS (Your Toolbox)
# ==============================================================================
#
# These functions are available to use inside `scraper.py`.
# You do NOT need to define them; they are imported from the Redscraping library.

def get_driver():
    \"\"\"
    Initializes and returns a pre-configured, stealthy Selenium WebDriver.
    It automatically handles options, services, and webdriver installation.

    :return: A ready-to-use Selenium driver.
    :rtype: selenium.webdriver.chrome.webdriver.WebDriver
    \"\"\"
    pass

def connect_to_sheets():
    \"\"\"
    Connects to the user's Google account and returns a gspread client.
    It automatically handles authentication using the user's `token.json`.

    :return: A ready-to-use gspread client.
    :rtype: gspread.client.Client
    \"\"\"
    pass

def connect_to_excel(filename="data.xlsx"):
    \"\"\"
    Reads an Excel file from the project folder into a Pandas DataFrame.

    :param filename: The name of the Excel file (defaults to 'data.xlsx').
    :return: A Pandas DataFrame with the Excel data.
    :rtype: pandas.DataFrame
    \"\"\"
    pass

# ==============================================================================
# == SECTION 3: ADVANCED FEATURES & BEST PRACTICES
# ==============================================================================
#
# Use these patterns to build robust and reliable scrapers.

def handle_captcha(driver):
    \"\"\"
    This is a placeholder for a function that would pause the script if a CAPTCHA is detected.
    The AI should check for CAPTCHA elements and call this function if they exist.
    
    EXAMPLE USAGE:
    if driver.find_elements(By.CSS_SELECTOR, 'iframe[title*="reCAPTCHA"]'):
        print("CAPTCHA detected! Please solve it manually.")
        # In a real library, this would pause and wait. For now, we just wait.
        time.sleep(60) # Pause for 60 seconds
    \"\"\"
    pass

def send_notification_email(subject, body):
    \"\"\"
    This is a placeholder for a function that sends an email.
    The AI should use this inside a main try/except block to report critical errors.
    The user would need to configure their email settings in a real scenario.
    
    EXAMPLE USAGE:
    try:
        # ... main scraping logic ...
    except Exception as e:
        error_details = f"The script crashed! Error: {e}"
        send_notification_email("Scraper CRASHED!", error_details)
    \"\"\"
    pass

# --- ERROR HANDLING ---
# When looping through items (like keywords), always wrap the logic for a
# single item in a try/except block. This prevents the entire script from
# crashing if one keyword fails.

# --- WORKING WITH MULTIPLE FILES ---
# The user can work with multiple sheets or Excel files in the same project.
# - To open another sheet: `sheet2 = gc.open("Another Sheet Name").worksheet("Sheet1")`
# - To open another Excel file: `df2 = connect_to_excel("another_data.xlsx")`

# ==============================================================================
# == SECTION 4: COMPLETE EXAMPLES & PATTERNS
# ==============================================================================

# --- PATTERN 1: Standard Google Sheet Scraper ---
def example_google_sheet_scraper():
    # 1. Connect
    gc = connect_to_sheets()
    sheet = gc.open("Redscraping").worksheet("Scrape")
    data = sheet.get_all_records()

    # 2. Start Browser
    driver = get_driver()

    # 3. Loop and Scrape
    for index, row in enumerate(data):
        try:
            keyword = row.get('Keyword')
            print(f"Processing: {keyword}")
            # ... your selenium logic here ...
            
            # Update the sheet (row is index + 2)
            sheet.update_cell(index + 2, 4, "Scraped Result")

        except Exception as e:
            print(f"Could not process row {index + 2}. Error: {e}")
            continue # Move to the next row

    # 4. Quit
    driver.quit()


# --- PATTERN 2: Standard Excel Scraper ---
def example_excel_scraper():
    # 1. Connect
    df = connect_to_excel("data.xlsx")

    # 2. Start Browser
    driver = get_driver()

    # 3. Loop and Scrape
    for index, row in df.iterrows():
        try:
            keyword = row['Keyword']
            print(f"Processing: {keyword}")
            # ... your selenium logic here ...
            
            # Update the DataFrame
            df.at[index, 'Ranking URL'] = "Scraped Result"

        except Exception as e:
            print(f"Could not process row {index}. Error: {e}")
            continue # Move to the next row

    # 4. Save and Quit
    df.to_excel("data.xlsx", index=False)
    driver.quit()

# ==============================================================================
# == IMPORTANT NOTES FOR THE AI
# ==============================================================================
#
# - DO NOT redefine the functions `get_driver`, `connect_to_sheets`, etc.
#   They are provided by the library.
# - ALWAYS use these provided functions for setup. Do not write your own
#   Selenium options or gspread authentication code.
# - Modify the user's `scraper.py` file IN-PLACE. Do not generate a new file.
# - The user's `scraper.py` will already contain the basic structure.
#   Your job is to add the custom logic inside the `if __name__ == "__main__":` block.
#
# ==============================================================================
# == END OF CONTEXT
# ==============================================================================
"""