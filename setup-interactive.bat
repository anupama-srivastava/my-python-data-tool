@echo off
echo Setting up Advanced Interactive Python Data Analysis Tool...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.7+ first.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements-interactive.txt

echo.
echo Setup complete!
echo.
echo To run the interactive tool:
echo   python interactive_main.py
echo.
echo To run the basic tool:
echo   python main.py --symbols AAPL GOOGL --start-date 2023-01-01
echo.
pause
