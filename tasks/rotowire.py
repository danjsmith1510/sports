import os, asyncio
from io import StringIO
import pandas as pd
from prefect import task
from playwright.async_api import async_playwright

async def login_rotowire(page):
    print("🔐 Starting login to Rotowire...")
    
    print("🌐 Navigating to login page...")
    await page.goto(os.environ.get("rotowire_login_url", ""))
    
    print("🧾 Filling in username...")
    await page.fill('input[placeholder="Enter username"]', os.environ.get("rotowire_username", ""))
    
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

async def fetch_projected_statistics(page, url: str) -> pd.DataFrame:
    await page.goto(url)
    pre = await page.text_content("body > pre")
    return pd.read_json(StringIO(pre))

@task(retries=5, retry_delay_seconds=5)
def get_projected_minutes(team_list, url):
    print("Launching Playwright...")

    async def run():
        async with async_playwright() as p:
            browser = await p.chromium.launch()  # headless=True
            context = await browser.new_context()
            page = await context.new_page()

            await login_rotowire(page)
            print("Logged into Rotowire successfully.")

            all_dfs = []
            for team in team_list:
                print(f"Fetching projected minutes for team: {team}")
                team_url = url + team
                df = await fetch_projected_minutes(page, team_url)
                all_dfs.append(df)
                await asyncio.sleep(2)

            await browser.close()
            combined_df = pd.concat(all_dfs, ignore_index=True)
            return combined_df.to_json(orient="records")
        
    return asyncio.run(run())

@task
def get_projected_statistics(current_date_est, url):
    print("Launching Playwright...")

    async def run():
        async with async_playwright() as p:
            browser = await p.chromium.launch()  # headless=True
            context = await browser.new_context()
            page = await context.new_page()

            await login_rotowire(page)
            print("Logged into Rotowire successfully.")

            print(f"Fetching projected statistics for todays games")
            full_url = url + current_date_est
            print (full_url)
            df = await fetch_projected_statistics(page, full_url)
            await browser.close()
            return df.to_json(orient="records")
        
    return asyncio.run(run())