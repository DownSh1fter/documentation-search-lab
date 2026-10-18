@echo off
cd /d "%~dp0"
start "Documentation Search" http://127.0.0.1:8000
python -m doc_search.web
pause
