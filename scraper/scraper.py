import asyncio
from playwright.async_api import async_playwright
from urllib.parse import quote
import pandas as pd
import random
import json
import sys
import os

# --- Configuration ---
OUTPUT_CSV_PATH = "/tmp/job_offers_results.csv"

# Redirect all print statements to stderr so they don't pollute stdout
def log(message):
    """Print to stderr instead of stdout"""
    print(message, file=sys.stderr)

async def agent_scraper_linkedin(query, location, num_pages=1):
    all_offers = []
    log("🕵️ Agent_Scraper (mode STEALTH 🥷): Launching for LinkedIn...")

    async with async_playwright() as p:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=user_agent
        )
        page = await context.new_page()

        job_urls_to_scrape = []
        for page_num in range(num_pages):
            url = f"https://www.linkedin.com/jobs/search?keywords={quote(query)}&location={quote(location)}&start={page_num * 25}"
            log(f"→ Navigating to search results page: {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=120000)
                await page.wait_for_selector("ul.jobs-search__results-list", timeout=20000)
                
                job_links = await page.locator("a.base-card__full-link").all()
                if not job_links:
                    log("⚠️ No job links found on this page. Stopping.")
                    break

                for link_element in job_links:
                    title = await link_element.text_content()
                    href = await link_element.get_attribute("href")
                    if href:
                        job_urls_to_scrape.append({"title": title.strip(), "url": href})

                await asyncio.sleep(random.uniform(2, 5))

            except Exception as e:
                log(f"❌ Error during search results page scraping: {e}")
                break

        offers_to_process = job_urls_to_scrape[:5]
        log(f"✅ Found {len(job_urls_to_scrape)} job offers from search results. Now scraping {len(offers_to_process)} individual pages.")

        for job_data in offers_to_process:
            job_url = job_data['url']
            log(f"→ Navigating to job page: {job_url}")
            try:
                await page.goto(job_url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(2)

                # Modal Handling
                modal_selectors = [
                    "button[aria-label='Dismiss']",
                    "button.modal__dismiss",
                    "button[aria-label='Fermer']",
                    "button[aria-label='Close']",
                ]
                
                for selector in modal_selectors:
                    try:
                        if await page.locator(selector).count() > 0:
                            log(f"  Closing modal with selector: {selector}")
                            await page.locator(selector).first.click(timeout=3000, force=True)
                            await asyncio.sleep(1) 
                    except Exception:
                        pass

                try:
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(0.5)
                    await page.wait_for_selector("div.modal__overlay", state="hidden", timeout=1000)
                except Exception:
                    pass

                # "See More" Button Handling
                see_more_selectors = [
                    'button[aria-label^="Voir la description complète"]',
                    'button.show-more-less-button',
                    'button[aria-label^="Show more"]',
                    'button[aria-label^="See more"]'
                ]

                for selector in see_more_selectors:
                    try:
                        if await page.locator(selector).count() > 0:
                            log(f"  Clicking 'See more' button with selector: {selector}")
                            await page.locator(selector).first.click(timeout=5000, force=True)
                            await asyncio.sleep(1)
                            break
                    except Exception as e:
                        continue

                # Description Extraction
                description_selectors = [
                    "div#job-details",
                    "div.description__text",
                    "div.jobs-description__content",
                    "div.show-more-less-html__markup",
                ]

                description_text = "Description non trouvée."
                for selector in description_selectors:
                    try:
                        description_element = page.locator(selector).first
                        if await description_element.count() > 0:
                            description_text = await description_element.inner_text(timeout=5000)
                            log(f"  ✓ Description found using selector: {selector}")
                            break
                    except Exception:
                        continue

                job_data['description'] = description_text.strip()
                all_offers.append(job_data)
                await asyncio.sleep(random.uniform(1, 3))

            except Exception as e:
                log(f"❌ Could not scrape job description from {job_url}: {e}")
                job_data['description'] = "Description non disponible en raison d'une erreur de scraping."
                all_offers.append(job_data)

        await browser.close()
        log(f"✨ Agent_Scraper: Finished. {len(all_offers)} offers with descriptions found.")

    return all_offers


def save_to_csv(data, filename):
    """Saves a list of job dictionaries to a CSV file."""
    if data:
        df = pd.DataFrame(data)
        df = df[['title', 'url', 'description']] 
        df.to_csv(filename, index=False, encoding='utf-8')
        log(f"\n✅ Results saved to temporary file: {filename}")
        return True
    else:
        log("\n⚠️ No data to save to CSV.")
        return False

if __name__ == "__main__":
    # Set default values
    query = "AI engineer"
    location = "France"
    num_pages = 1

    # Argument Parsing
    if len(sys.argv) >= 4:
        query = sys.argv[1].strip()
        location = sys.argv[2].strip()
        
        try:
            pages_arg = sys.argv[3].strip()
            if pages_arg:
                num_pages = int(pages_arg)
            if num_pages < 1:
                num_pages = 1
        except ValueError:
            log(f"⚠️ Warning: Invalid number of pages argument provided ('{sys.argv[3]}'). Using default value of 1.")
            num_pages = 1
        
        if not query: query = "AI engineer"
        if not location: location = "Worldwide"

    log(f"🔎 Searching for: '{query}' in '{location}' ({num_pages} page(s))")
    
    # Execute Scraper
    job_offers_data = asyncio.run(agent_scraper_linkedin(query, location, num_pages))
    
    # Save CSV
    if save_to_csv(job_offers_data, OUTPUT_CSV_PATH):
        # Output ONLY the CSV file path to stdout for n8n to read
        print(OUTPUT_CSV_PATH)
    else:
        log("Failed to create CSV file")
        sys.exit(1)