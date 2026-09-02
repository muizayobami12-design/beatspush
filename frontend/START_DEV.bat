@echo off
echo ========================================
echo   BeatPush Frontend Development Server
echo ========================================
echo.
echo Starting Next.js development server...
echo Server will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
npm run dev
