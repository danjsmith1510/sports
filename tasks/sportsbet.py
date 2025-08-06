import json
import time
from prefect import task, flow
from playwright.sync_api import sync_playwright

@task
def run_browser_session(competition_url: str, group_ids: str, market_url_template: str):
    print("🚀 Launching Playwright browser...")
    group_ids = [team.strip() for team in group_ids.split(",")]
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Fetch competition JSON
        response = page.request.get(competition_url)
        if not response.ok:
            print(f"❌ Failed to fetch competition URL: {competition_url}")
            return []

        data = response.json()
        events = data.get("events", [])
        print(f"🔍 Found {len(events)} events.")

        for event in events:
            event_id = event.get("id")
            event_name = event.get("name", "Unnamed Event")
            startTime = event.get("startTime")
            if not event_id:
                print(f"⚠️ Skipping event with missing ID: {event_name}")
                continue

            print(f"\n🎯 Processing event: {event_name} (ID: {event_id})")
            event_result = {
                "event_id": event_id, 
                "event_name": event_name, 
                "startTime": startTime, 
                "markets": {}
            }

            for group_id in group_ids:
                url = market_url_template.format(event_id=event_id, group_id=group_id)
                print(f"📡 Fetching group {group_id} markets...")
                market_response = page.request.get(url)

                if market_response.ok:
                    market_data = market_response.json()
                    event_result["markets"][group_id] = market_data
                    print(f"✅ Success: group {group_id} markets fetched.")
                else:
                    print(f"❌ Failed: group {group_id} markets not fetched.")

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
