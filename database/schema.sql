-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS smartbus;

-- Use the database
USE smartbus;

-- Create the buses table with available_seats as a generated column
CREATE TABLE IF NOT EXISTS buses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    route VARCHAR(255) NOT NULL,
    lat DOUBLE NOT NULL,
    lng DOUBLE NOT NULL,
    number VARCHAR(50) NOT NULL,
    arrival VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_seats INT NOT NULL,
    passengers INT NOT NULL
);


-- Insert initial data
INSERT INTO buses (name, route, lat, lng, number, arrival, status, total_seats, passengers)
VALUES
('KSRTC Express', 'City A → City B', 12.964049585701693, 77.59498516878607, 'KA-01-1234', '10:15 AM', 'Stopped', 40, 28),
('Green Line Deluxe', 'City A → City C', 13.077671526248151, 80.27362119563348, 'TN-01-5678', '10:45 AM', 'Stopped', 45, 25),
('City Connect', 'City A → City D', 17.382362370393697, 78.48590641070402, 'AP-09-4321', '11:05 AM', 'On time', 50, 20);
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
INSERT INTO admin (username, password)
VALUES ('aadidev', 'aadi123'),('abhay','abhay456');
