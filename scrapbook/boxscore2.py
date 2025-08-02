import json, os, time, random
import pytz, datetime as dt
import pyodbc
import traceback
import requests
from dotenv import load_dotenv
from nba_api.stats.endpoints import boxscoretraditionalv3, scoreboardv2, BoxScoreAdvancedV2

# season	PRE_SEASON_START	PLAYOFFS_END
# 2022	2022-09-30	2023-06-12
# 2023	2023-10-05	2024-06-17
# 2024	2024-10-04	2025-06-22

# --- Date setup ---
def xget_date_ranges():
    date_range_dict = {}
    date_range_dict['today_et'] = dt.datetime.today().astimezone(pytz.timezone('US/Eastern')).date()
    date_range_dict['boxscore_start_date'] = dt.date(year=2023, month=1, day=1)
    date_range_dict['boxscore_end_date'] = dt.date(year=2023, month=6, day= 13) 
    return date_range_dict

# --- Load environment variables ---
load_dotenv(verbose=True, override=True)
conn_str = os.environ.get("conn_str_sports")
if not conn_str:
    raise ValueError("Missing 'conn_str_sports' in environment variables.")

# --- Retry wrapper for unstable requests ---
def safe_nba_api_call(func, *args, max_retries=3, delay_range=(3.5, 6.0), **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1}/{max_retries} failed: {e}")
            traceback.print_exc()
            if attempt < max_retries - 1:
                time.sleep(random.uniform(*delay_range))
            else:
                raise

# --- Get games for the day ---
def get_schedule_nba(game_date):
    game_list = []
    league_id = "00"
    print(f"Requesting NBA schedule for {game_date}...")
    day_scoreboard = safe_nba_api_call(scoreboardv2.ScoreboardV2, game_date=game_date.strftime('%Y-%m-%d'), league_id=league_id, timeout=180)
    game_list_dict = day_scoreboard.get_normalized_dict()['GameHeader']
    print(f"Found {len(game_list_dict)} games for {game_date}")
    for game in game_list_dict:
        game['league_id'] = league_id
        game_list.append(game)
    time.sleep(random.uniform(3.5, 6.0))
    return game_list

# --- DB insert ---
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

# --- Stored procedures ---
def usp_load_silver_boxscore_traditional(league_id):
    print(f"Executing: usp_load_silver_boxscore_traditional {league_id}")
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute("exec [dbo].[usp_load_silver_boxscore_traditional] ?", league_id)
        conn.commit()
    print("✅ Stored procedure completed")

def usp_load_silver_boxscore_advanced_team(league_id):
    print(f"Executing: usp_load_silver_boxscore_advanced_team {league_id}")
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute("exec [dbo].[usp_load_silver_boxscore_advanced_team] ?", league_id)
        conn.commit()
    print("✅ Stored procedure completed")

def usp_load_silver_boxscore_advanced_player(league_id):
    print(f"Executing: usp_load_silver_boxscore_advanced_player {league_id}")
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute("exec [dbo].[usp_load_silver_boxscore_advanced_player] ?", league_id)
        conn.commit()
    print("✅ Stored procedure completed")

# --- Main loop ---
date_ranges = xget_date_ranges()
boxscore_current_date = date_ranges['boxscore_start_date']
boxscore_end_date = date_ranges['boxscore_end_date']

print(f"\n📅 Starting boxscore extraction from {boxscore_current_date} to {boxscore_end_date}")

while boxscore_current_date <= boxscore_end_date:
    print(f"\n🗓️ Processing date: {boxscore_current_date}")
    game_list = get_schedule_nba(boxscore_current_date)

    box_score_traditional_list = []
    box_score_adv_team_list = []
    box_score_adv_player_list = []

    for idx, game in enumerate(game_list, start=1):
        game_id = game['GAME_ID']
        status = game['GAME_STATUS_TEXT']
        print(f"  🎮 Game {idx}/{len(game_list)} (ID: {game_id}), status: {status}")
        if status == 'Final':
            try:
                # Traditional box score
                print(f"    ⏳ Fetching traditional box score...")
                box_score_traditional_raw = safe_nba_api_call(boxscoretraditionalv3.BoxScoreTraditionalV3, game_id=game_id, timeout=180)
                box_score = box_score_traditional_raw.get_dict()['boxScoreTraditional']
                box_score_traditional_list.append(box_score)
                time.sleep(random.uniform(3.5, 6.0))

                # Advanced box score
                print(f"    ⏳ Fetching advanced box score...")
                box_score_adv_raw = safe_nba_api_call(BoxScoreAdvancedV2, game_id=game_id, timeout=180)
                box_score_adv_team = box_score_adv_raw.get_normalized_dict()['TeamStats']
                box_score_adv_player = box_score_adv_raw.get_normalized_dict()['PlayerStats']
                box_score_adv_team_list.append(box_score_adv_team)
                box_score_adv_player_list.append(box_score_adv_player)
                time.sleep(random.uniform(3.5, 6.0))

                print(f"    ✅ Box scores added.")

            except (AttributeError, requests.exceptions.RequestException) as e:
                print(f"    ❌ Skipped game {game_id} due to error: {e}")
                traceback.print_exc()
                continue
        else:
            print(f"    ⏭️ Skipping game {game_id} (not Final).")

    # Insert into DB
    print(f"\n💾 Inserting {len(box_score_traditional_list)} box scores for {boxscore_current_date}...")
    insert_bronze_extracts('boxscore-nba', json.dumps(box_score_traditional_list))
    insert_bronze_extracts('adv-team-boxscore-nba', json.dumps(box_score_adv_team_list))
    insert_bronze_extracts('adv-player-boxscore-nba', json.dumps(box_score_adv_player_list))

    # Stored procedures
    usp_load_silver_boxscore_traditional(1)
    time.sleep(2)
    usp_load_silver_boxscore_advanced_team(1)
    time.sleep(2)
    usp_load_silver_boxscore_advanced_player(1)

    boxscore_current_date += dt.timedelta(days=1)

print("\n✅ Boxscore extraction script completed successfully.")
