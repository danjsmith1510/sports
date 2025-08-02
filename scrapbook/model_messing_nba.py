import pyodbc
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.feature_selection import SelectFromModel
import joblib

# Connection setup
conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:35.197.174.203,1433;"
    "Database=danieljsmith1510;"
    "Uid=dan;"
    "Pwd=Ernie2022;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=30;"
)
conn = pyodbc.connect(conn_str)

# Load data
query = """
SELECT *
FROM modelling.player_performance_train
WHERE POINTS IS NOT NULL AND REBOUNDS IS NOT NULL AND ASSISTS IS NOT NULL and league_id = 1
"""
df = pd.read_sql(query, conn)
print(f"✅ Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# Targets and input columns
target_cols = ['POINTS', 'REBOUNDS', 'ASSISTS']
id_cols = [
    'LEAGUE_ID', 'season', 'game_id', 'game_type', 'GAME_DATE_EST',
    'TEAM_ID', 'OPPONENT_TEAM_ID', 'PERSON_ID', 'PLAYER_SLUG'
]

# Candidate feature pool (based on domain knowledge and SHAP pruning)
feature_pool = df.columns.difference(id_cols + target_cols).tolist()

X = df[feature_pool].fillna(0)
y = df[target_cols]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)
print(f"📊 Train shape: {X_train.shape}, Test shape: {X_test.shape}")

# ---- 🔍 Feature selection per target ----
selected_feature_sets = {}
for col in target_cols:
    print(f"\n📌 Selecting features for {col}...")
    fs_model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6)
    fs_model.fit(X_train, y_train[col])
    selector = SelectFromModel(fs_model, threshold="median", prefit=True)
    features = X_train.columns[selector.get_support()]
    selected_feature_sets[col] = list(features)
    print(f"✅ {col}: selected {len(features)} features: {list(features)}")

# 🔗 Merge all features used in at least one model
combined_features = sorted(set(f for features in selected_feature_sets.values() for f in features))
print(f"\n🔗 Union of selected features: {len(combined_features)} total\n")

# Re-prepare X with selected features
X_train_sel = X_train[combined_features]
X_test_sel = X_test[combined_features]

# ---- 🧠 Train MultiOutput Model ----
print("🚀 Training final multi-output model...")
xgb = XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=6, n_jobs=-1)
model = MultiOutputRegressor(xgb)
model.fit(X_train_sel, y_train)
print("✅ Training complete.")

# ---- 📈 Evaluation ----
print("\n📊 Model Evaluation:")
y_pred = model.predict(X_test_sel)
for i, col in enumerate(target_cols):
    mae = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
    r2 = r2_score(y_test.iloc[:, i], y_pred[:, i])
    print(f"{col}: MAE = {mae:.2f}, R² = {r2:.3f}")

# Save the model
joblib.dump(model, 'models/nba_model.joblib')
joblib.dump(combined_features, 'models/nba_feature_columns.joblib')

print("✅ Model and feature columns saved.")
