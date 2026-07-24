# PyInstaller 文件夹版打包脚本实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增一个可重复执行的 PowerShell 脚本，使用固定 `donna` 环境和现有 `Donna.spec` 构建 Windows 10/11 64 位文件夹版程序。

**Architecture:** `build.ps1` 负责项目路径定位、环境与依赖预检、PyInstaller 调用和构建产物校验。脚本提供 `-ValidateOnly` 参数用于只执行预检，默认执行完整构建；不包含任何 ZIP 或 Git 操作。

**Tech Stack:** Windows PowerShell 5.1+、Python 3.12、PyInstaller 6.19、pytest；所有 Python 命令固定使用 `D:\miniconda\envs\donna\python.exe`。

---

### Task 1: 为打包脚本编写失败测试

**Files:**
- Create: `tests/test_build_script.py`
- Test: `tests/test_build_script.py`

- [ ] **Step 1: 编写脚本预检与范围约束测试**

```python
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = PROJECT_ROOT / "build.ps1"


def run_build_script(script: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            *arguments,
        ],
        cwd=script.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def test_validate_only_passes_for_project():
    assert BUILD_SCRIPT.is_file()

    result = run_build_script(BUILD_SCRIPT, "-ValidateOnly")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Preflight checks passed." in result.stdout


def test_validate_only_fails_when_project_files_are_missing(tmp_path):
    copied_script = tmp_path / "build.ps1"
    shutil.copy2(BUILD_SCRIPT, copied_script)

    result = run_build_script(copied_script, "-ValidateOnly")

    assert result.returncode != 0
    assert "Required file not found:" in result.stdout + result.stderr


def test_script_contains_no_zip_operations():
    script_content = BUILD_SCRIPT.read_text(encoding="utf-8").lower()

    assert "compress-archive" not in script_content
    assert ".zip" not in script_content
```

- [ ] **Step 2: 在 donna 环境确认测试因脚本不存在而失败**

Run:

```powershell
& 'D:\miniconda\envs\donna\python.exe' -m pytest -p no:cacheprovider tests/test_build_script.py -v
```

Expected: 测试在 `assert BUILD_SCRIPT.is_file()` 或读取 `build.ps1` 时失败，证明缺少打包脚本是失败原因。

### Task 2: 实现 PowerShell 打包脚本

**Files:**
- Create: `build.ps1`
- Test: `tests/test_build_script.py`

- [ ] **Step 1: 创建包含环境预检和完整构建流程的脚本**

```powershell
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
                "import PyInstaller, matplotlib, numpy, xlrd, tkinter; import main"
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
```

- [ ] **Step 2: 在 donna 环境运行打包脚本测试**

Run:

```powershell
& 'D:\miniconda\envs\donna\python.exe' -m pytest -p no:cacheprovider tests/test_build_script.py -v
```

Expected: `3 passed`，且 `-ValidateOnly` 不执行 PyInstaller 构建。

### Task 3: 执行真实打包并验证产物

**Files:**
- Execute: `build.ps1`
- Verify: `dist/Donna/Donna.exe`
- Verify: `dist/Donna/_internal/`

- [ ] **Step 1: 执行完整文件夹版打包**

Run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

Expected: PyInstaller 返回零状态，脚本输出 `Build completed successfully.` 和生成的 `Donna.exe` 绝对路径。

- [ ] **Step 2: 核对输出结构和文件大小**

Run:

```powershell
Get-Item -LiteralPath 'dist\Donna\Donna.exe' | Select-Object FullName, Length, LastWriteTime
Get-Item -LiteralPath 'dist\Donna\_internal' | Select-Object FullName, LastWriteTime
```

Expected: `Donna.exe` 是非空文件，`_internal` 是目录，修改时间对应本次构建。

- [ ] **Step 3: 重新运行脚本测试，确认构建后预检仍通过**

Run:

```powershell
& 'D:\miniconda\envs\donna\python.exe' -m pytest -p no:cacheprovider tests/test_build_script.py -v
```

Expected: `3 passed`。

### Task 4: 核对修改范围

**Files:**
- Inspect: `build.ps1`
- Inspect: `tests/test_build_script.py`

- [ ] **Step 1: 检查差异和空白错误**

Run:

```powershell
git diff --check
git diff -- build.ps1 tests/test_build_script.py docs/superpowers/specs/2026-07-24-pyinstaller-build-script-design.md docs/superpowers/plans/2026-07-24-pyinstaller-build-script.md
```

Expected: 没有空白错误；脚本不含 ZIP 操作；未修改 `Donna.spec`、`version/` 或 Git 状态。

- [ ] **Step 2: 确认不执行 Git 写操作**

不运行 `git add`、`git commit`、`git push` 或分支命令，版本控制交由用户手动完成。
