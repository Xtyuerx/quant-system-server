@echo off
cd /d "%~dp0"

echo.
echo Starting tests...
echo.

echo Step 1: Unit tests
poetry run pytest tests/test_data_feed.py -v

echo.
echo Step 2: Paper trading test
poetry run python -m tests.test_simple_paper_trading

echo.
echo Done!
echo.
pause