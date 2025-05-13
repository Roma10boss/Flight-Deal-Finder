@echo off
echo ====================================
echo Running Comprehensive Airport Extractor
echo ====================================

cd scripts

echo.
echo Installing required packages...
pip install requests beautifulsoup4 lxml

echo.
echo Running extractor...
python comprehensive_airport_extractor.py

echo.
echo Moving files to public directory...
copy airportData.js ..\public\
copy test_airports.html ..\public\

echo.
echo ====================================
echo COMPLETE!
echo ====================================
echo.
echo Files created:
echo - scripts\airports_complete.json (full data)
echo - public\airportData.js (for website)
echo - public\test_airports.html (test page)
echo.
echo Next steps:
echo 1. Test that airports load: open public\test_airports.html
echo 2. Restart your server
echo 3. Test autocomplete on your main site
echo.
pause