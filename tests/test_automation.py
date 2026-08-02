import datetime as dt
import os
import tempfile
import unittest
from pathlib import Path

from automation.automation import ToursPlannerAutomation, load_environment


class AutomationTests(unittest.TestCase):
    def setUp(self):
        self.automation = ToursPlannerAutomation()
        self.data = {
            "location": "Skardu", "trip_name": "Summer-Trip", "adults": 4,
            "children": 2, "infants": 0, "senior_citizens": 0,
            "booking_date": "2026-08-01", "check_in_date": "2026-08-10",
            "check_out_date": "2026-08-13", "seating_capacity": 6, "vehicle_type": "Car",
            "transport_cost": 25000, "initial_deposit": 10000,
            "payment_method": "Bank transfer", "contact_phone": "+92 300 1234567",
            "emergency_phone": "+92 300 7654321", "driver_phone": "+92 300 1111111",
            "activities": ["Skardu Sightseeing"], "equipment": ["First Aid Kit"]
        }

    def test_clean_and_calculate(self):
        result = self.automation.process_form_submission(self.data)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["total_guests"], 6)
        self.assertEqual(result["data"]["vehicles_needed"], 1)
        self.assertEqual(result["data"]["total_trip_cost"], 28200)

    def test_dates_are_validated(self):
        invalid = dict(self.data, check_out_date="2026-08-09")
        result = self.automation.process_form_submission(invalid)
        self.assertEqual(result["status"], "error")

    def test_zero_capacity_is_rejected(self):
        result = self.automation.process_form_submission(dict(self.data, seating_capacity=0))
        self.assertEqual(result["status"], "error")

    def test_format_date(self):
        self.assertEqual(ToursPlannerAutomation.format_date(dt.datetime(2026, 8, 1)), "2026-08-01")

    def test_environment_values_can_be_loaded_from_repo_env_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "config").mkdir(parents=True, exist_ok=True)
            (root / ".env").write_text("TOURS_SPREADSHEET_ID=sheet-123\n", encoding="utf-8")
            (root / "config" / ".env").write_text("TOURS_FORM_ID=form-456\n", encoding="utf-8")
            os.environ.pop("TOURS_SPREADSHEET_ID", None)
            os.environ.pop("TOURS_FORM_ID", None)
            load_environment(root)
            self.assertEqual(os.environ.get("TOURS_SPREADSHEET_ID"), "sheet-123")
            self.assertEqual(os.environ.get("TOURS_FORM_ID"), "form-456")

    def test_available_vehicle_catalog(self):
        labels = self.automation.available_vehicle_labels()
        self.assertEqual(len(labels), 7)
        self.assertIn("V8 - Prado TZ/TX up model (2003-2007)", labels)

    def test_unknown_vehicle_is_rejected(self):
        result = self.automation.process_form_submission(dict(self.data, vehicle_booked="Unknown vehicle"))
        self.assertEqual(result["status"], "error")

    def test_richer_booking_fields_are_preserved(self):
        payload = dict(self.data, trip_style="Adventure Expedition", travel_priority="Luxury comfort", accommodation_category="Luxury 5-Star / Resort", room_count=2, meal_plan="Full board", special_requests="Quiet room", accessibility_notes="No stairs", transport_notes="Airport pickup at 10am", vehicle_type="V8 4x4 SUV")
        cleaned = self.automation.clean_form_data(payload)
        self.assertEqual(cleaned["trip_style"], "Adventure Expedition")
        self.assertEqual(cleaned["travel_priority"], "Luxury comfort")
        self.assertEqual(cleaned["room_count"], 2)
        self.assertEqual(cleaned["meal_plan"], "Full board")
        self.assertEqual(cleaned["special_requests"], "Quiet room")
        self.assertEqual(cleaned["accessibility_notes"], "No stairs")
        self.assertEqual(cleaned["transport_notes"], "Airport pickup at 10am")


if __name__ == "__main__":
    unittest.main()
