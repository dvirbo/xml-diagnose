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
- **Logging**: Configured to `mizrahi.txt` with UTF-8 encoding (supports Hebrew)