#!/bin/bash
# Script to download all required Python 3.6.8 compatible libraries
# Run this on a machine with internet access and Python 3.6

# Create destination directory
DEST_DIR="wheels_xml"
mkdir -p "$DEST_DIR"

echo "Downloading Python 3.6.8 compatible libraries to $DEST_DIR..."

# Core Dependencies (Required)
echo "Downloading core dependencies..."
pip download pyodbc==4.0.39 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:
pip download requests==2.27.1 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:
pip download cryptography==3.4.8 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:

# Requests Dependencies
echo "Downloading requests dependencies..."
pip download certifi==2021.10.8 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:
pip download charset-normalizer==2.0.12 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:
pip download idna==3.3 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:
pip download urllib3==1.26.18 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:

# Optional: SOAP Dependencies (uncomment if needed)
# echo "Downloading SOAP dependencies..."
# pip download zeep==4.1.0 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:
# pip download requests-cache==0.9.8 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:
# pip download lxml==4.9.3 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:
# pip download isodate==0.6.1 --dest "$DEST_DIR" --python-version 3.6 --platform linux_x86_64 --only-binary=:all:

echo "Download complete! Wheel files are in $DEST_DIR/"
echo "Transfer these files to your libs/ folder using WinSCP"

