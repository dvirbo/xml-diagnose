# Alert Update Implementation - SQL-Based

## Summary

Alert updates have been migrated from REST API to SQL-based updates. Alerts are now updated directly in the `actone.alerts` table via SQL UPDATE statements.

## Changes Made

### 1. Configuration (`config.ini`)
- Added `[alerts_db]` section with:
  - `host = localhost`
  - `port = 1521`
  - `service_name = FREEPDB1`
  - `username = actone`
  - `password_key = AlertDB`

### 2. Password Manager Setup
**IMPORTANT**: You need to add the AlertDB password to PasswordManager:
```bash
cd /opt/xml-diagnose
python3.6 -c "from secure_password_store.password_manager import PasswordManager; pm = PasswordManager(); pm.add_password('AlertDB', 'ActOne123')"
```

### 3. Database Connection (`database/connection.py`)
- Added `connect_to_alerts_database()` function
- Creates separate connection to `actone` user database

### 4. SQL Queries (`database/queries.py`)
- Added `UPDATE_ALERT` query:
```sql
UPDATE actone.alerts 
SET p17 = :1, p18 = :2, p19 = :3 
WHERE alert_id = :4
```

### 5. Database Updater (`database/updater.py`)
- Added `_prepare_alert_update()` method to prepare alert update data
- Modified `_execute_bulk_updates()` to handle alert updates
- Alert updates are executed in the same flow as report log updates
- Committed after main transaction (separate connection, but sequential commits)

### 6. Pipeline (`core/pipeline.py`)
- Removed REST API alert update code
- Alerts are now updated automatically during database update process

### 7. API Folder
- Moved `api/` folder to `api_old/` (kept for reference, not deleted)

## Field Mapping

| Source (from XML/Report Data) | Target Column | Description |
|-------------------------------|---------------|-------------|
| `status_category` | `p17` | Status description (e.g., "דיווח תקין", "דיווח לא תקין") |
| `mispar_tkina` (from FinalResponse) | `p18` | Status ID from XML |
| `report_number` (without leading zeros) | `p19` | Report number |

**Data Types**: All fields are `VARCHAR2(50)`

## Error Handling

- If `alert_id` doesn't exist in `actone.alerts`, the UPDATE will execute but update 0 rows (no error)
- If alert update fails (SQL error), it logs an error/warning and continues with the main transaction
- Individual alert failures don't prevent report log updates from completing

## Transaction Flow

1. Connect to main database (MIZRAHI_CUSTOM user)
2. Connect to alerts database (actone user)
3. Prepare all updates (report log, status tracking, alerts)
4. Execute bulk updates:
   - Update IMP_REPORT_LOG
   - Insert into IMP_REPORT_STATUS_TRACKING
   - Update actone.alerts (if connection available)
5. Commit main transaction
6. Commit alerts transaction
7. Close connections

## Testing

To test the implementation:

1. Ensure password is added to PasswordManager (see above)
2. Run the pipeline:
```bash
cd /opt/xml-diagnose
python3.6 main.py 01012025
```

3. Check logs for:
   - "Updated X records in actone.alerts" (success)
   - Any error messages about alert updates

## Notes

- Alert updates use batch processing (same as report log updates)
- If alerts connection fails, the pipeline continues with report log updates only
- The `api_old/` folder contains the old REST API implementation for reference
