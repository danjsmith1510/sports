from dotenv import load_dotenv
import time, requests, os, pyodbc, datetime, json
from datetime import timezone 

# --- Load environment variables ---
load_dotenv(verbose=True, override=True)
conn_str = os.environ.get("conn_str_sports")
if not conn_str:
    raise ValueError("Missing 'conn_str_sports' in environment variables.")

oddsapi_apikey = '68ff94a0bce8551f98d0b776275cbe2d'
oddsapi_url_get_events = 'https://api.the-odds-api.com/v4/sports/basketball_wnba/events?apiKey=' + oddsapi_apikey
oddsapi_url_get_event_markets = 'https://api.the-odds-api.com/v4/sports/basketball_wnba/events/'
oddsapi_regions = 'au,us'
oddsapi_markets = 'player_points,player_rebounds,player_assists'

now_utc = datetime.datetime.now(timezone.utc).isoformat()

def get_nba_playerprop_odds():
    """Get all nba events from odds api"""
    oddsList = []
    response = requests.get(oddsapi_url_get_events)
    events = response.json()
    time.sleep(2)
    for event in events:
        timeDiff = datetime.datetime.fromisoformat(event['commence_time']) - datetime.datetime.fromisoformat(now_utc)
        if (timeDiff.total_seconds()//3600) < 24: #change to 4? day before season
            print(f"{event['id']} - {event['away_team']} @ {event['home_team']} - {event['commence_time']} is {str(timeDiff.total_seconds()//3600)} hours away --> fetching player props")
            markets_url = oddsapi_url_get_event_markets + event['id'] + '/odds?apiKey=' + oddsapi_apikey + '&regions=' + oddsapi_regions + '&markets=' + oddsapi_markets
            markets = requests.get(markets_url)
            print(f"{event['id']} - {event['away_team']} @ {event['home_team']} - {event['commence_time']} --> got player props from {str(len(markets.json()))} bookies")
            oddsList.append(markets.json())
        else:
            print(f"{event['id']} - {event['away_team']} @ {event['home_team']} - {event['commence_time']} is {str(timeDiff.total_seconds()//3600)} hours away --> not fetching player props")
        # time.sleep(1.5)
    return (oddsList)

def insert_bronze_extracts(extract_type: str, json_str: str):
    with pyodbc.connect(conn_str, timeout=180) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO [bronze].[extracts]([extract_type],[extract_data]) VALUES (?, ?)",
                extract_type,
                json_str
            )
        conn.commit()
    print(f"✅ INSERTED: {extract_type} ({len(json.loads(json_str))} records)")

odds_list = get_nba_playerprop_odds()
insert_bronze_extracts('player-prop-odds-wnba', json.dumps(odds_list))