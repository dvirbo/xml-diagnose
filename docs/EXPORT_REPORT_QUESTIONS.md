# Export Report Functionality - Clarification Questions (Saved for Later)

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
