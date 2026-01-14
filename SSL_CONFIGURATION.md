# SSL Configuration for ActOne API

## Overview

The API connection has been updated to use HTTPS/SSL with the following configuration:

- **URL**: `https://10.205.6.19:8443/ActOne/api`
- **TrustStore Path**: `/opt/tomcat9/acm/conf/IFS-LAB-Redhat.jks`
- **TrustStore Password**: `changeit`

## Implementation Details

### Configuration (`config.ini`)

The SSL configuration is stored in the `[ssl]` section:

```ini
[ssl]
truststore_path = /opt/tomcat9/acm/conf/IFS-LAB-Redhat.jks
truststore_password = changeit
verify_ssl = True
```

### SSL Verification

**Important Note**: Python's `requests` library does not natively support JKS (Java KeyStore) files. The current implementation uses Python's default SSL certificate verification.

The `verify_ssl` parameter in `config.ini` controls SSL verification:
- `True` (default): Uses Python's default certificate store (certifi bundle)
- `False`: Disables SSL verification (not recommended for production)

### Current Implementation

The code has been updated to:
1. Use HTTPS URLs for all API requests
2. Respect the `verify_ssl` configuration setting
3. Store truststore information in config (for reference)

## Using the JKS TrustStore

If you need to use the JKS truststore file directly, you have the following options:

### Option 1: Convert JKS to PEM (Recommended)

Convert the JKS file to PEM format so Python can use it:

```bash
# Export certificates from JKS
keytool -export -alias <alias_name> -keystore /opt/tomcat9/acm/conf/IFS-LAB-Redhat.jks -file cert.der -storepass changeit

# Convert to PEM format
openssl x509 -inform DER -in cert.der -out cert.pem
```

Then update the code to use the PEM file with `verify='path/to/cert.pem'`.

### Option 2: Use Java KeyStore Library

Install a library that can read JKS files (requires additional dependencies):
- `jks` library (may not be compatible with Python 3.6.8)
- `pyjks` library

### Option 3: Disable SSL Verification (Not Recommended)

Set `verify_ssl = False` in `config.ini` to disable SSL verification. This is **not secure** and should only be used for testing.

## Testing

To test the SSL connection:

```bash
python3.6 -c "from api.api_session import login_and_get_session; session = login_and_get_session(); print('Connection successful' if session else 'Connection failed')"
```

## Security Considerations

1. **Certificate Verification**: Always verify SSL certificates in production
2. **TrustStore Protection**: Keep the truststore password secure
3. **Network Security**: Ensure the connection is made over a secure network
4. **Self-Signed Certificates**: If the server uses a self-signed certificate, you'll need to either:
   - Add the certificate to Python's trust store
   - Convert and use the JKS truststore (Option 1)
   - Disable verification (not recommended)

## Files Modified

- `config.ini`: Added `[ssl]` section
- `api/api_session.py`: Added SSL verification support
- `api/update_alert_rest.py`: Added SSL verification support
- `utils/config_loader.py`: Added SSL configuration reading
