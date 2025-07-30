# XML Report Processing System

## Overview

This system processes XML reports, classifies them by status, exports results to CSV, updates a database, and manages alerts.
The main entry point is `main.py`, which manages the entire pipeline through `XMLDiagnosePipeline`.

## System Architecture

### Main Components
- **Main Pipeline**: `XMLDiagnosePipeline` - Manages the entire processing workflow
- **XML Processing**: `XMLReportProcessor` - Handles XML parsing and classification
- **Database Operations**: `DatabaseManager` - Manages database connections and updates
- **Alert Management**: `AlertUpdater` - Handles alert updates via API
- **Report Classification**: `classify_reports_by_status` - Classifies reports based on legal status

### Processing Flow
`XML Files → Parse → Classify → Export CSV → Update DB → Update Alerts`

## Data Flow

### Input
- XML files from `reports` directory
- Configuration from `config.py`

### Processing Steps
- **XML Parsing**: Parse `FirstResponse` and `FinalResponse` XML files
- **Classification**: Combine and classify reports by legal status
- **CSV Export**: Generate timestamped CSV files in the `csv` directory
- **Database Update**: Store valid and error reports in the database
- **Alert Updates**: Update the relevant alerts in ActOne via Rest API

### Output
- Error reports CSV
- Valid reports CSV
- Database updates
- Alert updates
- Comprehensive logging to a log file

## Error Handling
- Database connection failures are logged, and processing continues
- Alert update failures are logged, but don't stop the pipeline
- XML parsing errors are handled gracefully
- Comprehensive logging throughout the system

## Configuration
- **Input directory**: Configurable via `main()` (default: `reports`)
- **Export directory**: Auto-created as `{input_directory}/exported_reports`
- **Logging**: Configured to `PipelineProcess.log` with UTF-8 encoding (supports Hebrew)


# How to Run Password Manager

## Prerequisites
- Python 3.6 or higher
- Install the cryptography library:
```bash
pip install cryptography
```

## Setup
1. Save the password manager code as `password_manager.py`
2. Run the script - it will automatically create the necessary files:
   - `secret.key` (encryption key)
   - `passwords.json` (encrypted password storage)

## Usage Example
```python
from password_manager import PasswordManager

# Create password manager instance
pm = PasswordManager()

# Add passwords
pm.add_password("gmail", "mySecretPassword123")
pm.add_password("facebook", "anotherPassword456")

# Retrieve passwords
password = pm.get_password("gmail")
print(f"Gmail password: {password}")
```

## Important Notes
- Keep `secret.key` file secure - if lost, passwords cannot be recovered
- The script creates files in the same directory as the Python file
- Passwords are encrypted using Fernet symmetric encryption
- Each identifier must be unique

## File Structure
```
your_project/
├── password_manager.py
├── secret.key (auto-generated)
└── passwords.json (auto-generated)
```

## How to Run

### Prerequisites
- Python 3.6 or higher
- Required dependencies:
  ```bash
  pip install requests
  ```
### Quick Start
1. Navigate to the project directory
   ```bash
   python main.py
   ```

2. Run the application
   ```bash
   python main.py
   ```
3. Enter the report date

   - When prompted, enter the date in ddmmyyyy format
   Example: 13072025 for July 13, 2025
   Check the results

4. Check the results
   - CSV files will be generated in the csv/ directory
   Logs will be saved to logs/PipelineProcess.log
   Database and alerts will be updated automatically