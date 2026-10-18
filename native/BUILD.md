# Building

Use an i686 MinGW-w64 C++17 compiler. The release workflow cross-compiles the DLL and builds the standalone GUI on Windows.

From the package root:

```sh
i686-w64-mingw32-g++ -std=c++17 -O2 -Wall -Wextra -Wno-cast-function-type -Wno-misleading-indentation -fno-exceptions -fno-rtti -shared -static -static-libgcc native/texture_lab.cpp native/exports.def -o d3d9.dll -Wl,--no-insert-timestamp -s
python -c "from pathlib import Path; import hashlib; Path('DLL_SHA256.txt').write_text(hashlib.sha256(Path('d3d9.dll').read_bytes()).hexdigest()+'  d3d9.dll\n')"
```

The compiler may be named `i686-w64-mingw32-g++-posix`. The native proxy's private-export forwarding stubs target x86; do not compile it as an x64 DLL.

Tests:

```sh
python -m unittest discover -s tests -v
g++ -std=c++17 -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer -DTEXTURELAB_HOST_TEST -Wno-format tests/test_native_callbacks.cpp -o test_callbacks
ASAN_OPTIONS=detect_leaks=0 ./test_callbacks
```

The host test compiles the actual callback bodies against a portable Win32/COM fixture. It does not execute the generated full-interface forwarders or validate the Windows ABI, real driver behavior or private forwarding exports. The Windows SDK cross-build compiles those forwarders and checks every slot position. To compile the same callback test against the real Windows SDK headers, use the i686 MinGW compiler on `tests/test_native_callbacks.cpp`; its test macro disables the private x86 forwarding stubs. Run that resulting test EXE only in a suitable Windows test environment.

The UI test needs a display; it skips when headless. It uses a fake executable header and mocks Windows process enumeration, and never launches a game.

The standalone GUI uses tools/build_windows.ps1 and PyInstaller, not the earlier Python-dependent native launcher.
