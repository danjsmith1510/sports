import json
import time, pytz
import datetime as dt
from nba_api.stats.endpoints import  boxscoretraditionalv3, scoreboardv2
from tasks.common.data_loading import insert_bronze_extracts

def xget_date_ranges():
    date_range_dict = {}
    date_range_dict['today_et'] = dt.datetime.today().astimezone(pytz.timezone('US/Eastern')).date()
    date_range_dict['boxscore_start_date'] = dt.date(year=2021, month=5, day=1)
    date_range_dict['boxscore_end_date'] = dt.date(year=2021, month=10, day=18) 
    return date_range_dict

def get_schedule_nba(schedule_start_date, schedule_end_date):
    league_id = "10"  # WNBA
    game_list=[]
    current_date = schedule_start_date
    while current_date <= schedule_end_date:
        day_scoreboard = scoreboardv2.ScoreboardV2(game_date=current_date.strftime('%Y-%m-%d'), league_id=league_id, timeout=180) 
        game_list_dict = day_scoreboard.get_normalized_dict()['GameHeader']
        print ("Got NBA schedule for date " + current_date.strftime('%Y-%m-%d') + ': ' + str(len(game_list_dict)) + " games")
        if (len(game_list_dict) > 0):
            for game in game_list_dict:
                game['league_id'] = league_id
                game_list.append(game)
        time.sleep(1.5)
        current_date += dt.timedelta(days=1)
    return game_list

date_ranges = xget_date_ranges()

game_list = get_schedule_nba(date_ranges['boxscore_start_date'], date_ranges['boxscore_end_date'])

box_score_list = []
gameCounter = 1
gameCount = len(game_list)
for game in game_list:
    print ('Getting box score ' + str(gameCounter) + ' of ' + str(gameCount))
    status = game['GAME_STATUS_TEXT']
    if (status == 'Final'):
        try:
            box_score_raw = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game['GAME_ID'], timeout=180)
            box_score = box_score_raw.get_dict()['boxScoreTraditional']
            box_score['league_id'] = 2
            box_score_list.append(box_score)
            time.sleep(1.5)
        except AttributeError:
            continue 
    gameCounter += 1

print (len(box_score_list), "box scores retrieved")
insert_bronze_extracts('boxscore-wnba', json.dumps(box_score_list))

# box_score_list = []
# for game in game_list:
#     try:
#         box_score_raw = BoxScoreAdvancedV2(game_id=game['GAME_ID'])
#         box_score = box_score_raw.get_normalized_dict()['TeamStats']
#         # box_score['league_id'] = league_id
#         box_score_list.append(box_score)
#         time.sleep(2.5)
#     except AttributeError:
#         continue 
# return box_score_list