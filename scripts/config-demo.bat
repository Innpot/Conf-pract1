@echo off
cd /d "%~dp0.."
call run.bat --vfs examples/vfs/minimal.xml --log logs/config.xml --script examples/stage1.txt
call run.bat --vfs examples/vfs/deep.xml --log "logs/with spaces.xml" --script examples/stage1.txt
