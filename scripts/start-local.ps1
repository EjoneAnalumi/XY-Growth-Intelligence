$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

# Starting an existing local project is safe and does not recreate its database.
npx.cmd supabase start | Out-Host

$statusLines = npx.cmd supabase status -o env 2>$null
foreach ($line in $statusLines) {
    if ($line -match '^([A-Z_]+)="(.*)"$') {
        Set-Item -Path "Env:$($matches[1])" -Value $matches[2]
    }
}

if (-not $env:DB_URL -or -not $env:API_URL -or -not $env:ANON_KEY) {
    throw "Supabase is running, but its local connection values could not be read."
}

$env:DATABASE_URL = $env:DB_URL
$env:AUTH_MODE = "supabase"
$env:SUPABASE_URL = $env:API_URL
$env:SUPABASE_ANON_KEY = $env:ANON_KEY
$env:SUPABASE_SERVICE_ROLE_KEY = $env:SERVICE_ROLE_KEY
$env:NEXT_PUBLIC_API_BASE_URL = "http://localhost:8000"
$env:NEXT_PUBLIC_SUPABASE_URL = $env:API_URL
$env:NEXT_PUBLIC_SUPABASE_ANON_KEY = $env:ANON_KEY

$backendCommand = "Set-Location -LiteralPath '$repoRoot\backend'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
$frontendCommand = "Set-Location -LiteralPath '$repoRoot\frontend'; npm.cmd run dev -- --port 3000"

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $backendCommand
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host "Backend:  http://localhost:8000"
Write-Host "Frontend: http://localhost:3000/login"
Write-Host "Database: http://localhost:54323"
Write-Host "Close the two service windows to stop backend and frontend. Do not run db reset."
