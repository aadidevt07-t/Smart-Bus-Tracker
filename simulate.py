import mysql.connector
import random
import time

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'smvsch',
    'database': 'smartbus'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def update_buses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, lat, lng, total_seats FROM buses")
    buses = cursor.fetchall()

    for bus in buses:
        bus_id = bus['id']
        lat = bus['lat']
        lng = bus['lng']
        total_seats = bus['total_seats']

        # Small incremental move: +/- 0.001 degree
        new_lat = lat + random.uniform(-0.001, 0.001)
        new_lng = lng + random.uniform(-0.001, 0.001)

        # Random passengers and status
        new_passengers = random.randint(0, total_seats)
        status = random.choice(["On time", "Delayed", "Stopped"])

        cursor.execute(
            "UPDATE buses SET lat=%s, lng=%s, passengers=%s, status=%s WHERE id=%s",
            (new_lat, new_lng, new_passengers, status, bus_id)
        )

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    while True:
        update_buses()
        print("Bus positions updated...")
        time.sleep(3)
