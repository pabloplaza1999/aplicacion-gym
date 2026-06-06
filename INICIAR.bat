
@echo off
cd /d "%~dp0backend"
start "Backend - GymOS" cmd /k "uvicorn app.main:app --reload"
 
timeout /t 2 /nobreak >nul
 
cd /d "%~dp0frontend"
start "Frontend - GymOS" cmd /k "npm install && npm run dev"
 
timeout /t 5 /nobreak >nul
start http://localhost:5173