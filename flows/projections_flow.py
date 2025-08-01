import json, os
from dotenv import load_dotenv
from prefect import flow
from tasks.database import insert_bronze_extracts, usp_batch_load_projections, usp_load_silver_predicted_player_performance
from tasks.modelling import generate_daily_predictions
from tasks.utils import get_date_ranges
from tasks.rotowire import get_projected_minutes, get_projected_statistics

load_dotenv(verbose=True, override=True)
league_active_nba = os.environ.get("league_active_nba")
league_active_wnba = os.environ.get("league_active_wnba")
teams_nba = os.environ.get("teams_nba")
teams_wnba = os.environ.get("teams_wnba")
nba_teams = [team.strip() for team in teams_nba.split(",")]
wnba_teams = [team.strip() for team in teams_wnba.split(",")]
rotowire_url_mins_wnba = os.environ.get("rotowire_url_mins_wnba")
rotowire_url_mins_nba = os.environ.get("rotowire_url_mins_nba")
rotowire_url_stats_wnba = os.environ.get("rotowire_url_stats_wnba")
rotowire_url_stats_nba = os.environ.get("rotowire_url_stats_nba")
internal_league_id_nba = os.environ.get("internal_league_id_nba")
internal_league_id_wnba = os.environ.get("internal_league_id_wnba")
current_season_nba = os.environ.get("current_season_nba")
current_season_wnba = os.environ.get("current_season_wnba")

@flow(log_prints=True)
def projections_flow() -> str:

    date_ranges = get_date_ranges()
    current_date_est = date_ranges['today_et'].strftime('%Y-%m-%d')

    if (league_active_nba == "False"):
        print("NBA league is not active, skipping projected minutes extraction")
    else:
        projected_minutes_list_nba = get_projected_minutes(nba_teams, rotowire_url_mins_nba)
        print(f"Got projected minutes for {len(wnba_teams)} nba teams")  
        insert_bronze_extracts("projected-mins-nba", json.dumps(projected_minutes_list_nba))

        projected_statistics_list_nba = get_projected_statistics(current_date_est, rotowire_url_stats_nba)
        print(f"Got projected statistics - todays games - {len(projected_statistics_list_nba)} nba players")  
        insert_bronze_extracts("projected-stats-nba", projected_statistics_list_nba)

        usp_batch_load_projections(internal_league_id_nba, current_season_nba, current_date_est)

        predicted_daily_performance = generate_daily_predictions(league_id=internal_league_id_nba, current_date_est=current_date_est)
        print(f"Generated predicted performance for NNBA games on or after {current_date_est} - {len(predicted_daily_performance)} predictions")  
        insert_bronze_extracts("nba-model-predictions", predicted_daily_performance)

        usp_load_silver_predicted_player_performance(internal_league_id_nba)

    if (league_active_wnba == "False"):
        print("WNBA league is not active, skipping projected minutes extraction")
    else:
        projected_minutes_list_wnba = get_projected_minutes(wnba_teams, rotowire_url_mins_wnba)
        print(f"Got projected minutes for {len(wnba_teams)} wnba teams")  
        insert_bronze_extracts("projected-mins-wnba", projected_minutes_list_wnba)

        projected_statistics_list_wnba = get_projected_statistics(current_date_est, rotowire_url_stats_wnba)
        print(f"Got projected statistics - todays games - {len(projected_statistics_list_wnba)} wnba players")  
        insert_bronze_extracts("projected-stats-wnba", projected_statistics_list_wnba)

        usp_batch_load_projections(internal_league_id_wnba, current_season_wnba, current_date_est)

        predicted_daily_performance = generate_daily_predictions(league_id=internal_league_id_wnba, current_date_est=current_date_est)
        print(f"Generated predicted performance for WNBA games on {current_date_est}")  
        insert_bronze_extracts("wnba-model-predictions", predicted_daily_performance)

        usp_load_silver_predicted_player_performance(internal_league_id_wnba)

    return "projections_flow flow completed successfully"

if __name__ == "__main__":
    projections_flow()