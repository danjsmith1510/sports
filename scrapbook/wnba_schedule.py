import time
import pytz
import datetime as dt
from nba_api.stats.endpoints import scoreboardv2

league_id = '10'  # WNBA
local_tz = pytz.timezone('Australia/Sydney')
et_tz = pytz.timezone('US/Eastern')
today_et = dt.datetime.today().astimezone(pytz.timezone('US/Eastern')).date()

print(f"Today in ET: {today_et}")

schedule_start_date = dt.date(year=2025, month=5, day=15)
# schedule_end_date = dt.date(year=2025, month=9, day=12)
schedule_end_date = dt.date(year=2025, month=5, day=16)

print (f"Schedule start date: {schedule_start_date}, end date: {schedule_end_date}")

"""Get all nba or wnba games"""
game_list=[]
current_date = schedule_start_date
while current_date <= schedule_end_date:
    day_scoreboard = scoreboardv2.ScoreboardV2(game_date=current_date.strftime('%Y-%m-%d'), league_id=league_id, timeout=100) 
    game_list_dict = day_scoreboard.get_normalized_dict()['GameHeader']
    print (current_date.strftime('%Y-%m-%d') + ': ' + str(len(game_list_dict)))
    if (len(game_list_dict) > 0):
        for game in game_list_dict:
            game['league_id'] = league_id
            game_list.append(game)
    time.sleep(2.5)
    current_date += dt.timedelta(days=1)
print(f"Total games found: {len(game_list)}")
print (game_list[0])