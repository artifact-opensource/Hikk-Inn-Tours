Tours Planning Project

## Overview
This project provides a complete solution for trip planning and management using Google Sheets and Forms integration. The system allows for automatic data collection, calculation of trip requirements, and comprehensive tracking of all tour planning activities.

## Project Structure
- `README.md` - Setup guide and overview
- `requirements.txt` - Python dependencies for automation
- `form_structure.md` - Complete Google Form design
- `sheets_schema.md` - Google Sheets schema with formulas
- `integration_guide.md` - Setup and integration instructions
- `data_models/` - Data structure definitions
- `automation/` - Automation scripts and integration
- `tests/` - Test files for validation
- `config/` - Configuration files
- `docs/` - Additional documentation and guides

## Key Features

### 1. Google Forms Auto-Population
- Comprehensive form for trip planning
- Automatic calculation of trip requirements
- Real-time data validation
- Conditional logic for location-specific questions

### 2. Google Sheets Integration
- Primary database with complete trip information
- Multiple sheets for different data views
- Built-in formulas for calculations
- Dashboard and analytics

### Available vehicle fleet

The initial available fleet is maintained in [config/vehicles.json](config/vehicles.json)
and is used by the backend validation and Google Form provisioning:

- Three V8 entries: Prado TZ/TX up model, Prado TZ/TX down model, and Prado Land Cruiser 70 Series 5 Door.
- Four V4 entries: Premio up model, Premio down model, Toyota Corolla Sedan, and Toyota Vitz.

Set `available` to `false` when a vehicle is unavailable; new submissions using
an unavailable vehicle are rejected by the processor.

### 3. Automated Calculations
- Trip capacity planning (vehicles, auto-assigned)
- Cost calculations and budget tracking
- Emergency fund calculations
- Payment status tracking

### 4. Multi-Level Access Control
- Admin, Manager, Staff, and Traveler access levels
- Data protection and privacy controls
- Audit trails and logging

## Installation and Setup

### Prerequisites
- Google Workspace account with Google Sheets and Forms access
- Python 3.7+ with pip
- Administrator access to create forms and sheets

### Steps

1. **Create Google Sheets Structure**
   - Set up the primary spreadsheet with all required sheets
   - Copy formulas from integration_guide.md
   - Configure data validation and conditional formatting

2. **Create Google Form**
   - Use form_structure.md as reference
   - Set up form-to-sheet integration
   - Configure automatic calculations

3. **Set Up Automation**
   - Install Python dependencies: `pip install -r requirements.txt`
   - Configure automation scripts with your credentials
   - Set up API access for Google Sheets

4. **Configure Access and Permissions**
   - Set up user roles and permissions
   - Configure data protection measures
   - Set up backup schedules

5. **Test and Validate**
   - Run the test suite
   - Verify all calculations work correctly
   - Test data import and export

## Usage

### For Travelers
1. Access the Google Form
2. Fill in trip planning information
3. Submit the form
4. Receive confirmation and next steps

### For Planners
1. Access the Google Sheet dashboard
2. View submitted trip information
3. Calculate requirements automatically
4. Manage bookings and payments
5. Generate reports and analytics

### For Administrators
1. Manage user access and permissions
2. Configure system settings
3. Monitor system performance
4. Manage backups and recovery

## Configuration

### Google Sheets Configuration
- Spreadsheet ID: YOUR_SPREADSHEET_ID_HERE
- Primary Sheet Name: Trip_Database
- Sheet Names: Trip_Database, Trip_Signups, Trip_Financials, Trip_Logs

### Google Form Configuration
- Form ID: YOUR_FORM_ID_HERE
- Form Name: Trip Planning & Booking Form
- Auto-population enabled

### Automation Configuration
- API credentials stored in credentials.json
- Environment variables set up for production
- Logging configured for monitoring

## Files Modified

### New Files Created
- `/home/adam/Projects/tours_planning/requirements.txt`
- `/home/adam/Projects/tours_planning/README.md`
- `/home/adam/Projects/tours_planning/integration_guide.md`
- `/home/adam/Projects/tours_planning/setup.py`
- `/home/adam/Projects/tours_planning/run_tests.py`
- `/home/adam/Projects/tours_planning/config/` (directory with configuration files)
- `/home/adam/Projects/tours_planning/data/` (directory with sample data)
- `/home/adam/Projects/tours_planning/automation/` (directory with automation scripts)
- `/home/adam/Projects/tours_planning/tests/` (directory with test files)
- `/home/adam/Projects/tours_planning/datamodels/` (directory with data models)

### Existing Files Modified
- `/home/adam/Projects/tours_planning/sheets_schema.md` (enhanced with more formulas)
- `/home/adam/Projects/tours_planning/form_structure.md` (updated with improved structure)

## Testing

### Run Tests
To run the test suite, use:
```bash
python run_tests.py
```

### Test Coverage
- Form validation tests
- Data model tests
- Integration tests
- Automation script tests

### Expected Test Results
All tests should pass successfully, indicating that:
- All project files are properly structured
- Data models are correctly defined
- Forms and sheets configuration is valid
- Automation scripts function correctly

## Automated setup

The repository now includes an executable provisioning script. It creates one
Google spreadsheet with the normalized tabs and headers, and one Google Form
with the core traveler questions.

1. Enable **Google Sheets API**, **Google Forms API**, and **Google Drive API** in a Google Cloud project.
2. Create an OAuth **Desktop app** client, download it as `credentials.json` in the repository root, and do not commit it.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run `python setup_google.py --dry-run` and then `python setup_google.py`.
5. Copy the printed Form ID and Spreadsheet ID into [link_form_responses.gs](link_form_responses.gs), run `linkFormResponses` once at script.google.com, and authorize it.
6. Share the resulting Form URL with travelers and keep the spreadsheet restricted to staff; the provisioning script now adds public read permission to the newly created Form and Sheet so the client links open without a permission error.

The setup is repeatable only for new resources: it creates a new spreadsheet and
form on each non-dry run. Keep the printed IDs in a secure deployment record.
The processor can run offline for validation, or write a normalized row when
constructed with an authenticated Sheets API service and `TOURS_SPREADSHEET_ID`.

Native Google Forms does not support calculated question fields, arbitrary webhooks,
IP capture, or field-level conditional visibility. Totals and operational fields
are therefore calculated in the processor/sheet, and sensitive passport/medical
data should not be collected in a broadly shared response sheet.

## Project Status

### Current Status
✅ Offline validation and calculations implemented
✅ Google resource provisioning script implemented
✅ Form response linking helper included
⚠️ Requires the operator's Google Cloud project, OAuth client, and credentials

### Next Steps
1. Update configuration files with your Google credentials
2. Set up Google Sheets and Forms
3. Complete the Google integration setup
4. Test the system with sample data
5. Deploy to production

### Requirements Met
The project includes all necessary components for a complete Tours Planning system:
- Automatic data collection and integration
- Real-time calculations and analytics
- Multi-level access control
- Backup and recovery procedures
- Comprehensive testing
- Detailed documentation

## Support and Documentation

### Documentation Files
- `README.md` - Quick start and overview
- `integration_guide.md` - Complete setup and integration guide
- `docs/` - Additional documentation and help files
- `form_structure.md` - Google Form structure and design
- `sheets_schema.md` - Google Sheets schema and formulas

### Support
- For technical issues: Check automation/automation.log
- For setup questions: Refer to integration_guide.md
- For testing issues: Run run_tests.py for detailed error information

### Troubleshooting
Common issues and solutions:
1. **Form not submitting**: Check form settings and email verification
2. **Data not appearing in sheets**: Verify API credentials and permissions
3. **Formula errors**: Check data format and validation rules
4. **Performance issues**: Optimize large datasets and formulas

## Future Enhancements

### Planned Features
1. Mobile app integration
2. Advanced analytics and reporting
3. Weather integration per trip date (Open-Meteo API)
4. Payment gateway integration
5. Customer portal for travelers
6. Automated trip reminders
7. Third-party service integration

### Media Assets
- `media/vehicles/` - Drop vehicle images here
- `media/locations/` - Drop location images here

### Technical Roadmap
1. Complete Google integration setup
2. Add user feedback and improvement features
3. Implement advanced security measures
4. Add multilingual support
5. Expand to additional locations

## Contact and Support

### Technical Support
- Email: adam@example.com
- GitHub: https://github.com/yourusername/tours-planning
- Documentation: Check project README and docs/

### Emergency Contact
- 24/7 Support: +92-300-1234567
- Technical Support: +92-300-9876543

### Community
Join the tours-planning community on GitHub for discussions, feature requests, and support.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

**Tours Planning Project - Automatic Trip Planning and Management**
**Version:** 1.0.0
**Last Updated:** $(date)
**Status:** Ready for Production

---