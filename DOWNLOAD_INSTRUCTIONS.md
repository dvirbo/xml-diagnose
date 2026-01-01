# Library Download Instructions

## Where to Run the Script

Run `download_libs.sh` on a machine that has:
- ✅ Internet access
- ✅ Python 3.6 installed (or Python 3.6+)
- ✅ pip installed

**Do NOT run it on your target machine** (which has no internet access).

## Step-by-Step Instructions

### Step 1: On a Machine with Internet Access

1. Copy the `download_libs.sh` script to your machine with internet access
2. Make it executable (if needed):
   ```bash
   chmod +x download_libs.sh
   ```

3. Run the script:
   ```bash
   ./download_libs.sh
   ```
   
   Or if you prefer to use Python 3.6 explicitly:
   ```bash
   python3.6 -m pip download pyodbc==4.0.39 --dest wheels_xml --python-version 3.6 --platform linux_x86_64 --only-binary=:all:
   # (repeat for each library)
   ```

4. The script will create a `wheels_xml/` folder with all the `.whl` files

### Step 2: Transfer Files to Target Machine

1. Transfer all `.whl` files from `wheels_xml/` to your target machine's `libs/` folder using WinSCP
2. Make sure all `.whl` files are in `/opt/xml-diagnose/libs/`

### Step 3: Install on Target Machine

On your target machine (the one with no internet), run:
```bash
cd /opt/xml-diagnose
python3.6 -m pip install --no-index libs/*.whl
```

## Alternative: Manual Download

If you prefer to run commands manually instead of using the script, you can copy commands from `DOWNLOAD_COMMANDS.txt` and run them one by one.

## Verification

After installation on the target machine, verify:
```bash
python3.6 -c "import pyodbc, requests, cryptography; print('All libraries installed successfully!')"
```

## Troubleshooting

- **"pip: command not found"**: Use `python3.6 -m pip` instead of just `pip`
- **"No matching distribution"**: Make sure you're using Python 3.6 and have internet access
- **Wrong platform wheels**: Make sure you're downloading for `linux_x86_64` platform

