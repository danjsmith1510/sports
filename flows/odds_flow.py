import os
from dotenv import load_dotenv
from prefect import flow
from tasks.database import insert_bronze_extracts, usp_load_silver_odds
from tasks.odds_api import get_nba_playerprops_oddsapi, get_wnba_playerprops_oddsapi
from tasks.sportsbet import sportsbet_flow
from tasks.tab import tab_flow

load_dotenv(verbose=True, override=True)
league_active_nba = os.environ.get("league_active_nba")
league_active_wnba = os.environ.get("league_active_wnba")
internal_league_id_nba = os.environ.get("internal_league_id_nba")
internal_league_id_wnba = os.environ.get("internal_league_id_wnba")
sportsbet_competition_url_wnba = os.environ.get("sportsbet_competition_url_wnba")
sportsbet_market_group_ids_wnba = os.environ.get("sportsbet_market_group_ids_wnba")
sportsbet_market_url_template_wnba = os.environ.get("sportsbet_market_url_template_wnba")
tab_url_wnba = os.environ.get("tab_url_wnba")

@flow(log_prints=True)
def odds_flow() -> str:
    """Flow to extract player prop odds from OddsAPI and load them into the database"""
    if (league_active_nba == "False"):
        print("NBA league is not active, skipping player prop odds extraction from the odds api")
    else:
        playerprop_odds = get_nba_playerprops_oddsapi()
        print(f"Got {len(playerprop_odds)} nba player prop odds")  
        insert_bronze_extracts("player-prop-odds-nba", playerprop_odds)
        usp_load_silver_odds(internal_league_id_nba)

    if (league_active_wnba == "False"):
        print("WNBA league is not active, skipping player prop odds extraction")
    else:
        playerprops_oddsapi = get_wnba_playerprops_oddsapi()
        print(f"Got wnba player prop odds from the odds api")  
        insert_bronze_extracts("player-prop-odds-wnba-oddsapi", playerprops_oddsapi)
        usp_load_silver_odds(internal_league_id_wnba, 'odds-api')

        playerprops_sportsbet = sportsbet_flow(sportsbet_competition_url_wnba, sportsbet_market_group_ids_wnba, sportsbet_market_url_template_wnba)
        print(f"Got wnba player prop odds from sportsbet") 
        insert_bronze_extracts("player-prop-odds-wnba-sportsbet", playerprops_sportsbet)
        usp_load_silver_odds(internal_league_id_wnba, 'sportsbet')

        # playerprops_tab = tab_flow(tab_url_wnba)
        # print(f"Got wnba player prop odds from tab") 
        # insert_bronze_extracts("player-prop-odds-wnba-tab", playerprops_tab)

    return "Odds flow flow completed successfully"

if __name__ == "__main__":
    odds_flow()