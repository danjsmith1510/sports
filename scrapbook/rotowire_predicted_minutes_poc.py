import os
import time
import pandas as pd
import pyodbc
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Load environment variables from .env file
load_dotenv()

def fetch_projected_minutes(driver, url: str) -> pd.DataFrame:
    driver.get(url)
    time.sleep(3)
    response_text = driver.find_element(By.XPATH, "/html/body/pre").text
    return pd.read_json(response_text)

def insert_json_to_sql(conn_str: str, extract_type: str, json_str: str):
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO [bronze].[extracts]([extract_type],[extract_data]) VALUES (?, ?)",
                extract_type,
                json_str
            )
            conn.commit()

def login_rotowire(driver):
    """Logs into Rotowire using credentials from environment variables."""
    driver.get("https://www.rotowire.com/subscribe/login/")
    time.sleep(10)  # Wait for page to load

    userNameElement = driver.find_element(By.XPATH, '//input[@placeholder="Enter username or email"]')
    userNameElement.send_keys(os.environ.get("rotowire_username", ""))

    passwordElement = driver.find_element(By.XPATH, '//input[@placeholder="Enter your password"]')
    passwordElement.send_keys(os.environ.get("rotowire_password", ""))

    time.sleep(2)

    loginButton = driver.find_element(By.XPATH, '//button[normalize-space(text())="Login"]')
    loginButton.click()

    time.sleep(5)  # Wait for login to complete

def main():
    wnba_teams = os.environ.get("teams_wnba")
    if not wnba_teams:
        raise ValueError("Missing 'teams_wnba' in environment variables.")
    wnba_teams = [team.strip() for team in wnba_teams.split(",")]
    all_dfs = []

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Uncomment to run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Optional: for Windows

    driver = webdriver.Chrome(options=chrome_options)
    login_rotowire(driver)

    # Fetch projected minutes for each team
    for team in wnba_teams:
        url = f"https://www.rotowire.com/wnba/ajax/get-projected-minutes.php?team={team}"
        df = fetch_projected_minutes(driver, url)
        all_dfs.append(df)

    driver.quit()

    # Combine all dataframes and insert as JSON
    combined_df = pd.concat(all_dfs, ignore_index=True)
    json_str = combined_df.to_json(orient="records")
    conn_str = os.environ.get("conn_str_sports")
    if not conn_str:
        raise ValueError("Missing 'conn_str_sports' in environment variables.")
    insert_json_to_sql(conn_str, "pred-lineup-wnba", json_str)
    print("Data inserted successfully.")

if __name__ == "__main__":
    main()