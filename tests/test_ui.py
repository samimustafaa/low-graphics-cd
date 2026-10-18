"""Run with an available display; installation actions use a fake game folder."""
import sys
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import texture_lab as core
from texture_ui import App
import tkinter as tk


class UITests(unittest.TestCase):
    def test_upgrade_apply_toggle_diagnostics_and_restore(self):
        try: root = tk.Tk()
        except tk.TclError: self.skipTest('No display available')
        app = App(root, remember=False)
        self.addCleanup(app.close)
        with tempfile.TemporaryDirectory() as temp:
            exe = Path(temp) / 'client.exe'
            data = bytearray(160); data[:2] = b'MZ'
            struct.pack_into('<I', data, 0x3c, 64)
            data[64:68] = b'PE\0\0'; data[68:70] = b'\x4c\x01'; data[88:90] = b'\x0b\x01'
            exe.write_bytes(data)
            app.path.set(str(exe)); app.load_selected()
            with patch.object(core, 'require_closed', lambda value: None):
                app.install(); self.assertIn('1.0.0', app.install_status.get())
                app.select(4); app.apply(); self.assertEqual(core.read_settings(exe.parent)['bias'], 10)
                app.load_selected(); self.assertEqual(app.profile.get(), 4)
                app.choose_profile(6); app.apply(); self.assertEqual(core.read_settings(exe.parent)['bias'], 15)
                app.load_selected(); self.assertEqual(app.profile.get(), 6)
                self.assertTrue(core.read_settings(exe.parent)['neutral_sky'])
                self.assertIn('You are using Potato Graphics textures', app.using.get())
                app.enabled.set(False); app.apply(); self.assertFalse(core.read_settings(exe.parent)['enabled'])
                app.show('Diagnostics'); root.update()
                app.passthrough.set(True); app.save_passthrough()
                self.assertTrue(core.read_settings(exe.parent)['bypass'])
                app.passthrough.set(False); app.save_passthrough()
                self.assertFalse(core.read_settings(exe.parent)['bypass'])
                app.show('About'); root.update()
                app.show('Graphics'); root.geometry('960x660'); root.update()
                self.assertGreaterEqual(app.page_canvas.bbox('all')[3], 0)
                with patch.object(core, 'require_closed', side_effect=ValueError('game running')):
                    with self.assertRaisesRegex(ValueError, 'game running'): app.apply()
                app.remove(); self.assertFalse((exe.parent / core.DLL).exists())
            self.assertEqual(exe.read_bytes(), data)
