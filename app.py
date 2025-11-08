from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random

# -------------------------
# Flask App Configuration
# -------------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database (SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# -------------------------
# User Model
# -------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# -------------------------
# Authentication Routes
# -------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"], method="pbkdf2:sha256")

        if User.query.filter_by(username=username).first():
            return "⚠️ Username already exists!"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        return "❌ Invalid credentials!"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# -------------------------
# Dashboard + Map Routes
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

@app.route("/map/<disaster>")
def map_page(disaster):
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("map.html", disaster=disaster)

# -------------------------
# API Endpoint (Simulated Disaster Data)
# -------------------------
@app.route("/api/disaster/<disaster>")
def get_disaster_data(disaster):
    # Realistic clusters for each disaster type
    regions = {
    # 🔥 Wildfire hotspots
    "fire": [
        (-25, 133),   # Australia (Northern Territory)
        (37, -120),   # California, USA
        (43, -2),     # Spain/Portugal
        (60, -135),   # Canada / Alaska
        (-15, 28),    # Zambia
        (20, 78),     # Central India
        (41, 21),     # Greece / Balkans
        (-34, 18),    # South Africa (Cape Town)
        (-9, -75),    # Amazon, Peru
        (55, 100)     # Siberia (Taiga fires)
    ],

    # 🌊 Flood-prone regions
    "flood": [
        (23, 90),     # Bangladesh
        (13, 80),     # Chennai, India
        (5, -1),      # Ghana
        (30, 120),    # Eastern China
        (10, -84),    # Central America (Costa Rica)
        (-1, 36),     # Kenya
        (16, 105),    # Laos / Vietnam
        (50, 30),     # Eastern Europe (Ukraine region)
        (0, 103),     # Singapore / Malaysia
        (6, 3)        # Nigeria (Lagos)
    ],

    # 🌎 Earthquake zones (major tectonic boundaries)
    "earthquake": [
        (35, 140),    # Japan
        (38, -122),   # San Francisco, USA
        (19, -99),    # Mexico City
        (-15, -72),   # Peru
        (39, 23),     # Turkey / Greece
        (30, 70),     # Pakistan
        (37, 142),    # Japan trench
        (17, 121),    # Philippines
        (-7, 107),    # Indonesia (Java)
        (-36, -72),   # Chile
        (40, 125),    # North Korea region
        (64, -149),   # Alaska
        (35, 51),     # Iran
        (45, 14),     # Italy / Balkans
        (12, -86)     # Nicaragua
    ],

    # 🌪️ Tropical storms / cyclones
    "storm": [
        (15, -90),    # Caribbean
        (10, 100),    # Thailand / Malaysia
        (25, 80),     # Bay of Bengal
        (35, 140),    # Japan (typhoons)
        (12, 125),    # Philippines
        (-18, 147),   # Coral Sea / Queensland
        (20, -80),    # Cuba / Bahamas
        (22, 120),    # Taiwan
        (30, -90),    # Gulf of Mexico
        (-15, 45)     # Madagascar / Mozambique
    ],

    # Fallback default (neutral)
    "default": [(20, 0)]
}


    centers = regions.get(disaster.lower(), regions["default"])
    data = []

    for center in centers:
        lat_c, lon_c = center
        for _ in range(25):
            lat = lat_c + random.uniform(-5, 5)
            lon = lon_c + random.uniform(-5, 5)
            chance = random.uniform(40, 100)
            data.append({
                "lat": lat,
                "lon": lon,
                "chance": chance
            })

    print(f"[API] Generated {len(data)} points for {disaster}")
    return jsonify(data)

# -------------------------
# Run Flask App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
