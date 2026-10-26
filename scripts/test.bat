@echo off
cd /d "%~dp0.."
if defined PYTHON ("%PYTHON%" -m unittest discover -s tests -v) else (python -m unittest discover -s tests -v)
