@echo off
cd /d "%~dp0"

echo.
echo ==========================================
echo Week 1 Test Suite
echo ==========================================
echo.

echo [1/3] Running data feed unit tests...
poetry run pytest tests/test_data_feed.py -v
echo.

echo [2/3] Running paper trading integration test...
poetry run python -m tests.test_simple_paper_trading
echo.

echo [3/3] Running all tests summary...
poetry run pytest tests/ --tb=no -q
echo.

echo ==========================================
echo Tests completed!
echo ==========================================
echo.
pause