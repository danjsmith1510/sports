import asyncio
from typing import List

from prefect import flow, task
from playwright.async_api import async_playwright

BASE_URL = "https://www.sportsbet.com.au"


@task
async def get_event_links() -> List[str]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            locale="en-AU",
            timezone_id="Australia/Sydney",
            geolocation={"longitude": 151.2093, "latitude": -33.8688},
            permissions=["geolocation"],
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/116.0.0.0 Safari/537.36"
            )
        )

        page = await context.new_page()
        await page.goto(f"{BASE_URL}/betting/basketball-us/wnba", wait_until="networkidle")

        event_links = await page.eval_on_selector_all(
            "a.linkMultiMarket_fcmecz0",
            "els => els.map(e => e.getAttribute('href'))"
        )
        event_urls = [BASE_URL + href for href in event_links if href]

        await browser.close()
        return event_urls


@flow
def scraping_test():
    """Prefect flow to scrape WNBA event links from Sportsbet."""
    urls = asyncio.run(get_event_links())
    for u in urls:
        print(u)


if __name__ == "__main__":
    scraping_test()