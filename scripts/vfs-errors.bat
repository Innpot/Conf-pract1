@echo off
cd /d "%~dp0.."
for %%V in (minimal files deep) do (
  call run.bat --vfs examples/vfs/%%V.xml ^
    --log logs/check-%%V.xml --script examples/stage3.txt
)
call run.bat --vfs missing.xml --log logs/error.xml --script examples/stage3.txt
