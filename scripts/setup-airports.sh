#!/bin/bash
# setup-airports.sh - Setup script for airport data extraction and integration

echo "======================================"
echo "Flight Deals Airport Data Setup"
echo "======================================"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not found!"
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check for required files
required_files=("airport_extractor.py" "integrate_airports.py" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "ERROR: Required file '$file' not found!"
        echo "Please ensure all script files are in the current directory."
        exit 1
    fi
done

# Create virtual environment
echo ""
echo "Setting up Python virtual environment..."
python3 -m venv airport_env

# Activate virtual environment
source airport_env/bin/activate

# Install dependencies
echo ""
echo "Installing required packages..."
pip install -r requirements.txt

# Create backups
echo ""
echo "Creating backups..."
mkdir -p backups
timestamp=$(date +%Y%m%d_%H%M%S)

if [ -f "public/index.html" ]; then
    cp public/index.html "backups/index.html.backup.$timestamp"
    echo "Backed up public/index.html"
fi

if [ -f "server.js" ]; then
    cp server.js "backups/server.js.backup.$timestamp"
    echo "Backed up server.js"
fi

# Run extraction
echo ""
echo "======================================"
echo "STEP 1: Extracting Airport Data"
echo "======================================"
python airport_extractor.py

# Check if extraction was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Extraction failed!"
    exit 1
fi

if [ ! -f "airports.json" ]; then
    echo "ERROR: airports.json was not created!"
    exit 1
fi

# Run integration
echo ""
echo "======================================"
echo "STEP 2: Integrating Airport Data"
echo "======================================"
python integrate_airports.py

# Check if integration was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Integration failed!"
    exit 1
fi

# Show summary
echo ""
echo "======================================"
echo "SETUP COMPLETE!"
echo "======================================"

# Count airports
airport_count=$(python3 -c "import json; print(len(json.load(open('airports.json'))))")
country_count=$(python3 -c "import json; airports=json.load(open('airports.json')); print(len(set(a['country'] for a in airports)))")

echo ""
echo "Success! Your flight deals website now has:"
echo "✓ $airport_count international airports"
echo "✓ $country_count countries"
echo "✓ Full autocomplete functionality"
echo "✓ Updated server and client files"

echo ""
echo "Next steps:"
echo "1. Start your server: npm start"
echo "2. Test the autocomplete functionality"
echo "3. Try searching for flights"
echo "4. Check the settings page"

echo ""
echo "Backup files created in ./backups/"
echo "Virtual environment created in ./airport_env/"

# Deactivate virtual environment
deactivate

echo ""
echo "Done! You can now delete the virtual environment if you want:"
echo "rm -rf airport_env"