import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONDA_SH = "/home/umang/miniconda3/etc/profile.d/conda.sh"


def launcher_env(data_dir: Path, extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "ARBORIA_DATA_DIR": str(data_dir),
            "ARBORIA_SETUP_PASSWORD": "correct horse battery staple",
            "ARBORIA_LAUNCHER_CHECK": "1",
        }
    )
    if extra is not None:
        env.update(extra)
    return env


def run_launcher(
    root: Path, data_dir: Path, extra: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(root / "run.sh")],
        cwd="/tmp",
        env=launcher_env(data_dir, extra),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
        check=False,
    )


def test_launcher_rejects_invalid_port(tmp_path: Path) -> None:
    result = run_launcher(ROOT, tmp_path, {"ARBORIA_PORT": "70000"})

    assert result.returncode == 2
    assert "Invalid ARBORIA_PORT" in result.stdout


def test_launcher_check_mode_builds_and_repeats_without_rebuild(tmp_path: Path) -> None:
    result = run_launcher(ROOT, tmp_path)
    assert result.returncode == 0, result.stdout
    assert "Launcher check passed" in result.stdout
    assert "Conda environment" in result.stdout
    stamp = ROOT / "web" / "dist" / ".arboria-build-stamp"
    first_stamp = stamp.read_text(encoding="utf-8")

    repeated = run_launcher(ROOT, tmp_path)

    assert repeated.returncode == 0, repeated.stdout
    assert "Building browser assets" not in repeated.stdout
    assert stamp.read_text(encoding="utf-8") == first_stamp


def test_launcher_rebuilds_when_stamp_is_stale(tmp_path: Path) -> None:
    stamp = ROOT / "web" / "dist" / ".arboria-build-stamp"
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text("stale", encoding="utf-8")

    result = run_launcher(ROOT, tmp_path)

    assert result.returncode == 0, result.stdout
    assert "Building browser assets" in result.stdout
    assert stamp.read_text(encoding="utf-8") != "stale"


def test_launcher_runs_from_path_with_spaces(tmp_path: Path) -> None:
    copy_root = tmp_path / "Arboria Copy With Spaces"
    shutil.copytree(
        ROOT,
        copy_root,
        ignore=shutil.ignore_patterns(".git", "var", "web/node_modules", "web/dist"),
    )

    result = run_launcher(copy_root, tmp_path / "data")


    assert result.returncode == 0, result.stdout
    assert "Launcher check passed" in result.stdout
