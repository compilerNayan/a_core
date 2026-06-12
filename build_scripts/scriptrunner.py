"""
PlatformIO extraScript entry point: runs a_core pre-build scripts in order.
"""

Import("env")

import hashlib
import os
import sys
from pathlib import Path

_RUNNER_DIR_NAME = "build_scripts"
_RUNNER_FILE = "scriptrunner.py"
_PRE_BUILD_SCRIPTS = (
    "core_scripts/springbootplusplus_web_pre_build.py",
    "serializationlib_scripts/serializationlib_pre_build.py",
    "springbootplusplus_data_scripts/springbootplusplus_data_pre_build.py",
)

# Stamp file lives in the consuming project (next to `src/`), NOT inside the
# library, so each project tracks its own pre-build state and library updates
# do not pollute the library tree.
_STAMP_DIR_NAME = "generated"
_STAMP_FILE_NAME = ".a_core_prebuild.stamp"


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


def _ensure_python_on_path():
    """CMake/ESP-IDF subprocesses may omit PlatformIO penv from PATH; child scripts invoke sys.executable."""
    python_dir = str(Path(sys.executable).resolve().parent)
    current_path = os.environ.get("PATH", "")
    if python_dir not in current_path.split(os.pathsep):
        os.environ["PATH"] = python_dir + os.pathsep + current_path


def _run_script(library_root, relative_path):
    script_path = (library_root / relative_path).resolve()
    if not script_path.is_file():
        raise FileNotFoundError(f"Pre-build script not found: {script_path}")

    _propagate_project_dir()
    _ensure_python_on_path()

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


def _compute_scripts_fingerprint(library_root):
    """SHA-256 over (relative_path, file_contents) of every pre-build script.

    If any script is edited, added, removed or reordered the digest changes,
    which forces a re-run on the next build. This is the same idea as
    Make/Ninja/CMake stamp files.
    """
    hasher = hashlib.sha256()
    for relative_script in _PRE_BUILD_SCRIPTS:
        script_path = (library_root / relative_script).resolve()
        hasher.update(relative_script.encode("utf-8"))
        hasher.update(b"\0")
        with open(script_path, "rb") as f:
            hasher.update(f.read())
        hasher.update(b"\0")
    return hasher.hexdigest()


def _get_stamp_path():
    project_dir = _get_project_dir()
    if not project_dir:
        return None
    return Path(project_dir) / _STAMP_DIR_NAME / _STAMP_FILE_NAME


def _read_stamp(stamp_path):
    try:
        return stamp_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None


def _write_stamp(stamp_path, fingerprint):
    stamp_path.parent.mkdir(parents=True, exist_ok=True)
    # Keep the `generated/` folder out of version control by default.
    gitignore = stamp_path.parent / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n", encoding="utf-8")
    stamp_path.write_text(fingerprint + "\n", encoding="utf-8")


def _log(message):
    sys.stdout.write(f"[a_core scriptrunner] {message}\n")
    sys.stdout.flush()


library_root = find_library_root()
stamp_path = _get_stamp_path()
fingerprint = _compute_scripts_fingerprint(library_root)

if stamp_path is not None and _read_stamp(stamp_path) == fingerprint:
    _log(f"pre-build scripts already up to date (stamp: {stamp_path}); skipping.")
else:
    for relative_script in _PRE_BUILD_SCRIPTS:
        _run_script(library_root, relative_script)
    if stamp_path is not None:
        _write_stamp(stamp_path, fingerprint)
        _log(f"pre-build scripts completed; stamp written to {stamp_path}.")
    else:
        _log("PROJECT_DIR not resolved; ran pre-build scripts without writing stamp.")
