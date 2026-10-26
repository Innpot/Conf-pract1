@echo off
cd /d "%~dp0"
if defined PYTHON ("%PYTHON%" -m src.main %*) else (python -m src.main %*)
