# BeatsPush Cleanup Script
# Removes all temporary status and development documentation files

$RootPath = $PSScriptRoot

# Files to KEEP (essential documentation)
$FilesToKeep = @(
    "README.md",
    "REGISTRATION_SETUP_GUIDE.md",
    "R2_SETUP_GUIDE.md",
    "SECURITY_SETUP_GUIDE.md", 
    "SETUP_GUIDE.md",
    "QUICK_START_GUIDE.md",
    "LOGO_DESIGN_GUIDE.md",
    "BEATPUSH_COMPLETE_ROADMAP.txt"
)

# Get all .md and .txt files in root
$FilesToDelete = Get-ChildItem -Path $RootPath -Filter "*.md" -File |
    Where-Object { $_.Name -notin $FilesToKeep } |
    Select-Object -ExpandProperty FullName

# Also get standalone .txt status files
$TextFilesToDelete = Get-ChildItem -Path $RootPath -Filter "*_*.txt" -File |
    Where-Object { $_.Name -notin $FilesToKeep } |
    Select-Object -ExpandProperty FullName

$AllFilesToDelete = @($FilesToDelete) + @($TextFilesToDelete) | Where-Object { $_ }

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "BEATPUSH CLEANUP - UNUSED FILES REMOVAL" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "FILES TO DELETE: $($AllFilesToDelete.Count)" -ForegroundColor Yellow
Write-Host "FILES TO KEEP: $($FilesToKeep.Count)" -ForegroundColor Green
Write-Host ""

Write-Host "Files to KEEP:" -ForegroundColor Green
$FilesToKeep | ForEach-Object { Write-Host "  [KEEP] $_" }

Write-Host ""
Write-Host "Files to DELETE:" -ForegroundColor Red
$AllFilesToDelete | ForEach-Object { Write-Host "  [DELETE] $(Split-Path -Leaf $_)" }

Write-Host ""
$confirm = Read-Host "Continue with deletion? (yes/no)"

if ($confirm -eq "yes") {
    $deleted = 0
    $AllFilesToDelete | ForEach-Object {
        try {
            Remove-Item -Path $_ -Force
            $deleted++
            Write-Host "  Deleted: $(Split-Path -Leaf $_)" -ForegroundColor Gray
        } catch {
            Write-Host "  Failed: $(Split-Path -Leaf $_) - $_" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "CLEANUP COMPLETE" -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "Files deleted: $deleted" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Cleanup cancelled" -ForegroundColor Yellow
}
