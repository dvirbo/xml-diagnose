# Library Dependencies (Wheel Files)

This folder contains all Python wheel files (`.whl`) required for the project.

## Installation

Install all libraries from this folder using:
```bash
python3.6 -m pip install --no-index libs/*.whl
```

## Required Libraries

### Core Dependencies (Required)
Place the following wheel files in this directory:

1. **pyodbc** - Database connectivity (SQL Server)
   - Example: `pyodbc-4.0.34-cp36-cp36m-linux_x86_64.whl`

2. **requests** - HTTP library for API calls
   - Example: `requests-2.27.1-py2.py3-none-any.whl`

3. **cryptography** - Password encryption/decryption
   - Example: `cryptography-3.4.8-cp36-cp36m-linux_x86_64.whl`

4. **requests dependencies** (automatically included with requests, but may need separate wheels):
   - `certifi` - SSL certificates
   - `charset-normalizer` or `chardet` - Character encoding
   - `idna` - Internationalized Domain Names
   - `urllib3` - HTTP client library

### Optional Dependencies
(Only needed if using SOAP functionality)

5. **zeep** - SOAP client library
   - Example: `zeep-4.1.0-py2.py3-none-any.whl`

6. **requests-cache** - Caching for requests
   - Example: `requests_cache-0.9.8-py2.py3-none-any.whl`

## Downloading Wheels

### Method 1: Using pip download (on machine with internet)
```bash
# Create a virtual environment with Python 3.6
python3.6 -m venv venv
source venv/bin/activate

# Download wheels for Python 3.6 on Linux x86_64
pip download --python-version 3.6 \
             --platform linux_x86_64 \
             --only-binary=:all: \
             pyodbc requests cryptography certifi charset-normalizer idna urllib3

# Optional: SOAP dependencies
pip download --python-version 3.6 \
             --platform linux_x86_64 \
             --only-binary=:all: \
             zeep requests-cache lxml isodate

# Copy all .whl files to libs/ folder
cp *.whl /path/to/xml-diagnose/libs/
```

### Method 2: Manual download from PyPI
1. Visit https://pypi.org/
2. Search for each package
3. Go to "Download files"
4. Download the wheel file matching:
   - Python version: cp36 (Python 3.6)
   - Platform: linux_x86_64 (for most Linux systems)
   - Example: `package-name-version-cp36-cp36m-linux_x86_64.whl`

### Method 3: Using pip wheel
```bash
pip wheel --python-version 3.6 --platform linux_x86_64 pyodbc requests cryptography
# Copy generated wheels to libs/
```

## Python 3.6 Compatible Versions

Recommended versions that work with Python 3.6.8:

- **pyodbc**: 4.0.34 or earlier (latest compatible with 3.6)
- **requests**: 2.27.1 or earlier (2.28.0+ requires Python 3.7+)
- **cryptography**: 3.4.8 or earlier (latest compatible with 3.6)
- **certifi**: Any version (compatible with 3.6)
- **charset-normalizer**: 2.0.12 or earlier (for Python 3.6)
- **idna**: 3.3 or earlier (3.4+ requires Python 3.7+)
- **urllib3**: 1.26.18 or earlier (2.0+ requires Python 3.7+)

## Verification

After installation, verify libraries are installed:
```bash
python3.6 -c "import pyodbc, requests, cryptography; print('All core libraries installed successfully')"
```

## Notes

- All wheels must be compatible with Python 3.6
- Platform must match your Linux system (usually `linux_x86_64`)
- Some libraries may have dependencies on system libraries (e.g., pyodbc needs ODBC drivers)
- Transfer wheels to this folder using WinSCP or similar tool

