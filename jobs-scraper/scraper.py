import asyncio
from playwright.async_api import async_playwright
from urllib.parse import quote
from playwright_stealth import stealth_async  # ✅ IMPORT CORRECT
import pandas as pd
import random
import json
import sys


async def agent_scraper_linkedin(query, location, num_pages=1):
    all_offers = []
    print("🕵️ Agent_Scraper (mode STEALTH 🥷): Launching for LinkedIn...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # ✅ Apply stealth mode - VERSION CORRECTE
        await stealth_async(page)

        job_urls_to_scrape = []
        for page_num in range(num_pages):
            url = f"https://www.linkedin.com/jobs/search?keywords={quote(query)}&location={quote(location)}&start={page_num * 25}"
            print(f"→ Navigating to search results page: {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=120000)
                await page.wait_for_selector("ul.jobs-search__results-list", timeout=20000)
                job_links = await page.locator("a.base-card__full-link").all()
                if not job_links:
                    print("⚠️ No job links found on this page. Stopping.")
                    break

                for link_element in job_links:
                    title = await link_element.text_content()
                    href = await link_element.get_attribute("href")
                    if href:
                        job_urls_to_scrape.append({"title": title.strip(), "url": href})

                await asyncio.sleep(random.uniform(2, 5))

            except Exception as e:
                print(f"❌ Error during search results page scraping: {e}")
                await page.screenshot(path=f'/scripts/debug_search_error_{page_num}.png')
                break

        print(f"✅ Found {len(job_urls_to_scrape)} job offers from search results. Now scraping individual pages.")

        for job_data in job_urls_to_scrape:
            job_url = job_data['url']
            print(f"→ Navigating to job page: {job_url}")
            try:
                await page.goto(job_url, wait_until="domcontentloaded", timeout=60000)

                # Handle modal overlays
                try:
                    dismiss_selector = "button[aria-label='Dismiss']"
                    if await page.locator(dismiss_selector).count() > 0:
                        print("  Found a modal overlay. Clicking 'Dismiss'.")
                        await page.locator(dismiss_selector).first.click(timeout=5000)
                except Exception:
                    pass

                # Handle cookie banners
                try:
                    cookies_selector = "button[data-tracking-control-name='guest_contextual-auth-modal_dismiss']"
                    if await page.locator(cookies_selector).count() > 0:
                        print("  Found a cookies banner. Clicking 'Dismiss'.")
                        await page.locator(cookies_selector).first.click(timeout=5000)
                except Exception:
                    pass

                # Handle "See more" buttons
                see_more_selectors = [
                    'button[aria-label="Voir la description complète de l’offre"]',
                    'button.show-more-less-button',
                    'button[aria-label="Show more"]',
                    'button[aria-label="See more"]'
                ]

                for selector in see_more_selectors:
                    if await page.locator(selector).count() > 0:
                        print(f"  Clicking 'See more' button with selector: {selector}")
                        await page.locator(selector).first.click(timeout=30000)
                        await page.wait_for_selector(f'{selector}[aria-expanded="true"]', timeout=5000)
                        break

                # Extract description text
                description_selectors = [
                    "div#job-details",
                    "div.description__text",
                    "div.jobs-description__content",
                    "div.job-description"
                ]

                description_text = "Description non trouvée."
                for selector in description_selectors:
                    try:
                        description_element = page.locator(selector).first
                        await description_element.wait_for(state="visible", timeout=10000)
                        description_text = await description_element.inner_text()
                        print(f"  Description found using selector: {selector}")
                        break
                    except Exception:
                        continue

                job_data['description'] = description_text.strip()
                all_offers.append(job_data)
                await asyncio.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"❌ Could not scrape job description from {job_url}: {e}")
                job_data['description'] = "Description non disponible."
                all_offers.append(job_data)

        await browser.close()
        print(f"✨ Agent_Scraper: Finished. {len(all_offers)} offers with descriptions found.")

    return all_offers


def save_to_csv(data, filename="job_offers.csv"):
    """
    Saves a list of job dictionaries to a CSV file.
    """
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n✅ Results saved to {filename}")
    else:
        print("\n⚠️ No data to save.")


# ✅ MAIN ENTRYPOINT (for n8n and direct CLI use)
if __name__ == "__main__":
    # Parse command-line arguments if provided
    if len(sys.argv) >= 4:
        query = sys.argv[1]
        location = sys.argv[2]
        num_pages = int(sys.argv[3])
    else:
        query = "AI engineer"
        location = "France"
        num_pages = 1

    print(f"🔍 Searching for: '{query}' in '{location}' ({num_pages} page(s))")
    
    job_offers_data = asyncio.run(agent_scraper_linkedin(query, location, num_pages))
    
    # Output as JSON for n8n to parse
    print("\n" + "="*50)
    print("JSON OUTPUT:")
    print(json.dumps(job_offers_data, indent=2, ensure_ascii=False))
    print("="*50)