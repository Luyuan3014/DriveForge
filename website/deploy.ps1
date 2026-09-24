<#
.SYNOPSIS
    DriveForge Web Landing Page - Deployment Automation Script (Windows PowerShell)

.DESCRIPTION
    Automates deploying/syncing the web landing page to:
    1. PocketBase (pb_public directory)
    2. Local/Remote Nginx or static file server directory
    3. Docker container build and run

.EXAMPLE
    # Deploy to PocketBase:
    .\deploy.ps1 -Target pocketbase -PocketBasePath "C:\Tools\pocketbase"

    # Deploy to a custom web server directory:
    .\deploy.ps1 -Target custom -DestinationPath "D:\wwwroot\driveforge"

    # Run locally with Docker Compose:
    .\deploy.ps1 -Target docker
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("pocketbase", "docker", "custom", "preview")]
    [string]$Target = "preview",

    [Parameter(Mandatory=$false)]
    [string]$PocketBasePath = "",

    [Parameter(Mandatory=$false)]
    [string]$DestinationPath = "",

    [Parameter(Mandatory=$false)]
    [int]$Port = 8080
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  DriveForge Web Landing Page Deployment Helper   " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

switch ($Target) {
    "preview" {
        Write-Host "[Preview] Starting lightweight local web server on port $Port..." -ForegroundColor Green
        Write-Host "URL: http://localhost:$Port" -ForegroundColor Yellow
        python -m http.server $Port
    }

    "pocketbase" {
        if (-not $PocketBasePath) {
            Write-Error "Please specify -PocketBasePath (the directory where pocketbase executable resides)."
            exit 1
        }
        $PbPublicDir = Join-Path $PocketBasePath "pb_public"
        Write-Host "[PocketBase] Syncing landing page assets to: $PbPublicDir" -ForegroundColor Green

        if (-not (Test-Path $PbPublicDir)) {
            New-Item -ItemType Directory -Path $PbPublicDir -Force | Out-Null
        }

        # Exclude development/deploy scripts and docker configs
        $ExcludeList = @("*.ps1", "*.sh", "Dockerfile", "docker-compose.yml", "nginx.conf", "*.bak")
        Copy-Item -Path "$ScriptDir\*" -Destination $PbPublicDir -Recurse -Force -Exclude $ExcludeList

        Write-Host "✓ Successfully synced DriveForge landing page to PocketBase pb_public!" -ForegroundColor Green
        Write-Host "Start PocketBase with: .\pocketbase.exe serve" -ForegroundColor Yellow
        Write-Host "Your landing page will be immediately available at: http://localhost:8090/" -ForegroundColor Cyan
    }

    "docker" {
        Write-Host "[Docker] Building and launching DriveForge web container..." -ForegroundColor Green
        docker compose up -d --build
        Write-Host "✓ Container is running! Access at: http://localhost:$Port" -ForegroundColor Green
    }

    "custom" {
        if (-not $DestinationPath) {
            Write-Error "Please specify -DestinationPath (e.g. C:\nginx\html or /var/www/html)."
            exit 1
        }
        Write-Host "[Custom Deploy] Copying assets to $DestinationPath..." -ForegroundColor Green
        if (-not (Test-Path $DestinationPath)) {
            New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
        }
        $ExcludeList = @("*.ps1", "*.sh", "Dockerfile", "docker-compose.yml", "nginx.conf", "*.bak")
        Copy-Item -Path "$ScriptDir\*" -Destination $DestinationPath -Recurse -Force -Exclude $ExcludeList
        Write-Host "✓ Deployment to $DestinationPath completed!" -ForegroundColor Green
    }
}
