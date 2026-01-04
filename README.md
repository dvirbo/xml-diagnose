# XML Report Processing System

## Overview

This system processes XML reports, classifies them by status, exports results to CSV, updates a database, and manages alerts.
The main entry point is `main.py`, which manages the entire pipeline through `XMLDiagnosePipeline`.

## Project Structure

```
xml-diagnose/
├── main.py                      # Main entry point
├── config.ini                   # Unified configuration file
├── requirements.txt             # Python dependencies (Python 3.6 compatible)
├── libs/                        # Local wheel files for offline installation
│   └── README.md                # Installation instructions
├── core/                        # Core processing modules
│   └── pipeline.py              # Main processing pipeline
├── utils/                       # Utility modules
│   ├── config_loader.py         # Configuration loading
│   └── logging_setup.py         # Logging setup and cleanup
├── processors/                  # XML processing modules
│   ├── xml_parser.py            # XML file parsing (FirstResponse/FinalResponse)
│   └── xml_processor.py         # XML report processor
├── database/                    # Database modules
│   ├── config.py                # Database configuration
│   ├── connection.py            # Database connection management
│   ├── manager.py               # Database manager
│   ├── updater.py               # Database update operations
│   └── queries.py               # SQL queries
├── api/                         # API modules for alert updates
├── secure_password_store/       # Password encryption/decryption
├── soap/                        # SOAP service modules (optional)
└── reports/                     # Input XML reports directory
```

## System Architecture

### Main Components
- **Main Pipeline**: `core.pipeline.XMLDiagnosePipeline` - Manages the entire processing workflow
- **XML Processing**: `processors.xml_processor.XMLReportProcessor` - Handles XML parsing and classification
- **XML Parser**: `processors.xml_parser` - Parses FirstResponse and FinalResponse XML files
- **Database Operations**: `database.manager.DatabaseManager` - Manages database connections and updates
- **Alert Management**: `api.alert_updater.AlertUpdater` - Handles alert updates via API

### Processing Flow
`XML Files → Parse → Classify → Export CSV → Update DB → Update Alerts`

## Installation

### Prerequisites
- Python 3.6.8
- ODBC Driver for SQL Server
- Required Python packages (see requirements.txt)

### Installing Libraries (Offline)

Since this environment has no internet access:

1. Download wheel files (`.whl`) for Python 3.6 and Linux x86_64 from a machine with internet access
2. Transfer all wheel files to the `libs/` folder using WinSCP
3. Install libraries:
   ```bash
   python3.6 -m pip install --no-index libs/*.whl
   ```

See `libs/README.md` for detailed instructions on which libraries to download.

### Required Libraries
- pyodbc==4.0.39
- requests==2.27.1
- cryptography==3.4.8
- certifi, charset-normalizer==2.0.12, idna==3.3, urllib3==1.26.18

## Usage

### Running the Pipeline

```bash
python3.6 main.py
```

The script will:
1. Set up logging
2. Process XML files from the configured reports directory
3. Update the database with report statuses
4. Update alerts via API

### Configuration

Edit `config.ini` to configure:
- `log_directory`: Directory for log files
- `retention_days`: How long to keep log files
- `reports`: Base directory for report folders

### Input Format

XML files should be placed in date-specific folders under the reports directory:
```
reports/
└── 01_01_2025/
    ├── FirstResponse_*.XML
    └── FinalResponse_*.XML
```

**Filename format**: `ReportDate-?-UAR-ST-ReportNumber-ReportInstanceReference.FinR.XML`

## Data Flow

### Input
- XML files from `reports` directory (organized by date)
- Configuration from `config.ini`

### Processing Steps
1. **XML Parsing**: Parse `FirstResponse` and `FinalResponse` XML files
2. **Classification**: Combine and classify reports by legal status
3. **Database Update**: Store report statuses in the database
4. **Alert Updates**: Update the relevant alerts in ActOne via REST API

### Output
- Database updates (IMP_REPORT_LOG, IMP_REPORT_STATUS_TRACKING tables)
- Alert updates in ActOne system
- Comprehensive logging to log files

## Error Handling
- Database connection failures are logged, and processing continues where possible
- Alert update failures are logged, but don't stop the pipeline
- XML parsing errors are handled gracefully
- Comprehensive logging throughout the system

## Logging
- Log files are created daily in the configured log directory
- Format: `PipelineProcess_YYYY-MM-DD.log`
- Old log files are automatically cleaned up based on retention policy
- Logs support Hebrew characters (UTF-8 encoding)

## Development Notes

### Python 3.6 Compatibility
This project is specifically designed for Python 3.6.8 compatibility:
- Uses regular classes instead of dataclasses
- Compatible library versions specified in requirements.txt
- All code tested with Python 3.6 syntax

### File Naming Convention
- Core modules in `core/`
- Utility functions in `utils/`
- Processing logic in `processors/`
- Database operations in `database/`

See `MIGRATION_SUMMARY.md` for details on recent project reorganization.

## Troubleshooting

### Database Connection Issues
- Verify ODBC Driver is installed
- Check `database/config.py` for correct server settings
- Ensure password is set in secure password store

### Missing Libraries
- Verify all wheel files are in `libs/` folder
- Re-run: `python3.6 -m pip install --no-index libs/*.whl`
- Check `libs/README.md` for required library versions

### XML Parsing Errors
- Check XML file format matches expected structure
- Verify files have correct root tags (FirstResponse/FinalResponse)
- Check log files for detailed error messages
