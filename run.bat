@echo off
echo Installing requests module...
python -m pip install requests
echo.
echo Running Password Strength Tester...
python password_tester.py
pause
