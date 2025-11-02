from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import psycopg2
import mysql.connector
import os
import random
import datetime

app = Flask(__name__)
app.secret_key = "smartbus_secret_key"  # Needed for session handling

# --- MySQL configuration ---
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


# ---------------- Public Pages ----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["GET"])
def search():
    from_place = request.args.get("from_place")
    to_place = request.args.get("to_place")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buses")
    buses = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("buslist.html", from_place=from_place, to_place=to_place, buses=buses)


@app.route("/bus/<int:bus_id>")
def bus_info(bus_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *, (total_seats - passengers) AS available_seats
        FROM buses WHERE id=%s
    """, (bus_id,))

    bus = cursor.fetchone()
    cursor.close()
    conn.close()

    if not bus:
        return "Bus not found", 404

    return render_template("bus-info.html", bus=bus)



@app.route("/bus-data/<int:bus_id>")
def bus_data(bus_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT lat, lng FROM buses WHERE id=%s", (bus_id,))
    bus = cursor.fetchone()
    cursor.close()
    conn.close()

    if not bus:
        return jsonify({"error": "Bus not found"}), 404

    return jsonify(bus)


# ---------------- Admin Panel ----------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin:
            session["admin"] = admin["username"]
            return redirect(url_for("dashboard"))
        else:
            error = "❌ Incorrect username or password"

    return render_template("admin-login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buses")
    buses = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("dashboard.html", buses=buses)


@app.route('/add-bus', methods=['GET', 'POST'])
def add_bus():
    if request.method == 'POST':
        name = request.form.get('name')
        route = request.form.get('route')
        number = request.form.get('number')
        total_seats = request.form.get('total_seats')

        # Check required fields
        if not all([name, route, number, total_seats]):
            return "Error: All fields are required", 400

        # --- Auto-fill missing fields ---
        # Better Kerala-only range (avoids sea)
        lat = round(random.uniform(8.75, 12.95), 6)
        lng = round(random.uniform(76.25, 77.35), 6)
        arrival = (datetime.datetime.now() + datetime.timedelta(minutes=random.randint(10, 120))).strftime("%H:%M")
        status = random.choice(["On Time", "Delayed", "Cancelled"])
        passengers = random.randint(0, int(total_seats))

        # --- Insert into database ---
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO buses (name, route, number, total_seats, lat, lng, arrival, status, passengers)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, route, number, total_seats, lat, lng, arrival, status, passengers))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Bus added successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_bus.html')


@app.route("/delete-bus/<int:bus_id>", methods=["POST"])
def delete_bus(bus_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM buses WHERE id=%s", (bus_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("🗑️ Bus deleted successfully!", "info")
    except Exception as e:
        flash(f"Error deleting bus: {e}", "danger")

    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("admin_login"))


# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)
