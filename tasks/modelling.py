import json
import joblib
import pandas as pd
from prefect import task
from tasks.database import select_player_performance_predict

@task(retries=5, retry_delay_seconds=10)
def get_daily_games_to_predict(league_id, current_date_est) -> dict:
    games_to_predict = select_player_performance_predict(league_id, current_date_est)
    return games_to_predict

@task(retries=5, retry_delay_seconds=10)
def generate_daily_predictions(league_id, current_date_est) -> dict:
    # Load trained multi-output model
    model = joblib.load("models/wnba_model.joblib")
    feature_cols = joblib.load("models/wnba_feature_columns.joblib")
    #Get today's games to predict
    games_to_predict = get_daily_games_to_predict(league_id, current_date_est)
    if games_to_predict.empty:
        print("No games to predict for today.")
        return json.dumps([])
    games_to_predict = games_to_predict.drop(columns=['POINTS', 'REBOUNDS', 'ASSISTS'])
    # Prepare data for prediction
    player_meta = games_to_predict[['GAME_ID', 'TEAM_ID', 'PERSON_ID']].copy()
    X_today = games_to_predict[feature_cols].fillna(0)
    y_pred = model.predict(X_today)
    # Convert predictions to DataFrame
    predictions = pd.DataFrame(
        y_pred, 
        columns=['PRED_POINTS', 'PRED_REBOUNDS', 'PRED_ASSISTS']
    )
    # Join with player metadata
    predictions = pd.concat([player_meta.reset_index(drop=True), predictions], axis=1)
    return json.dumps(predictions.to_dict(orient='records'))