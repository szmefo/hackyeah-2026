$ErrorActionPreference = 'Stop'
$taskRepo = Split-Path -Parent $PSScriptRoot
$taskEnvPath = Join-Path $taskRepo '.env.local'
if (-not (Test-Path -LiteralPath $taskEnvPath)) {
    Copy-Item -LiteralPath (Join-Path $taskRepo '.env.example') -Destination $taskEnvPath
}
$taskEnvText = [System.IO.File]::ReadAllText($taskEnvPath)
$taskMatch = [regex]::Match($taskEnvText, '(?m)^ENGINE_SHARED_SECRET=([^\r\n]*)')
$taskSecret = $taskMatch.Groups[1].Value.Trim()
if (-not $taskSecret) {
    $taskBytes = [byte[]]::new(32)
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($taskBytes)
    $taskSecret = [Convert]::ToHexString($taskBytes).ToLowerInvariant()
    $taskEnvText = [regex]::Replace($taskEnvText, '(?m)^ENGINE_SHARED_SECRET=[^\r\n]*', "ENGINE_SHARED_SECRET=$taskSecret")
    [System.IO.File]::WriteAllText($taskEnvPath, $taskEnvText, [System.Text.UTF8Encoding]::new($false))
}
$env:ENGINE_SHARED_SECRET = $taskSecret
Set-Location -LiteralPath (Join-Path $taskRepo 'engine')
& '.\.venv\Scripts\python.exe' -m uvicorn main:app --host 127.0.0.1 --port 8000 --no-access-log
