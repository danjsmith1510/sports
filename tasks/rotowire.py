from io import StringIO
import os
import asyncio
import pandas as pd
from prefect import task
from playwright.async_api import async_playwright

async def login_rotowire(page):
    print("🔐 Starting login to Rotowire...")
    
    print("🌐 Navigating to login page...")
    await page.goto("https://www.rotowire.com/subscribe/login/")
    
    print("🧾 Filling in username...")
    await page.fill('input[placeholder="Enter username or email"]', os.environ.get("rotowire_username", ""))
    
    print("🔒 Filling in password...")
    await page.fill('input[placeholder="Enter your password"]', os.environ.get("rotowire_password", ""))
    
    print("➡️ Clicking login button...")
    await page.click('button:has-text("Login")')
    
    print("⏳ Waiting for log in to complete...")
    await page.wait_for_selector('button.rwnav-top-account')
    
    print("✅ Login completed successfully.")

async def fetch_projected_minutes(page, url: str) -> pd.DataFrame:
    await page.goto(url)
    pre = await page.text_content("body > pre")
    return pd.read_json(StringIO(pre))

@task
def get_projected_minutes(team_list):
    print("Launching Playwright...")

    async def run():
        async with async_playwright() as p:
            browser = await p.chromium.launch() #headless=True
            context = await browser.new_context()
            page = await context.new_page()

            await login_rotowire(page)
            print("Logged into Rotowire successfully.")

            all_dfs = []
            for team in team_list:
                print(f"Fetching projected minutes for team: {team}")
                url = f"https://www.rotowire.com/wnba/ajax/get-projected-minutes.php?team={team}"
                df = await fetch_projected_minutes(page, url)
                all_dfs.append(df)

            await browser.close()
            combined_df = pd.concat(all_dfs, ignore_index=True)
            return combined_df.to_json(orient="records")

    return asyncio.run(run())