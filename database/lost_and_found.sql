-- ============================================================================
-- Lost and Found Management System
-- Database Setup Script
-- Database: lost_and_found
-- Table: items
-- ============================================================================

-- 1. Create the database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS lost_and_found
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 2. Switch to the lost_and_found database
USE lost_and_found;

-- 3. Create the items table
CREATE TABLE IF NOT EXISTS items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    found_location VARCHAR(100) NOT NULL,
    date_found DATE NOT NULL,
    contact VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'LOST',
    CONSTRAINT chk_status CHECK (status IN ('LOST', 'FOUND'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
