# Lost and Found Management System - Setup & Execution Guide

This guide walks you through setting up and running the Lost and Found Management System on Windows.

---

## 🚀 Quick Start (Automated 1-Click Launch)

If you have already installed the prerequisites (Java, Python, MySQL), you can start the entire stack with a single command:

```cmd
d:\APP\run_application.bat
```

**What `run_application.bat` does automatically:**
1. Checks if MySQL is listening on port `3306` (starts local server if needed).
2. Starts the Java Spring Boot backend in a dedicated window.
3. Polls the backend health check endpoint (`http://localhost:8080/api/health`) until MySQL and Spring Boot confirm `UP` and `CONNECTED`.
4. Activates Python virtual environments (if present) and verifies dependencies.
5. Launches the Python Tkinter Desktop GUI only after the backend is ready.

---

## 🛠️ Prerequisites

| Software | Minimum Version | Check Command | Purpose |
|---|---|---|---|
| **Java Development Kit (JDK)** | Java 17+ (Java 21/25 supported) | `java -version` | Runs the Spring Boot REST API |
| **Python** | Python 3.10+ | `python --version` | Runs the desktop GUI (Tkinter included) |
| **MySQL Server** | MySQL 8.0+ or MariaDB 10.6+ | Port `3306` active | Relational database storage |
| **Apache Maven** | 3.8+ | *Optional* | Project includes bundled `mvnw.cmd` wrapper |

---

## 📖 Step-by-Step Manual Setup

### Step 1: Database Setup
1. Ensure your MySQL server is running on port `3306`.
2. Open MySQL Workbench, MySQL CLI, or Command Prompt:
   ```cmd
   mysql -u root -p < d:\APP\database\lost_and_found.sql
   ```
3. This creates the database `lost_and_found` and the `items` table with all constraints.

---

### Step 2: Configure Database Credentials

The system never requires hardcoded passwords in source code.

#### Option A: Using `application-local.properties` (Recommended)
1. In `java_backend\src\main\resources\`, copy `application-local.properties.example` to `application-local.properties`.
2. Fill in your MySQL credentials:
   ```properties
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=lost_and_found
   DB_USERNAME=root
   DB_PASSWORD=your_mysql_password
   ```
*(Note: `application-local.properties` is already excluded in `.gitignore` so your secrets will not be committed).*

#### Option B: Using Environment Variables
Set the following environment variables in PowerShell or Windows System Environment:
```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"
$env:DB_NAME = "lost_and_found"
$env:DB_USERNAME = "root"
$env:DB_PASSWORD = "your_mysql_password"
```

---

### Step 3: Setup Python Dependencies

1. Open Command Prompt or PowerShell:
   ```cmd
   cd d:\APP
   ```
2. *(Optional)* Create and activate a virtual environment:
   ```cmd
   python -m venv venv
   call venv\Scripts\activate.bat
   ```
3. Install required packages:
   ```cmd
   pip install -r requirements.txt
   ```

---

### Step 4: Build and Start Java Backend

1. Navigate to the backend folder:
   ```cmd
   cd d:\APP\java_backend
   ```
2. Build the project:
   ```cmd
   .\mvnw.cmd clean package -DskipTests
   ```
3. Start the backend:
   ```cmd
   d:\APP\run_backend.bat
   ```
4. Verify backend health in your browser or curl:
   ```bash
   curl http://localhost:8080/api/health
   ```
   *Expected Response:* `{"status":"UP","database":"CONNECTED","catalog":"lost_and_found"}`

---

### Step 5: Start Python Desktop Application

In a new terminal window:
```cmd
d:\APP\run_frontend.bat
```
The desktop application window will open, verify the backend connection, and display the live dashboard.

---

## 🔍 Verification & Testing

To run the automated end-to-end integration test suite against the live system:
```cmd
python d:\APP\python_frontend\e2e_integration_test.py
```
This tests:
- Health check verification
- Adding an item via REST and verifying the row in MySQL
- Listing items and confirming zero hardcoded records
- Case-insensitive search by name
- Multi-criteria filtering by category and status
- Updating status from `LOST` to `FOUND` and verifying MySQL update
- Live dashboard count synchronization
- Persistence across sessions
- Error handling (invalid IDs, empty fields, illegal status transitions)

---

## ❓ Troubleshooting

| Issue | Cause | Resolution |
|---|---|---|
| `Backend: Offline` in Tkinter | Java backend is not started | Run `d:\APP\run_backend.bat` and check console output. |
| `MySQL database could not be reached on port 3306` | MySQL is stopped | Start MySQL via `d:\APP\start_database.bat` or Windows Services (`net start MySQL`). |
| `Access denied for user 'root'@'localhost'` | Incorrect MySQL password | Configure correct password in `application-local.properties` or set `$env:DB_PASSWORD`. |
| `ModuleNotFoundError: No module named 'requests'` | Python package not installed | Run `pip install -r requirements.txt`. |
| `The JAVA_HOME environment variable is not defined` | JDK path not detected | Install JDK 17+ and set `JAVA_HOME=C:\Program Files\Java\jdk-<version>`. |
