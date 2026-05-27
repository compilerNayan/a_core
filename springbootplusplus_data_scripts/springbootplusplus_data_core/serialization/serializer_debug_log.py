"""Debug logging helpers for serialization pre-build pipelines."""

import os
import re
from pathlib import Path

PIPELINE = os.environ.get("SERIALIZER_PIPELINE", "serializer")


def log(msg, level="INFO"):
    print(f"[SERIALIZER:{PIPELINE}:{level}] {msg}", flush=True)


def log_banner(title):
    log("=" * 72)
    log(title)
    log("=" * 72)


def expected_annotation_name(serializable_macro):
    if serializable_macro == "_Entity":
        return "@Entity"
    if serializable_macro == "Serializable":
        return "@Serializable"
    return "@Serializable"


def scan_annotation_markers(file_path):
    """Collect @Entity / @Serializable markers (processed and unprocessed) by line number."""
    markers = {
        "entity_unprocessed": [],
        "entity_processed": [],
        "serializable_unprocessed": [],
        "serializable_processed": [],
    }
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, 1):
                stripped = line.strip()
                if re.search(r"/\*--\s*@Entity\s*--\*/", stripped):
                    markers["entity_processed"].append(line_no)
                elif re.search(r"/\*\s*@Entity\s*\*/", stripped):
                    markers["entity_unprocessed"].append(line_no)
                if re.search(r"/\*--\s*@Serializable\s*--\*/", stripped):
                    markers["serializable_processed"].append(line_no)
                elif re.search(r"/\*\s*@Serializable\s*\*/", stripped):
                    markers["serializable_unprocessed"].append(line_no)
    except OSError as exc:
        markers["read_error"] = str(exc)
    return markers


def format_markers(markers):
    parts = []
    for key in (
        "entity_unprocessed",
        "entity_processed",
        "serializable_unprocessed",
        "serializable_processed",
    ):
        if markers.get(key):
            parts.append(f"{key}@lines={markers[key]}")
    if markers.get("read_error"):
        parts.append(f"read_error={markers['read_error']}")
    return ", ".join(parts) if parts else "none"


def log_annotation_markers(file_path, serializable_macro):
    markers = scan_annotation_markers(file_path)
    if format_markers(markers) == "none":
        return markers
    log(
        f"MARKERS file={file_path} active_macro={serializable_macro} "
        f"expects={expected_annotation_name(serializable_macro)} found=[{format_markers(markers)}]"
    )
    return markers


def log_macro_mismatch(file_path, serializable_macro, markers):
    expected = expected_annotation_name(serializable_macro)
    if expected == "@Entity":
        has_pending = bool(markers.get("entity_unprocessed"))
        has_other_pending = bool(markers.get("serializable_unprocessed"))
    else:
        has_pending = bool(markers.get("serializable_unprocessed"))
        has_other_pending = bool(markers.get("entity_unprocessed"))

    if has_other_pending and not has_pending:
        log(
            f"MACRO_MISMATCH file={file_path} pipeline_macro={serializable_macro} "
            f"looks_for={expected} but file has different pending annotation: [{format_markers(markers)}]",
            level="WARN",
        )
    elif markers.get("entity_processed") or markers.get("serializable_processed"):
        if expected == "@Entity" and markers.get("serializable_unprocessed"):
            log(
                f"ALREADY_PROCESSED_OTHER file={file_path} @Entity may be done but @Serializable still pending "
                f"(other pipeline?): [{format_markers(markers)}]",
                level="WARN",
            )
        elif expected == "@Serializable" and markers.get("entity_unprocessed"):
            log(
                f"ALREADY_PROCESSED_OTHER file={file_path} @Serializable may be done but @Entity still pending "
                f"(other pipeline?): [{format_markers(markers)}]",
                level="WARN",
            )


def library_layout_flags(lib_root):
    root = Path(lib_root)
    return {
        "src": (root / "src").is_dir(),
        "include": (root / "include").is_dir(),
        "endpoint": (root / "endpoint").is_dir(),
        "internal": (root / "internal").is_dir(),
    }


def format_layout(flags):
    enabled = [name for name, present in flags.items() if present]
    return ",".join(enabled) if enabled else "none"
