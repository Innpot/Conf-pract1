@echo off
cd /d "%~dp0.."
call run.bat --vfs examples/vfs/deep.xml --log logs/errors.xml --script missing.txt
call run.bat --vfs examples/vfs/deep.xml --log logs/errors.xml --script examples/stage1.txt
call run.bat --unknown
