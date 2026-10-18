@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set "PYTHON=.venv\Scripts\python.exe"
) else (
  set "PYTHON=python"
)
start "" /min cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000"
"%PYTHON%" -m doc_search.web
pause
