import joblib


# Load trained model
model = joblib.load("model/food_surplus_model.pkl")


# Example event data
expected_people = 500
food_prepared = 580
previous_surplus = 70


# Make prediction
prediction = model.predict([
    [
        expected_people,
        food_prepared,
        previous_surplus
    ]
])


print("--------------------------------")
print("       FOODRESCUE AI")
print("--------------------------------")
print("Expected People:", expected_people)
print("Food Prepared:", food_prepared)
print("Previous Surplus:", previous_surplus)
print()
print("Predicted Surplus:",
      round(prediction[0]),
      "meals")
print("--------------------------------")