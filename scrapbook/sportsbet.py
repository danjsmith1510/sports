from playwright.sync_api import sync_playwright
import time
import json

# Base URLs
COMPETITION_URL = "https://www.sportsbet.com.au/apigw/sportsbook-sports/Sportsbook/Sports/Competitions/29909"
MARKET_GROUP_IDS = [567, 568, 569]
MARKET_URL_TEMPLATE = "https://www.sportsbet.com.au/apigw/sportsbook-sports/Sportsbook/Sports/Events/{event_id}/MarketGroupings/{group_id}/Markets"

def fetch_json(page, url):
    response = page.request.get(url)
    if response.ok:
        return response.json()
    else:
        print(f"❌ Failed request: {url} - Status {response.status}")
        return None

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Get competition events
        competition_data = fetch_json(page, COMPETITION_URL)
        if not competition_data:
            print("❌ Could not fetch competition data.")
            return

        events = competition_data.get("events", [])
        print(f"🔍 Found {len(events)} total events.")

        all_results = []

        for event in events:
            event_id = event.get("id")
            event_name = event.get("name", "Unnamed Event")

            if not event_id:
                print(f"⚠️ Skipping event with missing ID: {event_name}")
                continue

            print(f"\n🎯 Processing event: {event_name} (ID: {event_id})")

            event_result = {"event_id": event_id, "event_name": event_name, "markets": {}}

            for group_id in MARKET_GROUP_IDS:
                url = MARKET_URL_TEMPLATE.format(event_id=event_id, group_id=group_id)
                print(f"📡 Fetching group {group_id} markets...")

                market_data = fetch_json(page, url)
                if market_data:
                    event_result["markets"][group_id] = market_data
                    print(f"✅ Success: group {group_id} markets fetched.")
                else:
                    print(f"❌ Failed: group {group_id} markets not fetched.")

                time.sleep(0.5)

            all_results.append(event_result)


        print(f"✅ Finished fetching {len(all_results)} event market sets.")
        context.close()
        browser.close()

        # Optional: Save results
        with open("sportsbet_markets.json", "w") as f:
            json.dump(all_results, f, indent=2)

        return all_results

if __name__ == "__main__":
    main()
