import time
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
    
    print("Navigating to Google...")
    driver.get("https://www.google.com")

    try:
        # Give the page some time to load
        time.sleep(3) 
        
        # Find the search bar by its name attribute 'q'
        # Using a try-except block for robustness in finding elements
        try:
            search_bar = driver.find_element(By.NAME, "q")
        except Exception:
            print("❌ Could not find the Google search bar (element with name 'q').")
            raise # Re-raise the exception to be caught by the outer except block

        print("Searching for 'myntra'...")
        search_bar.send_keys("myntra")
        search_bar.send_keys(Keys.RETURN)
        
        # Give time for search results to load
        time.sleep(5) 

        print("Scraping URLs from the first page of search results...")
        links = driver.find_elements(By.TAG_NAME, "a")
        scraped_urls = []
        
        for link in links:
            href = link.get_attribute("href")
            # Filter out invalid hrefs, internal Google links, and other non-result links
            if href and href.startswith("http") and \
               "google.com" not in href and \
               "gstatic.com" not in href and \
               "schema.org" not in href and \
               "accounts.google.com" not in href and \
               "support.google.com" not in href:
                scraped_urls.append(href)
        
        # Remove duplicates while preserving order
        scraped_urls = list(dict.fromkeys(scraped_urls))

        print(f"Found {len(scraped_urls)} unique URLs.")

        # Update Google Sheet
        if scraped_urls:
            print("Updating Google Sheet with scraped URLs...")
            
            # Clear the entire worksheet content to ensure a clean slate for new data.
            # WARNING: This is a destructive operation and will remove all existing data
            # from the specified worksheet.
            sheet.clear() 
            
            # Add header for the scraped URLs in the first cell (A1)
            sheet.update_cell(1, 1, "Scraped URL")
            
            # Prepare data for batch update: gspread expects a list of lists,
            # where each inner list represents a row.
            urls_to_write = [[url] for url in scraped_urls]
            
            # Update the sheet starting from the second row, first column (A2).
            # This will populate column A with the scraped URLs.
            sheet.update(f'A2', urls_to_write)
            
            print("✅ Google Sheet updated successfully with scraped URLs!")
        else:
            print("No URLs found to update the Google Sheet.")

    except Exception as e:
        print(f"❌ An error occurred during scraping or sheet update: {e}")
    
    # ==========================================
    # 🤖 AI GENERATED LOGIC ENDS HERE
    # ==========================================
    
    print("🏁 Done.")
    driver.quit()