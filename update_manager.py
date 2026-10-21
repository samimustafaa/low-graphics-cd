"""Opt-in installation of HTTPS GitHub releases; no shell commands or unverified execution."""
from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

REPOSITORY = 'samimustafaa/low-graphics-cd'
LATEST_URL = f'https://api.github.com/repos/{REPOSITORY}/releases/latest'
MAX_EXE = 64 * 1024 * 1024

class HTTPSOnlyRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if urlparse(newurl).scheme != 'https':
            raise ValueError('Update redirect did not use HTTPS.')
        return super().redirect_request(request, fp, code, msg, headers, newurl)

_OPENER = build_opener(HTTPSOnlyRedirect())

def version_tuple(text):
    match = re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)', text)
    if not match:
        raise ValueError('Unsupported update version.')
    return tuple(int(p) for p in match.groups())

def asset_url(url, version, filename):
    expected = f'https://github.com/{REPOSITORY}/releases/download/v{version}/{filename}'
    if url != expected:
        raise ValueError('Update asset is outside the expected release.')
    return url

def open_url(url):
    if urlparse(url).scheme != 'https':
        raise ValueError('Updates require HTTPS.')
    return _OPENER.open(Request(url, headers={'User-Agent': 'TextureLab-Updater', 'Accept': 'application/vnd.github+json'}), timeout=20)

def read_url(url, limit):
    with open_url(url) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Update response exceeded its size limit.')
    return data

@dataclass(frozen=True)
class Release:
    version: str
    filename: str
    url: str
    size: int
    sums_url: str
    page: str

def parse_release(data, current_version, installed):
    info = json.loads(data)
    if info.get('draft') or info.get('prerelease'):
        return None
    tag = info.get('tag_name', '')
    if version_tuple(tag) <= version_tuple(current_version):
        return None
    version = tag.removeprefix('v')
    # Folder/ZIP and legacy bridge users migrate through the same installer.
    assets = {a['name']: a for a in info.get('assets', [])}
    filename = f'sg0hann-BOOST-Setup-{version}.exe'
    if filename not in assets: filename = f'TextureLab-Setup-{version}.exe'
    target, sums = assets.get(filename), assets.get('SHA256SUMS.txt')
    if not target or not sums:
        raise ValueError('The release has no compatible app and checksum file.')
    size = target.get('size')
    if not isinstance(size, int) or not 0 < size <= MAX_EXE:
        raise ValueError('Update executable size is invalid.')
    return Release(version, filename, asset_url(target['browser_download_url'], version, filename), size,
                   asset_url(sums['browser_download_url'], version, 'SHA256SUMS.txt'),
                   f'https://github.com/{REPOSITORY}/releases/tag/v{version}')

def is_installed(executable=None):
    executable = Path(executable or sys.executable)
    marker = executable.parent / 'TextureLab-installed.txt'
    return executable.name.lower() == 'texturelab.exe' and marker.is_file() and marker.read_text(encoding='ascii').strip() == 'Texture Lab per-user installation'

def check_for_update(current_version, installed=None):
    return parse_release(read_url(LATEST_URL, 2 * 1024 * 1024), current_version,
                         is_installed() if installed is None else installed)

def expected_checksum(text, filename):
    matches = []
    for line in text.decode('utf-8-sig').splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[1].lstrip('*') == filename:
            if not re.fullmatch('[0-9a-fA-F]{64}', fields[0]):
                raise ValueError('Invalid update checksum.')
            matches.append(fields[0].lower())
    if len(matches) != 1:
        raise ValueError('A unique checksum for this update was not found.')
    return matches[0]

def download_verified(release, directory, progress=None, cancelled=None):
    # Revalidate persisted/offered metadata before any request.
    asset_url(release.url, release.version, release.filename)
    asset_url(release.sums_url, release.version, 'SHA256SUMS.txt')
    if not 0 < release.size <= MAX_EXE:
        raise ValueError('Update executable size is invalid.')
    digest = expected_checksum(read_url(release.sums_url, 65536), release.filename)
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='TextureLab-download-', suffix='.part', dir=directory)
    temporary = Path(name); total = 0; hasher = hashlib.sha256()
    try:
        with os.fdopen(fd, 'wb') as output, open_url(release.url) as response:
            while True:
                if cancelled and cancelled.is_set():
                    raise InterruptedError('Update download cancelled.')
                chunk = response.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > release.size or total > MAX_EXE:
                    raise ValueError('Update download exceeded its expected size.')
                hasher.update(chunk); output.write(chunk)
                if progress: progress(total, release.size)
        if total != release.size or hasher.hexdigest() != digest:
            raise ValueError('Update verification failed. Nothing was installed.')
        with temporary.open('rb') as stream:
            if stream.read(2) != b'MZ':
                raise ValueError('Update is not a Windows executable.')
        destination = directory / f'{Path(release.filename).stem}-{digest[:12]}.exe'
        os.replace(temporary, destination)
        return destination, digest
    finally:
        temporary.unlink(missing_ok=True)

def fresh_environment(bundle_dir=None, environ=None):
    """A detached update must not reuse its parent's one-file extraction folder."""
    result = dict(os.environ if environ is None else environ)
    for key in list(result):
        if key.upper().startswith('_PYI_') or key.upper() == '_MEIPASS2':
            del result[key]
    result['PYINSTALLER_RESET_ENVIRONMENT'] = '1'
    if bundle_dir:
        bundle = Path(bundle_dir).resolve()
        def inside(value):
            try: return Path(value).resolve().is_relative_to(bundle)
            except (OSError, ValueError): return False
        for key in list(result):
            if key.upper() in ('PATH','PYTHONPATH'):
                result[key] = os.pathsep.join(p for p in result[key].split(os.pathsep) if not p or not inside(p))
            elif key.upper() in ('TCL_LIBRARY','TK_LIBRARY','PYTHONHOME') and inside(result[key]):
                del result[key]
    return result


@contextmanager
def external_dll_search():
    """Clear the inherited Windows DLL search override only around CreateProcess."""
    if os.name != 'nt' or not getattr(sys, 'frozen', False):
        yield
        return
    import ctypes as c
    kernel = c.WinDLL('kernel32', use_last_error=True)
    kernel.GetDllDirectoryW.argtypes = [c.c_uint, c.c_wchar_p]
    kernel.GetDllDirectoryW.restype = c.c_uint
    kernel.SetDllDirectoryW.argtypes = [c.c_wchar_p]
    kernel.SetDllDirectoryW.restype = c.c_int
    buffer = c.create_unicode_buffer(32768)
    count = kernel.GetDllDirectoryW(len(buffer), buffer)
    if count >= len(buffer): raise OSError('DLL search path is too long to safely preserve.')
    previous = buffer.value if count else None
    if not kernel.SetDllDirectoryW(None): raise c.WinError(c.get_last_error())
    try: yield
    finally:
        if not kernel.SetDllDirectoryW(previous): raise c.WinError(c.get_last_error())


def start_update(candidate, digest, root, installed=None, executable=None, pid=None):
    candidate = Path(candidate).resolve()
    if hashlib.sha256(candidate.read_bytes()).hexdigest() != digest:
        raise ValueError('The verified update file changed. Installation was cancelled.')
    executable = Path(executable or sys.executable).resolve()
    installed = is_installed(executable) if installed is None else installed
    installer = bool(re.fullmatch(r'(?:TextureLab|sg0hann-BOOST)-Setup-\d+\.\d+\.\d+-[0-9a-f]{12}\.exe', candidate.name))
    if installed or installer:
        args = [str(candidate), '/SILENT', '/SUPPRESSMSGBOXES', '/NORESTART',
                '/TEXTURELABUPDATE=1']
        if installed: args.append('/DIR=' + str(executable.parent))
    else:
        helper = Path(root) / 'TextureLab-Updater.exe'
        if not helper.is_file():
            raise ValueError('The standalone update helper is missing. Install the latest release.')
        target_helper = candidate.parent / 'TextureLab-Updater.exe'
        shutil.copy2(helper, target_helper)
        args = [str(target_helper), str(pid or os.getpid()), str(candidate), str(executable), digest]
    environment = fresh_environment(getattr(sys, '_MEIPASS', None))
    with external_dll_search():
        return subprocess.Popen(args, env=environment, cwd=str(executable.parent),
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), close_fds=True)
