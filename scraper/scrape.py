import requests
from bs4 import BeautifulSoup
import urllib.robotparser
import time
import argparse
import os
import sys
import pathlib

# Ensure project root is on sys.path so we can import the app package
ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
# Ensure .env at project root is discovered by pydantic-settings
try:
    os.chdir(str(ROOT_DIR))
except Exception:
    pass

from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app import models


WEBSITES = "https://books.toscrape.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.89 Safari/537.36"
}

scraped_urls = []

# Simple CLI setup
def setup_cli():
    parser = argparse.ArgumentParser(description='Book Scraper')
    parser.add_argument('--pages', type=int, default=1, help='Number of pages to scrape')
    parser.add_argument('--db', action='store_true', help='Save to database')
    return parser.parse_args()

def respect_robots_txt(url,pages):
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(url + "robots.txt")
    rp.read()
    flag=rp.can_fetch("*", url)
    print(f"Robots.txt allows scraping: {url} , page {pages+1}")
    if flag:
        return True
    else:
        return False

# Fetch HTML content of a URL
def fetch_data(url,i):
    try:
        if respect_robots_txt(url,i):
            print(f"Fetching data from {url} , page {i+1}")
            response = requests.get(url, headers=HEADERS, timeout=10)  # Added timeout to avoid hanging
            response.raise_for_status()
            return response.text
        else:
            print(f"Skipping page {i+1} because it is blocked by robots.txt")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None



# Extract book data from books.toscrape.com
def get_book_data(website,i):
    if i==0:
        html = fetch_data(website,i)
    else:
        html = fetch_data(website + f"/catalogue/page-{i+1}.html",i)
    if not html:
        print(f"Failed to fetch HTML from {website}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    books = []

    # Select each book article
    for article in soup.select("article.product_pod"):
        try:
            # Extract link
            link_element = article.select_one("h3 a[href]")
            if not link_element:
                continue
                
            link = link_element.get("href")
            full_link = link if link.startswith("http") else website.rstrip('/') + '/' + link.lstrip('/')
            
            # Extract image and alt text
            img_element = article.select_one(".image_container img")
            image_url = ""
            alt_text = ""
            if img_element:
                image_url = img_element.get("src", "")
                if image_url and not image_url.startswith("http"):
                    image_url = website.rstrip('/') + '/' + image_url.lstrip('/')
                alt_text = img_element.get("alt", "")
            
            # Extract price
            price_element = article.select_one("p.price_color")
            price = price_element.get_text(strip=True) if price_element else "No price"
            
            # Skip if already scraped
            if full_link not in scraped_urls:
                book_data = {
                    "title": alt_text,  # Alt text contains the book title
                    "link": full_link,
                    "image_url": image_url,
                    "alt_text": alt_text,
                    "price": price.replace("£", "").replace("Â", "") if price != "No price" else price,
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                books.append(book_data)
                scraped_urls.append(full_link)
                
        except Exception as e:
            print(f"Error processing book: {e}")
            continue

    return books

def save_to_json(data, filename="samples/scraped.json"):
    """Save scraped data to JSON file in scraper folder"""
    import json
    
    try:
        # Resolve path relative to project root if not absolute
        if not os.path.isabs(filename):
            filename = os.path.join(str(ROOT_DIR), filename)
        # Ensure destination directory exists
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
        return data
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return None

def save_to_db(data):
    """Insert scraped items into scraped_resources using the app's DB."""
    if not data:
        print("No data to save to DB")
        return 0
    session = SessionLocal()
    inserted = 0
    try:
        for item in data:
            link = item.get("link")
            if not link:
                continue
            # skip if exists
            exists = session.query(models.ScrapedResource).filter(models.ScrapedResource.link == link).first()
            if exists:
                continue
            row = models.ScrapedResource(
                title=item.get("title", ""),
                link=link,
                image_url=item.get("image_url", ""),
                price=item.get("price", ""),
                scraped_at=item.get("scraped_at", ""),
            )
            session.add(row)
            inserted += 1
        session.commit()
        print(f"Inserted {inserted} new rows into scraped_resources")
        return inserted
    except IntegrityError as ie:
        session.rollback()
        print(f"Integrity error inserting rows: {ie}")
        return inserted
    except Exception as e:
        session.rollback()
        print(f"Error saving to DB: {e}")
        return inserted
    finally:
        session.close()


# Main scraping function
def scrape_and_save(websites, pages=1, use_db=False):
    all_data = []
    for i in range(pages):
        print(f"Scraping page {i+1}...")
        books = get_book_data(websites,i)
        all_data.extend(books)
        if i < pages - 1:
            time.sleep(1)
    
    if all_data:
        data=save_to_json(all_data)
        if use_db:
            save_to_db(data)
        else:
            print(f"Data is not saved to database")
        print(f"Total: {len(all_data)} books scraped!")
    else:
        print("No data scraped")



if __name__ == "__main__":
    # Get CLI arguments
    args = setup_cli()
    
    # Run scraper with arguments
    scrape_and_save(WEBSITES, pages=args.pages, use_db=args.db)

