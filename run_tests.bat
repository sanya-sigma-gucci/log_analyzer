@echo off
setlocal
cd /d "%~dp0"

python -m pytest tests ^
    --cov=log_analyzer ^
    --cov-config=.coveragerc ^
    --cov-report=html:htmlcov ^
    --cov-report=term-missing ^
    --cov-fail-under=80 ^
    --html=test-report.html ^
    --self-contained-html

set EXITCODE=%ERRORLEVEL%
echo.
echo HTML test report:      %CD%\test-report.html
echo HTML coverage report:  %CD%\htmlcov\index.html
exit /b %EXITCODE%