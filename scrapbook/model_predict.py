import json
import joblib
import pyodbc
import pandas as pd
from datetime import date

# Load trained multi-output model
model = joblib.load("models/wnba_model.joblib")
feature_cols = joblib.load("models/wnba_feature_columns.joblib")

# Connection string
conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:35.197.174.203,1433;"
    "Database=danieljsmith1510;"
    "Uid=dan;"
    "Pwd=Ernie2022;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)
conn = pyodbc.connect(conn_str)

# Load today’s game data
query = f"""
select * from modelling.player_performance_predict where PERSON_ID is not null
"""
df_today = pd.read_sql(query, conn)

# Keep metadata for output
player_meta = df_today[['GAME_ID', 'PERSON_ID']].copy()

# Prepare features
X_today = df_today[feature_cols].fillna(0)

# Predict [POINTS, REBOUNDS, ASSISTS]
y_pred = model.predict(X_today)

# Create result DataFrame
predictions = pd.DataFrame(
    y_pred, 
    columns=['PRED_POINTS', 'PRED_REBOUNDS', 'PRED_ASSISTS']
)

# Join with player metadata
result = pd.concat([player_meta.reset_index(drop=True), predictions], axis=1)

with conn.cursor() as cursor:
    cursor.execute(
        "INSERT INTO [bronze].[extracts]([extract_type],[extract_data]) VALUES (?, ?)",
        'wnba-model-predictions',
        json.dumps(result.to_dict(orient='records'))
    )
conn.commit()