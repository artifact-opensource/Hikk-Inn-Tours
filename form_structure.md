{"TripID": "unique_identifier", "Timestamp": "YYYY-MM-DD HH:MM:SS", "Location": "Skardu/Hunza/Deosai/etc.", "TripName": "descriptive_name", "Region": "Gilgit-Baltistan/Hypothetical", 
"PlannerContact": "contact_person", "PlannerPhone": "phone_number", "PlannerEmail": "email_address",

# Demographics
"TotalGuests": "number",
"Adults": "number", 
"Children": "number",
"Infants": "number",
"SeniorCitizens": "number",

# Booking Details
"BookingReference": "reference_number",
"BookingDate": "YYYY-MM-DD",
"TravelStartDate": "YYYY-MM-DD",
"TravelEndDate": "YYYY-MM-DD",
"TripDuration": "number_days",
"DepartureCity": "city",
"ArrivalAirport": "airport_code",
"FlightNumber": "flight_number",

# Accommodation
"HotelName": "hotel_name",
"RoomType": "single/double/triple/suite",
"RoomCount": "number",
"RoomRate": "amount_currency",
"CheckInDate": "YYYY-MM-DD",
"CheckOutDate": "YYYY-MM-DD",
"HalfBoardIncluded": "boolean",
"FullBoardIncluded": "boolean",
"SpecialRequests": "text",

# Transportation
"VehicleType": "car/bus/taxi/private_vehicle",
"VehicleBooked": "vehicle_company/model/number",
"SeatingCapacity": "number",
"DriverName": "driver_name",
"DriverPhone": "phone_number",
"TransportCost": "amount_currency",
"PickupLocation": "address",
"DropoffLocation": "address",
"FuelCharges": "amount_currency",
"TollCharges": "amount_currency",
"ParkingCharges": "amount_currency",

# Available Vehicles (backend catalog: config/vehicles.json)
# V8: Prado TZ/TX up model (2003-2007); Prado TZ/TX down model (1998-2002);
#     Prado Land Cruiser 70 series, 5 Door (1990-1997)
# V4: Premio up model (2008-2013); Premio down model (2004-2007);
#     Toyota Corolla Sedan (2001-2006); Toyota Vitz (2001-2013)

# Excursions & Activities
"SkarduSightseeing": "boolean",
"SkarduSightseeingCost": "amount_currency",
"HunzaSightseeing": "boolean", 
"HunzaSightseeingCost": "amount_currency",
"DeosaiActivities": "text",
"DeosaiActivitiesCost": "amount_currency",
"CamelSafari": "boolean",
"CamelSafariCost": "amount_currency",
"MTK2Climb": "boolean",
"MTK2ClimbCost": "amount_currency",
"Rafting": "boolean",
"RaftingCost": "amount_currency",

# Equipment Rental
"TentsRent": "boolean",
"TentsCost": "amount_currency",
"BedsRent": "boolean",
"BedsCost": "amount_currency",
"CookwareRent": "boolean",
"CookwareCost": "amount_currency",
"GeneratorRent": "boolean",
"GeneratorCost": "amount_currency",
"FirstAidKit": "boolean",
"FirstAidKitCost": "amount_currency",

# Travel Insurance
"InsuranceProvider": "insurance_company",
"InsurancePolicy": "policy_number",
"CoverageAmount": "amount_currency",
"InsuranceCost": "amount_currency",
"InsuranceContact": "insurance_contact",

# Travel Documents
"PassportNumber": "passport_number",
"VisaRequired": "boolean",
"VisaType": "tourist/business/other",
"VisaCost": "amount_currency",
"VisaIssueDate": "YYYY-MM-DD",
"VisaExpiryDate": "YYYY-MM-DD",
"TravelInsurance": "boolean",
"InsurancePolicyNumber": "policy_number",

# Emergency & Safety
"EmergencyContact": "emergency_contact_name",
"EmergencyPhone": "phone_number",
"EmergencyAddress": "address",
"MedicalConditions": "text",
"Medications": "text",
"Allergies": "text",
"PreferredHospital": "hospital_name",
"BloodType": "A+/A-/B+/B-/O+/O-/AB+/AB-",
"MedicationList": "text",
"PreviousTrips": "text",
"EmergencyKit": "boolean",
"SafetyBriefing": "boolean",

# Financial Details
"InitialDeposit": "amount_currency",
"RemainingBalance": "amount_currency",
"TotalTripCost": "amount_currency",
"PaidAmount": "amount_currency",
"PaymentMethod": "cash/card/bank_transfer/online",
"PaymentStatus": "paid/partial/unpaid",
"PaymentDueDate": "YYYY-MM-DD",
"Currency": "currency_code",
"ExchangeRate": "rate",
"GST": "amount_currency",
"LocalTaxes": "amount_currency",
"Discounts": "amount_currency",
"Tips": "amount_currency",
"RefundAmount": "amount_currency",
"RefundDate": "YYYY-MM-DD",

# Trip Configuration
"MaxCapacity": "number",
"CurrentOccupancy": "number",
"CancellationPolicy": "policy_text",
"WeatherCondition": "sunny/cloudy/rainy/snowy/windy",
"TripStatus": "confirmed/pending/cancelled/completed",
"BookingStatus": "active/inactive/dropped",
"WeatherStatus": "normal/adverse",
"GuideRequired": "boolean",
"GuideName": "guide_name",
"GuideContact": "contact_info",
"GuideFee": "amount_currency",

# System Fields
"CreatedBy": "user_id",
"CreatedAt": "timestamp",
"LastUpdatedBy": "user_id",
"LastUpdatedAt": "timestamp",
"Signature": "digital_signature",
"VerificationStatus": "verified/pending/rejected",
"ApprovalStatus": "approved/pending/rejected",
"PriorityLevel": "high/medium/low",
"ReviewComments": "text"}