# Export Report Functionality - Implementation Plan

## Requirements

### 1. Export Location
- Export folder path defined in `config.ini`
- Create export folder if it doesn't exist
- Export files with date-based naming

### 2. Report Structure
Two separate CSV files:
- **Valid Reports** (approved/proper approval): `reports_valid_YYYYMMDD_HHMMSS.csv`
- **Error Reports** (with errors): `reports_errors_YYYYMMDD_HHMMSS.csv`

### 3. Required Fields in CSV

For each report, export the following fields:

1. **Report ID** (Report Number) - From `ReportNumber`
2. **Alert ID** - From database (`alert_id`)
3. **SAR Folder Name** - From database (`SAR_FOLDER_NAME`)
4. **First Response Data** - Summary or key fields from FirstResponse
5. **Final Response Data** - Summary or key fields from FinalResponse
6. **Error Code** - From FinalResponse (`ErrorCode`)
7. **Error Description** - From FinalResponse (`ReportInstanceStatusReason`)
8. **Status** - Status category (e.g., "דיווח תקין", "דיווח לא תקין")

### 4. Classification Logic

**Valid Reports** (export to `reports_valid_*.csv`):
- Reports where `status_category == "דיווח תקין"` (both first and final responses are valid)

**Error Reports** (export to `reports_errors_*.csv`):
- All other status categories:
  - "דיווח לא תקין"
  - "FIRST_VALID_FINAL_INVALID"
  - "FIRST_INVALID_FINAL_VALID"
  - "MISSING_FIRST_RESPONSE"

### 5. Data Sources

- **Report Data**: Already available in `processed_report` objects
- **Database Fields**: `alert_id`, `SAR_FOLDER_NAME` - already fetched during database update
- **Error Data**: Available in `FinalResponse` dictionary:
  - `ErrorCode`: From `FinalResponse['ErrorCode']`
  - `ReportInstanceStatusReason`: From `FinalResponse['ReportInstanceStatusReason']`

## Implementation Steps

### Step 1: Configuration
- Add `export_directory` to `config.ini` [general] section

### Step 2: Create Export Module
- Create `utils/report_exporter.py`:
  - `export_reports_to_csv(reports, export_dir, date_filter)`
  - Split reports into valid/error categories
  - Generate CSV files with required fields
  - Handle encoding (UTF-8 for Hebrew text)

### Step 3: Integration
- Update `core/pipeline.py`:
  - Call export function after database updates
  - Use `result.summary_reports` (contains report_id, alert_id, sar_folder_name)
  - Combine with original report data for export

### Step 4: CSV Format
- Use Python's `csv` module (built-in, no dependencies)
- UTF-8 encoding with BOM for Excel compatibility
- Headers in first row
- One report per row

## Questions for Clarification

1. **Email Integration**: 
   - Should we implement email sending now, or just create the CSV files first?
   - What email system should we use? (SMTP, specific service?)

2. **First/Final Response Data**:
   - Should we export all fields from FirstResponse and FinalResponse?
   - Or just key fields? Which fields are most important?

3. **File Format**:
   - CSV is good, or prefer Excel (.xlsx)? (CSV is simpler, Excel requires openpyxl library)

4. **Export Timing**:
   - Export after database updates? (recommended - we have all data including DB fields)
   - Or export before database updates?

5. **File Naming**:
   - Include timestamp? (e.g., `reports_valid_20260114_123045.csv`)
   - Or just date? (e.g., `reports_valid_20260114.csv`)

## Next Steps

Once we clarify the questions above, I'll implement:
1. Configuration setup
2. Export module
3. Integration into pipeline
4. Testing
