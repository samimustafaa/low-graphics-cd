"""CD Texture Lab 1.3.0 — public COM forwarding wrappers, Windows x86 Direct3D 9.

Python 3.9+ standard library only. No network operations. See README.md.
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import os
import struct
import subprocess
import tempfile
import platform
import zipfile
import shutil
import configparser

import sys
ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
DLL = "d3d9.dll"
INI = "CD_TextureLab.ini"
MANIFEST = "CD_TextureLab_install.json"
LOG = "CD_TextureLab.log"
# Stable ownership identifiers keep removal compatible with version 0.1.
APP = "CD Texture Lab 0.1"
MARKER = "; Created by CD Texture Lab 0.1"
PRESETS = {
    0: (0, 256), 2: (2, 256), 4: (10, 128), 6: (15, 32),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate_exe(path):
    path = Path(path).resolve(strict=True)
    if path.suffix.lower() != ".exe":
        raise ValueError("Choose the actual game .exe, rather than its shortcut.")
    with path.open("rb") as f:
        if f.read(2) != b"MZ":
            raise ValueError("This is not a Windows executable.")
        f.seek(0x3C)
        raw = f.read(4)
        if len(raw) != 4:
            raise ValueError("Incomplete executable header.")
        f.seek(struct.unpack("<I", raw)[0])
        pe = f.read(26)
    if len(pe) != 26 or pe[:4] != b"PE\0\0" or pe[4:6] != b"\x4c\x01" or pe[24:26] != b"\x0b\x01":
        raise ValueError("This helper supports 32-bit x86 games only.")
    return path


def require_closed(exe):
    if os.name != "nt":
        raise OSError("Installation is supported on Windows only.")
    result = subprocess.run(["tasklist", "/FO", "CSV", "/NH"],
                            capture_output=True, text=True, errors="replace",
                            creationflags=subprocess.CREATE_NO_WINDOW, check=True)
    for row in csv.reader(io.StringIO(result.stdout)):
        if row and row[0].casefold() == exe.name.casefold():
            raise ValueError("To change the textures you need to leave the game! Close the game completely first.")


def settings(bias=2, bypass=False, neutral_sky=True, allow_mipmaps=True, collect_stats=False):
    bias = int(bias)
    if bias not in PRESETS:
        raise ValueError("Choose Normal, Low, Ultra, or Potato Graphics.")
    actual_bias, size = PRESETS[bias]
    return (f"{MARKER}\n[TextureLab]\nEnabled=1\nBias={actual_bias}\n"
            f"MinTextureSize={size}\nCollectStats={int(collect_stats)}\nNeutralSky={int(bias == 6 and neutral_sky)}\nIncludeAutogen={int(bias == 6)}\nMinMipLevel={4 if bias == 6 and allow_mipmaps else 0}\n"
            f"CoarsestMip=0\nForceMipFilter={int(bias == 6 and allow_mipmaps)}\nBypass={int(bypass)}\n").encode("ascii")


def preset_from_settings(config):
    """Map saved renderer values back to their UI preset, including old builds."""
    pair = (config['bias'], config['size'])
    for mode, values in PRESETS.items():
        if values == pair:
            return mode
    if config['size'] <= 64:
        return 6
    return config['bias'] if config['bias'] in PRESETS else 2


def owned_manifest(folder):
    if (folder / MANIFEST).is_symlink():
        raise ValueError("Refusing a redirected installation record.")
    value = json.loads((folder / MANIFEST).read_text(encoding="utf-8"))
    if value.get("app") != APP or not isinstance(value.get("dll_sha256"), str):
        raise ValueError("This installation does not have a valid Texture Lab record.")
    return value


def install(folder, dll_bytes):
    """Create only new files; roll back our own files if any step fails."""
    folder = Path(folder)
    targets = [folder / n for n in (DLL, INI, MANIFEST)]
    for p in targets:
        if p.exists() or p.is_symlink():
            raise ValueError(f"{p.name} already exists. Nothing was overwritten. "
                             "Remove an existing Texture Lab installation first; keep other graphics wrappers separate.")
    created = []
    blobs = [dll_bytes, settings(), json.dumps({"app": APP, "build_version": "1.3.0", "dll_sha256": sha(dll_bytes)}, indent=2).encode()]
    try:
        for path, data in zip(targets, blobs):
            with path.open("xb") as f:
                created.append(path)
                f.write(data)
    except Exception:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise


def apply_bias(folder, bias, bypass=False):
    folder = Path(folder)
    record = owned_manifest(folder)
    if bypass and record.get("build_version") != "1.3.0":
        raise ValueError("Install/update the 1.3.0 helper before using Bypass. Restart the game afterward.")
    ini = folder / INI
    if ini.is_symlink() or not ini.is_file() or not ini.read_text(encoding="ascii").startswith(MARKER + "\n"):
        raise ValueError("The settings file is missing or is not owned by this app.")
    fd, name = tempfile.mkstemp(prefix="CD_TextureLab_", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(settings(bias, bypass=bypass))
        os.replace(name, ini)
    finally:
        Path(name).unlink(missing_ok=True)


def uninstall(folder):
    """Never remove a changed DLL, other wrapper, or arbitrary manifest paths."""
    folder = Path(folder)
    manifest = owned_manifest(folder)
    dll, ini = folder / DLL, folder / INI
    if dll.is_symlink() or (dll.exists() and sha(dll.read_bytes()) != manifest["dll_sha256"]):
        raise ValueError("d3d9.dll changed after installation. Refusing to remove it automatically.")
    if ini.is_symlink() or (ini.exists() and not ini.read_text(encoding="ascii").startswith(MARKER + "\n")):
        raise ValueError("The INI no longer has our ownership marker. Refusing automatic removal.")
    # DLL first: if Windows has it locked, preserve the recovery record and INI.
    dll.unlink(missing_ok=True)
    ini.unlink(missing_ok=True)
    (folder / MANIFEST).unlink()


def diagnostic_payload(exe, events=None):
    """Read only. Collect no memory dump or unrelated Windows events."""
    exe = Path(exe)
    data = {"system.txt": f"Texture Lab 1.3.0 diagnostic export\nWindows/platform: {platform.platform()}\n"
            f"Python: {platform.python_version()} ({struct.calcsize('P') * 8}-bit)\n"
            f"Game executable: {exe}\n"}
    for name in (LOG, INI, MANIFEST):
        path = exe.parent / name
        if path.is_file() and not path.is_symlink():
            with path.open("rb") as f:
                f.seek(max(0, path.stat().st_size - 65536))
                data[name + ".txt"] = f.read(65536).decode("utf-8", "replace")
    dll = exe.parent / DLL
    data["system.txt"] += "Installed DLL SHA256: " + (sha(dll.read_bytes()) if dll.is_file() else "missing") + "\n"
    if events is None:
        if os.name != "nt":
            events = "Windows event export is available on Windows only."
        else:
            query = ('*[System[(EventID=1000 or EventID=1001 or EventID=1002) and '
                     'TimeCreated[timediff(@SystemTime)<=604800000]]] and '
                     f'*[EventData[Data="{exe.name}"]]')
            try:
                result = subprocess.run(["wevtutil", "qe", "Application", "/q:" + query,
                                         "/rd:true", "/c:10", "/f:text"],
                                        capture_output=True, text=True, errors="replace", timeout=15,
                                        creationflags=subprocess.CREATE_NO_WINDOW)
                events = result.stdout or result.stderr or "No matching Windows application-error events were found."
            except (OSError, subprocess.SubprocessError) as exc:
                events = f"Windows error-event export failed: {exc}"
    data["windows_errors.txt"] = events
    return data


def write_diagnostics(exe, destination, events=None):
    data = diagnostic_payload(exe, events)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, value in data.items(): archive.writestr(name, value)



def install_or_update(folder, dll_bytes):
    folder = Path(folder)
    if not (folder / MANIFEST).exists():
        install(folder, dll_bytes)
        return "installed"
    record = owned_manifest(folder)
    dll = folder / DLL
    if dll.is_symlink() or not dll.is_file() or sha(dll.read_bytes()) != record["dll_sha256"]:
        raise ValueError("The installed DLL changed or is missing. Use recovery before updating.")
    ini = folder / INI
    if ini.is_symlink() or not ini.is_file() or not ini.read_text(encoding="ascii").startswith(MARKER + "\n"):
        raise ValueError("Settings ownership cannot be verified. Nothing was updated.")
    backup = Path(tempfile.mkdtemp(prefix="TextureLab_recovery_", dir=folder))
    names = (DLL, INI, MANIFEST)
    for name in names:
        shutil.copy2(folder / name, backup / name)
    blobs = (dll_bytes, settings(), json.dumps({"app": APP, "build_version": "1.3.0", "dll_sha256": sha(dll_bytes)}, indent=2).encode())
    try:
        for name, blob in zip(names, blobs):
            _atomic_write(folder / name, blob)
    except Exception as exc:
        errors = []
        for name in names:
            try:
                original_data = (backup / name).read_bytes()
                if not (folder / name).is_file() or (folder / name).read_bytes() != original_data:
                    _atomic_write(folder / name, original_data)
            except OSError as rollback_error: errors.append(str(rollback_error))
        if errors:
            raise OSError(f"Update failed. Recovery copies kept at {backup}. Close the game before recovery. {exc}") from exc
        shutil.rmtree(backup)
        raise
    shutil.rmtree(backup)
    return "updated"


def _atomic_write(path, data):
    fd, temporary = tempfile.mkstemp(prefix="TextureLab_", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream: stream.write(data)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def read_settings(folder):
    parser = configparser.ConfigParser()
    parser.read(Path(folder) / INI)
    section = parser["TextureLab"] if parser.has_section("TextureLab") else {}
    return {"bias": int(section.get("Bias", "2")), "size": int(section.get("MinTextureSize", "256")),
            "enabled": section.get("Enabled", "1") != "0", "bypass": section.get("Bypass", "0") != "0", "neutral_sky": section.get("NeutralSky", "0") != "0", "allow_mipmaps": section.get("ForceMipFilter", "0") != "0", "collect_stats": section.get("CollectStats", "0") != "0"}


def save_preset(folder, mode, enabled=True, bypass=False, neutral_sky=True, allow_mipmaps=True, collect_stats=False):
    data = settings(mode, bypass=bypass, neutral_sky=neutral_sky, allow_mipmaps=allow_mipmaps, collect_stats=collect_stats)
    if not enabled: data = data.replace(b"Enabled=1", b"Enabled=0")
    record = owned_manifest(Path(folder))
    if record.get("build_version") != "1.3.0":
        raise ValueError("Click Install / update first to replace the old helper.")
    current = Path(folder) / DLL
    if current.is_symlink() or not current.is_file() or sha(current.read_bytes()) != record["dll_sha256"]:
        raise ValueError("The installed DLL does not match its installation record.")
    ini = Path(folder) / INI
    if ini.is_symlink() or not ini.read_text(encoding="ascii").startswith(MARKER + "\n"):
        raise ValueError("Settings ownership cannot be verified.")
    _atomic_write(ini, data)


if __name__ == "__main__":
    from texture_ui import main
    main()
