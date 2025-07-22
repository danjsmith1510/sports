import json, os
from dotenv import load_dotenv
from prefect import flow
from tasks.common.data_loading import usp_merge_reference_basketball, insert_bronze_extracts
from tasks.nba_api import get_traditional_box_scores, get_date_ranges, get_players, get_schedule, get_teams_nba, get_teams_wnba, get_advanced_box_scores

load_dotenv()
external_league_id_nba = os.environ.get("external_league_id_nba")
external_league_id_wnba = os.environ.get("external_league_id_wnba")
internal_league_id_nba = os.environ.get("internal_league_id_nba")
internal_league_id_wnba = os.environ.get("internal_league_id_wnba")
current_season_nba = os.environ.get("current_season_nba")
current_season_wnba = os.environ.get("current_season_wnba")
league_active_nba = os.environ.get("league_active_nba")
league_active_wnba = os.environ.get("league_active_wnba")
current_combined_schedule_end_date = os.environ.get("current_combined_schedule_end_date")

@flow(log_prints=True)
def nba_api_flow() -> str:

    date_ranges = get_date_ranges(current_combined_schedule_end_date)    
    for key, value in date_ranges.items():
        print(f"{key}: {value}")

    if (league_active_nba == "False"):
        print("NBA league is not active, skipping NBA data extraction")
    else:
        nba_teams = get_teams_nba()
        print(f"Got {len(nba_teams)} nba teams")  
        insert_bronze_extracts("teams-nba", json.dumps(nba_teams))

        nba_players = get_players(external_league_id_nba, current_season_nba)
        print(f"Got {len(nba_players)} nba players")
        insert_bronze_extracts("players-nba", json.dumps(nba_players))

        nba_schedule = get_schedule(date_ranges['schedule_start_date'], date_ranges['schedule_end_date'], external_league_id_nba)
        print(f"Got {len(nba_schedule)} nba games")  
        insert_bronze_extracts("schedule-nba", json.dumps(nba_schedule))

        usp_merge_reference_basketball(internal_league_id_nba)

    if (league_active_wnba == "False"):
        print("WNBA league is not active, skipping WNBA data extraction")
    else:
        wnba_teams = get_teams_wnba()
        print(f"Got {len(wnba_teams)} wnba teams")  
        insert_bronze_extracts("teams-wnba", json.dumps(wnba_teams))

        wnba_players = get_players(external_league_id_wnba, current_season_wnba)
        print(f"Got {len(wnba_players)} wnba players")  
        insert_bronze_extracts("players-wnba", json.dumps(wnba_players))

        # wnba_schedule = get_schedule(date_ranges['schedule_start_date'], date_ranges['schedule_end_date'], external_league_id_wnba)
        # print(f"Got {len(wnba_schedule)} wnba games")  
        # insert_bronze_extracts("schedule-wnba", json.dumps(wnba_schedule))

        wnba_box_scores_to_get = get_schedule(date_ranges['boxscore_start_date'], date_ranges['boxscore_end_date'], external_league_id_wnba)

        traditional_box_score_list = get_traditional_box_scores(wnba_box_scores_to_get)
        print(f"Got {len(traditional_box_score_list)} traditional wnba box scores")  
        insert_bronze_extracts("boxscore-wnba", json.dumps(traditional_box_score_list))

        advanced_box_score_list = get_advanced_box_scores(wnba_box_scores_to_get)
        print(f"Got {len(advanced_box_score_list)} advanced wnba box scores")  
        insert_bronze_extracts("adv-team-boxscore-wnba", json.dumps(advanced_box_score_list[0]))
        insert_bronze_extracts("adv-player-boxscore-wnba", json.dumps(advanced_box_score_list[1]))

        usp_merge_reference_basketball(internal_league_id_wnba)

    return "NBA_API Flow completed successfully"

if __name__ == "__main__":
    nba_api_flow.serve(name="nba_api_flow")