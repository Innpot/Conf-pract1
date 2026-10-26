@echo off
cd /d "%~dp0.."
call run.bat --vfs examples/vfs/deep.xml --log logs/stage4.xml --script examples/stage4.txt
call run.bat --vfs examples/vfs/deep.xml --log logs/stage5.xml --script examples/stage5.txt
