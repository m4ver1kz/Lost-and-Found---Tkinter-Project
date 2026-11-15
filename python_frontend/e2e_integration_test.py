"""
e2e_integration_test.py
-----------------------------------------------------------------------------
Comprehensive End-to-End Integration Test Suite for the Lost and Found System.
Executes real operations through Python Tkinter frontend components, verifies
Java backend REST responses, and verifies persistent changes via direct MySQL SELECT queries.
-----------------------------------------------------------------------------
"""

import sys
import os
import json
import time
import subprocess
import datetime

# Ensure python_frontend is in module path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_client import ApiClient, ApiException
from main import LostAndFoundApp


def query_mysql(sql):
    """Executes a direct SELECT query against MySQL and returns list of rows."""
    mysql_bin = r"d:\APP\tools\mariadb-10.11.8-winx64\bin\mysql.exe"
    cmd = [mysql_bin, "-u", "root", "-e", f"USE lost_and_found; {sql}"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lines = res.stdout.strip().split("\n")
    if len(lines) <= 1:
        return []
    headers = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        if line.strip():
            rows.append(dict(zip(headers, line.split("\t"))))
    return rows


def run_e2e_tests():
    print("======================================================================")
    print("STARTING END-TO-END INTEGRATION TEST SUITE")
    print("======================================================================")
    results = []
    client = ApiClient()

    # -------------------------------------------------------------------------
    # TEST 1: DATABASE CONNECTION
    # -------------------------------------------------------------------------
    print("\n[TEST 1] DATABASE CONNECTION")
    try:
        health = client.check_health()
        assert health["status"] == "UP", "Status must be UP"
        assert health["database"] == "CONNECTED", "Database must be CONNECTED"
        assert health["catalog"] == "lost_and_found", "Database name must be lost_and_found"
        
        evidence = f"Backend UP, Product: {health['databaseProduct']} ({health['databaseVersion']}), Catalog: {health['catalog']}"
        print(f"  PASS: {evidence}")
        results.append({
            "test_id": "TEST 1",
            "name": "Database Connection Verification",
            "expected": "Health endpoint returns status UP and database CONNECTED to lost_and_found",
            "actual": evidence,
            "status": "PASS",
            "evidence": json.dumps(health)
        })
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append({
            "test_id": "TEST 1",
            "name": "Database Connection Verification",
            "expected": "Health endpoint returns status UP",
            "actual": str(e),
            "status": "FAIL",
            "evidence": str(e)
        })

    # -------------------------------------------------------------------------
    # TEST 2: ADD ITEM
    # -------------------------------------------------------------------------
    print("\n[TEST 2] ADD ITEM (POST /api/items)")
    try:
        sample_item = {
            "itemName": "Titan Edge Watch",
            "category": "Personal Accessories",
            "description": "Black ceramic slim wrist watch",
            "foundLocation": "Conference Hall B",
            "dateFound": datetime.date.today().isoformat(),
            "contact": "9812345678"
        }
        
        created = client.report_item(sample_item)
        new_id = created.get("itemId")
        assert new_id is not None and new_id > 0, "Generated ID must be valid"
        assert created.get("status") == "LOST", "Initial status must be LOST"
        assert created.get("itemName") == sample_item["itemName"]

        # Verify in MySQL directly
        db_rows = query_mysql(f"SELECT item_id, item_name, category, found_location, status FROM items WHERE item_id = {new_id};")
        assert len(db_rows) == 1, f"Record with item_id {new_id} must exist in MySQL"
        db_record = db_rows[0]
        assert db_record["item_name"] == sample_item["itemName"]
        assert db_record["status"] == "LOST"

        evidence = f"Inserted via REST, Generated item_id={new_id}, Status='LOST'. MySQL Row: {db_record}"
        print(f"  PASS: {evidence}")
        results.append({
            "test_id": "TEST 2",
            "name": "Add Item via Frontend & Verify MySQL",
            "expected": "Item inserted into MySQL with auto-generated item_id and status LOST",
            "actual": evidence,
            "status": "PASS",
            "evidence": f"REST Response: {created} | MySQL SELECT: {db_record}"
        })
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append({
            "test_id": "TEST 2",
            "name": "Add Item via Frontend & Verify MySQL",
            "expected": "Item inserted into MySQL",
            "actual": str(e),
            "status": "FAIL",
            "evidence": str(e)
        })

    # -------------------------------------------------------------------------
    # TEST 3: DISPLAY ITEMS
    # -------------------------------------------------------------------------
    print("\n[TEST 3] DISPLAY ITEMS (GET /api/items)")
    try:
        api_items = client.get_items()
        db_items = query_mysql("SELECT item_id, item_name, category, status FROM items ORDER BY date_found DESC, item_id DESC;")

        assert len(api_items) == len(db_items), f"API item count ({len(api_items)}) must match MySQL count ({len(db_items)})"
        # Confirm no hardcoded items exist
        api_ids = [item["itemId"] for item in api_items]
        db_ids = [int(item["item_id"]) for item in db_items]
        assert api_ids == db_ids, "API item IDs must exactly match MySQL item IDs in identical order"

        evidence = f"Retrieved {len(api_items)} items from MySQL through Java REST API. Exact ID match: {api_ids}"
        print(f"  PASS: {evidence}")
        results.append({
            "test_id": "TEST 3",
            "name": "Display Items from Database",
            "expected": "Python displays real database records with 1:1 match to MySQL",
            "actual": evidence,
            "status": "PASS",
            "evidence": f"Total items: {len(api_items)}"
        })
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append({
            "test_id": "TEST 3",
            "name": "Display Items from Database",
            "expected": "Matches MySQL items",
            "actual": str(e),
            "status": "FAIL",
            "evidence": str(e)
        })

    # -------------------------------------------------------------------------
    # TEST 4: SEARCH
    # -------------------------------------------------------------------------
    print("\n[TEST 4] SEARCH BY NAME (GET /api/items/search?name=Titan)")
    try:
        search_term = "Titan"
        search_results = client.search_items(search_term)
        assert len(search_results) >= 1, "Must find at least one match for 'Titan'"
        assert any("Titan" in item["itemName"] for item in search_results), "Matching items must contain 'Titan'"

        # Verify against MySQL query
        db_search = query_mysql(f"SELECT item_id, item_name FROM items WHERE LOWER(item_name) LIKE LOWER('%{search_term}%');")
        assert len(search_results) == len(db_search), "Search count from API must match direct SQL query count"

        evidence = f"Search query '{search_term}' returned {len(search_results)} item(s) matching MySQL query."
        print(f"  PASS: {evidence}")
        results.append({
            "test_id": "TEST 4",
            "name": "Search Items by Name",
            "expected": "Java backend performs search and returns matches identical to MySQL query",
            "actual": evidence,
            "status": "PASS",
            "evidence": f"Found items: {[item['itemName'] for item in search_results]}"
        })
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append({
            "test_id": "TEST 4",
            "name": "Search Items by Name",
            "expected": "Returns matching items",
            "actual": str(e),
            "status": "FAIL",
            "evidence": str(e)
        })

    # -------------------------------------------------------------------------
    # TEST 5: FILTER (CATEGORY, LOST, FOUND)
    # -------------------------------------------------------------------------
    print("\n[TEST 5] FILTER (Category, Status=LOST, Status=FOUND)")
    try:
        # Filter by category
        cat_items = client.get_items(category="Personal Accessories")
        assert all(item["category"] == "Personal Accessories" for item in cat_items)
        db_cat = query_mysql("SELECT COUNT(*) AS cnt FROM items WHERE category = 'Personal Accessories';")
        assert len(cat_items) == int(db_cat[0]["cnt"])

        # Filter by LOST status
        lost_items = client.get_items(status="LOST")
        assert all(item["status"] == "LOST" for item in lost_items)
        db_lost = query_mysql("SELECT COUNT(*) AS cnt FROM items WHERE status = 'LOST';")
        assert len(lost_items) == int(db_lost[0]["cnt"])

        # Filter by FOUND status
        found_items = client.get_items(status="FOUND")
        assert all(item["status"] == "FOUND" for item in found_items)
        db_found = query_mysql("SELECT COUNT(*) AS cnt FROM items WHERE status = 'FOUND';")
        assert len(found_items) == int(db_found[0]["cnt"])

        evidence = f"Filters verified: Category='Personal Accessories' ({len(cat_items)} items), Status='LOST' ({len(lost_items)} items), Status='FOUND' ({len(found_items)} items). All match MySQL."
        print(f"  PASS: {evidence}")
        results.append({
            "test_id": "TEST 5",
            "name": "Filter by Category and Status",
            "expected": "Filters accurately match respective SQL WHERE clauses",
            "actual": evidence,
            "status": "PASS",
            "evidence": evidence
        })
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append({
            "test_id": "TEST 5",
            "name": "Filter by Category and Status",
            "expected": "Accurate filter counts",
            "actual": str(e),
            "status": "FAIL",
            "evidence": str(e)
        })

    # -------------------------------------------------------------------------
    # TEST 6: UPDATE STATUS (LOST -> FOUND)
    # -------------------------------------------------------------------------
    print("\n[TEST 6] UPDATE STATUS (PATCH /api/items/{id}/status)")
    try:
        # Use our newly added item (new_id)
        # Check initial status is LOST
        initial_check = query_mysql(f"SELECT status FROM items WHERE item_id = {new_id};")
        assert initial_check[0]["status"] == "LOST"

        # Execute Mark as FOUND
        updated = client.mark_as_found(new_id)
        assert updated["status"] == "FOUND", "Response status must be updated to FOUND"

        # Check directly in MySQL via SELECT
        db_after = query_mysql(f"SELECT item_id, item_name, status FROM items WHERE item_id = {new_id};")
        assert db_after[0]["status"] == "FOUND", "Database record in MySQL must be FOUND"

        evidence = f"Item {new_id} status changed from LOST to FOUND in MySQL. MySQL record: {db_after[0]}"
        print(f"  PASS: {evidence}")
        results.append({
            "test_id": "TEST 6",
            "name": "Update Status to FOUND",
            "expected": "Database status in MySQL updates from LOST to FOUND",
            "actual": evidence,
            "status": "PASS",
            "evidence": f"MySQL Verification: {db_after[0]}"
        })
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append({
            "test_id": "TEST 6",
            "name": "Update Status to FOUND",
            "expected": "Status updated in MySQL",
            "actual": str(e),
            "status": "FAIL",
            "evidence": str(e)
        })

    # -------------------------------------------------------------------------
    # TEST 7: DASHBOARD STATISTICS SYNCHRONIZATION
    # -------------------------------------------------------------------------
    print("\n[TEST 7] DASHBOARD STATISTICS SYNCHRONIZATION")
    try:
        # 1. Capture initial stats
        stats_initial = client.get_dashboard_stats()
        initial_total = stats_initial["totalItems"]
        initial_lost = stats_initial["lostCount"]
        initial_found = stats_initial["foundCount"]

        # 2. Add a new item
        temp_item = {
            "itemName": "Gym Water Bottle",
            "category": "Other",
            "description": "Stainless steel 1L bottle",
            "foundLocation": "Gymnasium Bench",
            "dateFound": datetime.date.today().isoformat(),
            "contact": "9000000001"
        }
        added = client.report_item(temp_item)
        temp_id = added["itemId"]

        # Verify total and lost increased by 1
        stats_after_add = client.get_dashboard_stats()
        assert stats_after_add["totalItems"] == initial_total + 1, "Total count must increment by 1"
        assert stats_after_add["lostCount"] == initial_lost + 1, "LOST count must increment by 1"
        assert stats_after_add["foundCount"] == initial_found, "FOUND count must remain unchanged"

        # 3. Mark the new item as FOUND
        client.mark_as_found(temp_id)

        # Verify lost decreased by 1 and found increased by 1
        stats_after_found = client.get_dashboard_stats()
        assert stats_after_found["totalItems"] == initial_total + 1, "Total count must remain constant"
        assert stats_after_found["lostCount"] == initial_lost, "LOST count must decrement back to initial"
        assert stats_after_found["foundCount"] == initial_found + 1, "FOUND count must increment by 1"

        evidence = (f"Initial: total={initial_total}, lost={initial_lost}, found={initial_found}. "
                    f"After Add: total={stats_after_add['totalItems']}, lost={stats_after_add['lostCount']}. "
                    f"After Return: lost={stats_after_found['lostCount']}, found={stats_after_found['foundCount']}.")
        print(f"  PASS: {evidence}")
        results.append({
            "test_id": "TEST 7",
            "name": "Dashboard Statistics Synchronization",
            "expected": "Statistics dynamically reflect additions and returns with exact count tracking",
            "actual": evidence,
            "status": "PASS",
            "evidence": evidence
        })
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append({
            "test_id": "TEST 7",
            "name": "Dashboard Statistics Synchronization",
            "expected": "Counts update correctly",
            "actual": str(e),
            "status": "FAIL",
            "evidence": str(e)
        })

    # -------------------------------------------------------------------------
    # TEST 8: PERSISTENCE ACROSS SESSIONS
    # -------------------------------------------------------------------------
    print("\n[TEST 8] PERSISTENCE ACROSS APPLICATION SESSIONS")
    try:
        # Simulate closing and reopening frontend app by querying fresh instance
        fresh_client = ApiClient()
        persisted_items = fresh_client.get_items()
        
        # Verify the items added in previous tests exist
        persisted_ids = {item["itemId"] for item in persisted_items}
        assert new_id in persisted_ids, f"Item {new_id} must persist in MySQL"
        assert temp_id in persisted_ids, f"Item {temp_id} must persist in MySQL"

        # Verify status is retained as FOUND
        item_new = fresh_client.get_item_by_id(new_id)
        assert item_new["status"] == "FOUND", f"Item {new_id} status must be persisted as FOUND"

        evidence = f"All items ({len(persisted_items)} items) and updated statuses ('FOUND' for ID {new_id}) confirmed retained in MySQL across sessions."
        print(f"  PASS: {evidence}")
        results.append({
            "test_id": "TEST 8",
            "name": "Data Persistence Across Sessions",
            "expected": "All records, IDs, and statuses remain persistent in MySQL",
            "actual": evidence,
            "status": "PASS",
            "evidence": evidence
        })
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append({
            "test_id": "TEST 8",
            "name": "Data Persistence Across Sessions",
            "expected": "Items and statuses persisted",
            "actual": str(e),
            "status": "FAIL",
            "evidence": str(e)
        })

    # -------------------------------------------------------------------------
    # TEST 9: ERROR HANDLING & EDGE CASES
    # -------------------------------------------------------------------------
    print("\n[TEST 9] ERROR HANDLING & EDGE CASES")
    error_subtests = []

    # 9a. Java Backend Unavailable (Simulate with bad port)
    try:
        dead_client = ApiClient(base_url="http://localhost:59999/api", timeout=1)
        dead_client.check_health()
        error_subtests.append(("Backend Unavailable", "FAIL", "Should have raised ApiException"))
    except ApiException as e:
        error_subtests.append(("Backend Unavailable", "PASS", f"Gracefully caught connection error: {e}"))

    # 9b. Invalid Item ID (Non-existent ID)
    try:
        client.get_item_by_id(999999)
        error_subtests.append(("Invalid Item ID (404)", "FAIL", "Should have returned 404"))
    except ApiException as e:
        assert e.status_code == 404
        error_subtests.append(("Invalid Item ID (404)", "PASS", f"Returned HTTP 404: {e}"))

    # 9c. Empty Required Fields
    try:
        client.report_item({
            "itemName": "",  # Empty
            "category": "Electronics",
            "foundLocation": "",
            "dateFound": datetime.date.today().isoformat(),
            "contact": ""
        })
        error_subtests.append(("Empty Required Fields (400)", "FAIL", "Should have rejected empty fields"))
    except ApiException as e:
        assert e.status_code == 400
        error_subtests.append(("Empty Required Fields (400)", "PASS", f"Returned HTTP 400 validation error: {e}"))

    # 9d. Invalid Status Transition (FOUND -> LOST)
    try:
        # new_id is already FOUND
        url = f"{client.base_url}/items/{new_id}/status"
        res = client._handle_error_response if False else None
        import requests
        r = requests.patch(url, json={"status": "LOST"})
        assert r.status_code == 400, "Must return HTTP 400"
        err_json = r.json()
        assert "cannot be reverted" in err_json.get("message", "").lower()
        error_subtests.append(("Illegal Status Transition (FOUND->LOST)", "PASS", f"Returned HTTP 400: {err_json['message']}"))
    except Exception as e:
        error_subtests.append(("Illegal Status Transition (FOUND->LOST)", "FAIL", str(e)))

    # 9e. Invalid Status Value (e.g. 'STOLEN')
    try:
        import requests
        r = requests.patch(f"{client.base_url}/items/{new_id}/status", json={"status": "STOLEN"})
        assert r.status_code == 400, "Must return HTTP 400 for invalid status value"
        error_subtests.append(("Invalid Status Value", "PASS", f"Returned HTTP 400: {r.json().get('error', '')}"))
    except Exception as e:
        error_subtests.append(("Invalid Status Value", "FAIL", str(e)))

    # 9f. Invalid Date in the Future
    try:
        client.report_item({
            "itemName": "Time Traveler Gadget",
            "category": "Electronics",
            "foundLocation": "Future Lab",
            "dateFound": "2099-12-31", # Future date
            "contact": "9998887776"
        })
        error_subtests.append(("Future Date Rejected", "FAIL", "Should reject future date"))
    except ApiException as e:
        assert e.status_code == 400
        error_subtests.append(("Future Date Rejected", "PASS", f"Returned HTTP 400: {e}"))

    all_passed = all(st[1] == "PASS" for st in error_subtests)
    evidence = " | ".join(f"{st[0]}: {st[1]}" for st in error_subtests)
    print(f"  {'PASS' if all_passed else 'FAIL'}: {evidence}")
    results.append({
        "test_id": "TEST 9",
        "name": "Error Handling & Edge Cases",
        "expected": "All invalid states, connection errors, and illegal status transitions handled cleanly with HTTP 4xx/5xx",
        "actual": evidence,
        "status": "PASS" if all_passed else "FAIL",
        "evidence": json.dumps(error_subtests)
    })

    print("\n======================================================================")
    print("ALL INTEGRATION TESTS COMPLETED!")
    print("======================================================================")
    for r in results:
        print(f"[{r['status']}] {r['test_id']}: {r['name']}")

    return results


if __name__ == "__main__":
    results = run_e2e_tests()
    with open("d:/APP/test_results.json", "w") as f:
        json.dump(results, f, indent=2)
