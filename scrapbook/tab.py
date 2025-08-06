import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import json

load_dotenv(verbose=True, override=True)
headless = os.environ.get("headless", "true").lower() == "true"
URL = "https://api.beta.tab.com.au/v1/tab-info-service/sports/Basketball/competitions/WNBA?jurisdiction=NSW"
OUTPUT_FILE = "wnba_tab_data.json"

def main():
    print(f"🚀 Launching browser (headless={headless})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        ))
        page = context.new_page()

        # 👇 CRITICAL: Must navigate to same-origin page first
        print("🌐 Navigating to https://www.tab.com.au to set browser origin...")
        page.goto("https://www.tab.com.au", timeout=60000)

        print("📡 Fetching API JSON from inside browser context...")
        json_data = page.evaluate(f"""
            () => fetch("{URL}")
                .then(res => {{
                    if (!res.ok) throw new Error("Fetch failed: " + res.status);
                    return res.json();
                }})
        """)

        print("💾 Saving JSON...")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        print(f"✅ Done. Saved to {OUTPUT_FILE}")
        browser.close()

if __name__ == "__main__":
    main()
