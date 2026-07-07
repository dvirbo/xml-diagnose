# XML Report Processing System

## Overview

This system processes XML reports from Rashut, extracts relevant information, and updates the Oracle database with report statuses and alert information. The system automatically filters and processes only the reports that match the latest import process.

## What It Does

1. **Reads XML Files**: Processes FirstResponse and FinalResponse XML files from the configured input directory
2. **Filters Reports**: Automatically filters reports based on the latest database import process
3. **Extracts Data**: Parses XML files to extract report status, dates, and other relevant information
4. **Updates Database**: Updates three database tables:
   - `IMP_REPORT_LOG` - Main report information
   - `IMP_REPORT_STATUS_TRACKING` - Status tracking details
   - `actone.alerts` - Alert information
5. **Exports to CSV**: Exports all processed reports to a CSV file with Hebrew column headers (status, error code, error description, report folder, report ID, alert ID)
6. **Logs Everything**: Creates detailed log files for monitoring and troubleshooting

## Installation

### Installing Required Libraries

Since this environment is offline, all required libraries are provided as wheel files in the `libs/` folder. Install them before running the script:

```bash
python3 -m pip install --no-index libs/*.whl
```

This will install all required libraries including:
- `cx_Oracle` - Oracle database connectivity
- `requests` - HTTP library
- `cryptography` - Password encryption
- And other dependencies

**Note**: Make sure you're using Python 3.6, as the libraries are built for this version.

## Quick Start

### Running the Script

The script requires a date parameter in `dd/mm/yyyy` format:

```bash
python3 main.py dd/mm/yyyy
```

**Example**: To process reports for January 1st, 2025:
```bash
python3 main.py 01/01/2025
```

### Input Directory Structure

The system expects XML files in the following structure:
```
Response_From_Rashut_05/
├── FirstResponses/
│   └── 01012025-*.XML
└── FinalResponses/
    └── 01012025-*.XML
```

The date in the filename should match the date parameter you provide when running the script.

## Configuration

All configuration is stored in `config.ini`. The following sections must be configured before running the script:

### [general] Section

```ini
[general]
# General application settings
log_directory = logs                    # Directory where log files are stored
retention_days = 90                     # How long to keep log files (in days)
input_directory = Response_From_Rashut_05  # Base directory containing FirstResponses/ and FinalResponses/ subfolders
export_directory = /var/Reports_To_Send  # Directory for CSV export files
```

**Required Settings:**
- `log_directory`: Directory path for log files (relative to project root)
- `retention_days`: Number of days to keep log files before automatic cleanup
- `input_directory`: Name of the directory containing XML files (must be in project root)
- `export_directory`: Directory path for CSV export files (e.g. `/var/Reports_To_Send`)

### [database] Section

```ini
[database]
# Oracle database configuration
host = localhost                        # Database server hostname or IP
port = 1521                            # Database port (default: 1521)
service_name = FREEPDB1                # Oracle service name
username = MIZRAHI_CUSTOM              # Database username
password_key = custom                  # Key to retrieve password from PasswordManager
batch_size = 1000                      # Number of records to process per batch
timeout = 30                           # Connection timeout in seconds
```

**Required Settings:**
- `host`: Database server address
- `port`: Database port number
- `service_name`: Oracle service name (SID or service name)
- `username`: Database username for main connection
- `password_key`: Key name used to retrieve encrypted password from PasswordManager (not the password itself)
- `batch_size`: Number of records processed in each batch (optional, default: 1000)
- `timeout`: Connection timeout in seconds (optional, default: 30)

### [alerts_db] Section

```ini
[alerts_db]
# Oracle database configuration for ALERTS table (actone user)
# Inherits host, port, service_name from [database] section
username = actone                       # Database username for alerts table
password_key = actone                   # Key to retrieve password from PasswordManager
```

**Required Settings:**
- `username`: Database username for alerts table connection
- `password_key`: Key name used to retrieve encrypted password from PasswordManager

**Note:** This section inherits `host`, `port`, and `service_name` from the `[database]` section. If you need different values, you can override them here.

### Password Management

**Important:** Passwords are stored securely using the PasswordManager system. Before running the script, you must configure passwords using the PasswordManager:

```python
from secure_password_store.password_manager import PasswordManager

pm = PasswordManager()

# Add database password (key must match password_key in [database] section)
pm.add_password('custom', 'your_database_password_here')

# Add alerts database password (key must match password_key in [alerts_db] section)
pm.add_password('actone', 'your_alerts_database_password_here')
```

**Password Keys:**
- The `password_key` values in `config.ini` (`custom` and `actone`) must match the keys used in `PasswordManager.add_password()`
- These keys are used to retrieve the encrypted passwords, not the passwords themselves
- Never store plain-text passwords in `config.ini`

### Configuration Example

Here's a complete example `config.ini`:

```ini
[general]
log_directory = logs
retention_days = 90
input_directory = Response_From_Rashut_05
export_directory = /var/Reports_To_Send

[database]
host = localhost
port = 1521
service_name = FREEPDB1
username = MIZRAHI_CUSTOM
password_key = custom
batch_size = 1000
timeout = 30

[alerts_db]
username = actone
password_key = actone
```

## How It Works

### Processing Flow

1. **Query Report Scope**: Connects to the database and builds the report ID set from two sources:
   - Report IDs from the **latest import process** (`imp_report_processes_log`)
   - Report IDs with **no response at all** in `IMP_REPORT_LOG` (`FIRST_RESPONSE_ORIG IS NULL` and `FINAL_RESPONSE_VALID IS NULL`)
   The union is used for XML filtering so responses for older pending reports are still processed.
2. **Filter XML Files**: Only processes XML files whose report numbers match the combined report ID set
3. **Parse XML**: Extracts data from FirstResponse and FinalResponse XML files
4. **Link Reports**: Links FirstResponse and FinalResponse files by ReportNumber
5. **Update Database**: Updates all three database tables in a single transaction (SAR_FOLDER_NAME is required for export)
6. **Export to CSV**: After the DB update, builds rows for `latest_process_ids ∪ initial_pending_ids` (pending = both response fields NULL at run start). Answered reports show full status (from XML or `IMP_REPORT_LOG`); still-unanswered show placeholder `לא התקבלה תגובה מהרשות`. Header `דיווחים שנשלחו לרשות` = latest process count; `דיווחים שהתקבלו מהרשות` = pending-pool reports that received a Rashut response after update.
7. **Log Results**: Records all operations and results in log files

### Data Extraction

The system extracts the following information from XML files:

- **FirstResponse**: Report validity, received date, legal status description, `ReportInstanceStatusReason`
- **FinalResponse**: Report validity, mispar tkina (status ID), legal status description
- **FirstResponse-only (invalid first, no FinalResponse)**: Processed as a Rashut response; CSV **תיאור שגיאה** uses `ReportInstanceStatusReason`; **סטטוס תגובה סופית** is empty (no second response is sent)
- **Status Classification**: Automatically determines status description based on both responses when both exist

## Logging

Log files are created daily in the `logs/` directory with the format:
```
PipelineProcess_YYYY-MM-DD.log
```

Logs include:
- Processing start/end times
- Number of files processed
- Database update results
- Any errors or warnings
- Detailed debugging information

Old log files are automatically cleaned up based on the retention policy configured in `config.ini`.

## Troubleshooting

### Common Issues

**Error: Date argument is required**
- Make sure you provide the date parameter: `python3 main.py 01/01/2025`

**Error: Date must be in dd/mm/yyyy format**
- Use the correct format: `dd/mm/yyyy` (e.g., `01/01/2025` for January 1, 2025)

**Database connection failed**
- Verify database credentials are set in PasswordManager
- Check `config.ini` for correct database connection settings
- Ensure the database server is accessible

**No reports found from latest process**
- This is a warning, not an error - the system will process all files if no filter is found
- Verify that the latest import process exists in the database

**XML parsing errors**
- Check that XML files match the expected format
- Review log files for specific error messages
- Ensure files are in the correct subdirectories (FirstResponses/ and FinalResponses/)

## Project Structure

```
xml-diagnose/
├── main.py                      # Main entry point
├── sar_feedback.sh              # Shell wrapper for ControlM (passes date as dd/mm/yyyy)
├── config.ini                   # Configuration file
├── core/                        # Core processing logic
│   └── pipeline.py             # Main processing pipeline
├── processors/                  # XML processing
│   ├── xml_parser.py           # XML file parsing
│   └── xml_processor.py        # Report processor
├── database/                    # Database operations
│   ├── connection.py           # Database connections
│   ├── manager.py              # Database manager
│   ├── updater.py              # Update operations
│   └── queries.py              # SQL queries
├── utils/                       # Utilities
│   ├── config_loader.py        # Configuration loading
│   ├── logging_setup.py        # Logging setup
│   └── report_exporter.py      # CSV export for processed reports
└── secure_password_store/       # Password encryption
    └── password_manager.py     # Password management
```

## Support

For issues or questions:
1. Check the log files in `logs/` directory for detailed error messages
2. Verify configuration in `config.ini`
3. Ensure passwords are properly configured in PasswordManager
4. Review database connection settings
