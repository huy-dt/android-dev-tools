Clear-Host
Write-Host "======================================"
Write-Host " ANDROID PACKAGE REFACTOR TOOL (SAFE)"
Write-Host "======================================"
Write-Host "1. Run refactor"
Write-Host "0. Exit"
Write-Host ""

$choice = Read-Host "Choose option"
if ($choice -ne "1") { exit }

# ================= BLOCK IDE RUNNING =================
$ideRunning = Get-Process -Name "studio64","idea64" -ErrorAction SilentlyContinue
if ($ideRunning) {
    Write-Host "❌ Android Studio / IntelliJ is running. Close IDE before refactor!" -ForegroundColor Red
    Pause
    exit
}

# ================= INPUT =================
$ProjectDir   = Read-Host "Enter PROJECT_DIR (default: current folder)"
$TargetModule = Read-Host "Enter MODULE name (app / core / feature_x / empty = all)"
$OldPkg       = Read-Host "Enter OLD_PKG (default: com.xxx.app_mvvm)"
$NewPkg       = Read-Host "Enter NEW_PKG (default: com.zzz.app_mvvm)"

# ================= DEFAULT PROJECT DIR =================
if ([string]::IsNullOrWhiteSpace($ProjectDir)) {
    $ProjectDir = Get-Location
}

if ([string]::IsNullOrWhiteSpace($OldPkg)) {
    $OldPkg = "com.xxx.app_mvvm"
}
if ([string]::IsNullOrWhiteSpace($NewPkg)) {
    $NewPkg = "com.zzz.app_mvvm"
}

if ($OldPkg -eq $NewPkg) {
    Write-Host "OldPkg and NewPkg are the same!" -ForegroundColor Red
    Pause
    exit
}

# ================= LOG FILE (SAME DIR AS EXE) =================
$ExeDir = [System.AppDomain]::CurrentDomain.BaseDirectory.TrimEnd('\')
$LogFile = Join-Path $ExeDir "refactor.log"

Add-Content $LogFile "==============================="
Add-Content $LogFile ("Refactor started: " + (Get-Date))
Add-Content $LogFile ("$OldPkg -> $NewPkg")
Add-Content $LogFile ("Project: $ProjectDir")
Add-Content $LogFile ("Module: " + $(if ($TargetModule) { $TargetModule } else { "ALL" }))
Add-Content $LogFile "==============================="

# ================= HELPER =================
function Remove-EmptyParentDirs {
    param ($Path, $StopAt)

    $current = Split-Path $Path -Parent
    while ($current -and $current.StartsWith($StopAt) -and
          (Get-ChildItem $current -Force | Measure-Object).Count -eq 0) {
        Remove-Item $current -Force
        $current = Split-Path $current -Parent
    }
}

# ================= FIND SOURCE ROOTS =================
$sourceRoots = Get-ChildItem $ProjectDir -Recurse -Directory |
    Where-Object { $_.FullName -match "src\\main\\(java|kotlin)$" }

if ($TargetModule) {
    $sourceRoots = $sourceRoots | Where-Object {
        $_.FullName -like "*\$TargetModule\src\main\*"
    }
}

# ================= TEXT REPLACE =================
Get-ChildItem $ProjectDir -Recurse -File `
    -Include *.java,*.kt,*.xml,*.gradle,*.kts,*.properties |
ForEach-Object {

    if ($TargetModule -and $_.FullName -notlike "*\$TargetModule\*") { return }

    $content = Get-Content $_.FullName
    if ($content -like "*$OldPkg*") {
        ($content -replace [regex]::Escape($OldPkg), $NewPkg) |
            Set-Content $_.FullName
        Add-Content $LogFile ("UPDATED FILE: " + $_.FullName)
    }
}

# ================= PACKAGE FOLDER MIGRATION (SAFE) =================
$oldParts = $OldPkg.Split(".")
$newParts = $NewPkg.Split(".")

foreach ($root in $sourceRoots) {

    $oldPkgPath = Join-Path $root.FullName ($oldParts -join "\")
    $newPkgPath = Join-Path $root.FullName ($newParts -join "\")

    if (!(Test-Path $oldPkgPath)) { continue }

    if (!(Test-Path $newPkgPath)) {
        New-Item -ItemType Directory -Path $newPkgPath | Out-Null
    }

    Copy-Item "$oldPkgPath\*" $newPkgPath -Recurse -Force -ErrorAction Stop

    $src = (Get-ChildItem $oldPkgPath -Recurse -File | Measure-Object).Count
    $dst = (Get-ChildItem $newPkgPath -Recurse -File | Measure-Object).Count

    if ($src -eq $dst) {
        Remove-Item $oldPkgPath -Recurse -Force
        Remove-EmptyParentDirs -Path $oldPkgPath -StopAt $root.FullName
        Add-Content $LogFile ("MOVED: $oldPkgPath -> $newPkgPath")
    }
    else {
        Write-Host "❌ COPY VERIFY FAILED: $oldPkgPath" -ForegroundColor Red
    }
}

Add-Content $LogFile ("Finished: " + (Get-Date))
Write-Host "DONE! Log file at: $LogFile" -ForegroundColor Green
Pause
