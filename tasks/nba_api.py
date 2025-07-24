import datetime as dt, pytz, time
from prefect import task
from nba_api.stats.endpoints import playerindex, scoreboardv2, boxscoretraditionalv3, BoxScoreAdvancedV2
from nba_api.stats.static.teams import get_teams, get_wnba_teams

@task
def get_players(league_id, season) -> dict:
    players = playerindex.PlayerIndex(league_id, season)
    player_dict = players.get_normalized_dict()['PlayerIndex']
    return player_dict

@task
def get_teams_nba():
    nba_teams =  get_teams()
    return nba_teams

@task
def get_teams_wnba():
    wnba_teams =  get_wnba_teams()
    return wnba_teams

@task
def get_date_ranges():
    today_et = dt.datetime.today().astimezone(pytz.timezone('US/Eastern')).date()
    date_range_dict = {}
    date_range_dict['today_et'] = today_et
    date_range_dict['schedule_start_date'] = today_et - dt.timedelta(days=1)
    date_range_dict['schedule_end_date'] = today_et + dt.timedelta(days=7)
    date_range_dict['boxscore_start_date'] = today_et - dt.timedelta(days=2)
    date_range_dict['boxscore_end_date'] = today_et
    return date_range_dict

@task
def get_schedule(schedule_start_date, schedule_end_date, league_id):
    game_list=[]
    current_date = schedule_start_date
    while current_date <= schedule_end_date:
        day_scoreboard = scoreboardv2.ScoreboardV2(game_date=current_date.strftime('%Y-%m-%d'), league_id=league_id, timeout=120) 
        game_list_dict = day_scoreboard.get_normalized_dict()['GameHeader']
        print ("Got schedule for league id " + league_id + " -  date " + current_date.strftime('%Y-%m-%d') + ': ' + str(len(game_list_dict)) + " games")
        if (len(game_list_dict) > 0):
            for game in game_list_dict:
                game_list.append(game)
        time.sleep(1.5)
        current_date += dt.timedelta(days=1)
    return game_list

@task
def get_traditional_box_scores(box_scores_to_get):
    box_score_list = []
    gameCounter = 1
    gameCount = len(box_scores_to_get)
    for game in box_scores_to_get:
        print ('Getting traditional box score ' + str(gameCounter) + ' of ' + str(gameCount))
        status = game['GAME_STATUS_TEXT']
        if (status == 'Final'):
            try:
                box_score_raw = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game['GAME_ID'], timeout=120)
                box_score = box_score_raw.get_dict()['boxScoreTraditional']
                box_score_list.append(box_score)
                time.sleep(2.5)
            except AttributeError:
                continue 
        gameCounter += 1
    return box_score_list

@task
def get_advanced_box_scores(box_scores_to_get):
    box_score_list_team = []
    box_score_list_player = []
    gameCounter = 1
    gameCount = len(box_scores_to_get)
    for game in box_scores_to_get:
        print ('Getting advanced box score ' + str(gameCounter) + ' of ' + str(gameCount))
        status = game['GAME_STATUS_TEXT']
        if (status == 'Final'):
            try:
                box_score_raw = BoxScoreAdvancedV2(game_id=game['GAME_ID'], timeout=120)
                box_score_team = box_score_raw.get_normalized_dict()['TeamStats']
                box_score_player = box_score_raw.get_normalized_dict()['PlayerStats']
                box_score_list_team.append(box_score_team)
                box_score_list_player.append(box_score_player)
                time.sleep(1.5)
            except AttributeError:
                continue 
        gameCounter += 1
    return [box_score_list_team, box_score_list_player]