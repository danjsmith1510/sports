import json, os
from dotenv import load_dotenv
from prefect import flow
from tasks.common.data_loading import insert_bronze_extracts
from tasks.rotowire import get_projected_minutes

load_dotenv(verbose=True, override=True)
league_active_nba = os.environ.get("league_active_nba")
league_active_wnba = os.environ.get("league_active_wnba")
teams_nba = os.environ.get("teams_nba")
teams_wnba = os.environ.get("teams_wnba")
nba_teams = [team.strip() for team in teams_nba.split(",")]
wnba_teams = [team.strip() for team in teams_wnba.split(",")]

@flow(log_prints=True)
def rotowire_flow() -> str:

    if (league_active_nba == "False"):
        print("NBA league is not active, skipping projected minutes extraction")
    else:
        projected_minutes_list_nba = get_projected_minutes(nba_teams)
        print(f"Got projected minutes for {len(wnba_teams)} nba teams")  
        insert_bronze_extracts("projected-mins-nba", json.dumps(projected_minutes_list_nba))

    if (league_active_wnba == "False"):
        print("WNBA league is not active, skipping projected minutes extraction")
    else:
        projected_minutes_list_wnba = get_projected_minutes(wnba_teams)
        print(f"Got projected minutes for {len(wnba_teams)} wnba teams")  
        insert_bronze_extracts("projected-mins-wnba", projected_minutes_list_wnba)

    return "Rotowire flow completed successfully"

if __name__ == "__main__":
    rotowire_flow()