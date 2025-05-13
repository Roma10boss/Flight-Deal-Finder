@echo off
echo ==================================================
echo Flight Deals Airport Data Setup
echo ==================================================

echo Checking Python environment...
python --version

echo.
echo Setting up airport data...
cd scripts

REM Check if airportData.js exists
if exist airportData.js (
    echo Found airportData.js in scripts directory
    copy airportData.js ..\public\ >nul 2>&1
    echo Copied airportData.js to public directory
) else (
    echo airportData.js not found in scripts directory
)

REM Check if airports.json exists
if exist airports.json (
    echo Found airports.json in scripts directory
    copy airports.json ..\data\ >nul 2>&1
    copy airports.json ..\airports\ >nul 2>&1
    echo Copied airports.json to data and airports directories
) else (
    echo airports.json not found in scripts directory
)

cd ..

echo.
echo Setup complete!
echo Airport data files have been processed.
pause