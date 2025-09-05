# FramesDirect Eyeglasses — Production-style Web Scraper
<!-- Badges -->
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/<DATAWoman2005>/web_scraping_for_better_vision_accessory)](./LICENSE)
[![Built with Selenium](https://img.shields.io/badge/Built%20with-Selenium-43B02A?logo=selenium)](https://www.selenium.dev/)
[![BeautifulSoup](https://img.shields.io/badge/Parser-BeautifulSoup4-6DB33F)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
[![Headless Chrome](https://img.shields.io/badge/Browser-Headless%20Chrome-4285F4?logo=googlechrome&logoColor=white)](https://chromium.org/)

A robust scraper for the FramesDirect eyeglasses catalogue (`https://www.framesdirect.com/eyeglasses/`).  
It handles modern, JavaScript-rendered infinite scroll, normalizes prices to numeric types, and exports analysis-ready CSV/JSON.

- **Why Selenium?** The page loads products dynamically; a requests/BS4 approach would miss items without a JS engine.
- **Reliability:** Progress-aware scrolling, stable selectors, numeric normalization, graceful failure paths.

## Highlights (Results)
- **Items scraped:** 25 products_  
- **Runtime:** 0m14(headless Chrome)  
- **Outputs:** `framesdotcom_data.csv`, `framesdotcom.json`

## Tech Stack
**Python 3.12**, **Selenium (headless Chrome via webdriver-manager)**, **BeautifulSoup (HTML parsing)**

## How to Run

# 0) activate venv (Git Bash on Windows)
source venv/Scripts/activate   # Git Bash on Windows

# 1) install deps (or simply: pip install -r requirements.txt)
pip install selenium webdriver-manager beautifulsoup4

# 2) run the scraper
python project/framesdirect/framesdirect.py

##  Key Files

project/framesdirect/framesdirect.py — main scraper

requirements.txt — pinned dependencies

README.md — this document

data/ — (optional) outputs, typically gitignored

| Field           | Type        | Description                |
| --------------- | ----------- | -------------------------- |
| `Brand`         | str         | Brand name on product tile |
| `Product_Code`  | str         | Model/code on tile         |
| `Former_Price`  | float\|null | Original MSRP as number    |
| `Current_Price` | float\|null | Offer price as number      |
| `Discount`      | str\|null   | e.g., “30% Off”            |


## Approach (Design Rationale)

Deterministic readiness: Wait explicitly for real tiles to exist (CSS: .prod-holder) rather than generic containers.

Lazy-load control: Implement progress-aware infinite scroll - scroll → pause → recount. A small up/down “nudge” triggers any final IntersectionObserver loads; a safety cap prevents infinite loops.

Parsing with BeautifulSoup: Parse driver.page_source. Within each tile:

Brand: .catalog-name

Product name: .product_name, with fallback to the name link if present

Prices: .prod-catalog-retail-price (former) and .prod-aslowas (current) within .prod-price-wrap (fallback to tile if absent)

Discount: .frame-discount
Non-product promo tiles are skipped by requiring tiles that have both brand and product name.

Normalization: A compact regex ([\d\.,]+) extracts digits/commas/decimals; commas are removed and values cast to float.

Fail-safe saving: If no rows are parsed, the script exits cleanly; otherwise it writes both CSV and JSON.

## Challenges & Solutions

Dynamic / lazy loading: Only a subset renders initially.
Solution: Progress-aware scrolling with a nudge and termination when counts stop increasing (with a safety cap).

Promo/ad tiles in grid → filter by presence of mandatory sub-elements
Solution: Filter to tiles that have both a brand and a product name, e.g.  
  `div.prod-holder:has(.catalog-name):has(.product_name), div.product-holder:has(.catalog-name):has(.product_name)`  
  *(Fallback guard in code: require `holder.select_one(".catalog-name")` and `holder.select_one(".product_name")` or the name link before parsing.)*
Selector fragility & mixed classes: Tiles use .prod-holder; product names are .product_name.
Solution: Use union selectors and fallbacks (e.g., name link id containing ProductNameLink); scope all searches to the tile.

Price strings with symbols/text. Values include currency symbols and commas (e.g., “As low as $299.00”).
Solution: Regex normalization to float; missing values become null.

Headless vs. mobile layout differences. Small default headless viewport can change markup.
Solution: Force desktop layout with --window-size=1920,3000 and a standard desktop user agent.

Session lifecycle errors. Sending commands after driver.quit() causes “connection refused.”
Solution: On critical wait failure, quit and SystemExit(1); optional debug HTML
Ethics & Compliance

Educational/portfolio use; scrape responsibly. 
Respect site terms and avoid excessive request rates. This tool does not bypass authentication or access protected data.