import pandas as pd
import os, pyodbc
from dotenv import load_dotenv
from prefect import task

load_dotenv(verbose=True, override=True)

conn_str = os.environ.get("conn_str_sports")
if not conn_str:
    raise ValueError("Missing 'conn_str_sports' in environment variables.")

@task(retries=5, retry_delay_seconds=10)
def insert_bronze_extracts(extract_type: str, json_str: str):
    with pyodbc.connect(conn_str, timeout=180) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO [bronze].[extracts]([extract_type],[extract_data]) VALUES (?, ?)",
                extract_type,
                json_str
            )
        conn.commit()
        print(f"INSERT INTO [bronze].[extracts] - {extract_type} executed successfully ")

@task(retries=5, retry_delay_seconds=5)
def usp_batch_load_stats(league_id: str, current_season: str = None):
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute("exec [dbo].[usp_batch_load_stats] ?, ?", league_id, current_season)
        conn.commit()
        print("exec dbo.usp_batch_load_stats " + league_id + " executed successfully")

@task(retries=5, retry_delay_seconds=5)
def usp_batch_load_projections(league_id: str, current_season: str = None, current_date_est: str = None):
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute("exec [dbo].[usp_batch_load_projections] ?, ?, ?", league_id, current_season, current_date_est)
        conn.commit()
        print("exec dbo.usp_batch_load_projections " + league_id + " executed successfully")

@task(retries=5, retry_delay_seconds=5)
def select_player_performance_predict(league_id: str, current_date_est: str = None):
    query = f"""
    SELECT * 
    FROM modelling.player_performance_predict
    WHERE PERSON_ID IS NOT NULL AND league_id = ? AND game_date_est = ?
    """
    with pyodbc.connect(conn_str, timeout=180) as conn:
        df_today = pd.read_sql(query, conn, params=[league_id, current_date_est])
    return df_today

@task(retries=5, retry_delay_seconds=5)
def usp_load_silver_predicted_player_performance(league_id: str):
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute("exec [dbo].[usp_load_silver_predicted_player_performance] ?", league_id)
        conn.commit()
        print("exec dbo.usp_load_silver_predicted_player_performance " + league_id + " executed successfully")

@task(retries=5, retry_delay_seconds=5)
def usp_load_silver_odds(league_id: str):
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute("exec [dbo].[usp_load_silver_odds] ?", league_id)
        conn.commit()
        print("exec dbo.usp_load_silver_odds " + league_id + " executed successfully")