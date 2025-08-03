import os
from dotenv import load_dotenv
from prefect import flow
from tasks.database import insert_bronze_extracts, usp_load_silver_odds
from tasks.odds import get_nba_playerprop_odds, get_wnba_playerprop_odds

load_dotenv(verbose=True, override=True)
league_active_nba = os.environ.get("league_active_nba")
league_active_wnba = os.environ.get("league_active_wnba")
internal_league_id_nba = os.environ.get("internal_league_id_nba")
internal_league_id_wnba = os.environ.get("internal_league_id_wnba")

@flow(log_prints=True)
def odds_flow() -> str:
    """Flow to extract player prop odds from OddsAPI and load them into the database"""
    if (league_active_nba == "False"):
        print("NBA league is not active, skipping player prop odds extraction")
    else:
        playerprop_odds = get_nba_playerprop_odds()
        print(f"Got {len(playerprop_odds)} nba player prop odds")  
        insert_bronze_extracts("player-prop-odds-nba", playerprop_odds)
        usp_load_silver_odds(internal_league_id_nba)

    if (league_active_wnba == "False"):
        print("WNBA league is not active, skipping player prop odds extraction")
    else:
        playerprop_odds = get_wnba_playerprop_odds()
        print(f"Got {len(playerprop_odds)} wnba player prop odds")  
        insert_bronze_extracts("player-prop-odds-wnba", playerprop_odds)
        usp_load_silver_odds(internal_league_id_wnba)

    return "projections_flow flow completed successfully"

if __name__ == "__main__":
    odds_flow()