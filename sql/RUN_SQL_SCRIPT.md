# How to Run SQL Scripts

## Running `imp_report_log.sql`

This SQL script creates the `IMP_REPORT_LOG` table in Oracle database.

### Method 1: Using sqlplus (Command Line)

Using the database credentials from `config.ini`:

```bash
cd /opt/xml-diagnose
sqlplus MIZRAHI_CUSTOM/IfsOra123@localhost:1521/FREEPDB1 @sql/imp_report_log.sql
```

**Note**: If you're using PasswordManager for the database password, you'll need to retrieve it first:

```bash
cd /opt/xml-diagnose
python3.6 -c "from secure_password_store.password_manager import PasswordManager; pm = PasswordManager(); print(pm.get_password('OracleDB'))"
```

Then use the retrieved password in the sqlplus command.

### Method 2: Interactive sqlplus

1. Connect to the database:
```bash
sqlplus MIZRAHI_CUSTOM/IfsOra123@localhost:1521/FREEPDB1
```

2. Once connected, run the script:
```sql
@sql/imp_report_log.sql
```

Or if you're already in the sqlplus session:
```sql
@/opt/xml-diagnose/sql/imp_report_log.sql
```

### Method 3: Using Python (Alternative)

You can also run the SQL script programmatically using Python and cx_Oracle:

```python
import cx_Oracle
from database.connection import connect_to_database

connection = connect_to_database()
if connection:
    cursor = connection.cursor()
    with open('sql/imp_report_log.sql', 'r') as f:
        sql_script = f.read()
    cursor.execute(sql_script)
    connection.commit()
    cursor.close()
    connection.close()
    print("SQL script executed successfully")
```

### Database Connection Details

From `config.ini`:
- **Username**: MIZRAHI_CUSTOM
- **Password**: Use PasswordManager key `OracleDB`
- **Host**: localhost
- **Port**: 1521
- **Service Name**: FREEPDB1

**Easy Connect String format**: `username/password@host:port/service_name`

### Troubleshooting

1. **If sqlplus is not found**: Install Oracle Instant Client and sqlplus
2. **If connection fails**: Check that Oracle listener is running and accessible
3. **If table already exists**: The script will fail. You may need to drop the table first:
   ```sql
   DROP TABLE MIZRAHI_CUSTOM.IMP_REPORT_LOG;
   ```
4. **Permissions**: Ensure the user has CREATE TABLE permissions

### Running Multiple SQL Scripts

To run all SQL scripts in the `sql/` directory:

```bash
for script in sql/*.sql; do
    echo "Running $script..."
    sqlplus MIZRAHI_CUSTOM/IfsOra123@localhost:1521/FREEPDB1 @$script
done
```
