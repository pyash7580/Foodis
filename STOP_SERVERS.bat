@echo off
echo Stopping Foodis Servers...
taskkill /FI "WINDOWTITLE eq Foodis Backend" /F
taskkill /FI "WINDOWTITLE eq Foodis Frontend" /F
taskkill /IM node.exe /F
taskkill /IM python.exe /F
echo Servers Stopped.
pause
