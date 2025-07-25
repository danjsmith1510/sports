from io import StringIO
import os
import time
import pandas as pd
from prefect import task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def login_rotowire(driver):
    """Logs into Rotowire using credentials from environment variables."""
    driver.get("https://www.rotowire.com/subscribe/login/")
    time.sleep(10) 

    userNameElement = driver.find_element(By.XPATH, '//input[@placeholder="Enter username or email"]')
    userNameElement.send_keys(os.environ.get("rotowire_username", ""))

    passwordElement = driver.find_element(By.XPATH, '//input[@placeholder="Enter your password"]')
    passwordElement.send_keys(os.environ.get("rotowire_password", ""))

    time.sleep(2)

    loginButton = driver.find_element(By.XPATH, '//button[normalize-space(text())="Login"]')
    loginButton.click()

    time.sleep(5)  

def fetch_projected_minutes(driver, url: str) -> pd.DataFrame:
    driver.get(url)
    time.sleep(3)
    response_text = driver.find_element(By.XPATH, "/html/body/pre").text
    return pd.read_json(StringIO(response_text))

@task
def get_projected_minutes(team_list):

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--no-sandbox")  # Required for Docker
    chrome_options.add_argument("--disable-dev-shm-usage")  # Avoid limited /dev/shm size
    chrome_options.add_argument("--disable-gpu")  # Optional but helpful
    chrome_options.add_argument("--remote-debugging-port=9222")  # Prevent DevToolsActivePort error
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    login_rotowire(driver)
    
    all_dfs = []
    for team in team_list:
        url = f"https://www.rotowire.com/wnba/ajax/get-projected-minutes.php?team={team}"
        print (url)
        df = fetch_projected_minutes(driver, url)
        all_dfs.append(df)
    driver.quit()

    combined_df = pd.concat(all_dfs, ignore_index=True)

    return combined_df.to_json(orient="records")