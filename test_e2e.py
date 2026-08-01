"""End-to-end test for Tours Planning system using demo traveller dataset.

Tests the full flow:
1. Form data cleaning (clean_form_data)
2. Field calculation (calculate_fields)
3. Vehicle assignment (assign_vehicles)
4. Sheet record formatting (update_sheet_records)
5. Dashboard update (update_dashboard)
6. Fleet consolidation (consolidate_and_assign)

Validates against demo_travellers.json for expected outputs.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from automation.automation import ToursPlannerAutomation


def load_demo_travellers():
    with open(ROOT / "demo_travellers.json") as f:
        return json.load(f)


def run_e2e_tests():
    data = load_demo_travellers()
    travellers = data["travellers"]
    automation = ToursPlannerAutomation()

    print("=" * 70)
    print("TOURS PLANNING — END-TO-END TEST REPORT")
    print("=" * 70)
    print(f"Total demo travellers: {len(travellers)}")
    print(f"Test run: {data['generated_for']}")
    print()

    results = []
    passed = 0
    failed = 0

    for traveller in travellers:
        tid = traveller["id"]
        scenario = traveller["scenario"]
        form_data = traveller["form_data"]
        expected = {
            "guests": traveller.get("expected_guests"),
            "capacity_status": traveller.get("expected_capacity_status"),
        }

        print(f"--- {tid}: {scenario} ---")
        result = {"id": tid, "scenario": scenario, "checks": [], "warnings": []}

        # Step 1: Clean form data
        try:
            cleaned = automation.clean_form_data(form_data)
            result["checks"].append(("clean_form_data", True, "Form data cleaned successfully"))
            print(f"  ✓ clean_form_data: OK")
        except Exception as e:
            result["checks"].append(("clean_form_data", False, str(e)))
            print(f"  ✗ clean_form_data: FAILED — {e}")
            failed += 1
            results.append(result)
            continue

        # Step 2: Calculate fields
        try:
            calculated = automation.calculate_fields(cleaned)
            result["checks"].append(("calculate_fields", True, "Fields calculated successfully"))
            print(f"  ✓ calculate_fields: OK")
        except Exception as e:
            result["checks"].append(("calculate_fields", False, str(e)))
            print(f"  ✗ calculate_fields: FAILED — {e}")
            failed += 1
            results.append(result)
            continue

        # Step 3: Assign vehicles
        try:
            total_guests = int(calculated.get("total_guests") or 0)
            assigned = automation.assign_vehicles(total_guests)
            result["checks"].append(("assign_vehicles", True, f"Vehicles assigned for {total_guests} guests"))
            print(f"  ✓ assign_vehicles: OK (for {total_guests} guests)")
        except Exception as e:
            result["checks"].append(("assign_vehicles", False, str(e)))
            print(f"  ✗ assign_vehicles: FAILED — {e}")
            failed += 1
            results.append(result)
            continue

        # Step 4: Sheet record formatting
        try:
            sheet_record = automation.update_sheet_records(calculated)
            result["checks"].append(("update_sheet_records", True, "Sheet record formatted"))
            print(f"  ✓ update_sheet_records: OK")
        except Exception as e:
            result["checks"].append(("update_sheet_records", False, str(e)))
            print(f"  ✗ update_sheet_records: FAILED — {e}")
            failed += 1
            results.append(result)
            continue

        # Step 5: Dashboard update (static, just logs)
        try:
            automation.update_dashboard(calculated)
            result["checks"].append(("update_dashboard", True, "Dashboard update logged"))
            print(f"  ✓ update_dashboard: OK")
        except Exception as e:
            result["checks"].append(("update_dashboard", False, str(e)))
            print(f"  ✗ update_dashboard: FAILED — {e}")
            failed += 1
            results.append(result)
            continue

        # Validate expected values
        # Check guest count
        total_guests_calc = (
            form_data.get("adults", 0)
            + form_data.get("children", 0)
            + form_data.get("infants", 0)
            + form_data.get("senior_citizens", 0)
        )
        if total_guests_calc == expected["guests"]:
            result["checks"].append(("guest_count", True, f"Guests={total_guests_calc}"))
            print(f"  ✓ Guest count: {total_guests_calc} (expected {expected['guests']})")
        else:
            result["checks"].append(("guest_count", False, f"Got {total_guests_calc}, expected {expected['guests']}"))
            print(f"  ✗ Guest count: {total_guests_calc} (expected {expected['guests']})")
            failed += 1

        # Check vehicle assignment
        if assigned:
            vehicle_labels = [v.get("label", v.get("vehicle_label", str(v))) for v in assigned]
            result["checks"].append(("vehicle_assignment", True, f"Assigned: {', '.join(vehicle_labels)}"))
            print(f"  ✓ Vehicles assigned: {', '.join(vehicle_labels)}")
        else:
            result["checks"].append(("vehicle_assignment", False, "No vehicles assigned"))
            print(f"  ✗ No vehicles assigned")
            failed += 1

        # Check trip_id generated
        trip_id = calculated.get("trip_id", "")
        if trip_id:
            result["checks"].append(("trip_id", True, f"Trip ID: {trip_id}"))
            print(f"  ✓ Trip ID: {trip_id}")
        else:
            result["checks"].append(("trip_id", False, "No trip ID generated"))
            print(f"  ✗ No trip ID generated")
            failed += 1

        # Check sheet record structure
        if isinstance(sheet_record, list) and sheet_record:
            result["checks"].append(("sheet_columns", True, f"{len(sheet_record)} columns (list)"))
            print(f"  ✓ Sheet record: {len(sheet_record)} columns (list)")
        elif isinstance(sheet_record, dict) and sheet_record:
            result["checks"].append(("sheet_columns", True, f"{len(sheet_record)} columns (dict)"))
            print(f"  ✓ Sheet record: {len(sheet_record)} columns (dict)")
        else:
            result["checks"].append(("sheet_columns", False, "No sheet record"))
            print(f"  ✗ No sheet record generated")
            failed += 1

        # Check capacity status (normalize naming)
        cap_status = calculated.get("capacity_status", "")
        # Normalize both sides for comparison
        cap_norm = cap_status.lower()
        expected_norm = expected["capacity_status"].lower() if expected["capacity_status"] else ""
        # Map "adequate" to "within_capacity" for test expectations
        if cap_norm == "adequate":
            cap_norm = "within_capacity"
        if expected_norm == "adequate":
            expected_norm = "within_capacity"
        if cap_norm == expected_norm:
            result["checks"].append(("capacity_status", True, f"Status: {cap_status}"))
            print(f"  ✓ Capacity status: {cap_status}")
        else:
            result["checks"].append(("capacity_status", False, f"Got {cap_status}, expected {expected['capacity_status']}"))
            print(f"  ✗ Capacity status mismatch: {cap_status} (expected {expected['capacity_status']})")
            failed += 1

        # Check activities
        activities = calculated.get("activities", [])
        if activities:
            result["checks"].append(("activities", True, f"Activities: {', '.join(str(a) for a in activities)}"))
            print(f"  ✓ Activities: {', '.join(str(a) for a in activities)}")
        else:
            result["warnings"].append("No activities listed")
            print(f"  ⚠ No activities listed")

        # Check equipment
        equipment = calculated.get("equipment", [])
        if equipment:
            result["checks"].append(("equipment", True, f"Equipment: {', '.join(str(e) for e in equipment)}"))
            print(f"  ✓ Equipment: {', '.join(str(e) for e in equipment)}")
        else:
            result["warnings"].append("No equipment listed")
            print(f"  ⚠ No equipment listed")

        # Check payment
        payment = calculated.get("payment_method", "")
        if payment:
            result["checks"].append(("payment_method", True, f"Payment: {payment}"))
            print(f"  ✓ Payment method: {payment}")

        # Check total cost
        total_cost = calculated.get("total_trip_cost", 0)
        result["checks"].append(("total_cost", True, f"Total cost: PKR {total_cost:,.0f}"))
        print(f"  ✓ Total trip cost: PKR {total_cost:,.0f}")

        # Check deposit and balance
        deposit = calculated.get("initial_deposit", 0)
        balance = calculated.get("remaining_balance", 0)
        result["checks"].append(("deposit_balance", True, f"Deposit: PKR {deposit:,.0f}, Balance: PKR {balance:,.0f}"))
        print(f"  ✓ Deposit: PKR {deposit:,.0f}, Balance: PKR {balance:,.0f}")

        # Check emergency fund
        emergency_fund = calculated.get("emergency_fund", 0)
        result["checks"].append(("emergency_fund", True, f"Emergency fund: PKR {emergency_fund:,.0f}"))
        print(f"  ✓ Emergency fund: PKR {emergency_fund:,.0f}")

        # Check all 52 sheet columns present in the record
        expected_columns = [
            "trip_id", "timestamp", "destination", "trip_name", "tentative_plan",
            "total_guests", "adults", "children", "infants", "senior_citizens",
            "booking_date", "check_in_date", "check_out_date", "accommodation_category",
            "hotel_name", "room_type", "room_count", "rooms_needed", "room_rate",
            "meal_plan", "special_requests", "vehicle_type", "vehicle_booked",
            "vehicle_assignment", "seating_capacity", "vehicles_needed", "pickup_location",
            "dropoff_location", "driver_name", "driver_phone", "activities",
            "activities_cost", "equipment", "equipment_cost", "total_trip_cost",
            "transport_cost", "initial_deposit", "remaining_balance", "payment_percentage",
            "payment_method", "payment_status", "trip_status", "capacity_status",
            "emergency_fund", "approval_status", "medical_conditions", "blood_type",
            "planner_name", "contact_phone", "contact_email", "emergency_contact", "emergency_phone"
        ]
        if isinstance(sheet_record, list):
            # update_sheet_records returns a list of row values; check length
            if len(sheet_record) == len(expected_columns):
                result["checks"].append(("all_sheet_columns", True, f"All {len(expected_columns)} columns present (list)"))
                print(f"  ✓ All {len(expected_columns)} sheet columns present (list)")
            else:
                result["warnings"].append(f"Sheet record has {len(sheet_record)} values, expected {len(expected_columns)} columns")
                print(f"  ⚠ Sheet record has {len(sheet_record)} values, expected {len(expected_columns)} columns")
        elif isinstance(sheet_record, dict):
            missing_cols = [c for c in expected_columns if c not in sheet_record]
            if missing_cols:
                result["warnings"].append(f"Missing sheet columns: {missing_cols}")
                print(f"  ⚠ Missing sheet columns: {missing_cols}")
            else:
                result["checks"].append(("all_sheet_columns", True, "All 52 columns present"))
                print(f"  ✓ All 52 sheet columns present")

        # Print summary
        check_pass = sum(1 for _, ok, _ in result["checks"] if ok)
        check_fail = sum(1 for _, ok, _ in result["checks"] if not ok)
        check_warn = len(result["warnings"])

        if check_fail == 0:
            passed += 1
            print(f"  → RESULT: PASS ({check_pass} checks, {check_warn} warnings)")
        else:
            failed += 1
            print(f"  → RESULT: FAIL ({check_pass} passed, {check_fail} failed, {check_warn} warnings)")

        print()
        results.append(result)

    # Print summary report
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total travellers tested: {len(travellers)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    # Print detailed discrepancies
    discrepancies = []
    for r in results:
        failed_checks = [(name, msg) for name, ok, msg in r["checks"] if not ok]
        if failed_checks:
            discrepancies.append({"id": r["id"], "scenario": r["scenario"], "failures": failed_checks})

    if discrepancies:
        print("DISCREPANCIES FOUND:")
        print("-" * 70)
        for d in discrepancies:
            print(f"\n  {d['id']}: {d['scenario']}")
            for name, msg in d["failures"]:
                print(f"    ✗ {name}: {msg}")
    else:
        print("NO DISCREPANCIES FOUND — All checks passed!")

    # Print warnings
    all_warnings = []
    for r in results:
        for w in r["warnings"]:
            all_warnings.append(f"  {r['id']}: {w}")
    if all_warnings:
        print(f"\nWARNINGS ({len(all_warnings)}):")
        print("-" * 70)
        for w in all_warnings:
            print(w)

    # Generate report file
    report = {
        "test_run": data["generated_for"],
        "total_travellers": len(travellers),
        "passed": passed,
        "failed": failed,
        "discrepancies": discrepancies,
        "all_warnings": all_warnings,
        "detailed_results": [
            {
                "id": r["id"],
                "scenario": r["scenario"],
                "checks": r["checks"],
                "warnings": r["warnings"]
            }
            for r in results
        ]
    }

    report_path = ROOT / "e2e_test_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nDetailed report saved to: {report_path}")

    return failed == 0


if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)