import importlib.util
import configparser
import zipfile
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "texture_lab.py"
spec = importlib.util.spec_from_file_location("texture_lab", SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.dll = b"test DLL bytes, never executable"

    def test_install_change_remove_preserves_game_files(self):
        config = self.folder / "neox.xml"
        config.write_bytes(b"original compiled game config")
        m.install(self.folder, self.dll)
        m.apply_bias(self.folder, 4)
        self.assertIn(b"Bias=10", (self.folder / m.INI).read_bytes())
        m.uninstall(self.folder)
        self.assertEqual(config.read_bytes(), b"original compiled game config")
        self.assertEqual(list(self.folder.iterdir()), [config])

    def test_only_potato_allows_optional_mip_filter(self):
        m.install(self.folder, self.dll)
        for mode, expected in [(6, ("32", "4", "0", "1")),
                               (4, ("128", "0", "0", "0")),
                               (0, ("256", "0", "0", "0"))]:
            m.apply_bias(self.folder, mode)
            parser = configparser.ConfigParser()
            parser.read(self.folder / m.INI)
            cfg = parser["TextureLab"]
            self.assertEqual(tuple(cfg[k] for k in ("MinTextureSize", "MinMipLevel", "CoarsestMip", "ForceMipFilter")), expected)
        m.uninstall(self.folder)

    def test_flat_cannot_be_selected_in_recovery_build(self):
        with self.assertRaises(ValueError): m.settings(8)

    def test_profiles_round_trip_and_gate_mipmaps_to_potato(self):
        for mode, bias, size in [(0, 0, 256), (2, 2, 256),
                                 (4, 10, 128), (6, 15, 32)]:
            parser = configparser.ConfigParser()
            parser.read_string(m.settings(mode).decode('ascii'))
            cfg = parser['TextureLab']
            values = {'bias': int(cfg['Bias']), 'size': int(cfg['MinTextureSize'])}
            self.assertEqual(values, {'bias': bias, 'size': size})
            self.assertEqual(m.preset_from_settings(values), mode)
            self.assertEqual(cfg['ForceMipFilter'], str(int(mode == 6)))
            self.assertEqual(cfg['CoarsestMip'], '0')
        self.assertEqual(m.preset_from_settings({'bias': 4, 'size': 256}), 4)
        self.assertEqual(m.preset_from_settings({'bias': 4, 'size': 64}), 6)

    def test_neutral_sky_only_on_potato_and_can_be_disabled(self):
        for mode in (0,2,4,6):
            data = m.settings(mode)
            self.assertIn(f"NeutralSky={int(mode == 6)}".encode(), data)
            self.assertIn(f"IncludeAutogen={int(mode == 6)}".encode(), data)
        self.assertIn(b"NeutralSky=0", m.settings(6, neutral_sky=False))
        self.assertIn(b"ForceMipFilter=0", m.settings(6, allow_mipmaps=False))

    def test_black_sky_roundtrip_and_scope(self):
        self.assertIn(b"BlackSky=0", m.settings(6))
        for mode in (0,2,4):
            self.assertIn(b"BlackSky=0", m.settings(mode, black_sky=True))
        self.assertIn(b"BlackSky=0", m.settings(6, neutral_sky=False, black_sky=True))
        m.install(self.folder, self.dll)
        m.save_preset(self.folder, 6, black_sky=True)
        self.assertTrue(m.read_settings(self.folder)['black_sky'])
        m.save_preset(self.folder, 6, black_sky=False)
        self.assertFalse(m.read_settings(self.folder)['black_sky'])

    def test_upgrade_preserves_applied_graphics_settings(self):
        m.install(self.folder, self.dll)
        m.save_preset(self.folder, 6, enabled=False, black_sky=True)
        before=(self.folder / m.INI).read_bytes()
        m.install_or_update(self.folder, self.dll + b'new')
        self.assertEqual((self.folder / m.INI).read_bytes(), before)

    def test_default_install_uses_former_potato_as_low(self):
        m.install(self.folder, self.dll)
        parser = configparser.ConfigParser()
        parser.read(self.folder / m.INI)
        self.assertEqual(parser["TextureLab"]["Bias"], "2")
        self.assertEqual(parser["TextureLab"]["Bypass"], "0")

    def test_owned_old_helper_updates_and_preserves_game(self):
        m.install(self.folder, self.dll)
        import json
        manifest = self.folder / m.MANIFEST
        record = json.loads(manifest.read_text()); record["build_version"] = "0.3"
        manifest.write_text(json.dumps(record))
        game = self.folder / "game.dat"; game.write_bytes(b"game stays original")
        result = m.install_or_update(self.folder, b"replacement DLL")
        self.assertEqual(result, "updated")
        self.assertEqual((self.folder / m.DLL).read_bytes(), b"replacement DLL")
        self.assertEqual(game.read_bytes(), b"game stays original")
        self.assertEqual(json.loads(manifest.read_text())["build_version"], "1.4.0")
        self.assertEqual(list(self.folder.glob("TextureLab_recovery_*")), [])

    def test_failed_update_rolls_back_dll_settings_and_manifest(self):
        m.install(self.folder, self.dll)
        before = {p.name: p.read_bytes() for p in self.folder.iterdir()}
        original = m._atomic_write
        failed = False
        def fail_once(path, data):
            nonlocal failed
            if path.name == m.INI and not failed:
                failed = True; raise PermissionError("simulated mid-update failure")
            original(path, data)
        with patch.object(m, "_atomic_write", fail_once):
            with self.assertRaises(PermissionError): m.install_or_update(self.folder, b"new DLL")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.folder.iterdir()})

    def test_locked_update_keeps_unchanged_files_without_rewriting_them(self):
        m.install(self.folder, self.dll)
        before = {p.name: p.read_bytes() for p in self.folder.iterdir()}
        with patch.object(m, "_atomic_write", side_effect=PermissionError("DLL is locked")):
            with self.assertRaises(PermissionError): m.install_or_update(self.folder, b"new DLL")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.folder.iterdir()})

    def test_disabled_textures_and_bypass_are_distinct(self):
        m.install(self.folder, self.dll)
        m.save_preset(self.folder, 2, enabled=False)
        cfg = m.read_settings(self.folder)
        self.assertFalse(cfg["enabled"]); self.assertFalse(cfg["bypass"])
        m.save_preset(self.folder, 2, enabled=True, bypass=True)
        cfg = m.read_settings(self.folder)
        self.assertTrue(cfg["enabled"]); self.assertTrue(cfg["bypass"])

    def test_update_refuses_other_wrapper(self):
        (self.folder / m.DLL).write_bytes(b"other tool")
        with self.assertRaises(ValueError): m.install_or_update(self.folder, self.dll)
        self.assertEqual((self.folder / m.DLL).read_bytes(), b"other tool")

    def test_bypass_is_explicit_and_normal_clears_it(self):
        m.install(self.folder, self.dll)
        m.apply_bias(self.folder, 0, bypass=True)
        self.assertIn(b"Bypass=1", (self.folder / m.INI).read_bytes())
        m.apply_bias(self.folder, 0)
        self.assertIn(b"Bypass=0", (self.folder / m.INI).read_bytes())

    def test_diagnostic_export_does_not_change_game_files(self):
        m.install(self.folder, self.dll)
        (self.folder / m.LOG).write_text("test reset failure", encoding="utf-8")
        before = {p.name: p.read_bytes() for p in self.folder.iterdir()}
        output = self.folder / "diagnostics.zip"
        m.write_diagnostics(self.folder / "client.exe", output, events="mock fault module d3d9.dll")
        with zipfile.ZipFile(output) as archive:
            self.assertIn("mock fault module", archive.read("windows_errors.txt").decode())
            self.assertNotIn("d3d9.dll", archive.namelist())
            self.assertIsNone(archive.testzip())
        self.assertEqual(before, {name: (self.folder / name).read_bytes() for name in before})

    def test_existing_proxy_is_never_overwritten(self):
        path = self.folder / m.DLL
        path.write_bytes(b"another wrapper")
        with self.assertRaises(ValueError): m.install(self.folder, self.dll)
        self.assertEqual(path.read_bytes(), b"another wrapper")
        self.assertEqual(list(self.folder.iterdir()), [path])

    def test_modified_proxy_is_never_removed(self):
        m.install(self.folder, self.dll)
        (self.folder / m.DLL).write_bytes(b"replacement wrapper")
        with self.assertRaises(ValueError): m.uninstall(self.folder)
        self.assertTrue((self.folder / m.INI).is_file())
        self.assertTrue((self.folder / m.MANIFEST).is_file())

    def test_missing_dll_still_allows_recovery(self):
        m.install(self.folder, self.dll)
        (self.folder / m.DLL).unlink()
        m.uninstall(self.folder)
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_invalid_bias_preserves_ini_and_cleans_temp(self):
        m.install(self.folder, self.dll)
        before = (self.folder / m.INI).read_bytes()
        with self.assertRaises(ValueError): m.apply_bias(self.folder, 99)
        self.assertEqual((self.folder / m.INI).read_bytes(), before)
        self.assertEqual(len(list(self.folder.iterdir())), 3)

    def test_locked_dll_keeps_recovery_record(self):
        m.install(self.folder, self.dll)
        unlink = Path.unlink
        def locked(path, *args, **kwargs):
            if path.name == m.DLL: raise PermissionError("in use")
            return unlink(path, *args, **kwargs)
        with patch.object(Path, "unlink", locked):
            with self.assertRaises(PermissionError): m.uninstall(self.folder)
        self.assertTrue((self.folder / m.MANIFEST).is_file())
        self.assertTrue((self.folder / m.INI).is_file())

    def test_partial_install_rolls_back_only_its_files(self):
        game = self.folder / "game.dat"; game.write_bytes(b"untouched")
        open_method = Path.open
        def denied(path, *args, **kwargs):
            if path.name == m.INI: raise PermissionError("denied")
            return open_method(path, *args, **kwargs)
        with patch.object(Path, "open", denied):
            with self.assertRaises(PermissionError): m.install(self.folder, self.dll)
        self.assertEqual(list(self.folder.iterdir()), [game])

    def test_rejects_64bit_executable(self):
        data = bytearray(160)
        data[:2] = b"MZ"; struct.pack_into("<I", data, 0x3c, 64)
        data[64:68] = b"PE\0\0"; data[68:70] = b"\x64\x86"
        data[88:90] = b"\x0b\x02"
        exe = self.folder / "game.exe"; exe.write_bytes(data)
        with self.assertRaises(ValueError): m.validate_exe(exe)
        data[68:70] = b"\x4c\x01"; data[88:90] = b"\x0b\x01"
        exe.write_bytes(data)
        self.assertEqual(m.validate_exe(exe), exe)


if __name__ == "__main__":
    unittest.main()
