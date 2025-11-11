from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="smvsch",
        database="smartbus"
    )

# ✅ Home Page
@app.route("/")
def home():
    return render_template("index.html")

# ✅ Search Bus
@app.route("/search", methods=["GET"])
def search():
    start_point = request.args.get("from_place", "").strip().lower()
    end_point = request.args.get("to_place", "").strip().lower()

    if not start_point or not end_point:
        flash("⚠️ Please enter both start and end locations.", "warning")
        return render_template("buslist.html", query=None, buses=[])

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch all buses with route details
    cursor.execute("""
        SELECT 
            buses.id AS bus_id,
            buses.name AS bus_name,
            buses.number AS bus_number,
            buses.arrival AS bus_arrival,
            buses.status AS bus_status,
            buses.total_seats,
            buses.passengers,
            routes.start_location,
            routes.end_location,
            routes.stops
        FROM buses
        JOIN routes ON buses.route_id = routes.id
    """)
    buses = cursor.fetchall()

    matched_buses = []

    for bus in buses:
        # ✅ Normalize all route points cleanly
        route_points = []

        if bus["start_location"]:
            route_points.append(bus["start_location"].strip().lower())

        if bus["stops"]:
            stops_cleaned = [
                s.strip().lower()
                for s in bus["stops"].replace("\n", "").split(",")
                if s.strip()
            ]
            route_points.extend(stops_cleaned)

        if bus["end_location"]:
            route_points.append(bus["end_location"].strip().lower())

        # ✅ Debug info (optional)
        print(f"Bus: {bus['bus_name']}, Route: {route_points}")

        # ✅ Check if both points exist and are in correct order
        if start_point in route_points and end_point in route_points:
            start_index = route_points.index(start_point)
            end_index = route_points.index(end_point)
            if start_index < end_index:
                matched_buses.append({
                    "id": bus["bus_id"],
                    "name": bus["bus_name"],
                    "number": bus["bus_number"],
                    "arrival": bus["bus_arrival"],
                    "status": bus["bus_status"],
                    "total_seats": bus["total_seats"],
                    "passengers": bus["passengers"],
                    "start_location": bus["start_location"],
                    "end_location": bus["end_location"],
                    "route": route_points
                })

    cursor.close()
    conn.close()

    if not matched_buses:
        flash("🚫 No buses available for this route.", "warning")

    return render_template(
        "buslist.html",
        query=f"{start_point} → {end_point}",
        buses=matched_buses
    )

# ✅ Admin Login
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin:
            session["admin"] = True
            session["username"] = username
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."

    return render_template("admin_login.html", error=error)

# ✅ Admin Dashboard
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        flash("Please log in first!", "warning")
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Explicitly select route_name with alias
    cursor.execute("""
        SELECT 
            buses.id,
            buses.number,
            buses.name,
            buses.total_seats,
            routes.route_name AS route_name
        FROM buses
        JOIN routes ON buses.route_id = routes.id
    """)
    buses = cursor.fetchall()

    cursor.close()
    conn.close()

    # ✅ Pass username from session
    username = session.get("username", "Admin")

    print("DEBUG USERNAME:", username)
    print("DEBUG BUS DATA:", buses)  # Just to verify fields in terminal

    return render_template("dashboard.html", buses=buses, username=username)
# ✅ Delete Bus
@app.route("/delete-bus/<int:bus_id>", methods=["POST"])
def delete_bus(bus_id):
    if not session.get("admin"):
        flash("Please log in first!", "warning")
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the bus exists
    cursor.execute("SELECT id FROM buses WHERE id = %s", (bus_id,))
    bus_exists = cursor.fetchone()

    if not bus_exists:
        cursor.close()
        conn.close()
        flash("❌ Bus not found.", "danger")
        return redirect(url_for("dashboard"))

    # Delete the bus
    cursor.execute("DELETE FROM buses WHERE id = %s", (bus_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("🗑️ Bus deleted successfully!", "success")
    return redirect(url_for("dashboard"))
# ✅ Add Bus
@app.route("/add-bus", methods=["GET", "POST"])
def add_bus():
    if not session.get("admin"):
        flash("Please log in first!", "warning")
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, start_location, end_location FROM routes")
    routes = cursor.fetchall()

    if request.method == "POST":
        bus_number = request.form["bus_number"]
        bus_name = request.form["bus_name"]
        total_seats = int(request.form["total_seats"])
        route_id = int(request.form["route_id"])

        lat = round(random.uniform(8.0, 12.0), 4)
        lng = round(random.uniform(75.0, 77.0), 4)
        arrival_time = (datetime.now() + timedelta(minutes=random.randint(5, 60))).strftime("%I:%M %p")
        status = random.choice(["On Time", "Delayed", "Arriving Soon"])
        passengers = random.randint(0, total_seats - 1)

        cursor.execute("""
            INSERT INTO buses (name, route_id, lat, lng, number, arrival, status, total_seats, passengers)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (bus_name, route_id, lat, lng, bus_number, arrival_time, status, total_seats, passengers))

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Bus added successfully!", "success")
        return redirect(url_for("dashboard"))

    cursor.close()
    conn.close()
    return render_template("add_bus.html", routes=routes)
@app.route('/add-route', methods=['GET', 'POST'])
def add_route():
    if request.method == 'POST':
        start_location = request.form['start_location'].strip()
        end_location = request.form['end_location'].strip()
        stops = request.form['stops'].strip()

        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ Do NOT insert route_name — MySQL will auto-generate it
        cur.execute("""
            INSERT INTO routes (start_location, end_location, stops)
            VALUES (%s, %s, %s)
        """, (start_location, end_location, stops))
        conn.commit()

        cur.close()
        conn.close()

        flash("✅ Route added successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add-route.html')

# ✅ Bus Info Page
@app.route("/bus/<int:bus_id>")
def bus_info(bus_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT buses.*, routes.start_location, routes.end_location 
        FROM buses 
        JOIN routes ON buses.route_id = routes.id
        WHERE buses.id = %s
    """, (bus_id,))
    bus = cursor.fetchone()
    cursor.close()
    conn.close()

    if not bus:
        return "Bus not found", 404

    bus_data = {
        'id': bus["id"],
        'name': bus["name"],
        'number': bus["number"],
        'route': f"{bus['start_location']} → {bus['end_location']}",
        'arrival': bus["arrival"],
        'status': bus["status"],
        'lat': bus["lat"],
        'lng': bus["lng"],
        'total_seats': bus["total_seats"],
        'passengers': bus["passengers"],
        'available_seats': max(0, bus["total_seats"] - bus["passengers"])
    }

    return render_template("bus-info.html", bus=bus_data)

# ✅ Live Data API
@app.route("/bus-data/<int:bus_id>")
def bus_data(bus_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT lat, lng, passengers FROM buses WHERE id = %s", (bus_id,))
    bus = cursor.fetchone()
    cursor.close()
    conn.close()

    if not bus:
        return jsonify({"error": "Bus not found"}), 404

    return jsonify(bus)

# ✅ Logout
@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
