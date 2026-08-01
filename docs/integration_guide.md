# Tours Planning Project - Integration Guide
# Complete Google Sheets & Forms Setup Instructions

## Overview
This guide provides detailed instructions for setting up the complete Tours Planning Project with Google Sheets integration and automated Google Forms.

## Prerequisites

### Required Tools
1. Google account with access to Google Workspace
2. Google Sheets premium (if available) or standard version
3. Code editor (VS Code recommended)
4. Python 3.7+ with required dependencies (see requirements.txt)
5. Administrator access to create Google Forms and Sheets

### Setup Steps

## Step 1: Create Google Sheets Structure

### 1.1 Create Primary Sheets

#### Sheet 1: "Trip_Database"
**Purpose**: Main database for all trip information
**Columns**:
- A: Trip ID (unique identifier)
- B: Timestamp (auto-populated)
- C: Location (Skardu/Hunza/Deosai)
- D: Trip Name
- E: Total Guests
- F: Adults
- G: Children
- H: Infants
- I: Senior Citizens
- J: Booking Date
- K: Travel Dates (Start-End)
- L: Vehicle Type
- M: Vehicle Booked
- N: Seating Capacity
- O: Hotel Name
- P: Room Type
- Q: Room Count
- R: Room Rate
- S: Transport Cost
- T: Driver Name
- U: Driver Phone
- V: excursions_and_activities
- W: Equipment Rental
- X: Insurance Provider
- Y: Total Trip Cost
- Z: Initial Deposit
- AA: Remaining Balance
- AB: Payment Status
- AC: Trip Status
- AD: Emergency Contact
- AE: Emergency Phone
- AF: Contact Email

#### Sheet 2: "Trip_Signups"
**Purpose**: Track individual traveler registrations
**Columns**:
- A: Registration ID
- B: Trip ID (linked to primary sheet)
- C: Traveler Name
- D: Age
- E: Contact Information
- F: Emergency Contact
- G: Special Requirements
- H: Registration Date
- I: Payment Status

#### Sheet 3: "Trip_Financials"
**Purpose**: Complete financial tracking
**Columns**:
- A: Record ID
- B: Trip ID (linked)
- C: Expense Category
- D: Description
- E: Amount
- F: Currency
- G: Payment Date
- H: Payment Method
- I: Budget Category
- J: Approval Status
- K: Expense Date
- L: Vendor
- M: Receipt Attached

#### Sheet 4: "Trip_Logs"
**Purpose**: System logs and tracking
**Columns**:
- A: Log ID
- B: Timestamp
- C: Action Type
- D: User ID
- E: Details
- F: System Response

## Step 2: Create Google Form Structure

### 2.1 Form Configuration

#### Form Name: "Trip Planning & Booking Form"
#### Description: "Complete your trip planning and booking here"

#### Form Settings:
- **Responses**: Collect email addresses, allow multiple responses
- **Limit**: One response per person per trip
- **Language**: English (default)
- **Confirmation**: Show summary and next steps

### 2.2 Form Sections & Questions

#### Section 1: Basic Trip Information
1. **Location**: Multiple choice (Skardu, Hunza, Deosai, Custom)
2. **Trip Name**: Short answer
3. **Trip Dates**: Date range (Start-End)
4. **Number of Guests**: Number (Total, Adults, Children, Infants, Seniors)

#### Section 2: Transportation
1. **Vehicle Type**: Multiple choice (Car, Bus, Private)
2. **Vehicle Company**: Short answer
3. **Seating Capacity**: Number
4. **Driver Name**: Short answer
5. **Driver Phone**: Phone number

#### Section 3: Accommodation
1. **Hotel/AC Name**: Short answer
2. **Room Type**: Multiple choice (Single, Double, Triple, Suite)
3. **Number of Rooms**: Number
4. **Check-in Date**: Date
5. **Check-out Date**: Date
6. **Board Type**: Checkboxes (Half Board, Full Board)
7. **Room Rate**: Currency

#### Section 4: Activities & Excursions
1. **Skardu Sightseeing**: Checkboxes (list of locations)
2. **Hunza Sightseeing**: Checkboxes (list of locations)
3. **Deosai Activities**: Multiple choice (climbing, photography, etc.)
4. **Other Adventures**: Checkboxes (Camel Safari, K2 Climbing, Rafting)

#### Section 5: Equipment Rental
1. **Tents Rental**: Checkboxes
2. **Beds Rental**: Checkboxes
3. **Cookware Rental**: Checkboxes
4. **Generator Rental**: Checkboxes
5. **First Aid Kit**: Checkboxes

#### Section 6: Travel Insurance
1. **Insurance Required**: Yes/No
2. **If Yes**: Provider, Policy Number, Coverage Amount

#### Section 7: Travel Documents
1. **Passport Required**: Yes/No
2. **If Yes**: Passport Number, Visa Required (Yes/No)
3. **If Visa**: Visa Type, Cost, Issue/Expiry Dates

#### Section 8: Emergency & Medical
1. **Emergency Contact**: Name, Phone, Email
2. **Medical Conditions**: Checkboxes (none, diabetes, heart conditions, etc.)
3. **Emergency Kit Required**: Checkboxes
4. **Preferred Hospital**: Short answer
5. **Blood Type**: Multiple choice

#### Section 9: Financial Information
1. **Initial Deposit**: Currency
2. **Payment Method**: Multiple choice (Cash, Card, Bank Transfer)
3. **Accommodation Budget**: Currency
4. **Transportation Budget**: Currency
5. **Activities Budget**: Currency
6. **Equipment Budget**: Currency
7. **Total Trip Budget**: Calculated

#### Section 10: Emergency & Safety
1. **Emergency Contact**: Name, Phone
2. **Emergency Address**: Text
3. **Medical Conditions**: Text
4. **Medications**: Text
5. **Allergies**: Text
6. **Preferred Hospital**: Text
7. **Blood Type**: Dropdown
8. **Emergency Kit**: Yes/No
9. **Safety Briefing**: Yes/No

#### Section 11: System Information
1. **Submission Date**: Auto-populated
2. **User Email**: Auto-populated from Google account
3. **Submission IP**: Auto-populated
4. **Form Version**: Auto-populated

### 2.3 Form Validation Rules

#### Required Fields:
- Location
- Trip Name
- Trip Dates
- Total Guests
- Contact Information
- Payment Details

#### Validation Rules:
- Check-out date > Check-in date
- Seating capacity >= Total guests
- Email format validation
- Phone number format validation
- Amount validation (positive numbers)

### 2.4 Form Integration Setup

#### Auto-population Configuration:
1. **To Google Sheets**:
   - Select existing spreadsheet
   - Set up automatic form response logging
   - Configure data validation rules

2. **Conditional Logic**:
   - Based on Location: Show location-specific questions
   - Based on Vehicle Type: Show appropriate seating questions
   - Based on Insurance: Show insurance details if required

## Step 3: Form to Sheet Integration Setup

### 3.1 Connection Configuration

#### Google Sheets API Setup:
```python
# Client Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = 'your_spreadsheet_id_here'
RANGE_NAME = 'Trip_Database!A:Z'

# API Functions
def append_response(data):
    """Append form response to Google Sheets"""
    service = get_sheets_service()
    # Create row data
    row_data = format_form_data_for_sheet(data)
    # Append to sheet
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={'values': [row_data]}
    ).execute()
    return result
```

### 3.2 Data Formatting Rules

#### Data Cleaning:
1. **Date Formatting**:
   - Convert all dates to YYYY-MM-DD format
   - Handle timezone conversion
   - Validate date sequences

2. **Phone Format**:
   - Remove non-numeric characters
   - Standardize to E.164 format
   - Validate length

3. **Email Validation**:
   - Check domain validity
   - Remove duplicates
   - Mark verification status

4. **Currency Conversion**:
   - Apply appropriate exchange rates
   - Format consistently
   - Convert to base currency

### 3.3 Formulas & Calculations

#### Core Calculations:
**A: Basic Calculations**
```
=ROUNDUP(SUM(F2:H2), 0)  # Total guests
=IF(R2<ROUNDUP(SUM(F2:H2), 0), "Overbooked", "OK")  # Capacity check
=IF(D2="Skardu", SUM(U2,W2), IF(D2="Hunza", V2, IF(D2="Deosai", X2, 0)))  # Location cost
```

**B: Financial Calculations**
```
=Y2+Z2+U2+V2+W2+X2  # Total trip cost calculation
=IF(AA2>0, AB2-AA2, 0)  # Remaining balance
=IF(AC2>0, AB2/AC2*100, 0)  # Payment percentage
```

**C: Date Calculations**
```
=E2-F2  # Trip duration
=IF(G2<TODAY(), "Overdue", "Pending")  # Status check
=IF(H2=0, "Not Started", IF(H2=1, "In Progress", "Completed"))  # Phase tracking
```

**D: Driver Schedule**
```
=IF(AC2=TRUE AND D2<">", "Available", "Assigned")  # Driver availability
=COUNTIF(F2:F1000, E2)  # Trip frequency
```

**E: Equipment Requirements**
```
=IF(T2=TRUE AND SUM(F2:H2)>10, "Large Tent", "Standard Tent")  # Tent size
=IF(V2=TRUE AND SUM(F2:H2)>4, "Extra Beds", "Standard Beds")  # Bed requirements
```

**F: Emergency Fund Calculation**
```
=IF(AD2="High", SUM(F2:H2)*500, IF(AD2="Medium", SUM(F2:H2)*300, SUM(F2:H2)*100))  # Emergency fund
=IF(AG2="Medical", SUM(F2:H2)*50, 0)  # Medical allocation
```

**G: Vehicle Capacity Planning**
```
=ROUNDUP(SUM(F2:H2)/N2, 0)  # Vehicles needed
=IF(O2<ROUNDUP(SUM(F2:H2)/N2), "More Vehicles Needed", "Vehicle Capacity OK")  # Status
```

**H: Budget Tracking**
```
=Y2-AA2  # Budget remaining
=IF(Z2>0, (AB2/AB2+AC2)*100, 0)  # Budget utilization
```

**I: Payment Status**
```
=IF(AB2=AC2, "Paid", IF(AB2>0 && AB2<AC2, "Partial", "Pending"))  # Payment status
=IF(AD2="Approved", "Payment Released", "Payment Held")  # Approval status
```

## Step 4: Advanced Integration Features

### 4.1 Real-time Updates

#### Webhooks Configuration:
```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/form-response', methods=['POST'])
def handle_form_response():
    data = request.json
    # Process form response
    process_trip_form(data)
    return {'status': 'processed'}, 200

def process_trip_form(form_data):
    # Clean and validate data
    cleaned_data = clean_and_validate(form_data)
    # Append to Google Sheets
    append_to_sheets(cleaned_data)
    # Trigger notifications
    send_notifications(cleaned_data)
    # Update dashboard
    update_dashboard(cleaned_data)
```

### 4.2 Conditional Row Coloring

#### Smart Formatting Rules:
```excel
// Critical alerts
=IF(AC2="Cancelled", RED(), IF(AC2="Overbooked", ORANGE(), IF(AC2="Pending", YELLOW(), GREEN())))

// Financial alerts
=IF(AD2<0, RED(), IF(AD2<500, YELLOW(), GREEN()))

// Schedule alerts
=IF(AE2<TODAY(), RED(), IF(AE2-TODAY()<7, ORANGE(), GREEN()))

// Budget alerts
=IF(AF2<0, RED(), IF(AF2<1000, YELLOW(), GREEN()))
```

### 4.3 Dashboard Creation

#### Automated Dashboard:
```excel
// Summary statistics
=COUNTIF(AC2:AC1000, "Confirmed")  // Confirmed trips
=SUM(AF2:AF1000)  // Total revenue
=AVERAGE(AG2:AG1000)  // Average trip cost
=MAX(AI2:AI1000)  // Largest trip size

// Location distribution
=COUNTIF(D2:D1000, "Skardu")  // Skardu trips
=COUNTIF(D2:D1000, "Hunza")   // Hunza trips
=COUNTIF(D2:D1000, "Deosai")  // Deosai trips

// Monthly trends (if dates available)
=SUMIFS(AF2:AF1000, AE2:AE1000, "2024-01-01:*")  // January revenue
=SUMIFS(AF2:AF1000, AE2:AE1000, "2024-02-01:*")  // February revenue
```

## Step 5: Automation & Scheduling

### 5.1 Backup and Recovery

#### Automated Backups:
```python
import schedule
import time

def daily_backup():
    # Export current data
    export_to_csv()
    # Create backup copy
    create_backup_copy()
    # Send notification
    send_backup_notification()

def weekly_backup():
    # Full database backup
    full_backup()
    # Generate report
    generate_backup_report()

def monthly_backup():
    # Archive old data
    archive_old_data()
    # Clean temporary files
    cleanup_temp_files()

# Schedule backups
schedule.every().day.at("02:00").do(daily_backup)
schedule.every().sunday.at("23:59").do(weekly_backup)
schedule.every().last_day_of_month.at("23:59").do(monthly_backup)
```

### 5.2 Automated Calculations

#### Real-time Update Triggers:
```python
def update_calculations():
    # Update all formulas in real-time
    update_trip_totals()
    # update_vehicle_requirements()  # Now auto-assigned
    update_budget_allocations()
    update_payment_status()
    update_emergency_requirements()

def update_trip_totals():
    # Recalculate trip totals
    query_sheets_for_changes()
    apply_formulas()
    save_updates()
```

## Step 6: Security & Access Control

### 6.1 Data Protection

#### Access Levels:
1. **Admin**: Full access, edit all data
2. **Manager**: Edit trips, view financials, manage bookings
3. **Staff**: View only, submit forms
4. **Travelers**: View own data only

#### Security Measures:
- Row-level security based on user roles
- Data encryption for sensitive fields
- Audit trails for all changes
- Backup and recovery procedures

### 6.2 User Management

#### Role-Based Access:
```python
USER_ROLES = {
    'admin': ['full', 'read', 'write', 'delete', 'manage_users'],
    'manager': ['read', 'write', 'view_financials', 'manage_bookings'],
    'staff': ['read', 'write', 'submit_forms'],
    'traveler': ['read_own_data', 'submit_forms']
}
```

## Step 7: Testing & Validation

### 7.1 Test Coverage

#### Automated Tests:
1. **Form Testing**: Test all form fields and validation
2. **Data Integrity**: Test calculations and formulas
3. **Integration Testing**: Test form-to-sheet sync
4. **Security Testing**: Test access controls
5. **Performance Testing**: Test with large datasets

#### Test Scripts:
```python
# Form testing
def test_form_validation():
    # Test required fields
    # Test validation rules
    # Test conditional logic
    pass

# Data integrity testing
def test_calculations():
    # Test financial calculations
    # Test capacity planning
    # Test date validations
    pass

# Integration testing
def test_form_to_sheet():
    # Test data transfer
    # Test error handling
    # Test duplicate prevention
    pass
```

## Step 8: Documentation & Training

### 8.1 User Documentation

#### Quick Start Guide:
1. Access the Google Form
2. Fill in basic trip information
3. Complete all required sections
4. Review and submit
5. Receive confirmation and next steps

#### FAQ Section:
- How to edit submitted data?
- How to cancel a trip?
- How to add additional travelers?
- How to update payment status?

### 8.2 Admin Documentation

#### Admin Guide:
1. How to manage Google Forms
2. How to configure automated calculations
3. How to handle data imports/exports
4. How to manage user access
5. How to troubleshoot issues

## Step 9: Troubleshooting

### 9.1 Common Issues

#### Issue 1: Form Not Submitting
**Solution**: Check Google account permissions, verify form settings

#### Issue 2: Data Not Auto-populating
**Solution**: Check API credentials, verify spreadsheet access

#### Issue 3: Formula Errors
**Solution**: Validate input data, check formula syntax

#### Issue 4: Performance Issues
**Solution**: Optimize sheet formulas, consider data filters

### 9.2 Error Handling

#### Error Logging:
```python
def log_error(error_type, error_message, context):
    # Log to Google Sheets
    # Send notification to admin
    # Store for troubleshooting
    pass
```

## Implementation Checklist

### Pre-Launch:
- [ ] Google Sheets created with all required sheets
- [ ] Google Form created with all questions
- [ ] Form-to-sheet integration configured
- [ ] Data validation rules applied
- [ ] Security and access controls set up
- [ ] Backup schedules configured
- [ ] Test data populated (if needed)
- [ ] User training materials prepared
- [ ] Support contact information added

### Post-Launch:
- [ ] Monitor first 24 hours for issues
- [ ] Collect user feedback
- [ ] Optimize performance based on usage
- [ ] Schedule regular maintenance
- [ ] Update documentation as needed

## Contact & Support

### Technical Support:
- **Email**: adam@example.com
- **Phone**: +92-300-1234567
- **Slack**: #tours-planning

### Emergency Contact:
- **24/7 Support**: +92-300-9876543

---

*This guide was generated on $(date)
Last Updated: $(date)
Status: Ready for Implementation
Team: Tours Planning Project
Version: 1.0*"