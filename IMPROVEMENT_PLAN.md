# Project Improvement Plan

## Goals
1. Simplify code structure
2. Reorganize files with meaningful names
3. Ensure Python 3.6.8 compatibility
4. Improve maintainability

## Proposed Changes

### 1. File Renaming & Reorganization

#### Current Structure Issues:
- `report_xml_classifier_v2.py` - unclear naming (v2 suffix, classifier vs parser)
- Database files scattered (`db_manager.py`, `db_usage.py`, `establish_db.py`)
- Main file has utility functions mixed with main logic

#### Proposed Structure:
```
xml-diagnose/
├── main.py                          # Entry point (simplified)
├── config.json                      # Configuration file
├── requirements.txt                 # Library dependencies list
├── libs/                            # Local wheel files for offline installation
│   ├── README.md                    # Instructions for downloading wheels
│   └── (wheel files: *.whl)
├── core/
│   ├── __init__.py
│   ├── pipeline.py                  # Renamed from processors/xml_diagnose.py
│   ├── xml_parser.py                # Renamed from processors/report_xml_classifier_v2.py
│   └── xml_processor.py             # Moved from processors/
├── database/
│   ├── __init__.py
│   ├── connection.py                # Merged from establish_db.py
│   ├── manager.py                   # Simplified from db_manager.py
│   ├── updater.py                   # Renamed from db_usage.py
│   └── queries.py                   # Extracted from config.py
├── api/
│   └── (keep existing structure)
├── utils/
│   ├── __init__.py
│   ├── config_loader.py             # Extracted from main.py
│   └── logging_setup.py             # Extracted from main.py
└── (other directories remain)
```

### 2. Python 3.6 Compatibility Fixes

#### Issues to Fix:
- **dataclasses** (Python 3.7+) → Replace with regular classes with `__init__`
  - `ProcessingResult` in `xml_diagnose.py`
  - `ReportUpdate` and `ProcessedReport` in `db_usage.py`

- **Type hints**: Keep as-is (Python 3.6 compatible)
- **f-strings**: Keep as-is (Python 3.6 compatible)

### 3. Code Simplification

#### Changes:
1. **main.py**: Extract utility functions to `utils/` module
2. **Database module**: 
   - Merge `establish_db.py` into `connection.py`
   - Simplify `db_manager.py` → `manager.py`
   - Rename `db_usage.py` → `updater.py`
3. **XML processing**: 
   - Rename `report_xml_classifier_v2.py` → `xml_parser.py`
   - Rename `xml_diagnose.py` → `pipeline.py`

### 4. Import Path Updates
- Update all import statements after reorganization
- Ensure relative imports work correctly

## Library Management

### libs/ Folder Structure
- Create `libs/` directory for all wheel files
- Install libraries using: `python3.6 -m pip install --no-index libs/*.whl`
- Libraries needed (Python 3.6 compatible versions):
  - **Core dependencies:**
    - `pyodbc` - Database connectivity
    - `requests` - HTTP API calls
    - `cryptography` - Password encryption
    - `certifi`, `charset-normalizer`, `idna`, `urllib3` - Dependencies of requests
  - **Optional (for SOAP features):**
    - `zeep` - SOAP client (if using SOAP functionality)
    - `requests-cache` - Optional caching for requests

### Wheel Download Guide
1. Download wheels compatible with Python 3.6 and your OS architecture (Linux x86_64)
2. Use PyPI search or pip download on a machine with internet:
   ```bash
   pip download --python-version 3.6 --platform linux_x86_64 --only-binary=:all: pyodbc requests cryptography certifi charset-normalizer idna urllib3
   ```
3. Transfer all `.whl` files to `libs/` folder via WinSCP
4. Install using: `python3.6 -m pip install --no-index libs/*.whl`

## Implementation Steps

1. ✅ Create improvement plan document
2. Create `libs/` folder with README
3. Create new directory structure
4. Fix Python 3.6 compatibility (replace dataclasses)
5. Reorganize files with new names
6. Update all imports
7. Update requirements.txt with Python 3.6 compatible versions
8. Test that everything still works
9. Clean up old files

## Backward Compatibility
- Will maintain same functionality
- Only structural changes, no logic changes
- All existing config files remain compatible

