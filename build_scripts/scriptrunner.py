"""
PlatformIO extraScript entry point: runs a_core pre-build scripts in order.
"""

Import("env")

import os
from pathlib import Path

_RUNNER_DIR_NAME = "build_scripts"
_RUNNER_FILE = "scriptrunner.py"
_PRE_BUILD_SCRIPTS = (
    "core_scripts/springbootplusplus_web_pre_build.py",
    "serializationlib_scripts/serializationlib_pre_build.py",
)


def _is_library_root(path):
    root = Path(path)
    runner = root / _RUNNER_DIR_NAME / _RUNNER_FILE
    return runner.is_file()


def _search_library_root(start_path):
    current = Path(start_path).resolve()
    for _ in range(12):
        if _is_library_root(current):
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _search_pio_libdeps(project_root):
    pio_libdeps = Path(project_root) / ".pio" / "libdeps"
    if not pio_libdeps.is_dir():
        return None
    for env_dir in pio_libdeps.iterdir():
        if not env_dir.is_dir():
            continue
        for lib_dir in env_dir.iterdir():
            if lib_dir.is_dir() and _is_library_root(lib_dir):
                return lib_dir
    return None


def _get_project_dir():
    return (
        env.get("PROJECT_DIR")
        or os.environ.get("PROJECT_DIR")
        or os.environ.get("CMAKE_PROJECT_DIR")
    )


def _propagate_project_dir():
    """Library extraScript env often lacks PROJECT_DIR; child scripts read os.environ."""
    project_dir = _get_project_dir()
    if project_dir:
        os.environ["PROJECT_DIR"] = str(project_dir)
        os.environ.setdefault("CMAKE_PROJECT_DIR", str(project_dir))
    return project_dir


def find_library_root():
    try:
        candidate = Path(__file__).resolve().parent.parent
        if _is_library_root(candidate):
            return candidate
    except NameError:
        pass

    search_roots = [Path(os.getcwd())]
    project_dir = _get_project_dir()
    if project_dir:
        search_roots.append(Path(project_dir))

    for root in search_roots:
        found = _search_pio_libdeps(root)
        if found:
            return found
        found = _search_library_root(root)
        if found:
            return found

    raise ImportError(
        f"Could not find a_core library root (expected {_RUNNER_DIR_NAME}/{_RUNNER_FILE})"
    )


def _run_script(library_root, relative_path):
    script_path = (library_root / relative_path).resolve()
    if not script_path.is_file():
        raise FileNotFoundError(f"Pre-build script not found: {script_path}")

    _propagate_project_dir()

    with open(script_path, encoding="utf-8") as f:
        source = f.read()

    script_globals = {
        "env": env,
        "Import": Import,
        "__builtins__": __builtins__,
        "__file__": str(script_path),
        "__name__": "__main__",
    }
    exec(compile(source, str(script_path), "exec"), script_globals)


library_root = find_library_root()

for relative_script in _PRE_BUILD_SCRIPTS:
    _run_script(library_root, relative_script)
