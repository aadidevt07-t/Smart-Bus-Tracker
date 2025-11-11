-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS smartbus;
USE smartbus;

-- ======================
-- ROUTES TABLE
-- ======================
CREATE TABLE IF NOT EXISTS routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    start_location VARCHAR(100) NOT NULL,
    end_location VARCHAR(100) NOT NULL,
    stops TEXT NOT NULL,   -- comma-separated list of intermediate stops
    route_name VARCHAR(150) GENERATED ALWAYS AS (CONCAT(start_location, ' → ', end_location)) STORED
);

-- ======================
-- BUSES TABLE
-- ======================
CREATE TABLE IF NOT EXISTS buses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    route_id INT NOT NULL,
    lat DOUBLE NOT NULL,
    lng DOUBLE NOT NULL,
    number VARCHAR(50) NOT NULL,
    arrival VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_seats INT NOT NULL,
    passengers INT NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
);

-- ======================
-- ADMIN TABLE
-- ======================
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- ======================
-- EXAMPLE DATA
-- ======================

-- Routes
INSERT INTO routes (start_location, end_location, stops)
VALUES
('Trivandrum', 'Kollam', 'Varkala, Paravur'),
('Ernakulam', 'Thrissur', 'Aluva, Angamaly, Chalakudy'),
('Kozhikode', 'Kannur', 'Vadakara, Thalassery');

-- Buses
INSERT INTO buses (name, route_id, lat, lng, number, arrival, status, total_seats, passengers)
VALUES
('KSRTC Express', 1, 8.5241, 76.9366, 'KL-01-AA1234', '10:15 AM', 'On Time', 40, 28),
('Green Line Deluxe', 2, 9.9312, 76.2673, 'KL-07-BB5678', '10:45 AM', 'On Time', 45, 25),
('City Connect', 3, 11.2588, 75.7804, 'KL-10-CC4321', '11:05 AM', 'Delayed', 50, 20);

-- Admins
INSERT INTO admin (username, password)
VALUES ('aadidev', 'aadi123'), ('abhay', 'abhay456');
