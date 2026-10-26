@echo off
cd /d "%~dp0.."
for %%V in (minimal files deep) do (
  call run.bat --vfs examples/vfs/%%V.xml ^
    --log logs/%%V.xml --script examples/stage3.txt
)
