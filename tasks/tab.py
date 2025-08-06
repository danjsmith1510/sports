import os
import json
from prefect import task, flow
from playwright.sync_api import sync_playwright

@task
def get_headless_setting():
    return os.environ.get("headless", "true").lower() == "true"

@task
def fetch_tab_json(headless: bool, url: str):
    print(f"🚀 Launching browser (headless={headless})")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        ))
        page = context.new_page()

        print("🌐 Navigating to https://www.tab.com.au to set browser origin...")
        page.goto("https://www.tab.com.au", timeout=60000)

        print("📡 Fetching API JSON from inside browser context...")
        json_data = page.evaluate(f"""
            () => fetch("{url}")
                .then(res => {{
                    if (!res.ok) throw new Error("Fetch failed: " + res.status);
                    return res.json();
                }})
        """)
        browser.close()
        return json_data

@task
def save_json(data, output_file):
    print("💾 Saving JSON...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Done. Saved to {output_file}")

@flow
def tab_flow(URL):
    headless = get_headless_setting()
    json_data = fetch_tab_json(headless, URL)
    return (json.dumps(json_data))

if __name__ == "__main__":
    tab_flow()