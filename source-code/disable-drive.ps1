# ================= ADMIN CHECK =================
$IsAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent() `
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $IsAdmin) {
    Write-Host "Please run PowerShell as Administrator" -ForegroundColor Red
    Pause
    exit
}

# ================= CONFIG =================
$BaseKey = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceInstall\Restrictions"

function Block-Device {
    $HardwareID = Read-Host "Enter Hardware ID to BLOCK (ex: ACPI\PNP0303)"
    if ([string]::IsNullOrWhiteSpace($HardwareID)) {
        Write-Host "Hardware ID is empty" -ForegroundColor Red
        return
    }

    New-Item -Path $BaseKey -Force | Out-Null
    New-Item -Path "$BaseKey\DenyDeviceIDs" -Force | Out-Null

    Set-ItemProperty -Path $BaseKey -Name "DenyDeviceIDs" -Type DWord -Value 1
    Set-ItemProperty -Path $BaseKey -Name "DenyDeviceIDsRetroactive" -Type DWord -Value 1

    $Existing = (Get-Item "$BaseKey\DenyDeviceIDs").Property
    $Index = if ($Existing) { $Existing.Count + 1 } else { 1 }

    New-ItemProperty `
        -Path "$BaseKey\DenyDeviceIDs" `
        -Name $Index `
        -PropertyType String `
        -Value $HardwareID `
        -Force | Out-Null

    Write-Host "BLOCKED: $HardwareID" -ForegroundColor Green
}

function Unblock-All {
    if (Test-Path $BaseKey) {
        Remove-Item $BaseKey -Recurse -Force
        Write-Host "ALL BLOCK RULES REMOVED" -ForegroundColor Green
    } else {
        Write-Host "No rule found" -ForegroundColor Yellow
    }
}

Clear-Host
Write-Host "==============================="
Write-Host " DEVICE BLOCK TOOL (HARDWARE ID)"
Write-Host "==============================="
Write-Host "1. Block device"
Write-Host "2. Unblock all"
Write-Host "0. Exit"
Write-Host ""

$choice = Read-Host "Choose option"

switch ($choice) {
    "1" { Block-Device }
    "2" { Unblock-All }
    "0" { exit }
    default { Write-Host "Invalid choice" -ForegroundColor Red }
}

Write-Host ""
Write-Host "Restart computer to apply changes" -ForegroundColor Yellow
Pause
