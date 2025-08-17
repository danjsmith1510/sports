import json
import os
import shutil
import time
from prefect import task, flow
from playwright.sync_api import sync_playwright


def detect_headless_mode() -> bool:
    """
    Detect whether to run Playwright in headless mode.
    - If DISPLAY is set or xvfb-run exists, run headful (False).
    - Otherwise, force headless (True).
    """
    if os.getenv("DISPLAY"):
        print("💻 DISPLAY found -> running headful mode")
        return False
    elif shutil.which("xvfb-run"):
        print("🖼️ xvfb-run found -> assume headful mode (run with xvfb-run)")
        return False
    else:
        print("⚠️ No DISPLAY or xvfb found -> falling back to headless mode")
        return True


@task(retries=5, retry_delay_seconds=10)
def run_browser_session(competition_url: str, group_ids: str, market_url_template: str):
    headless = detect_headless_mode()
    print(f"🚀 Launching Playwright browser (headless={headless})")

    group_ids = [team.strip() for team in group_ids.split(",")]
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            locale="en-AU",
            timezone_id="Australia/Sydney"
        )
        page = context.new_page()

        # Always visit homepage first to set cookies
        print("🌐 Navigating to Sportsbet homepage...")
        page.goto("https://www.sportsbet.com.au/", wait_until="domcontentloaded")
        time.sleep(2)

        # Navigate to the competition's root site (not API endpoint)
        print(f"🌐 Navigating to competition root: {competition_url.split('/apigw/')[0]}")
        page.goto(competition_url.split("/apigw/")[0], wait_until="domcontentloaded")
        time.sleep(2)

        # Make request with cookies + headers
        response = context.request.get(
            competition_url,
            headers={
                "Referer": "https://www.sportsbet.com.au/",
                "Origin": "https://www.sportsbet.com.au",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

        if not response.ok:
            print(f"❌ Failed to fetch competition URL: {competition_url} ({response.status})")
            return []

        data = response.json()
        events = data.get("events", [])
        print(f"🔍 Found {len(events)} events.")

        for event in events:
            event_id = event.get("id")
            event_name = event.get("name", "Unnamed Event")
            start_time = event.get("startTime")

            if not event_id:
                print(f"⚠️ Skipping event with missing ID: {event_name}")
                continue

            print(f"\n🎯 Processing event: {event_name} (ID: {event_id})")
            event_result = {
                "event_id": event_id,
                "event_name": event_name,
                "startTime": start_time,
                "markets": {}
            }

            for group_id in group_ids:
                url = market_url_template.format(event_id=event_id, group_id=group_id)
                print(f"📡 Fetching group {group_id} markets...")

                market_response = context.request.get(
                    url,
                    headers={
                        "Referer": "https://www.sportsbet.com.au/",
                        "Accept": "application/json",
                        "Accept-Language": "en-US,en;q=0.9",
                    }
                )

                if market_response.ok:
                    market_data = market_response.json()
                    event_result["markets"][group_id] = market_data
                    print(f"✅ Success: group {group_id} markets fetched.")
                else:
                    print(f"❌ Failed: group {group_id} markets not fetched. ({market_response.status})")

                time.sleep(0.5)

            all_results.append(event_result)

        context.close()
        browser.close()

    print(f"✅ Finished fetching {len(all_results)} event market sets.")
    return json.dumps(all_results)


@flow
def sportsbet_flow(COMPETITION_URL, MARKET_GROUP_IDS, MARKET_URL_TEMPLATE):
    return run_browser_session(COMPETITION_URL, MARKET_GROUP_IDS, MARKET_URL_TEMPLATE)


if __name__ == "__main__":
    sportsbet_flow()
