# Lost and Found Management System

A production-ready, multi-tier desktop application for reporting, tracking, searching, and managing lost and found articles. Built with a responsive **Python Tkinter desktop GUI** that communicates over **HTTP/JSON REST APIs** with a robust **Java Spring Boot backend**, persisting records via **Spring JDBC** to a **MySQL database**.

---

## 📌 Problem Statement

In academic institutions, corporate offices, public venues, and transport hubs, personal belongings are frequently misplaced. Traditional lost-and-found management relies on manual physical registers or fragmented spreadsheets, leading to:
- Delays in returning valuable items to their rightful owners.
- Lack of centralized search and filtering capabilities.
- Poor visibility into item claim status and institutional metrics.
- High risk of data loss, human error, and duplicate tracking.

The **Lost and Found Management System** resolves these challenges by providing a centralized, secure, multi-tier desktop solution with real-time relational persistence, clear status transitions, and intuitive search/filtering tools.

---

## 🎯 Project Objectives

- **Strict Multi-Tier Decoupling:** Complete separation of presentation (Python GUI), business logic (Java Spring Boot REST API), and data persistence (MySQL relational database).
- **Relational Integrity:** Pure Spring `JdbcTemplate` implementation utilizing 100% parameterized queries with zero mock or hardcoded datasets.
- **Strict Status Lifecycle:** Clear operational distinction between `LOST` (item logged by finder, awaiting owner collection) and `FOUND` (item successfully returned to owner).
- **Security & Secret Isolation:** Zero hardcoded credentials, sensitive configuration isolated in untracked environment files, and masked errors in API responses.
- **Asynchronous User Interface:** Multi-threaded non-blocking HTTP requests ensure the desktop GUI remains responsive during backend network communications.

---

## ✨ Key Features

1. **Interactive Metrics Dashboard:**
   - Real-time KPI summary cards displaying Total Reported Items, Currently LOST (Active), and Successfully Returned (FOUND).
   - Category distribution summary ranking items across categories.
   - On-demand statistics refresh.

2. **Item Reporting Form:**
   - Form fields capturing Item Name, Category, Description, Found Location, Date Found, and Finder Contact.
   - Comprehensive client-side validation (required fields, character limits, prevention of future dates).
   - Instant confirmation popup displaying the database-generated `item_id`.
   - Automatic form clearing upon successful submission.

3. **Item Management Table (Treeview):**
   - Clean tabular display of all 8 database columns.
   - Status color-coding: `LOST` highlighted in amber/yellow; `FOUND` highlighted in light green.
   - Real-time item count indicator in status footer.

4. **Dynamic Search & Filtering:**
   - Case-insensitive search by item name via `/api/items/search?name=...`.
   - Category dropdown filter.
   - Status dropdown filter (`ALL`, `LOST`, `FOUND`).
   - One-click reset button restoring full catalog view.

5. **Mark as FOUND Return Workflow:**
   - Select any item marked `LOST` and click **Mark Selected as FOUND**.
   - Confirmation dialog preventing accidental updates.
   - Enforced business rule: items marked `FOUND` cannot be reverted to `LOST`.
   - Real-time status update in MySQL with automatic refresh of both the items table and dashboard metrics.

6. **Automated Health & Startup Verification:**
   - Built-in connection verification screen in Python before displaying the dashboard.
   - Health endpoint (`GET /api/health`) providing live MySQL ping (`SELECT 1`) and database metadata.

---

## 🛠️ Technologies Used

| Tier / Component | Technology | Version | Description |
|---|---|---|---|
| **Frontend GUI** | Python (Tkinter & ttk) | 3.10+ | Clean desktop user interface |
| **HTTP Client** | Python `requests` | >= 2.31.0 | JSON REST communication with backend |
| **Backend Service** | Java / Spring Boot | Java 17+ (Spring Boot 3.3.5) | RESTful API gateway, validation, business logic |
| **Data Access** | Spring JDBC (`JdbcTemplate`) | Spring 6.x | PreparedStatement parameterized SQL query execution |
| **Database Driver** | MySQL Connector/J | 8.x | High-throughput relational JDBC driver |
| **Database** | MySQL / MariaDB | 8.0+ / 10.11+ | Relational storage (`lost_and_found` schema) |
| **Build & Tooling** | Apache Maven | 3.8+ (wrapper included) | Java dependency management and packaging |

---

## 🏗️ System Architecture & Data Flow

```
+-------------------------------------------------------------+
|                      Python Client                          |
|             (Tkinter GUI Desktop Application)               |
|                                                             |
|   +---------------+   +----------------+   +------------+   |
|   | DashboardView |   | ReportItemView |   | ViewItems  |   |
|   +---------------+   +----------------+   +------------+   |
|                           |                                 |
|                     [api_client.py]                         |
+---------------------------|---------------------------------+
                            | HTTP / JSON Requests
                            | (Local REST API: port 8080)
                            v
+-------------------------------------------------------------+
|                       Java Backend                          |
|                 (Spring Boot REST Service)                  |
|                                                             |
|   +-----------------------------------------------------+   |
|   |                  REST Controllers                   |   |
|   | (ItemController.java, DashboardController.java,     |   |
|   |  HealthController.java)                             |   |
|   +-----------------------------------------------------+   |
|                           |                                 |
|                           v                                 |
|   +-----------------------------------------------------+   |
|   |                    Service Layer                    |   |
|   |                 (ItemService.java)                  |   |
|   +-----------------------------------------------------+   |
|                           |                                 |
|                           v                                 |
|   +-----------------------------------------------------+   |
|   |             JDBC Data Access (Repository)           |   |
|   |               (ItemRepositoryImpl.java)             |   |
|   +-----------------------------------------------------+   |
+---------------------------|---------------------------------+
                            | JDBC / Parameterized SQL
                            v
+-------------------------------------------------------------+
|                         Database                            |
|                          (MySQL)                            |
|                                                             |
|   Database: lost_and_found                                  |
|   Table:    items                                           |
+-------------------------------------------------------------+
```

### Status Convention
- **`LOST`**: The item has been reported by a finder but has **not yet been returned** to its rightful owner.
- **`FOUND`**: The item has been **successfully returned** to its rightful owner.

---

## 📂 Project Folder Structure

```
LostAndFound/
├── .gitignore                                 # Excludes build artifacts, virtualenvs, secrets
├── .env.example                               # Environment template with placeholder values
├── requirements.txt                           # Python dependencies (requests>=2.31.0)
├── setup_instructions.md                      # Detailed setup and configuration walkthrough
├── PROJECT_STATUS.md                          # Milestone tracker and test results matrix
├── INTEGRATION_TEST_REPORT.md                 # End-to-end integration test report
├── README.md                                  # Complete project documentation
├── run_application.bat                        # Master 1-click startup script (Windows)
├── run_backend.bat                            # Java Spring Boot backend startup script
├── run_frontend.bat                           # Python Tkinter frontend startup script
├── start_database.bat                         # Local MySQL launcher helper
│
├── database/                                  # Database Schemas & Migrations
│   └── lost_and_found.sql                     # DDL for database and items table
│
├── java_backend/                              # Java Spring Boot Backend
│   ├── mvnw.cmd                               # Windows Maven wrapper executable
│   ├── pom.xml                                # Maven build descriptor (Java 17+)
│   └── src/
│       ├── main/
│       │   ├── java/com/lostandfound/
│       │   │   ├── LostAndFoundApplication.java   # Spring Boot entry point
│       │   │   ├── config/
│       │   │   │   └── DatabaseConnectionVerifier.java # Startup JDBC health check
│       │   │   ├── controller/                # REST API controllers
│       │   │   ├── dto/                       # Request & response transfer objects
│       │   │   ├── exception/                 # Centralized error handler
│       │   │   ├── model/                     # Domain model (Item.java)
│       │   │   ├── repository/                # JdbcTemplate data access layer
│       │   │   └── service/                   # Business logic and validation
│       │   └── resources/
│       │       ├── application.properties     # Spring properties & env fallbacks
│       │       └── application-local.properties.example # Local credentials template
│       └── test/                              # Automated integration test suites
│
└── python_frontend/                           # Python Tkinter Desktop Frontend
    ├── api_client.py                          # Dedicated HTTP REST client
    ├── dashboard.py                           # Metric cards & category distribution view
    ├── main.py                                # Application root window & navigation layout
    ├── report_item.py                         # Found item reporting form view
    ├── view_items.py                          # Items table with search, filter, and return
    ├── requirements.txt                       # Client dependency declaration
    └── e2e_integration_test.py                # Automated end-to-end integration test suite
```

---

## 💻 Software Prerequisites

Ensure the following tools are installed on your machine:
1. **Java Development Kit (JDK 17 or later)**: Check with `java -version`.
2. **Python 3.10 or later**: Standard Windows Python includes Tkinter. Check with `python --version`.
3. **MySQL Server 8.0+** (or MariaDB 10.6+): Running on port `3306`.
4. **Apache Maven 3.8+**: Optional (the repository includes the `mvnw.cmd` wrapper).

---

## ⚙️ Installation & Configuration

### 1. MySQL Database Setup
Open MySQL Workbench, MySQL Command Line, or PowerShell and execute the SQL setup script:
```cmd
mysql -u root -p < database/lost_and_found.sql
```
This creates the database `lost_and_found` and the `items` table:
```sql
CREATE DATABASE IF NOT EXISTS lost_and_found CHARACTER SET utf8mb4;
USE lost_and_found;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

### 2. Environment & Database Credentials Configuration

Sensitive passwords and credentials are never hardcoded in source code.

#### Option A: Local Properties File (Recommended)
Copy `java_backend/src/main/resources/application-local.properties.example` to `application-local.properties` in the same directory and enter your MySQL credentials:
```properties
DB_HOST=localhost
DB_PORT=3306
DB_NAME=lost_and_found
DB_USERNAME=root
DB_PASSWORD=your_mysql_password
```
*(This file is excluded by `.gitignore` and will never be committed).*

#### Option B: Environment Variables
Alternatively, configure system environment variables:
```powershell
$env:DB_USERNAME = "root"
$env:DB_PASSWORD = "your_mysql_password"
```

---

### 3. Python Environment Setup
Install the required HTTP library (`requests`):
```cmd
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Option A: Master 1-Click Launch (Recommended)
Double-click or run from command line:
```cmd
run_application.bat
```
**Automated Execution Sequence:**
1. Verifies that MySQL is active on port `3306`.
2. Starts the Java Spring Boot backend server.
3. Polls the health endpoint until MySQL and Spring Boot report `status: UP` and `database: CONNECTED`.
4. Launches the Python Tkinter desktop GUI.

---

### Option B: Running Components Manually

1. **Start MySQL Server:**
   ```cmd
   start_database.bat
   ```
2. **Start Java Backend:**
   ```cmd
   run_backend.bat
   ```
   *Verify health in your browser:* `http://localhost:8080/api/health`
3. **Start Python Desktop GUI:**
   ```cmd
   run_frontend.bat
   ```

---

## 🧪 Testing the Application

### 1. Automated End-to-End Integration Test Suite
Run the comprehensive test script that executes every user action through the API and verifies changes with direct MySQL `SELECT` queries:
```cmd
python python_frontend/e2e_integration_test.py
```
**Test Coverage (9/9 Passed):**
- Database connectivity & health endpoint verification.
- Item creation via REST and verification in MySQL.
- Full items list display (confirming zero mock/hardcoded data).
- Case-insensitive search by name.
- Multi-criteria filtering by category and status.
- Status update (`LOST` ➔ `FOUND`) and database update verification.
- Real-time dashboard count synchronization.
- Data persistence across application sessions.
- Error handling (invalid IDs, empty fields, future dates, illegal transitions).

### 2. Java Backend Integration Tests
```cmd
cd java_backend
.\mvnw.cmd test
```

---

## 🔌 REST API Endpoint Reference

All endpoints return JSON and are hosted locally at `http://localhost:8080`.

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/api/health` | Health check verifying Java backend and live MySQL connection. | `200 OK` / `503` |
| `POST` | `/api/items` | Reports a new item. Auto-generates `item_id`, sets status to `LOST`. | `201 Created` |
| `GET` | `/api/items` | Retrieves all items ordered by date found descending. | `200 OK` |
| `GET` | `/api/items/{id}` | Retrieves a single item by database ID. Returns 404 if missing. | `200 OK` / `404` |
| `GET` | `/api/items/search?name={name}` | Case-insensitive search by item name. | `200 OK` |
| `GET` | `/api/items?category={category}` | Filters items by category. | `200 OK` |
| `GET` | `/api/items?status={status}` | Filters items by status (`LOST` or `FOUND`). | `200 OK` |
| `PATCH` | `/api/items/{id}/status` | Updates status (`LOST` ➔ `FOUND`). Blocks invalid transitions. | `200 OK` / `400` |
| `GET` | `/api/dashboard/stats` | Returns total items count, lost count, and found count. | `200 OK` |

### Example Request (`POST /api/items`)
```json
{
  "itemName": "Blue Backpack",
  "category": "Bags & Luggage",
  "description": "Navy canvas backpack with textbooks",
  "foundLocation": "Library 2nd Floor",
  "dateFound": "2026-11-15",
  "contact": "9876543210"
}
```

### Example Response (`201 Created`)
```json
{
  "itemId": 1,
  "itemName": "Blue Backpack",
  "category": "Bags & Luggage",
  "description": "Navy canvas backpack with textbooks",
  "foundLocation": "Library 2nd Floor",
  "dateFound": "2026-11-15",
  "contact": "9876543210",
  "status": "LOST"
}
```

---

## ❓ Common Errors & Troubleshooting

| Error / Symptom | Root Cause | Solution |
|---|---|---|
| `Backend: Offline` in Tkinter footer | Java backend is not running on port 8080. | Launch `run_backend.bat` and confirm it logs `Started LostAndFoundApplication`. |
| `MySQL database could not be reached on port 3306` | MySQL service is stopped. | Start MySQL using `start_database.bat` or verify MySQL service in Windows Services (`net start MySQL`). |
| `Access denied for user 'root'@'localhost'` | Incorrect MySQL password. | Set correct password in `application-local.properties` or set `$env:DB_PASSWORD`. |
| `Unknown database 'lost_and_found'` | Database schema not created yet. | Execute `database/lost_and_found.sql` using MySQL Workbench or CLI. |
| `Item is already marked as FOUND. It cannot be reverted to LOST` | Business rule protection. | Items returned to their owner cannot be reverted through normal workflows. |
| `Date found cannot be in the future` | Client-side validation rule. | Enter a date on or before the current calendar date (`YYYY-MM-DD`). |

---

## 📄 License
This project is licensed under the MIT License.
