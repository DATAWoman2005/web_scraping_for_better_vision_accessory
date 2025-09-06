import csv
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Step 1 - Configuration and Data Fetching
# Setup Selenium and WebDriver
print("Setting up webdriver...")

chrome_option = Options()
chrome_option.add_argument("--headless")
chrome_option.add_argument("--disable-gpu")
chrome_option.add_argument("--window-size=1920,3000")
chrome_option.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
)
print("done setting up..")

# Install the chrome driver (This is a one time thing)
print("Installing Chrome WD")
service = Service(ChromeDriverManager().install())
print("Final Setup")
driver = webdriver.Chrome(service=service, options=chrome_option)
print("Done")

# Make connection and get URL content
url = "https://www.framesdirect.com/eyeglasses/"
print(f"Visting {url} page")
driver.get(url)

# Further instruction: wait for JS to load the files
try:
    print("Waiting for product tiles to load")
    WDW(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "prod-holder"))
    )
    print("Done...Proceed to parse the data")
except (TimeoutError, Exception) as e:
    print(f"Error waiting for {url}: {e}")
    driver.quit()
    raise SystemExit(1)  # stop after quitting, avoid connection refused
    print("Closed")


# Step 2 - Data Parsing and Extraction
# Get page source and parse using BeautifulSoup
content = driver.page_source
page = BeautifulSoup(content, "html.parser")

# Temporary storage for the extracted data
frames_data = []

product_holder = page.select("div.prod-holder:has(.catalog-name):has(.product_name)")
print(f"Found {len(product_holder)} product tiles (ads excluded)")


for holder in product_holder:

    brand_tag = holder.find("div", class_="catalog-name")
    brand = brand_tag.get_text(" ", strip=True) if brand_tag else None  # brand name

    # product code
    code_tag = holder.find("div", class_="product_name")
    code_tag = code_tag.get_text(" ", strip=True) if code_tag else None  # product code

    price_wrap = holder.find("div", class_="prod-price-wrap") or holder

    # former (original) price
    former_price_tag = price_wrap.find("div", class_="prod-catalog-retail-price")
    former_price_text = (
        former_price_tag.get_text(strip=True) if former_price_tag else None
    )

    # current (offer) price
    current_price_tag = price_wrap.find("div", class_="prod-aslowas")
    current_price_text = (
        current_price_tag.get_text(strip=True) if current_price_tag else None
    )

    discount_tag = price_wrap.find("div", class_="frame-discount")
    discount = discount_tag.get_text(strip=True) if discount_tag else None

    # converting prices to NUMBERS ONLY (float) using regex
    def to_number(txt):
        if not txt:
            return None
        m = re.search(r"[\d\.,]+", txt)
        return float(m.group(0).replace(",", "")) if m else None

    former_price = to_number(former_price_text)
    current_price = to_number(current_price_text)

    # Assignment: Add the category

    data = {
        "Brand": brand,
        "Product_Code": code_tag,
        "Former_Price": former_price,
        "Current_Price": current_price,
        "Discount": discount,
    }
    # Append data to the list
    frames_data.append(data)

# Step 3 - Data Storage and Finalization
if not frames_data:  # to avoid crashing if nothing parsed
    print("No data parsed. Nothing to save.")
else:
    # Save to CSV file
    column_name = frames_data[0].keys()  # get the column names
    with open(
        "framesdotcom_data.csv", mode="w", newline="", encoding="utf-8"
    ) as csv_file:  # open up the file with context manager
        dict_writer = csv.DictWriter(csv_file, fieldnames=column_name)
        dict_writer.writeheader()
        dict_writer.writerows(frames_data)
    print(f"Saved {len(frames_data)} records to CSV")

    # Save to JSON file
    with open("framesdotcom.json", mode="w", encoding="utf-8") as json_file:
        json.dump(frames_data, json_file, indent=4, ensure_ascii=False)
    print(f"Saved {len(frames_data)} records to JSON")

# close the browser
driver.quit()
print("End of Web Extraction")
