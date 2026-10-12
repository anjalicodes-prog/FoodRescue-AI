import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import os


# -----------------------------
# TRAINING DATA
# -----------------------------

data = {
    "expected_people": [
        100, 150, 200, 250, 300,
        350, 400, 450, 500, 600,
        120, 180, 220, 280, 320,
        380, 420, 480, 550, 700
    ],

    "food_prepared": [
        120, 180, 230, 300, 350,
        400, 450, 520, 580, 700,
        140, 210, 250, 330, 380,
        430, 480, 550, 650, 800
    ],

    "previous_surplus": [
        10, 20, 25, 30, 40,
        45, 50, 60, 70, 80,
        15, 20, 30, 35, 40,
        45, 55, 65, 75, 90
    ],

    "surplus": [
        15, 25, 30, 35, 45,
        50, 55, 65, 75, 90,
        20, 25, 35, 40, 45,
        50, 60, 70, 80, 100
    ]
}


# Convert data into DataFrame
df = pd.DataFrame(data)

print("Training model...")


# Input features
X = df[
    [
        "expected_people",
        "food_prepared",
        "previous_surplus"
    ]
]

# Target
y = df["surplus"]


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# Create Random Forest model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# Train
model.fit(X_train, y_train)


# Model score
score = model.score(X_test, y_test)

print("Model trained successfully!")
print("R2 Score:", score)


# -----------------------------
# SAVE MODEL
# -----------------------------

model_path = os.path.join(
    os.path.dirname(__file__),
    "food_surplus_model.pkl"
)

joblib.dump(model, model_path)

print()
print("MODEL SAVED SUCCESSFULLY!")
print("Location:", os.path.abspath(model_path))