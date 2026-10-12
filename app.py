from flask import Flask, render_template, request
import joblib
import sqlite3
import os

app = Flask(__name__)


# =========================================================
# LOAD ML MODEL
# =========================================================

model_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "model",
    "food_surplus_model.pkl"
)

model = joblib.load(model_path)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    base_dir = os.path.dirname(os.path.abspath(__file__))

    database_path = os.path.join(
        base_dir,
        "foodrescue.db"
    )

    connection = sqlite3.connect(database_path)

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

def create_tables():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS donations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            expected_people INTEGER,

            food_prepared INTEGER,

            previous_surplus INTEGER,

            predicted_surplus INTEGER,

            urgency_score INTEGER,

            urgency_level TEXT

        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS receivers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            capacity INTEGER,

            distance REAL

        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS matches (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            donation_id INTEGER,

            receiver_id INTEGER,

            match_score REAL,

            status TEXT

        )
    """)

    connection.commit()

    connection.close()


# =========================================================
# ADD NEW COLUMNS TO EXISTING DONATIONS TABLE
# =========================================================

def add_missing_columns():

    connection = get_db_connection()

    columns = connection.execute("""
        PRAGMA table_info(donations)
    """).fetchall()

    existing_columns = [
        column["name"]
        for column in columns
    ]

    # Food Type
    if "food_type" not in existing_columns:

        connection.execute("""
            ALTER TABLE donations
            ADD COLUMN food_type TEXT
        """)

    # Preparation Time
    if "preparation_time" not in existing_columns:

        connection.execute("""
            ALTER TABLE donations
            ADD COLUMN preparation_time INTEGER
        """)

    # Shelf Life
    if "shelf_life" not in existing_columns:

        connection.execute("""
            ALTER TABLE donations
            ADD COLUMN shelf_life INTEGER
        """)

    # Safety Status
    if "safety_status" not in existing_columns:

        connection.execute("""
            ALTER TABLE donations
            ADD COLUMN safety_status TEXT
        """)

    connection.commit()

    connection.close()


# =========================================================
# FOOD SHELF LIFE
# =========================================================

def get_shelf_life(food_type):

    shelf_life_data = {

        "Rice": 4,

        "Curry": 4,

        "Vegetables": 5,

        "Bread": 8,

        "Salad": 3,

        "Other": 4

    }

    return shelf_life_data.get(
        food_type,
        4
    )


# =========================================================
# ADD DEFAULT RECEIVERS
# =========================================================

def add_default_receivers():

    connection = get_db_connection()

    count = connection.execute("""
        SELECT COUNT(*)
        FROM receivers
    """).fetchone()[0]

    if count == 0:

        receivers = [

            (
                "Helping Hands NGO",
                100,
                2.0
            ),

            (
                "Food Bank",
                50,
                4.0
            ),

            (
                "Community Center",
                80,
                3.0
            ),

            (
                "Local Shelter",
                120,
                5.0
            )

        ]

        connection.executemany("""
            INSERT INTO receivers
            (
                name,
                capacity,
                distance
            )

            VALUES (?, ?, ?)
        """, receivers)

        connection.commit()

    connection.close()


# =========================================================
# INITIALIZE DATABASE
# =========================================================

create_tables()

add_missing_columns()

add_default_receivers()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# DONATE / PREDICT PAGE
# =========================================================

@app.route("/donate")
def donate():

    return render_template(
        "donate.html"
    )


# =========================================================
# AI SURPLUS PREDICTION + FOOD SAFETY
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():

    # -----------------------------------------------------
    # BASIC INPUTS
    # -----------------------------------------------------

    expected_people = int(
        request.form["expected_people"]
    )

    food_prepared = int(
        request.form["food_prepared"]
    )

    previous_surplus = int(
        request.form["previous_surplus"]
    )


    # -----------------------------------------------------
    # FOOD SAFETY INPUTS
    # -----------------------------------------------------

    food_type = request.form["food_type"]

    preparation_time = int(
        request.form["preparation_time"]
    )


    # -----------------------------------------------------
    # AI SURPLUS PREDICTION
    # -----------------------------------------------------

    prediction = model.predict([
        [
            expected_people,
            food_prepared,
            previous_surplus
        ]
    ])

    predicted_surplus = round(
        prediction[0]
    )


    # -----------------------------------------------------
    # GET SHELF LIFE
    # -----------------------------------------------------

    shelf_life = get_shelf_life(
        food_type
    )


    # -----------------------------------------------------
    # FOOD SAFETY STATUS
    # -----------------------------------------------------

    if preparation_time <= shelf_life * 0.5:

        safety_status = "Safe to Rescue"

    elif preparation_time < shelf_life:

        safety_status = "Rescue Soon"

    else:

        safety_status = "Safety Warning"


    # -----------------------------------------------------
    # URGENCY CALCULATION
    # -----------------------------------------------------

    # Safety warning gets highest priority

    if safety_status == "Safety Warning":

        urgency_score = 100

        urgency_level = "Critical"

    elif predicted_surplus >= 80:

        urgency_score = 90

        urgency_level = "Critical"

    elif predicted_surplus >= 50:

        urgency_score = 70

        urgency_level = "High"

    elif predicted_surplus >= 30:

        urgency_score = 50

        urgency_level = "Medium"

    else:

        urgency_score = 30

        urgency_level = "Low"


    # -----------------------------------------------------
    # SAVE DONATION
    # -----------------------------------------------------

    connection = get_db_connection()

    cursor = connection.execute("""
        INSERT INTO donations
        (
            expected_people,
            food_prepared,
            previous_surplus,
            predicted_surplus,
            urgency_score,
            urgency_level,
            food_type,
            preparation_time,
            shelf_life,
            safety_status
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        expected_people,

        food_prepared,

        previous_surplus,

        predicted_surplus,

        urgency_score,

        urgency_level,

        food_type,

        preparation_time,

        shelf_life,

        safety_status

    ))

    donation_id = cursor.lastrowid

    connection.commit()

    connection.close()


    # -----------------------------------------------------
    # SHOW RESULT
    # -----------------------------------------------------

    return render_template(

        "donate.html",

        prediction=predicted_surplus,

        urgency_score=urgency_score,

        urgency_level=urgency_level,

        expected_people=expected_people,

        food_prepared=food_prepared,

        previous_surplus=previous_surplus,

        donation_id=donation_id,

        food_type=food_type,

        preparation_time=preparation_time,

        shelf_life=shelf_life,

        safety_status=safety_status

    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    connection = get_db_connection()

    donations = connection.execute("""
        SELECT *
        FROM donations
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return render_template(

        "dashboard.html",

        donations=donations

    )


# =========================================================
# FIND BEST RECEIVER
# =========================================================

@app.route("/match/<int:donation_id>")
def match_receiver(donation_id):

    connection = get_db_connection()


    # -----------------------------------------------------
    # GET DONATION
    # -----------------------------------------------------

    donation = connection.execute("""
        SELECT *
        FROM donations
        WHERE id = ?
    """, (
        donation_id,
    )).fetchone()


    if donation is None:

        connection.close()

        return "Donation not found."


    predicted_surplus = donation[
        "predicted_surplus"
    ]


    calculation_surplus = max(
        predicted_surplus,
        1
    )


    # -----------------------------------------------------
    # GET RECEIVERS
    # -----------------------------------------------------

    receivers = connection.execute("""
        SELECT *
        FROM receivers
        ORDER BY distance ASC
    """).fetchall()

    connection.close()


    suitable_receivers = []


    # -----------------------------------------------------
    # CALCULATE MATCH SCORES
    # -----------------------------------------------------

    for receiver in receivers:

        capacity = receiver["capacity"]

        distance = receiver["distance"]


        # -------------------------------------------------
        # CAPACITY SCORE
        # -------------------------------------------------

        if capacity >= predicted_surplus:

            capacity_score = 100 - (

                (
                    (capacity - predicted_surplus)
                    / calculation_surplus
                )

                * 20

            )

        else:

            capacity_score = (

                capacity
                / calculation_surplus

            ) * 70


        # -------------------------------------------------
        # DISTANCE SCORE
        # -------------------------------------------------

        distance_score = max(
            0,
            100 - (distance * 15)
        )


        # -------------------------------------------------
        # FINAL MATCH SCORE
        # -------------------------------------------------

        match_score = (

            (capacity_score * 0.60)

            +

            (distance_score * 0.40)

        )


        suitable_receivers.append({

            "id": receiver["id"],

            "name": receiver["name"],

            "capacity": capacity,

            "distance": distance,

            "match_score": round(
                match_score,
                1
            )

        })


    if not suitable_receivers:

        return "No receivers available."


    # -----------------------------------------------------
    # SORT BEST RECEIVER
    # -----------------------------------------------------

    suitable_receivers.sort(

        key=lambda x: x["match_score"],

        reverse=True

    )


    best_receiver = suitable_receivers[0]


    # -----------------------------------------------------
    # SAVE MATCH
    # -----------------------------------------------------

    connection = get_db_connection()


    connection.execute("""
        DELETE FROM matches
        WHERE donation_id = ?
    """, (
        donation_id,
    ))


    connection.execute("""
        INSERT INTO matches
        (
            donation_id,
            receiver_id,
            match_score,
            status
        )

        VALUES (?, ?, ?, ?)
    """, (

        donation_id,

        best_receiver["id"],

        best_receiver["match_score"],

        "Ready to Rescue"

    ))


    connection.commit()

    connection.close()


    # -----------------------------------------------------
    # SHOW MATCH PAGE
    # -----------------------------------------------------

    return render_template(

        "match.html",

        donation=donation,

        best_receiver=best_receiver,

        receivers=suitable_receivers

    )


# =========================================================
# MARK FOOD AS RESCUED
# =========================================================

@app.route("/rescue/<int:donation_id>")
def rescue_food(donation_id):

    connection = get_db_connection()


    match = connection.execute("""
        SELECT *
        FROM matches
        WHERE donation_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (
        donation_id,
    )).fetchone()


    if match is None:

        connection.close()

        return "No receiver match found."


    # -----------------------------------------------------
    # UPDATE STATUS
    # -----------------------------------------------------

    connection.execute("""
        UPDATE matches

        SET status = ?

        WHERE id = ?
    """, (

        "Rescued",

        match["id"]

    ))


    connection.commit()

    connection.close()


    return render_template(

        "rescue.html",

        donation_id=donation_id

    )


# =========================================================
# IMPACT DASHBOARD
# =========================================================

@app.route("/impact")
def impact():

    connection = get_db_connection()


    # -----------------------------------------------------
    # TOTAL DONATIONS
    # -----------------------------------------------------

    total_donations = connection.execute("""
        SELECT COUNT(*)
        FROM donations
    """).fetchone()[0]


    # -----------------------------------------------------
    # TOTAL PREDICTED SURPLUS
    # -----------------------------------------------------

    total_predicted = connection.execute("""
        SELECT COALESCE(
            SUM(predicted_surplus),
            0
        )

        FROM donations
    """).fetchone()[0]


    # -----------------------------------------------------
    # TOTAL RESCUES
    # -----------------------------------------------------

    total_rescues = connection.execute("""
        SELECT COUNT(*)
        FROM matches
        WHERE status = 'Rescued'
    """).fetchone()[0]


    # -----------------------------------------------------
    # TOTAL MEALS RESCUED
    # -----------------------------------------------------

    total_meals = connection.execute("""
        SELECT COALESCE(
            SUM(d.predicted_surplus),
            0
        )

        FROM donations d

        JOIN matches m
        ON d.id = m.donation_id

        WHERE m.status = 'Rescued'
    """).fetchone()[0]


    # -----------------------------------------------------
    # PENDING RESCUES
    # -----------------------------------------------------

    pending_rescues = connection.execute("""
        SELECT COUNT(*)
        FROM matches
        WHERE status = 'Ready to Rescue'
    """).fetchone()[0]


    # -----------------------------------------------------
    # URGENCY COUNTS
    # -----------------------------------------------------

    critical_count = connection.execute("""
        SELECT COUNT(*)
        FROM donations
        WHERE urgency_level = 'Critical'
    """).fetchone()[0]


    high_count = connection.execute("""
        SELECT COUNT(*)
        FROM donations
        WHERE urgency_level = 'High'
    """).fetchone()[0]


    medium_count = connection.execute("""
        SELECT COUNT(*)
        FROM donations
        WHERE urgency_level = 'Medium'
    """).fetchone()[0]


    low_count = connection.execute("""
        SELECT COUNT(*)
        FROM donations
        WHERE urgency_level = 'Low'
    """).fetchone()[0]


    # -----------------------------------------------------
    # RESCUE PERCENTAGE
    # -----------------------------------------------------

    if total_donations > 0:

        rescued_percentage = round(

            (
                total_rescues
                / total_donations
            ) * 100,

            1

        )

    else:

        rescued_percentage = 0


    connection.close()


    # -----------------------------------------------------
    # SHOW IMPACT PAGE
    # -----------------------------------------------------

    return render_template(

        "impact.html",

        total_donations=total_donations,

        total_predicted=int(
            total_predicted
        ),

        total_rescues=total_rescues,

        total_meals=int(
            total_meals
        ),

        pending_rescues=pending_rescues,

        rescued_percentage=rescued_percentage,

        critical_count=critical_count,

        high_count=high_count,

        medium_count=medium_count,

        low_count=low_count

    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )