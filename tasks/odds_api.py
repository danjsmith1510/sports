import os, time, datetime, json, requests
from datetime import timezone 
from dotenv import load_dotenv
from prefect import task

load_dotenv(verbose=True, override=True)
oddsapi_apikey = os.environ.get("oddsapi_apikey")
oddsapi_url_wnba_get_events = os.environ.get("oddsapi_url_wnba_get_events")
oddsapi_url_wnba_get_event_markets = os.environ.get("oddsapi_url_wnba_get_event_markets")
oddsapi_url_nba_get_events = os.environ.get("oddsapi_url_nba_get_events")
oddsapi_url_nba_get_event_markets = os.environ.get("oddsapi_url_nba_get_event_markets")
oddsapi_regions = os.environ.get("oddsapi_regions")
oddsapi_markets = os.environ.get("oddsapi_markets")
now_utc = datetime.datetime.now(timezone.utc).isoformat()

@task(retries=5, retry_delay_seconds=10)
def get_nba_playerprops_oddsapi():
    """Get nba player prop odds from OddsAPI"""
    oddsList = []
    response = requests.get(oddsapi_url_nba_get_events + oddsapi_apikey)
    events = response.json()
    time.sleep(2)
    for event in events:
        timeDiff = datetime.datetime.fromisoformat(event['commence_time']) - datetime.datetime.fromisoformat(now_utc)
        if 0 < (timeDiff.total_seconds() // 3600) < 5:
            print(f"{event['id']} - {event['away_team']} @ {event['home_team']} - {event['commence_time']} is {str(timeDiff.total_seconds()//3600)} hours away --> fetching player props")
            markets_url = oddsapi_url_nba_get_event_markets + event['id'] + '/odds?apiKey=' + oddsapi_apikey + '&regions=' + oddsapi_regions + '&markets=' + oddsapi_markets
            markets = requests.get(markets_url)
            print(f"{event['id']} - {event['away_team']} @ {event['home_team']} - {event['commence_time']} --> got player props")
            oddsList.append(markets.json())
        else:
            print(f"{event['id']} - {event['away_team']} @ {event['home_team']} - {event['commence_time']} is {str(timeDiff.total_seconds()//3600)} hours away --> not fetching player props")
    return json.dumps(oddsList)

@task(retries=5, retry_delay_seconds=10)
def get_wnba_playerprops_oddsapi():
    """Get wnba player prop odds from OddsAPI"""
    oddsList = []
    response = requests.get(oddsapi_url_wnba_get_events + oddsapi_apikey)
    events = response.json()
    time.sleep(2)
    for event in events:
        timeDiff = datetime.datetime.fromisoformat(event['commence_time']) - datetime.datetime.fromisoformat(now_utc)
        hoursDiff = round(timeDiff.total_seconds() / 3600, 2)
        if 0 < hoursDiff < 5: 
            print(f"{event['id']} - {event['away_team']} @ {event['home_team']} - {event['commence_time']} is {str(hoursDiff)} hours away --> fetching player props")
            markets_url = oddsapi_url_wnba_get_event_markets + event['id'] + '/odds?apiKey=' + oddsapi_apikey + '&regions=' + oddsapi_regions + '&markets=' + oddsapi_markets
            markets = requests.get(markets_url)
            print(f"{event['id']} - {event['away_team']} @ {event['home_team']} - {event['commence_time']} --> got player props")
            oddsList.append(markets.json())
        else:
            print(f"{event['id']} - {event['away_team']} @ {event['home_team']} - {event['commence_time']} is {str(hoursDiff)} hours away --> not fetching player props")
    return json.dumps(oddsList)