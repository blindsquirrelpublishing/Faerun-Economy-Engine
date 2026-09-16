<#
    Faerun Economy Engine - one-click launcher.

    Right-click this file and choose "Run with PowerShell", or from any
    PowerShell prompt:

        cd 'C:\Users\murrayfife\OneDrive\Workspaces\Faerun Economy Engine'
        .\run.ps1

    The script cd's to its own folder anyway, so it does not matter where you
    start it from.

        .\run.ps1              # check, then open the market board
        .\run.ps1 -Map         # open the 3D world map instead
        .\run.ps1 -Check       # only run the checks, do not start the server
        .\run.ps1 -SkipCheck   # go straight to the board
        .\run.ps1 -Port 9000   # serve on a different port
        .\run.ps1 -SeasonalInventory  # opt into daily seasonal stock replay

        # Drape your own copy of a Faerun poster map over the 3D world map.
        # Anything dropped in the maps\ folder is found automatically, so this
        # flag is only needed for a file kept somewhere else. Nothing is ever
        # copied into the project - the file is read where it sits.
        .\run.ps1 -Map -Underlay "$HOME\Downloads\Faerun Map.jpg"

    If Windows blocks the script with an execution-policy error, run:

        powershell -ExecutionPolicy Bypass -File .\run.ps1
#>

[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$SkipCheck,
    [int]$Port = 8765,
    [switch]$NoBrowser,
    [switch]$Map,
    [switch]$SeasonalInventory,
    [string]$Underlay = ''
)

$ErrorActionPreference = 'Stop'
# PowerShell 7.3+ otherwise turns any non-zero exit from a native command into
# a terminating error, which would bypass the exit-code handling below.
$PSNativeCommandUseErrorActionPreference = $false

# --- change to the project folder -----------------------------------------
# Everything below assumes the current directory is the folder holding this
# script, because that is where the "faerun" package and verify.py live and
# Python resolves "import faerun" from the working directory. So cd there
# ourselves rather than relying on wherever the shell happened to be started.
# $PSScriptRoot is empty when the file is dot-sourced or piped in, so fall
# back to the invocation path before giving up.
$projectRoot = $PSScriptRoot
if (-not $projectRoot -and $MyInvocation.MyCommand.Path) {
    $projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}
if (-not $projectRoot) {
    $projectRoot = (Get-Location).Path
}
Set-Location -LiteralPath $projectRoot

if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'faerun'))) {
    Write-Host ''
    Write-Host "   Cannot see the 'faerun' package in $projectRoot" -ForegroundColor Red
    Write-Host '   Move run.ps1 back beside the faerun folder, or cd there first:'
    Write-Host "     cd '$projectRoot'"
    exit 1
}

function Write-Step($text) {
    Write-Host ''
    Write-Host "== $text" -ForegroundColor Yellow
}

function Write-Ok($text) { Write-Host "   $text" -ForegroundColor Green }
function Write-Bad($text) { Write-Host "   $text" -ForegroundColor Red }

# --- find a usable Python -------------------------------------------------
# Being on PATH is not enough: Windows ships an "app execution alias" stub named
# python.exe that resolves fine but does nothing except open the Microsoft
# Store. So actually run each candidate and keep the first that reports a
# version.
$python = $null
$probeLog = @()
foreach ($candidate in @('python', 'py -3', 'python3', 'py')) {
    $exe, $prefix = $candidate -split ' ', 2
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) {
        $probeLog += "$candidate - not on PATH"
        continue
    }
    $probe = @()
    if ($prefix) { $probe += $prefix }
    $probe += '-c'
    $probe += 'import sys; print(sys.version_info[0])'
    $output = $null
    $code = $null
    try {
        $ErrorActionPreference = 'Continue'
        # Deliberately NOT piped into Select-Object. Piping a native command
        # into "Select-Object -First 1" stops the upstream pipeline as soon as
        # it has its object, which can tear python.exe down before it exits and
        # leave $LASTEXITCODE non-zero - so a perfectly good interpreter gets
        # rejected, intermittently. Capture everything, then pick the line.
        $output = & $exe @probe 2>$null
        $code = $LASTEXITCODE
    }
    catch {
        $probeLog += "$candidate - $($_.Exception.Message)"
        continue
    }
    finally {
        $ErrorActionPreference = 'Stop'
    }
    $first = "$(@($output) | Select-Object -First 1)".Trim()
    if ($first -eq '3') {
        # Trust the interpreter's own answer over its exit status: it told us it
        # is Python 3, which is the thing we actually needed to know.
        $python = $candidate
        break
    }
    $probeLog += "$candidate - exit $code, said '$first'"
}

if (-not $python) {
    Write-Bad 'No working Python 3 interpreter found on PATH.'
    Write-Host '   Tried:'
    foreach ($line in $probeLog) { Write-Host "     $line" }
    Write-Host '   Install Python 3.10 or newer from https://python.org and tick'
    Write-Host '   "Add python.exe to PATH" during setup, then run this again.'
    Write-Host '   If Python IS installed, run this to see what the probe sees:'
    Write-Host '     python -c "import sys; print(sys.version_info[0])"'
    exit 1
}

# Runs Python, streaming its output straight to the console.
#
# The call is deliberately NOT piped anywhere. Sending a native command through
# a pipeline while $ErrorActionPreference is 'Stop' makes Windows PowerShell
# wrap anything the process writes to stderr in a NativeCommandError and throw -
# and http.server logs every single request to stderr, so the first page load
# would kill the script. Calling it bare lets stdout and stderr go straight to
# the console, keeps Ctrl+C working, and still sets $LASTEXITCODE.
# The exit code is published here rather than returned, because a bare native
# call inside a function sends the program's stdout to the function's output
# stream - returning the code as well would hand the caller an array of every
# printed line with the number tacked on the end.
$script:PythonExit = 0

function Invoke-Python {
    param([string[]]$Arguments)
    $exe, $prefix = $python -split ' ', 2
    $all = @()
    if ($prefix) { $all += $prefix }
    $all += $Arguments
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $exe @all
    }
    finally {
        $ErrorActionPreference = $previous
        $script:PythonExit = $LASTEXITCODE
    }
}

Write-Step "Working in $projectRoot"
Write-Step "Using $python"
Invoke-Python @('--version')

# --- 1. syntax check ------------------------------------------------------
if (-not $SkipCheck) {
    Write-Step 'Compiling (catches syntax errors)'
    Invoke-Python @('-m', 'compileall', '-q', 'faerun', 'tests', 'verify.py')
    if ($script:PythonExit -ne 0) {
        Write-Bad 'Compilation failed - see the errors above.'
        exit $script:PythonExit
    }
    Write-Ok 'All modules compile.'

    # --- 2. smoke test ----------------------------------------------------
    Write-Step 'Running the smoke test (this walks 130 goods x 125 markets, allow a minute)'
    Invoke-Python @('verify.py')
    if ($script:PythonExit -ne 0) {
        Write-Bad 'verify.py reported failures - see the report above.'
        exit $script:PythonExit
    }
    Write-Ok 'Every check passed.'
}

if ($Check) {
    Write-Step 'Checks only (-Check given); not starting the server.'
    exit 0
}

# --- 3. the commodity board ----------------------------------------------
# The server bakes its pages in when it starts, so a copy left running from an
# earlier session will keep serving the old set and any page added since will
# look broken. Clear it out before binding.
$stale = $null
try {
    $stale = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop |
             Select-Object -First 1
} catch {
    $stale = $null
}
if ($stale) {
    $owner = Get-Process -Id $stale.OwningProcess -ErrorAction SilentlyContinue
    $who = if ($owner) { "$($owner.ProcessName) (PID $($owner.Id))" } else { "PID $($stale.OwningProcess)" }
    Write-Step "Port $Port is already in use by $who"
    if ($owner -and $owner.ProcessName -match '^py(thon|thonw)?$') {
        Write-Host '   That looks like an older copy of this server; stopping it.'
        Stop-Process -Id $owner.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 600
    } else {
        Write-Host "   Not a Python process, so leaving it alone."
        Write-Host "   Start on a free port instead:  .\run.ps1 -Port $($Port + 1)"
        exit 1
    }
}

Write-Step "Starting the market board on port $Port"
Write-Host "   Commodity board : http://127.0.0.1:$Port/"
Write-Host "   3D world map    : http://127.0.0.1:$Port/map.html"
Write-Host "   Location history: http://127.0.0.1:$Port/location.html"
Write-Host '   Press Ctrl+C in this window to stop it.'
$subcommand = if ($Map) { 'map' } else { 'serve' }
$serveArgs = @('-m', 'faerun.cli')
if ($SeasonalInventory) { $serveArgs += '--seasonal-inventory' }
$serveArgs += @($subcommand, '--port', "$Port")
if ($NoBrowser) { $serveArgs += '--no-browser' }
if ($Underlay) {
    if (-not (Test-Path -LiteralPath $Underlay)) {
        Write-Host "   No file at $Underlay - the poster overlay will be skipped." -ForegroundColor Yellow
    } else {
        $serveArgs += @('--underlay', (Resolve-Path -LiteralPath $Underlay).Path)
    }
}
Invoke-Python $serveArgs
exit $script:PythonExit
