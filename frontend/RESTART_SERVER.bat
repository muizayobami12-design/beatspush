@echo off
echo ========================================
echo RESTARTING NEXT.JS DEV SERVER
echo ========================================
echo.

echo Step 1: Clearing Next.js cache...
if exist .next (
    rmdir /s /q .next
    echo   [OK] .next folder deleted
) else (
    echo   [SKIP] .next folder doesn't exist
)

echo.
echo Step 2: Clearing node_modules cache...
if exist node_modules\.cache (
    rmdir /s /q node_modules\.cache
    echo   [OK] node_modules\.cache deleted
) else (
    echo   [SKIP] cache folder doesn't exist
)

echo.
echo Step 3: Starting development server...
echo   Running: npm run dev
echo.
echo ========================================
echo SERVER STARTING - DO NOT CLOSE THIS WINDOW
echo ========================================
echo.

npm run dev
