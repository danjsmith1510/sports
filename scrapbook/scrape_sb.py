import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://www.sportsbet.com.au"

async def scrape_main_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # set headless=True if you don’t want UI

        # Create an AU-style browser context
        context = await browser.new_context(
            locale="en-AU",
            timezone_id="Australia/Sydney",
            geolocation={"longitude": 151.2093, "latitude": -33.8688},  # Sydney coords
            permissions=["geolocation"],
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/116.0.0.0 Safari/537.36"
            )
        )

        page = await context.new_page()

        # Go to the WNBA main page
        await page.goto(f"{BASE_URL}/betting/basketball-us/wnba", wait_until="domcontentloaded")

        # Grab all event links
        event_links = await page.eval_on_selector_all(
            "a.linkMultiMarket_fcmecz0",
            "els => els.map(e => e.getAttribute('href'))"
        )

        # Make them absolute URLs
        event_urls = [BASE_URL + href for href in event_links if href]

        await browser.close()
        return event_urls


if __name__ == "__main__":
    urls = asyncio.run(scrape_main_page())
    for u in urls:
        print(u)