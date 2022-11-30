import os
import shutil
import zipfile
from fnmatch import fnmatch
from pathlib import Path

import pdm.backend
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def project(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    project = FIXTURES / "test-project"
    shutil.copytree(project, tmp_path / project.name)
    monkeypatch.chdir(tmp_path / project.name)
    return tmp_path / project.name


def test_build_with_mypyc(project: Path, tmp_path: Path):
    wheel_name = pdm.backend.build_wheel(tmp_path)
    suffix = ".pyd" if os.name == "nt" else ".so"
    with zipfile.ZipFile(tmp_path / wheel_name) as zf:
        namelist = zf.namelist()
        assert any(fnmatch(name, f"foo/fib.*{suffix}") for name in namelist)
        assert not any(fnmatch(name, f"foo/__init__.*{suffix}") for name in namelist)


def test_build_disable_mypy_with_env_var(
    project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("PDM_BUILD_WITHOUT_MYPYC", "true")
    wheel_name = pdm.backend.build_wheel(tmp_path)
    suffix = ".pyd" if os.name == "nt" else ".so"
    with zipfile.ZipFile(tmp_path / wheel_name) as zf:
        namelist = zf.namelist()
        assert not any(fnmatch(name, f"foo/*{suffix}") for name in namelist)
