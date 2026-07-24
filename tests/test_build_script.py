import shutil
import subprocess
import tempfile
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


def test_validate_only_fails_when_project_files_are_missing():
    with tempfile.TemporaryDirectory(
        prefix="donna-build-test-", dir=PROJECT_ROOT
    ) as temp_directory:
        copied_script = Path(temp_directory) / "build.ps1"
        shutil.copy2(BUILD_SCRIPT, copied_script)

        result = run_build_script(copied_script, "-ValidateOnly")

        assert result.returncode != 0
        assert "Required file not found:" in result.stdout + result.stderr


def test_script_contains_no_zip_operations():
    script_content = BUILD_SCRIPT.read_text(encoding="utf-8").lower()

    assert "compress-archive" not in script_content
    assert ".zip" not in script_content
