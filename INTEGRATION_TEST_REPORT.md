# Lost and Found Management System - Integration Test Report

## 📋 Executive Summary

- **Project:** Lost and Found Management System
- **Components Tested:**
  1. Python Tkinter Desktop Frontend (`main.py`, `dashboard.py`, `report_item.py`, `view_items.py`, `api_client.py`)
  2. Java Spring Boot REST Backend (Port 8080)
  3. Spring JDBC (`JdbcTemplate` with 100% Parameterized Queries)
  4. MySQL Database (Port 3306, Schema `lost_and_found`, Table `items`)
- **Execution Date:** 2026-11-15
- **Test Results Summary:** **9 / 9 Tests PASSED (100% Success Rate)**
- **Verification Rule:** Every write operation performed through the application was verified by direct SQL `SELECT` queries against MySQL.

---

## 🧪 Detailed Test Results

### TEST 1: Database Connection & Health Verification
- **Test Case:** Verify that MySQL is running, the Java Spring Boot backend is active, and the JDBC connection is established.
- **Verification Method:** Call `GET http://localhost:8080/api/health` via `ApiClient.check_health()`.
- **Expected Result:** HTTP 200 OK with `status: UP`, `backend: RUNNING`, `database: CONNECTED`, and schema `lost_and_found`.
- **Actual Result:**
  ```json
  {
    "timestamp": "2026-11-15T23:53:50.123",
    "backend": "RUNNING",
    "status": "UP",
    "database": "CONNECTED",
    "databaseProduct": "MySQL",
    "databaseVersion": "5.5.5-10.11.8-MariaDB",
    "catalog": "lost_and_found"
  }
  ```
- **Status:** **PASS**

---

### TEST 2: Add Item (Tkinter Frontend ➔ Java REST ➔ JDBC ➔ MySQL)
- **Test Case:** Report a sample item through the Python client and confirm database insertion.
- **Sample Payload:**
  ```json
  {
    "itemName": "Titan Edge Watch",
    "category": "Personal Accessories",
    "description": "Black ceramic slim wrist watch",
    "foundLocation": "Conference Hall B",
    "dateFound": "2026-11-15",
    "contact": "9812345678"
  }
  ```
- **Verification Method:**
  1. Frontend sends `POST /api/items`.
  2. Verify Java REST response returns HTTP 201 Created with auto-generated `itemId`.
  3. Verify initial status is strictly `LOST`.
  4. Run direct SQL in MySQL: `SELECT item_id, item_name, category, found_location, status FROM items WHERE item_id = 4;`.
- **Expected Result:** Item inserted into MySQL with auto-generated ID, status `LOST`, and matching row in `items` table.
- **Actual Result:**
  - REST Response: `itemId: 4, itemName: "Titan Edge Watch", status: "LOST"`.
  - MySQL SELECT Output: `{'item_id': '4', 'item_name': 'Titan Edge Watch', 'category': 'Personal Accessories', 'found_location': 'Conference Hall B', 'status': 'LOST'}`.
- **Status:** **PASS**

---

### TEST 3: Display Items (Zero Hardcoded Data)
- **Test Case:** Retrieve all items through `GET /api/items` and verify that the Python client displays actual records from MySQL.
- **Verification Method:** Compare items returned by the Java REST API with direct SQL query: `SELECT item_id, item_name, category, status FROM items ORDER BY date_found DESC, item_id DESC;`.
- **Expected Result:** Exact 1:1 match between API items and MySQL rows; no fake or hardcoded records.
- **Actual Result:**
  - API returned 4 items.
  - Direct MySQL query returned identical 4 items in the exact order: `[ID 4, ID 3, ID 1, ID 2]`.
- **Status:** **PASS**

---

### TEST 4: Search Items by Name
- **Test Case:** Search for an existing item using the search toolbar in the Python GUI (`GET /api/items/search?name=Titan`).
- **Verification Method:**
  1. Call `api_client.search_items("Titan")`.
  2. Compare with direct SQL query: `SELECT item_id, item_name FROM items WHERE LOWER(item_name) LIKE LOWER('%Titan%');`.
- **Expected Result:** Returns all items containing "Titan" (case-insensitive) matching the database query.
- **Actual Result:** Returned 1 match (`Titan Edge Watch`, ID 4). Matches MySQL query result.
- **Status:** **PASS**

---

### TEST 5: Filter Items by Category & Status
- **Test Case:** Verify filtering by category, status `LOST`, and status `FOUND`.
- **Verification Method:**
  - Category filter: `GET /api/items?category=Personal Accessories`
  - LOST filter: `GET /api/items?status=LOST`
  - FOUND filter: `GET /api/items?status=FOUND`
  - Compare counts with corresponding SQL queries:
    - `SELECT COUNT(*) FROM items WHERE category = 'Personal Accessories';`
    - `SELECT COUNT(*) FROM items WHERE status = 'LOST';`
    - `SELECT COUNT(*) FROM items WHERE status = 'FOUND';`
- **Expected Result:** Each filtered list accurately matches the respective SQL count.
- **Actual Result:**
  - Category 'Personal Accessories': 2 items (Matches MySQL count: 2).
  - Status 'LOST': 2 items (Matches MySQL count: 2).
  - Status 'FOUND': 2 items (Matches MySQL count: 2).
- **Status:** **PASS**

---

### TEST 6: Mark Item as FOUND (Status Transition in MySQL)
- **Test Case:** Select item 4 (`Titan Edge Watch`, currently `LOST`), click "Mark as FOUND", and verify database update.
- **Verification Method:**
  1. Confirm item 4 initial status is `LOST`.
  2. Execute `PATCH /api/items/4/status` with `{"status": "FOUND"}`.
  3. Verify Java backend response returns HTTP 200 with `status: FOUND`.
  4. Query MySQL directly: `SELECT item_id, item_name, status FROM items WHERE item_id = 4;`.
- **Expected Result:** Database status in MySQL updates from `LOST` to `FOUND`.
- **Actual Result:**
  - REST Response: `itemId: 4, itemName: "Titan Edge Watch", status: "FOUND"`.
  - Direct MySQL Query: `{'item_id': '4', 'item_name': 'Titan Edge Watch', 'status': 'FOUND'}`.
- **Status:** **PASS**

---

### TEST 7: Dashboard Statistics Synchronization
- **Test Case:** Verify that adding items and marking items as FOUND immediately and accurately updates dashboard statistics.
- **Verification Method:**
  1. Record baseline stats: `total=4, lost=1, found=3`.
  2. Add new item ("Gym Water Bottle"):
     - New stats: `total=5, lost=2, found=3` (Total +1, LOST +1, FOUND unchanged).
  3. Mark "Gym Water Bottle" as FOUND:
     - New stats: `total=5, lost=1, found=4` (Total unchanged, LOST -1, FOUND +1).
- **Expected Result:** Dashboard metrics dynamically reflect database modifications in real-time.
- **Actual Result:** Counts incremented and decremented with 100% mathematical accuracy matching database rows.
- **Status:** **PASS**

---

### TEST 8: Data Persistence Across Sessions
- **Test Case:** Verify that records, generated IDs, and updated statuses persist when the application is closed and reopened.
- **Verification Method:**
  1. Destroy client session.
  2. Initialize a fresh `ApiClient` session.
  3. Fetch all items and inspect items created in prior tests.
- **Expected Result:** All records, generated IDs, and updated statuses (`FOUND`) remain permanently in MySQL.
- **Actual Result:** All 5 items retained in MySQL; item 4 retained status `FOUND`.
- **Status:** **PASS**

---

### TEST 9: Error Handling & Edge Cases
- **Test Case:** Validate system resilience against network, validation, and business rule edge cases.
- **Sub-Tests Executed:**

| Sub-Test | Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| **9.1 Backend Offline** | Request sent to unreachable port `59999` | Handled gracefully without crash; raises `ApiException` | Gracefully caught: `Cannot connect to Java backend.` | **PASS** |
| **9.2 Invalid Item ID** | Request `GET /api/items/999999` | HTTP 404 Not Found | HTTP 404: `Item with ID 999999 not found.` | **PASS** |
| **9.3 Empty Required Fields** | Request `POST /api/items` with empty `itemName` | HTTP 400 Bad Request with field errors | HTTP 400: `Validation failed: itemName: Item name is required...` | **PASS** |
| **9.4 Illegal Status Transition** | Attempt to revert a `FOUND` item back to `LOST` | HTTP 400 Bad Request; database transition blocked | HTTP 400: `Item with ID 4 is already marked as FOUND. It cannot be reverted to LOST.` | **PASS** |
| **9.5 Invalid Status Value** | Attempt to set status to `STOLEN` | HTTP 400 Bad Request | HTTP 400: Validation rejects value | **PASS** |
| **9.6 Future Date** | Submit `dateFound: "2099-12-31"` | HTTP 400 Bad Request / Form validation rejected | HTTP 400: `Date found cannot be in the future.` | **PASS** |

- **Status:** **PASS**

---

## 🏆 Final Conclusion

The end-to-end integration of the **Lost and Found Management System** is complete and fully verified. 
- Python Tkinter acts as a pure presentation layer communicating solely over HTTP/JSON.
- Java Spring Boot acts as the API gateway and business validation layer.
- Spring JDBC executes 100% parameterized SQL queries.
- MySQL serves as the single source of truth, persisting all data changes reliably.
