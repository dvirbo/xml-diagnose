# Password Manager Setup Instructions

## Overview

The project now uses `PasswordManager` for secure password storage and retrieval for:
1. **API Passwords** (already configured)
2. **Database Passwords** (newly added)
3. **TrustStore Passwords** (newly added)

## Configuration Changes

### config.ini Updates

The following sections have been updated to use password keys instead of plain text:

```ini
[database]
password_key = OracleDB    # Changed from: password = IfsOra123

[ssl]
truststore_password_key = TrustStore    # Changed from: truststore_password = changeit
```

### Password Keys

- **API Password Key**: `ActOne` (already exists in passwords.json)
- **Database Password Key**: `OracleDB` (needs to be added)
- **TrustStore Password Key**: `TrustStore` (needs to be added)

## Setting Up Passwords

You need to add the database and truststore passwords to `secure_password_store/passwords.json` using the PasswordManager.

### Step 1: Add Database Password

```bash
cd /opt/xml-diagnose
python3.6 -c "
from secure_password_store.password_manager import PasswordManager
pm = PasswordManager()
pm.add_password('OracleDB', 'IfsOra123')
"
```

### Step 2: Add TrustStore Password

```bash
python3.6 -c "
from secure_password_store.password_manager import PasswordManager
pm = PasswordManager()
pm.add_password('TrustStore', 'changeit')
"
```

### Step 3: Verify Passwords

```bash
python3.6 -c "
from secure_password_store.password_manager import PasswordManager
pm = PasswordManager()
print('OracleDB:', pm.get_password('OracleDB'))
print('TrustStore:', pm.get_password('TrustStore'))
"
```

## Code Changes

### Database Connection (`database/connection.py`)

- Now uses `PasswordManager` to retrieve the database password
- Retrieves password using the key from `DB_CONFIG['PASSWORD_KEY']`
- Password is decrypted at runtime

### SSL Configuration (`utils/config_loader.py`)

- SSL configuration now stores `truststore_password_key` instead of plain text password
- The password key is stored in config (currently not used by Python requests, but available for future use)

### Configuration Files

- `config.ini`: Updated to use password keys
- `database/config.py`: Updated to use `PASSWORD_KEY` instead of `PASSWORD`
- `utils/config_loader.py`: Updated to read password keys instead of passwords

## Security Benefits

1. **Encrypted Storage**: Passwords are encrypted using Fernet (symmetric encryption)
2. **No Plain Text**: Passwords are no longer stored in plain text in config.ini
3. **Centralized Management**: All passwords are managed through PasswordManager
4. **Key-Based Access**: Passwords are accessed using keys, not stored directly

## Current Password Keys

Based on `secure_password_store/passwords.json`:
- `ActOne` - API password (already exists)
- `OracleDB` - Database password (needs to be added)
- `TrustStore` - TrustStore password (needs to be added)

## Troubleshooting

If you get an error like "Failed to retrieve database password":
1. Make sure the password key exists in passwords.json
2. Verify the key name matches exactly (case-sensitive)
3. Run the password setup commands above

## Migration Notes

- Old plain text passwords in config.ini have been replaced with password keys
- You must add the passwords to PasswordManager before running the application
- The application will fail if passwords are not added to PasswordManager
