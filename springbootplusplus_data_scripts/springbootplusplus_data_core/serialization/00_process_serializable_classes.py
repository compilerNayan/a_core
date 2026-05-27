#!/usr/bin/env python3
"""
00 Process Entity Classes Script

Orchestrator script that processes all classes with @Entity annotation in client files.
"""

import os
import sys
import importlib.util
import traceback
from pathlib import Path

os.environ["SERIALIZER_PIPELINE"] = "springbootplusplus_data"

# Import get_client_files from parent directory
# Handle both direct execution and dynamic loading
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback: use library_dir if available
    if 'library_dir' in globals():
        script_dir = os.path.join(globals()['library_dir'], 'springbootplusplus_data_scripts', 'springbootplusplus_data_core', 'serialization')
    else:
        # Last resort: try to get from current file location
        import inspect
        try:
            script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        except:
            script_dir = os.getcwd()
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, script_dir)

try:
    import serializer_debug_log as dbg
except ImportError:
    dbg = None

try:
    from get_client_files import get_client_files
except ImportError:
    get_client_files = None

# Import the serializer scripts
sys.path.insert(0, script_dir)

spec_s1 = importlib.util.spec_from_file_location("S1_check_dto_macro", os.path.join(script_dir, "S1_check_dto_macro.py"))
S1_check_dto_macro = importlib.util.module_from_spec(spec_s1)
spec_s1.loader.exec_module(S1_check_dto_macro)

spec_s3 = importlib.util.spec_from_file_location("S3_inject_serialization", os.path.join(script_dir, "S3_inject_serialization.py"))
S3_inject_serialization = importlib.util.module_from_spec(spec_s3)
spec_s3.loader.exec_module(S3_inject_serialization)

# Import enum serialization script from serializationlib (it's shared)
# Try to find serializationlib's serialization scripts
S8_handle_enum_serialization = None
try:
    # Method 1: Try to find from library_dir if available
    if 'library_dir' in globals():
        potential_lib1_scripts = os.path.join(globals()['library_dir'], 'serializationlib', 'serializationlib_scripts', 'serializationlib_serializer', 'S8_handle_enum_serialization.py')
        if os.path.exists(potential_lib1_scripts):
            spec_s8 = importlib.util.spec_from_file_location("S8_handle_enum_serialization", potential_lib1_scripts)
            S8_handle_enum_serialization = importlib.util.module_from_spec(spec_s8)
            spec_s8.loader.exec_module(S8_handle_enum_serialization)
    
    # Method 2: Try to find from project_dir
    if S8_handle_enum_serialization is None:
        project_dir = None
        if 'project_dir' in globals():
            project_dir = globals()['project_dir']
        elif 'PROJECT_DIR' in os.environ:
            project_dir = os.environ['PROJECT_DIR']
        elif 'CMAKE_PROJECT_DIR' in os.environ:
            project_dir = os.environ['CMAKE_PROJECT_DIR']
        
        if project_dir:
            potential_lib1_scripts = os.path.join(project_dir, 'serializationlib', 'serializationlib_scripts', 'serializationlib_serializer', 'S8_handle_enum_serialization.py')
            if os.path.exists(potential_lib1_scripts):
                spec_s8 = importlib.util.spec_from_file_location("S8_handle_enum_serialization", potential_lib1_scripts)
                S8_handle_enum_serialization = importlib.util.module_from_spec(spec_s8)
                spec_s8.loader.exec_module(S8_handle_enum_serialization)
    
    # Method 3: Try relative path from current script
    if S8_handle_enum_serialization is None:
        current_file = os.path.abspath(__file__)
        # Go up: serialization -> springbootplusplus_data_core -> springbootplusplus_data_scripts -> springbootplusplus_data -> project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        potential_lib1_scripts = os.path.join(project_root, 'serializationlib', 'serializationlib_scripts', 'serializationlib_serializer', 'S8_handle_enum_serialization.py')
        if os.path.exists(potential_lib1_scripts):
            spec_s8 = importlib.util.spec_from_file_location("S8_handle_enum_serialization", potential_lib1_scripts)
            S8_handle_enum_serialization = importlib.util.module_from_spec(spec_s8)
            spec_s8.loader.exec_module(S8_handle_enum_serialization)
except Exception:
    S8_handle_enum_serialization = None


def discover_all_libraries(project_dir):
    """Discover all library directories in build/_deps/ (CMake) and .pio/libdeps/ (PlatformIO)."""
    libraries = []
    seen_libraries = set()

    if not project_dir:
        if dbg:
            dbg.log("discover_all_libraries: project_dir is empty", level="WARN")
        return libraries

    project_path = Path(project_dir).resolve()
    if dbg:
        dbg.log(f"discover_all_libraries: project_dir={project_path}")

    build_deps = project_path / "build" / "_deps"

    if build_deps.exists() and build_deps.is_dir():
        if dbg:
            dbg.log(f"scanning CMake build/_deps at {build_deps}")
        for lib_dir in build_deps.iterdir():
            if lib_dir.is_dir() and not lib_dir.name.startswith("."):
                lib_name = lib_dir.name
                layout = dbg.library_layout_flags(lib_dir) if dbg else {}

                if lib_name.endswith("-src"):
                    lib_root = lib_dir.resolve()
                    lib_path_str = str(lib_root)
                    if lib_path_str not in seen_libraries:
                        seen_libraries.add(lib_path_str)
                        libraries.append(lib_root)
                        if dbg:
                            dbg.log(
                                f"LIB_INCLUDED source=cmake name={lib_name} path={lib_root} "
                                f"reason=ends-with-src layout={dbg.format_layout(layout)}"
                            )
                elif (lib_dir / "src").exists() and (lib_dir / "src").is_dir():
                    lib_root = lib_dir.resolve()
                    lib_path_str = str(lib_root)
                    if lib_path_str not in seen_libraries:
                        seen_libraries.add(lib_path_str)
                        libraries.append(lib_root)
                        if dbg:
                            dbg.log(
                                f"LIB_INCLUDED source=cmake name={lib_name} path={lib_root} "
                                f"reason=has-src layout={dbg.format_layout(layout)}"
                            )
                elif dbg:
                    dbg.log(
                        f"LIB_SKIPPED source=cmake name={lib_name} path={lib_dir} "
                        f"reason=no-src-and-not-*-src layout={dbg.format_layout(layout)}",
                        level="WARN",
                    )
    elif dbg:
        dbg.log(f"no CMake build/_deps directory at {build_deps}")

    pio_libdeps = project_path / ".pio" / "libdeps"

    if pio_libdeps.exists() and pio_libdeps.is_dir():
        if dbg:
            dbg.log(f"scanning PlatformIO .pio/libdeps at {pio_libdeps}")
        for env_dir in pio_libdeps.iterdir():
            if env_dir.is_dir():
                if dbg:
                    dbg.log(f"pio env={env_dir.name}")
                for lib_dir in env_dir.iterdir():
                    if lib_dir.is_dir():
                        lib_root = lib_dir.resolve()
                        lib_path_str = str(lib_root)
                        has_src = (lib_root / "src").exists() and (lib_root / "src").is_dir()
                        has_include = (lib_root / "include").exists() and (lib_root / "include").is_dir()
                        has_endpoint = (lib_root / "endpoint").exists() and (lib_root / "endpoint").is_dir()
                        has_internal = (lib_root / "internal").exists() and (lib_root / "internal").is_dir()
                        layout = dbg.library_layout_flags(lib_root) if dbg else {}
                        if has_src or has_include or has_endpoint or has_internal:
                            if lib_path_str not in seen_libraries:
                                seen_libraries.add(lib_path_str)
                                libraries.append(lib_root)
                                if dbg:
                                    dbg.log(
                                        f"LIB_INCLUDED source=pio env={env_dir.name} name={lib_dir.name} "
                                        f"path={lib_root} layout={dbg.format_layout(layout)}"
                                    )
                        elif dbg:
                            dbg.log(
                                f"LIB_SKIPPED source=pio env={env_dir.name} name={lib_dir.name} "
                                f"path={lib_root} reason=no-src/include/endpoint/internal "
                                f"layout={dbg.format_layout(layout)}",
                                level="WARN",
                            )
    elif dbg:
        dbg.log(f"no PlatformIO .pio/libdeps directory at {pio_libdeps}")

    if dbg:
        dbg.log(f"discover_all_libraries: total_included={len(libraries)}")
    return libraries


def process_all_serializable_classes(dry_run=False, serializable_macro=None):
    """Process all client files that contain classes with @Entity annotation."""
    if serializable_macro is None:
        if 'serializable_macro' in globals():
            serializable_macro = globals()['serializable_macro']
        elif 'SERIALIZABLE_MACRO' in os.environ:
            serializable_macro = os.environ['SERIALIZABLE_MACRO']
        else:
            serializable_macro = "_Entity"

    if dbg:
        dbg.log_banner("springbootplusplus_data 00_process_serializable_classes START")
        dbg.log(f"cwd={os.getcwd()}")
        dbg.log(f"dry_run={dry_run}")
        dbg.log(f"serializable_macro={serializable_macro} (env SERIALIZABLE_MACRO={os.environ.get('SERIALIZABLE_MACRO')})")
        dbg.log(f"looks_for_annotation={dbg.expected_annotation_name(serializable_macro)}")
        dbg.log(f"S8_handle_enum_serialization={'loaded' if S8_handle_enum_serialization else 'NOT_LOADED'}")
        dbg.log(f"get_client_files={'loaded' if get_client_files else 'NOT_LOADED'}")

    project_dir = None
    library_dir = None
    for name, mod in sys.modules.items():
        if hasattr(mod, 'process_all_serializable_classes') and mod.process_all_serializable_classes == process_all_serializable_classes:
            if hasattr(mod, 'project_dir') and mod.project_dir is not None:
                project_dir = mod.project_dir
            if hasattr(mod, 'library_dir') and mod.library_dir is not None:
                library_dir = mod.library_dir
            if project_dir is not None:
                break
            if hasattr(mod, '__dict__'):
                if project_dir is None and mod.__dict__.get('project_dir') is not None:
                    project_dir = mod.__dict__['project_dir']
                if library_dir is None and mod.__dict__.get('library_dir') is not None:
                    library_dir = mod.__dict__['library_dir']
                if project_dir is not None:
                    break

    if not project_dir and 'project_dir' in globals() and globals()['project_dir'] is not None:
        project_dir = globals()['project_dir']
    if not library_dir and 'library_dir' in globals() and globals()['library_dir'] is not None:
        library_dir = globals()['library_dir']

    if not project_dir:
        if 'PROJECT_DIR' in os.environ:
            project_dir = os.environ['PROJECT_DIR']
        elif 'CMAKE_PROJECT_DIR' in os.environ:
            project_dir = os.environ['CMAKE_PROJECT_DIR']
    if not library_dir and 'LIBRARY_DIR' in os.environ:
        library_dir = os.environ['LIBRARY_DIR']

    if dbg:
        dbg.log(f"resolved project_dir={project_dir}")
        dbg.log(f"resolved library_dir={library_dir}")

    if not project_dir:
        if dbg:
            dbg.log("ABORT: project_dir not set (set PROJECT_DIR / CMAKE_PROJECT_DIR or pass project_dir)", level="ERROR")
        return 0

    if get_client_files is None:
        if dbg:
            dbg.log("ABORT: get_client_files import failed", level="ERROR")
        return 0

    all_libraries = discover_all_libraries(project_dir)
    header_files = []
    files_by_source = {}

    try:
        project_files = get_client_files(project_dir, file_extensions=['.h', '.hpp'])
        header_files.extend(project_files)
        files_by_source["project"] = len(project_files)
        if dbg:
            dbg.log(f"project headers: count={len(project_files)} root={project_dir}")
    except Exception as exc:
        files_by_source["project"] = 0
        if dbg:
            dbg.log(f"project header scan FAILED: {exc}", level="ERROR")
            dbg.log(traceback.format_exc(), level="ERROR")

    for lib_dir in all_libraries:
        try:
            lib_files = get_client_files(str(lib_dir), skip_exclusions=True, file_extensions=['.h', '.hpp'])
            header_files.extend(lib_files)
            files_by_source[str(lib_dir)] = len(lib_files)
            if dbg:
                dbg.log(f"library headers: lib={lib_dir} count={len(lib_files)}")
        except Exception as exc:
            files_by_source[str(lib_dir)] = 0
            if dbg:
                dbg.log(f"library header scan FAILED lib={lib_dir}: {exc}", level="ERROR")
                dbg.log(traceback.format_exc(), level="ERROR")

    unique_header_files = sorted(set(header_files))
    if dbg:
        dbg.log(
            f"header scan summary: total_paths={len(header_files)} unique={len(unique_header_files)} "
            f"by_source={files_by_source}"
        )

    if not unique_header_files:
        if dbg:
            dbg.log("DONE: no header files to scan", level="WARN")
        return 0

    processed_count = 0
    skipped_no_annotation = 0
    skipped_already_processed = 0
    skipped_macro_mismatch = 0
    failed_inject = 0
    interesting_names = ("MqttCredentials", "ConnectionConfig", "PublishTopics", "SubscribeTopics", "RetDto")

    primitive_types = ['int', 'Int', 'CInt', 'long', 'Long', 'CLong', 'float', 'Float', 'CFloat',
                      'double', 'Double', 'CDouble', 'bool', 'Bool', 'CBool', 'char', 'Char', 'CChar',
                      'unsigned', 'UInt', 'CUInt', 'short', 'Short', 'CShort']

    for file_path in unique_header_files:
        is_interesting = any(name in file_path for name in interesting_names)
        if not os.path.exists(file_path):
            if dbg and is_interesting:
                dbg.log(f"SKIP missing file: {file_path}", level="WARN")
            continue

        markers = dbg.scan_annotation_markers(file_path) if dbg else {}
        has_any_marker = dbg.format_markers(markers) != "none" if dbg else False
        if dbg and (has_any_marker or is_interesting):
            dbg.log_annotation_markers(file_path, serializable_macro)

        if S8_handle_enum_serialization:
            enum_info = S8_handle_enum_serialization.check_enum_annotation(file_path, serializable_macro)
            if enum_info and enum_info.get('has_enum'):
                if dbg:
                    dbg.log(f"ENUM_MATCH file={file_path} enum={enum_info.get('enum_name')}")
                if not dry_run:
                    enum_name = enum_info['enum_name']
                    enum_line = enum_info['enum_line']
                    annotation_line = enum_info['annotation_line']
                    enum_values = S8_handle_enum_serialization.extract_enum_values(file_path, enum_name, enum_line)
                    if enum_values:
                        code = S8_handle_enum_serialization.generate_enum_serialization_code(enum_name, enum_values)
                        S8_handle_enum_serialization.add_include_if_needed(file_path, "<SerializationUtility.h>")
                        S8_handle_enum_serialization.add_include_if_needed(file_path, "<algorithm>")
                        S8_handle_enum_serialization.add_include_if_needed(file_path, "<cctype>")
                        success = S8_handle_enum_serialization.inject_enum_code(file_path, code, dry_run=False)
                        if success:
                            S8_handle_enum_serialization.mark_enum_annotation_processed(file_path, annotation_line, dry_run=False)
                            processed_count += 1
                            if dbg:
                                dbg.log(f"ENUM_PROCESSED file={file_path} enum={enum_name}", level="OK")
                        elif dbg:
                            dbg.log(f"ENUM_INJECT_FAILED file={file_path} enum={enum_name}", level="ERROR")
                    elif dbg:
                        dbg.log(f"ENUM_NO_VALUES file={file_path} enum={enum_name}", level="WARN")

        dto_info = S1_check_dto_macro.check_dto_macro(file_path, serializable_macro)

        if not dto_info or not dto_info.get('has_dto'):
            if dbg and has_any_marker:
                if markers.get("entity_processed") or markers.get("serializable_processed"):
                    skipped_already_processed += 1
                    if is_interesting:
                        dbg.log(
                            f"SKIP already_processed file={file_path} active_macro={serializable_macro} "
                            f"markers=[{dbg.format_markers(markers)}]"
                        )
                else:
                    skipped_macro_mismatch += 1
                    dbg.log_macro_mismatch(file_path, serializable_macro, markers)
                    if is_interesting:
                        dbg.log(
                            f"SKIP no_match_for_active_macro file={file_path} "
                            f"active_macro={serializable_macro} expects={dbg.expected_annotation_name(serializable_macro)}",
                            level="WARN",
                        )
            elif dbg and is_interesting:
                skipped_no_annotation += 1
                dbg.log(f"SKIP no_pending_annotation file={file_path} active_macro={serializable_macro}")
            continue

        class_name = dto_info['class_name']
        if dbg:
            dbg.log(
                f"CLASS_MATCH file={file_path} class={class_name} "
                f"dto_line={dto_info.get('dto_line')} class_line={dto_info.get('class_line')}"
            )

        import S2_extract_dto_fields
        spec_s2 = importlib.util.spec_from_file_location("S2_extract_dto_fields", os.path.join(script_dir, "S2_extract_dto_fields.py"))
        S2_extract_dto_fields = importlib.util.module_from_spec(spec_s2)
        spec_s2.loader.exec_module(S2_extract_dto_fields)

        fields = S2_extract_dto_fields.extract_all_fields(file_path, class_name)
        boundaries = S2_extract_dto_fields.find_class_boundaries(file_path, class_name)
        if dbg:
            dbg.log(f"FIELDS file={file_path} class={class_name} count={len(fields)} boundaries={boundaries}")
            if not fields:
                dbg.log(f"WARN no_fields_extracted file={file_path} class={class_name}", level="WARN")

        optional_fields = [field for field in fields if S3_inject_serialization.is_optional_type(field['type'].strip())]
        non_optional_fields = [field for field in fields if not S3_inject_serialization.is_optional_type(field['type'].strip())]
        if dbg:
            dbg.log(
                f"FIELD_TYPES file={file_path} optional={len(optional_fields)} "
                f"non_optional={len(non_optional_fields)}"
            )

        import S6_discover_validation_macros
        spec_s6 = importlib.util.spec_from_file_location("S6_discover_validation_macros", os.path.join(script_dir, "S6_discover_validation_macros.py"))
        S6_discover_validation_macros = importlib.util.module_from_spec(spec_s6)
        spec_s6.loader.exec_module(S6_discover_validation_macros)

        validation_macros = S6_discover_validation_macros.find_validation_macro_definitions(None)

        import S7_extract_validation_fields
        spec_s7 = importlib.util.spec_from_file_location("S7_extract_validation_fields", os.path.join(script_dir, "S7_extract_validation_fields.py"))
        S7_extract_validation_fields = importlib.util.module_from_spec(spec_s7)
        spec_s7.loader.exec_module(S7_extract_validation_fields)

        validation_fields_by_macro = S7_extract_validation_fields.extract_validation_fields(
            file_path, class_name, validation_macros
        )

        try:
            from extract_id_fields import extract_id_fields
            id_fields = extract_id_fields(file_path, class_name)
        except Exception as exc:
            id_fields = []
            if dbg:
                dbg.log(f"ID_FIELDS extract failed file={file_path}: {exc}", level="WARN")

        if dbg and id_fields:
            dbg.log(f"ID_FIELDS file={file_path} count={len(id_fields)} names={[f.get('name') for f in id_fields]}")

        methods_code = S3_inject_serialization.generate_serialization_methods(class_name, fields, validation_fields_by_macro, id_fields)

        if not dry_run and optional_fields:
            S3_inject_serialization.add_include_if_needed(file_path, "<optional>")

        needs_serializer = False
        for field in fields:
            field_type = field['type'].strip()
            if S3_inject_serialization.is_optional_type(field_type):
                inner_type = S3_inject_serialization.extract_inner_type_from_optional(field_type)
                is_primitive = any(prim in inner_type for prim in primitive_types)
                is_string = 'StdString' in inner_type or 'CStdString' in inner_type or 'string' in inner_type.lower()
                if not is_primitive and not is_string:
                    needs_serializer = True
                    break
        if not dry_run and needs_serializer:
            S3_inject_serialization.add_include_if_needed(file_path, "<NayanSerializer.h>")
            if dbg:
                dbg.log(f"INCLUDE_ADDED file={file_path} include=<NayanSerializer.h>")

        success = S3_inject_serialization.inject_methods_into_class(file_path, class_name, methods_code, dry_run=dry_run)

        if success:
            if not dry_run:
                marked = S3_inject_serialization.comment_dto_macro(file_path, dry_run=False, serializable_macro=serializable_macro)
                if dbg:
                    dbg.log(
                        f"CLASS_PROCESSED file={file_path} class={class_name} "
                        f"annotation_marked={marked}",
                        level="OK",
                    )
            processed_count += 1
        else:
            failed_inject += 1
            if dbg:
                dbg.log(
                    f"CLASS_INJECT_FAILED file={file_path} class={class_name} "
                    f"boundaries={boundaries} fields={len(fields)}",
                    level="ERROR",
                )

    if dbg:
        dbg.log_banner("springbootplusplus_data 00_process_serializable_classes DONE")
        dbg.log(
            f"summary processed={processed_count} skipped_no_annotation={skipped_no_annotation} "
            f"skipped_already_processed={skipped_already_processed} skipped_macro_mismatch={skipped_macro_mismatch} "
            f"failed_inject={failed_inject} files_scanned={len(unique_header_files)}"
        )
    return processed_count


def main():
    """Main function to process all Entity classes."""
    serializable_macro = None
    if 'serializable_macro' in globals():
        serializable_macro = globals()['serializable_macro']
    elif 'SERIALIZABLE_MACRO' in os.environ:
        serializable_macro = os.environ['SERIALIZABLE_MACRO']

    if dbg:
        dbg.log(f"main() serializable_macro={serializable_macro}")

    processed_count = process_all_serializable_classes(dry_run=False, serializable_macro=serializable_macro)

    if dbg:
        dbg.log(f"main() exit processed_count={processed_count}")

    return 0


if __name__ == "__main__":
    exit(main())

