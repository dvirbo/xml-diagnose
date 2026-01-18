# XML Diagnose Pipeline - Program Flow

This document describes the complete execution flow of the XML Diagnose Pipeline from start to finish.

## Entry Point: `main.py`

### 1. Initialization Phase
```
main() function
├── setup_logging()           # Configure logging system
├── cleanup_logs()            # Remove old log files (> 90 days)
└── load_config()             # Load configuration from config.ini
```

### 2. Pipeline Creation
```
Input: reports/Response_From_Rashut_05
├── Creates XMLDiagnosePipeline instance
├── Initializes XMLReportProcessor (for XML parsing)
├── Initializes DatabaseManager (for database operations)
└── Initializes AlertUpdater (for API updates)
```

---

## Main Pipeline: `core/pipeline.py` → `run()`

### Step 1: XML Processing
```
xml_processor.process_xml_files()
├── parse_xml_files(directory)
│   ├── Reads FirstResponses/ subfolder
│   │   └── Parses each XML file with <FirstResponse> root tag
│   │       └── Extracts: ReportNumber, ReportDate, ReportInstanceDate, 
│   │                     ReportInstanceLegalStatusDesc, etc.
│   └── Reads FinalResponses/ subfolder
│       └── Parses each XML file with <FinalResponse> root tag
│           └── Extracts: ReportNumber, ReportInstanceReference,
│                         ReportInstanceLegalStatusDesc, mispar_tkina, etc.
│
└── link_responses(first_responses, final_responses)
    └── Links by ReportNumber
    └── Determines status:
        ├── first_response_valid (FIR valid?)
        ├── final_response_valid (FIN valid?)
        ├── overall_valid (both valid?)
        └── status_category (one of: "דיווח תקין", "דיווח לא תקין", 
                             "MISSING_FIRST_RESPONSE", etc.)
    
Returns: Dictionary of combined reports {ReportNumber: {FirstResponse, FinalResponse, Status}}
```

### Step 2: Database Updates
```
db_manager.connect()
└── connect_to_database()
    └── Establishes Oracle connection (cx_Oracle)
    └── Uses credentials from config.ini [database] section

db_manager.update_reports(all_reports)
└── update_db(connection, reports)
    └── DatabaseUpdater.update_database_bulk(reports)
        ├── For each report:
        │   ├── SELECT report_id, alert_id FROM IMP_REPORT_LOG 
        │   │   WHERE report_id = :1
        │   │   (Lookup report in database)
        │   │
        │   ├── UPDATE IMP_REPORT_LOG SET
        │   │       report_date = :1
        │   │       first_response_valid = :2
        │   │       final_response_valid = :3
        │   │       received_date = :4 (from ReportInstanceDate - FIR)
        │   │       mispar_tkina = :5 (from FinalResponse)
        │   │       status_desc = :6
        │   │   WHERE report_id = :7
        │   │
        │   └── INSERT INTO IMP_REPORT_STATUS_TRACKING
        │       (Report_id, alert_id, update_date, status, 
        │        tech_comment, buiss_comment)
        │       VALUES (:1, :2, :3, :4, :5, :6)
        │       WHERE:
        │       - update_date = System date/time
        │       - tech_comment = ReportInstanceLegalStatusDesc (FIR)
        │       - buiss_comment = ReportInstanceLegalStatusDesc (FIN)
        │
        └── Executes in batches (default: 1000 records per batch)
        
Returns: List of updated reports with report_id and alert_id
```

### Step 3: API Alert Updates
```
alert_updater.initialize_session()
└── login_and_get_session()
    ├── Reads API config from config.ini [api] and [credentials] sections
    ├── POST to /public/v1/auth/login
    └── Returns authenticated requests.Session object

alert_updater.update_alerts(all_reports)
└── For each report in all_reports:
    └── process_alert(session, report_data)
        ├── Extracts alert_id from report data
        ├── POST to /v1/alerts/{alert_id}/update
        │   └── Sends status update via REST API
        └── Returns success/failure
```

### Step 4: Cleanup (Finally Block)
```
finally:
├── db_manager.close()
│   └── connection.close()    # Close Oracle database connection
│
└── end_session(session)
    ├── POST to /v1/auth/logout
    └── session.close()       # Close HTTP session
```

---

## Data Flow Summary

```
XML Files (FirstResponses/ + FinalResponses/)
    ↓
XML Parser (parse_xml_files)
    ↓
Linked Reports Dictionary (by ReportNumber)
    ↓
Database Updates (IMP_REPORT_LOG UPDATE + IMP_REPORT_STATUS_TRACKING INSERT)
    ↓
API Alert Updates (REST API POST requests)
    ↓
Pipeline Complete
```

## Key Data Structures

### Input
- **Directory Structure**: `Response_From_Rashut_05/`
  - `FirstResponses/*.XML` - FirstResponse XML files
  - `FinalResponses/*.XML` - FinalResponse XML files

### Processed Report Structure
```python
{
    "ReportNumber": "251531",
    "FirstResponse": {
        "ReportDate": "...",
        "ReportInstanceDate": "...",
        "ReportInstanceLegalStatusDesc": "...",
        "valid": True/False,
        ...
    },
    "FinalResponse": {
        "ReportInstanceReference": "...",
        "ReportInstanceLegalStatusDesc": "...",
        "mispar_tkina": "...",
        "valid": True/False,
        ...
    },
    "Status": {
        "first_response_valid": True/False,
        "final_response_valid": True/False,
        "overall_valid": True/False,
        "status_category": "דיווח תקין" | "דיווח לא תקין" | ...
    }
}
```

### Database Updates
- **IMP_REPORT_LOG**: Updated with report status, dates, validation flags
- **IMP_REPORT_STATUS_TRACKING**: New record inserted with tech/business comments

---

## Error Handling

1. **XML Parsing Errors**: Logged as warnings, file skipped
2. **Database Connection Failures**: Pipeline stops, no database updates
3. **API Session Failures**: Pipeline continues but skips API updates
4. **Database Update Errors**: Logged, batch processing continues
5. **All errors logged to**: `logs/PipelineProcess_YYYY-MM-DD.log`

---

## Configuration Files

- **config.ini**: Central configuration
  - `[general]`: Log directory, retention days
  - `[database]`: Oracle connection details
  - `[api]`: API endpoints
  - `[credentials]`: API authentication
  - `[logging]`: Log messages
