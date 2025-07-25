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
def usp_merge_reference_basketball(league_id: str):
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute("exec [dbo].[usp_merge_reference_basketball] ?", league_id)
        conn.commit()
        print("exec dbo.usp_merge_reference_basketball " + league_id + " executed successfully")