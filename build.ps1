[CmdletBinding()]
param(
    [switch]$ValidateOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$pythonPath = "D:\miniconda\envs\donna\python.exe"
$requiredFiles = @(
    "main.py",
    "Donna.spec",
    "version.txt",
    "icon\111.ico"
)

function Invoke-PythonCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [Parameter(Mandatory = $true)]
        [string]$FailureMessage
    )

    & $pythonPath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw $FailureMessage
    }
}

try {
    if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
        throw "Donna Python not found: $pythonPath"
    }

    foreach ($relativePath in $requiredFiles) {
        $fullPath = Join-Path $projectRoot $relativePath
        if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
            throw "Required file not found: $fullPath"
        }
    }

    Push-Location $projectRoot
    try {
        Invoke-PythonCommand `
            -Arguments @(
                "-c",
                "import struct; assert struct.calcsize('P') * 8 == 64, '64-bit Python is required'"
            ) `
            -FailureMessage "The donna environment must use 64-bit Python."

        Invoke-PythonCommand `
            -Arguments @(
                "-c",
                "import PyInstaller, matplotlib, numpy, xlrd, openpyxl, tkinter; import main"
            ) `
            -FailureMessage "Required packaging or application dependencies are unavailable."

        Write-Host "Preflight checks passed."

        if ($ValidateOnly) {
            exit 0
        }

        Write-Host "Building Donna with PyInstaller..."
        Invoke-PythonCommand `
            -Arguments @("-m", "PyInstaller", "--clean", "--noconfirm", "Donna.spec") `
            -FailureMessage "PyInstaller build failed."

        $executablePath = Join-Path $projectRoot "dist\Donna\Donna.exe"
        $internalPath = Join-Path $projectRoot "dist\Donna\_internal"

        if (-not (Test-Path -LiteralPath $executablePath -PathType Leaf)) {
            throw "Build output not found: $executablePath"
        }
        if (-not (Test-Path -LiteralPath $internalPath -PathType Container)) {
            throw "Build dependency directory not found: $internalPath"
        }

        Write-Host "Build completed successfully."
        Write-Host "Output: $executablePath"
    }
    finally {
        Pop-Location
    }
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
