# ======================================================================
# Redis Auto-Start Configuration Script
# ======================================================================
# Purpose: Configure Redis to start automatically on Windows boot
# Run as: Administrator PowerShell
# Date: August 12, 2026
# ======================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Redis Auto-Start Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERROR: This script must run as Administrator" -ForegroundColor Red
    Write-Host ""
    Write-Host "To run as Administrator:" -ForegroundColor Yellow
    Write-Host "1. Right-click PowerShell" -ForegroundColor Yellow
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "3. Navigate to:" -ForegroundColor Yellow
    Write-Host "   cd 'C:\Users\Asus\Desktop\beatspush'" -ForegroundColor Yellow
    Write-Host "4. Run:" -ForegroundColor Yellow
    Write-Host "   .\SETUP_REDIS_AUTOSTART.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green
Write-Host ""

# ======================================================================
# STEP 1: Check Redis Installation
# ======================================================================

Write-Host "STEP 1: Checking Redis Installation..." -ForegroundColor Cyan

$redisPath = "C:\Program Files\Redis"
$redisExe = "$redisPath\redis-server.exe"
$redisCliExe = "$redisPath\redis-cli.exe"

if (Test-Path $redisExe) {
    Write-Host "✅ Redis found at: $redisPath" -ForegroundColor Green
    
    # Get Redis version
    $version = & "$redisCliExe" --version
    Write-Host "   Version: $version" -ForegroundColor Gray
} else {
    Write-Host "❌ Redis not found at: $redisPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Redis first:" -ForegroundColor Yellow
    Write-Host "https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ======================================================================
# STEP 2: Check Redis Service Status
# ======================================================================

Write-Host "STEP 2: Checking Redis Service..." -ForegroundColor Cyan

$service = Get-Service -Name "Redis" -ErrorAction SilentlyContinue

if ($service) {
    Write-Host "✅ Redis service found" -ForegroundColor Green
    Write-Host "   Status: $($service.Status)" -ForegroundColor Gray
    Write-Host "   Start Type: $($service.StartType)" -ForegroundColor Gray
} else {
    Write-Host "❌ Redis service not found" -ForegroundColor Red
    Write-Host "   Redis may not be installed as a service" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ======================================================================
# STEP 3: Configure Auto-Start
# ======================================================================

Write-Host "STEP 3: Configuring Auto-Start..." -ForegroundColor Cyan

if ($service.StartType -eq "Automatic") {
    Write-Host "✅ Redis already configured for auto-start" -ForegroundColor Green
    Write-Host "   No changes needed" -ForegroundColor Gray
} else {
    Write-Host "⚙️  Setting Redis to start automatically..." -ForegroundColor Yellow
    
    try {
        Set-Service -Name "Redis" -StartupType Automatic
        Write-Host "✅ Redis configured for auto-start" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to configure auto-start: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# ======================================================================
# STEP 4: Start Redis Service (if not running)
# ======================================================================

Write-Host "STEP 4: Starting Redis Service..." -ForegroundColor Cyan

$service = Get-Service -Name "Redis"

if ($service.Status -eq "Running") {
    Write-Host "✅ Redis is already running" -ForegroundColor Green
} else {
    Write-Host "⚙️  Starting Redis service..." -ForegroundColor Yellow
    
    try {
        Start-Service -Name "Redis"
        Write-Host "✅ Redis started successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to start Redis: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# ======================================================================
# STEP 5: Test Redis Connection
# ======================================================================

Write-Host "STEP 5: Testing Redis Connection..." -ForegroundColor Cyan

try {
    $response = & "$redisCliExe" ping
    
    if ($response -eq "PONG") {
        Write-Host "✅ Redis connection successful" -ForegroundColor Green
        Write-Host "   Response: $response" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Unexpected response: $response" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to connect to Redis: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ======================================================================
# STEP 6: Add Redis to PATH
# ======================================================================

Write-Host "STEP 6: Adding Redis to System PATH..." -ForegroundColor Cyan

$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

if ($currentPath -like "*$redisPath*") {
    Write-Host "✅ Redis already in PATH" -ForegroundColor Green
} else {
    Write-Host "⚙️  Adding Redis to PATH..." -ForegroundColor Yellow
    
    try {
        $newPath = "$currentPath;$redisPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Host "✅ Redis added to PATH" -ForegroundColor Green
        Write-Host "   Restart PowerShell to use 'redis-cli' command" -ForegroundColor Yellow
    } catch {
        Write-Host "❌ Failed to add to PATH: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   You can still use: & '$redisCliExe'" -ForegroundColor Yellow
    }
}

Write-Host ""

# ======================================================================
# SUMMARY
# ======================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           CONFIGURATION COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$service = Get-Service -Name "Redis"

Write-Host "✅ Redis Status:" -ForegroundColor Green
Write-Host "   • Status: $($service.Status)" -ForegroundColor Gray
Write-Host "   • Start Type: $($service.StartType)" -ForegroundColor Gray
Write-Host "   • Location: $redisPath" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ Auto-Start: ENABLED" -ForegroundColor Green
Write-Host "   Redis will start automatically on boot" -ForegroundColor Gray
Write-Host ""

Write-Host "📋 Test Commands:" -ForegroundColor Cyan
Write-Host "   redis-cli ping              # Test connection" -ForegroundColor Gray
Write-Host "   redis-cli --version         # Check version" -ForegroundColor Gray
Write-Host "   Get-Service Redis           # Check status" -ForegroundColor Gray
Write-Host ""

Write-Host "🔧 Service Commands:" -ForegroundColor Cyan
Write-Host "   net start Redis             # Start service" -ForegroundColor Gray
Write-Host "   net stop Redis              # Stop service" -ForegroundColor Gray
Write-Host "   net restart Redis           # Restart service" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ Next Steps:" -ForegroundColor Green
Write-Host "   1. Restart PowerShell (to use redis-cli)" -ForegroundColor Yellow
Write-Host "   2. Run: cd C:\Users\Asus\Desktop\beatspush\backend" -ForegroundColor Yellow
Write-Host "   3. Run: python test_security_features.py" -ForegroundColor Yellow
Write-Host "   4. Expected: 100% pass rate!" -ForegroundColor Yellow
Write-Host ""

Write-Host "🎉 Redis is ready!" -ForegroundColor Green
Write-Host ""
