#!/usr/bin/env python3
"""Validate, calculate, and optionally write trip submissions to Google Sheets."""
import datetime as dt
import json
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

BASE_PATH = Path(__file__).resolve().parents[1]


def load_environment(root: Optional[Path] = None) -> None:
    """Load .env values from the repository root and config directory if present."""
    base = Path(root or BASE_PATH)
    for env_path in (base / ".env", base / "config" / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)

    if not os.environ.get("TOURS_SPREADSHEET_ID") and os.environ.get("GOOGLE_SPREADSHEET_ID"):
        os.environ.setdefault("TOURS_SPREADSHEET_ID", os.environ["GOOGLE_SPREADSHEET_ID"])
    if not os.environ.get("TOURS_FORM_ID") and os.environ.get("GOOGLE_FORM_ID"):
        os.environ.setdefault("TOURS_FORM_ID", os.environ["GOOGLE_FORM_ID"])


load_environment()
LOG_PATH = BASE_PATH / "logs" / "automation.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()])
LOGGER = logging.getLogger(__name__)


class ToursPlannerAutomation:
    """Business logic with an optional Google Sheets service dependency."""
    def __init__(self, sheets_service=None, spreadsheet_id: Optional[str] = None, config_file: Optional[str] = None):
        self.config_file = Path(config_file or os.getenv("TOURS_CONFIG", BASE_PATH / "config" / "app_config.json"))
        self.sheets_service = sheets_service
        self.spreadsheet_id = spreadsheet_id or os.getenv("TOURS_SPREADSHEET_ID")

    def load_configuration(self):
        try:
            with self.config_file.open(encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            LOGGER.error("Failed to load configuration: %s", exc)
            return None

    def available_vehicle_labels(self) -> list:
        """Return labels for vehicles currently marked available."""
        try:
            catalog = json.loads((BASE_PATH / "config" / "vehicles.json").read_text(encoding="utf-8"))
            return [item["label"] for item in catalog["vehicles"] if item.get("available")]
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            return []

    def available_vehicles(self) -> list:
        return [item for item in self._vehicle_catalog() if item.get("available")]

    @staticmethod
    def _vehicle_catalog() -> list:
        try:
            catalog = json.loads((BASE_PATH / "config" / "vehicles.json").read_text(encoding="utf-8"))
            return catalog["vehicles"]
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            return []

    def assign_vehicles(self, guest_count: int) -> list:
        """Assign smallest available vehicles until the requested group fits."""
        remaining = guest_count
        assignments = []
        for vehicle in sorted(self.available_vehicles(), key=lambda item: (item.get("capacity", 0), item["id"])):
            if remaining <= 0:
                break
            assignments.append({"vehicle_id": vehicle["id"], "vehicle_label": vehicle["label"], "capacity": vehicle["capacity"], "guests": min(remaining, vehicle["capacity"])})
            remaining -= vehicle["capacity"]
        if remaining > 0:
            raise ValueError("not enough available vehicle capacity for this group")
        return assignments

    def _destinations_catalog(self) -> list:
        try:
            catalog = json.loads((BASE_PATH / "config" / "destinations.json").read_text(encoding="utf-8"))
            return catalog.get("destinations", [])
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            return []

    def _destinations(self) -> list:
        return self._destinations_catalog()

    def get_destination_config(self, name: str) -> Optional[dict]:
        if not name:
            return None
        normalized = str(name).strip().lower()
        candidates = [
            d for d in self._destinations_catalog()
            if d.get("name", "").strip().lower() == normalized
            or d.get("id", "").strip().lower() == normalized
        ]
        return candidates[0] if candidates else None

    def assign_fleet_for_group(self, destination_name: str, guest_count: int) -> list:
        """Assign vehicles for a consolidated group based on destination rules."""
        dest = self.get_destination_config(destination_name)
        allowed_ids = None
        if dest:
            allowed_ids = dest.get("allowed_vehicle_ids")
        pool = [v for v in self._vehicle_catalog() if v.get("available")]
        if allowed_ids:
            pool = [v for v in pool if v.get("id") in allowed_ids]
        remaining = guest_count
        assignments = []
        for vehicle in sorted(pool, key=lambda item: (item.get("capacity", 0), item.get("id", ""))):
            if remaining <= 0:
                break
            assignments.append({"vehicle_id": vehicle["id"], "vehicle_label": vehicle.get("label"), "capacity": vehicle.get("capacity", 0), "guests": min(remaining, vehicle.get("capacity", 0))})
            remaining -= vehicle.get("capacity", 0)
        if remaining > 0:
            LOGGER.warning("Not enough capacity for %s guests at %s; remaining=%s", guest_count, destination_name, remaining)
        return assignments

    def consolidate_and_assign(self, destination_name: str, date_iso: str) -> dict:
        if not destination_name:
            raise ValueError("destination_name required")
        if not self.sheets_service or not self.spreadsheet_id:
            LOGGER.info("Sheets service not configured — returning dry-run assignment for %s on %s", destination_name, date_iso)
            return {"destination": destination_name, "date": date_iso, "assignments": self.assign_fleet_for_group(destination_name, 0), "dry_run": True}
        range_name = "Trip_Database!A2:Z"
        resp = self.sheets_service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        rows = resp.get("values", [])
        config = self.load_configuration() or {}
        headers = config.get("sheets", {}).get("Trip_Database", {}).get("headers", [])
        matched = []
        total_guests = 0
        for idx, r in enumerate(rows):
            row = {headers[i]: (r[i] if i < len(r) else "") for i in range(len(headers))}
            if row.get("destination", "").strip().lower() == destination_name.strip().lower() and row.get("check_in_date", "") == date_iso and row.get("trip_status", "") in ("Pending", "", "pending"):
                matched.append((idx, row))
                total_guests += int(row.get("total_guests", 0) or 0)
        assignments = self.assign_fleet_for_group(destination_name, total_guests)
        updates = []
        for idx, trip in matched:
            row_number = idx + 2
            values_map = trip.copy()
            values_map["vehicle_assignment"] = json.dumps({"assignments": assignments, "finalized_date": date_iso}, ensure_ascii=False)
            values_map["trip_status"] = "Assigned"
            row_values = [values_map.get(h, "") for h in headers]
            range_to_update = f"Trip_Database!A{row_number}:{chr(ord('A') + max(0, len(headers)-1))}{row_number}"
            try:
                self.sheets_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=range_to_update, valueInputOption="USER_ENTERED", body={"values": [row_values]}).execute()
                LOGGER.info("Updated row %s for trip %s", row_number, trip.get("trip_id"))
                updates.append({"row": row_number, "trip_id": trip.get("trip_id")})
            except Exception as exc:
                LOGGER.error("Failed to update row %s: %s", row_number, exc)
        return {"destination": destination_name, "date": date_iso, "total_guests": total_guests, "assignments": assignments, "updated_rows": updates}

    def process_form_submission(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            cleaned = self.clean_form_data(form_data)
            calculated = self.calculate_fields(cleaned)
            if self.is_duplicate_submission(calculated):
                return {"status": "duplicate", "data": calculated}
            result = self.update_sheet_records(calculated)
            self.send_notifications(calculated, result)
            self.update_dashboard(calculated)
            return {"status": "success", "data": calculated, "result": result}
        except (TypeError, ValueError) as exc:
            LOGGER.error("Invalid form submission: %s", exc)
            return {"status": "error", "error": str(exc), "data": form_data}

    def clean_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        location = str(form_data.get("destination", form_data.get("location", ""))).strip().title()
        trip_name = str(form_data.get("trip_name", form_data.get("trip_title", ""))).strip()
        if not trip_name:
            trip_name = f"{location} Tour"
        if not location:
            raise ValueError("location and trip_name are required")
        cleaned: Dict[str, Any] = {
            "trip_id": str(form_data.get("trip_id") or self.generate_trip_id()),
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "location": location,
            "destination": location,
            "trip_name": trip_name,
            "tentative_plan": str(form_data.get("tentative_plan", form_data.get("itinerary", ""))).strip()
        }
        demographic_fields = ("adults", "children", "infants", "senior_citizens")
        for field in demographic_fields:
            cleaned[field] = self.non_negative_int(form_data.get(field, 0), field)
        cleaned["total_guests"] = sum(cleaned[field] for field in demographic_fields)
        if cleaned["total_guests"] == 0:
            raise ValueError("at least one guest is required")

        cleaned["booking_date"] = self.format_date(form_data.get("booking_date") or dt.date.today().isoformat(), True)
        cleaned["check_in_date"] = self.format_date(form_data.get("check_in_date") or form_data.get("start_date"), True)
        cleaned["check_out_date"] = self.format_date(form_data.get("check_out_date") or form_data.get("end_date"), True)
        if cleaned["check_out_date"] <= cleaned["check_in_date"]:
            raise ValueError("check_out_date must be after check_in_date")

        cleaned.update({
            "planner_name": str(form_data.get("planner_name", form_data.get("traveler_name", form_data.get("lead_traveler", "")))).strip(),
            "contact_phone": self.format_phone(form_data.get("contact_phone")),
            "contact_email": str(form_data.get("contact_email", "")).lower().strip(),
            "emergency_contact": str(form_data.get("emergency_contact", "")).strip(),
            "emergency_phone": self.format_phone(form_data.get("emergency_phone")),
            "accommodation_category": str(form_data.get("accommodation_category", form_data.get("accommodation_pref", "Executive / 3-4 Star"))).strip(),
            "hotel_name": str(form_data.get("hotel_name", "")).strip(),
            "vehicle_type": str(form_data.get("vehicle_type", "V8 4x4 SUV")).strip(),
            "vehicle_booked": "",
            "pickup_location": str(form_data.get("pickup_location", form_data.get("pickup_city", ""))).strip(),
            "dropoff_location": str(form_data.get("dropoff_location", form_data.get("dropoff_city", ""))).strip(),
            "driver_name": str(form_data.get("driver_name", "")).strip(),
            "payment_method": str(form_data.get("payment_method", "Bank Transfer")).strip().title(),
            "medical_conditions": str(form_data.get("medical_conditions", "")).strip(),
            "blood_type": str(form_data.get("blood_type", "Unknown")).strip(),
            "trip_style": str(form_data.get("trip_style", "")).strip(),
            "travel_priority": str(form_data.get("travel_priority", "")).strip(),
            "meal_plan": str(form_data.get("meal_plan", "")).strip(),
            "special_requests": str(form_data.get("special_requests", "")).strip(),
            "accessibility_notes": str(form_data.get("accessibility_notes", "")).strip(),
            "transport_notes": str(form_data.get("transport_notes", "")).strip(),
            "package_option": str(form_data.get("package_option", form_data.get("tour_package", "Skardu Select"))).strip(),
        })

        cleaned["driver_phone"] = self.format_phone(form_data.get("driver_phone"))
        cleaned["initial_deposit"] = self.non_negative_float(form_data.get("initial_deposit", 0), "initial_deposit")
        cleaned["transport_cost"] = self.non_negative_float(form_data.get("transport_cost", 0), "transport_cost")

        # Auto-assign vehicle based on party size (backend-managed, not traveler-facing)
        provided_vehicle = str(form_data.get("vehicle_booked", form_data.get("selected_vehicle", ""))).strip()
        if provided_vehicle and "Flexible" not in provided_vehicle:
            labels = self.available_vehicle_labels()
            ids = [v.get("id") for v in self._vehicle_catalog()]
            if provided_vehicle not in labels and provided_vehicle not in ids:
                raise ValueError("vehicle_booked is not in the available vehicle catalog")
            cleaned["vehicle_booked"] = provided_vehicle
        else:
            cleaned["vehicle_assignment"] = self.assign_vehicles(cleaned["total_guests"])

        cleaned["package_option"] = cleaned.get("package_option", "Skardu Select")

        activities, equipment = self.as_list(form_data.get("activities")), self.as_list(form_data.get("equipment"))
        for name, label in (("skardu_sightseeing", "Skardu Sightseeing"), ("hunza_sightseeing", "Hunza Sightseeing"), ("deosai_activities", "Deosai Activities")):
            cleaned[name] = any(label.lower() in str(act).lower() for act in activities)
        for name, label in (("tents_rent", "Tents"), ("beds_rent", "Beds"), ("cookware_rent", "Cookware"), ("generator_rent", "Generator"), ("first_aid_kit", "First Aid Kit")):
            cleaned[name] = any(label.lower() in str(eq).lower() for eq in equipment)

        cleaned["activities"] = ", ".join([str(a) for a in activities]) if activities else ""
        cleaned["equipment"] = ", ".join([str(e) for e in equipment]) if equipment else ""
        cleaned.update({"trip_status": "Pending", "payment_status": "Unpaid"})
        return cleaned

    def _assign_vehicle(self, data: Dict[str, Any], vehicles: list) -> dict:
        """Auto-assign a vehicle based on party size and vehicle availability."""
        total_guests = data.get("total_guests", 0)
        for vehicle in vehicles:
            if vehicle.get("status") == "Available" and vehicle.get("seating_capacity", 0) >= total_guests:
                return {"vehicle_type": vehicle.get("label", "Unknown"), "vehicle_id": vehicle.get("id"), "seating_capacity": vehicle.get("seating_capacity")}
        # Fallback to largest available
        for vehicle in sorted(vehicles, key=lambda v: v.get("seating_capacity", 0), reverse=True):
            if vehicle.get("status") == "Available":
                return {"vehicle_type": vehicle.get("label", "Unknown"), "vehicle_id": vehicle.get("id"), "seating_capacity": vehicle.get("seating_capacity")}
        return {"error": "No available vehicles for party size"}

    def get_vehicle_info(self, vehicle_type: str) -> dict:
        """Return vehicle catalog info for a selected vehicle type."""
        normalized = str(vehicle_type or "").strip().lower()
        for vehicle in self._vehicle_catalog():
            if vehicle.get("label", "").strip().lower() == normalized:
                return vehicle
            if vehicle.get("id", "").strip().lower() == normalized:
                return vehicle
        return {"seating_capacity": 7}

    def _fetch_weather(self, data: Dict[str, Any]) -> dict:
        """Fetch weather details for trip dates and destinations."""
        try:
            dest = data.get("destination", "")
            dest_info = next((d for d in self._destinations() if d.get("name") == dest), None)
            if not dest_info or not dest_info.get("latitude") or not dest_info.get("longitude"):
                return {}
            from weather import get_weather_for_dates
            dates = [data.get("departure_date", ""), data.get("return_date", "")]
            dates = [d for d in dates if d]
            if not dates:
                return {}
            records = get_weather_for_dates(dest_info["latitude"], dest_info["longitude"], dates)
            return [{"date": r["date"], "temp_max_c": r["temp_max_c"], "temp_min_c": r["temp_min_c"], "precip_mm": r["precip_mm"], "wind_kph": r["wind_kph"], "conditions": r["weather_code"]} for r in records]
        except Exception:
            return {}

    def calculate_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        calculated = data.copy()
        vehicle_type = data.get("vehicle_type", "Sedan")
        vehicle_info = self.get_vehicle_info(vehicle_type)
        seating = vehicle_info.get("seating_capacity", 7) if vehicle_info else 7
        total_guests = int(data.get("total_guests", 0) or 0)
        calculated["vehicles_needed"] = max(1, (total_guests + seating - 1) // seating) if seating > 0 else 1
        activities_cost = sum(data.get(name, 0) * amount for name, amount in (("skardu_sightseeing", 3000), ("hunza_sightseeing", 2500), ("deosai_activities", 5000)))
        equipment_cost = sum(data.get(name, 0) * amount for name, amount in (("tents_rent", 2000), ("beds_rent", 500), ("cookware_rent", 300), ("generator_rent", 1500), ("first_aid_kit", 200)))
        calculated["activities_cost"], calculated["equipment_cost"] = activities_cost, equipment_cost
        calculated["total_activities_cost"] = activities_cost + equipment_cost
        transport_cost = data.get("transport_cost", 0) or 0
        calculated["total_trip_cost"] = transport_cost + calculated["total_activities_cost"]
        initial_deposit = data.get("initial_deposit", 0) or 0
        calculated["remaining_balance"] = max(0, calculated["total_trip_cost"] - initial_deposit)
        calculated["payment_percentage"] = (initial_deposit / calculated["total_trip_cost"] * 100) if calculated["total_trip_cost"] else 0
        calculated["capacity_status"] = "Overbooked" if seating < total_guests else "Adequate"
        calculated["emergency_fund"] = total_guests * {"High": 500, "Medium": 300, "Low": 100}.get(data.get("emergency_level", "Medium"), 300)
        calculated["approval_status"] = "Approved" if initial_deposit > 0 and data.get("payment_method") else "Pending"
        return calculated

    @staticmethod
    def non_negative_int(value: Any, field: str) -> int:
        try:
            result = int(value or 0)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be an integer") from exc
        if result < 0:
            raise ValueError(f"{field} cannot be negative")
        return result

    @staticmethod
    def non_negative_float(value: Any, field: str) -> float:
        try:
            result = float(value or 0)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be numeric") from exc
        if result < 0:
            raise ValueError(f"{field} cannot be negative")
        return result

    @staticmethod
    def as_list(value: Any) -> list:
        return [] if value is None else ([value] if isinstance(value, str) else list(value))

    @staticmethod
    def generate_trip_id() -> str:
        return f"TRIP-{dt.datetime.now(dt.timezone.utc):%Y%m%d%H%M%S}-{uuid.uuid4().hex[:8].upper()}"

    @staticmethod
    def format_date(date_input: Any, required: bool = False) -> str:
        if not date_input:
            if required:
                raise ValueError("date is required")
            return ""
        value = date_input.date() if isinstance(date_input, dt.datetime) else date_input
        try:
            return dt.date.fromisoformat(str(value).split("T")[0]).isoformat()
        except ValueError as exc:
            raise ValueError(f"invalid date: {date_input}") from exc

    @staticmethod
    def format_phone(phone_input: Any) -> str:
        if not phone_input:
            return ""
        cleaned = re.sub(r"[^0-9+]", "", str(phone_input))
        if cleaned.count("+") > 1 or ("+" in cleaned and not cleaned.startswith("+")) or len(cleaned.lstrip("+")) < 7:
            raise ValueError("invalid phone number")
        return cleaned

    def is_duplicate_submission(self, data: Dict[str, Any]) -> bool:
        if not self.sheets_service or not self.spreadsheet_id:
            return False
        values = self.sheets_service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range="Trip_Database!A2:A").execute().get("values", [])
        return any(row and row[0] == data["trip_id"] for row in values)

    def update_sheet_records(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.sheets_service or not self.spreadsheet_id:
            return {"trip_id": data["trip_id"], "status": "validated", "dry_run": True}
        config = self.load_configuration() or {}
        headers = config.get("sheets", {}).get("Trip_Database", {}).get("headers", [])
        row = [data.get(header, "") for header in headers]
        result = self.sheets_service.spreadsheets().values().append(spreadsheetId=self.spreadsheet_id, range="Trip_Database!A1", valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body={"values": [row]}).execute()
        return {"trip_id": data["trip_id"], "status": "created", "updated_range": result.get("updates", {}).get("updatedRange")}

    @staticmethod
    def send_notifications(data: Dict[str, Any], result: Dict[str, Any]):
        LOGGER.info("Notification hook completed for trip: %s", result.get("trip_id"))

    @staticmethod
    def update_dashboard(data: Dict[str, Any]):
        LOGGER.info("Dashboard is formula-driven; new trip available: %s", data.get("trip_id"))


if __name__ == "__main__":
    LOGGER.info("Automation module loaded. Use setup_google.py for Google setup.")
