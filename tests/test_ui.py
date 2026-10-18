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
                app.install(); self.assertIn('1.2.0', app.install_status.get())
                app.select(4); app.apply(); self.assertEqual(core.read_settings(exe.parent)['bias'], 10)
                app.load_selected(); self.assertEqual(app.profile.get(), 4)
                app.choose_profile(6); app.apply(); self.assertEqual(core.read_settings(exe.parent)['bias'], 15)
                app.load_selected(); self.assertEqual(app.profile.get(), 6)
                self.assertTrue(core.read_settings(exe.parent)['neutral_sky'])
                self.assertTrue(core.read_settings(exe.parent)['allow_mipmaps'])
                self.assertIn('You are using Potato Graphics textures', app.using.get())
                app.apply(); self.assertIn('You are using Potato Graphics textures', app.status.get())
                app.choose_profile(4)
                self.assertIn('Potato Graphics', app.using.get()) # Selection alone is not Apply.
                app.apply(); self.assertIn('You are using Ultra textures', app.using.get())
                app.choose_profile(6);app.apply()
                app.enabled.set(False); app.apply(); self.assertFalse(core.read_settings(exe.parent)['enabled'])
                app.show('Diagnostics'); root.update()
                app.passthrough.set(True); app.save_passthrough()
                self.assertTrue(core.read_settings(exe.parent)['bypass'])
                app.passthrough.set(False); app.save_passthrough()
                self.assertFalse(core.read_settings(exe.parent)['bypass'])
                app.show('About'); root.update()
                app.show('Graphics'); root.geometry('960x660'); root.update()
                self.assertLessEqual(app.content.winfo_reqheight(), app.content.winfo_height())
                with patch.object(core, 'require_closed', side_effect=ValueError('game running')):
                    with self.assertRaisesRegex(ValueError, 'game running'): app.apply()
                app.remove(); self.assertFalse((exe.parent / core.DLL).exists())
            self.assertEqual(exe.read_bytes(), data)

    def test_tray_hide_reveal_and_update_popup(self):
        try: root = tk.Tk()
        except tk.TclError: self.skipTest('No display available')
        app = App(root, remember=False); self.addCleanup(app.close)
        from unittest.mock import Mock
        app.tray=Mock(available=True)
        app.hide(); self.assertTrue(app.hidden); self.assertEqual(root.state(),'withdrawn')
        app.reveal(); self.assertFalse(app.hidden); root.update()
        with patch('texture_ui.messagebox.askyesno',return_value=False) as popup:
            from update_manager import Release
            r=Release('1.3.0','file','','1','','')
            app.offer_update(r,False); popup.assert_called_once()
            app.offer_update(r,False); popup.assert_called_once()
            app.offer_update(r,True); self.assertEqual(popup.call_count,2)
        app.close(); app.tray.stop.assert_called_once()

    def test_compact_pages_fit_and_buttons_support_pointer_and_keyboard(self):
        try: root = tk.Tk()
        except tk.TclError: self.skipTest('No display available')
        app=App(root,remember=False);self.addCleanup(app.close)
        root.geometry('%dx%d' % root.minsize())
        for route in ('Graphics','Diagnostics','About','Graphics'):
            app.show(route);root.update()
            self.assertLessEqual(app.content.winfo_reqheight(),app.content.winfo_height(),route)
            self.assertLessEqual(app.content.winfo_reqwidth(),app.content.winfo_width(),route)
        self.assertTrue(app.apply_button.winfo_ismapped())
        self.assertLessEqual(app.apply_button.winfo_rooty()+app.apply_button.winfo_height(),root.winfo_rooty()+root.winfo_height())
        button=app.profile_buttons[6]
        button.event_generate('<Enter>');button.event_generate('<ButtonPress-1>');button.event_generate('<ButtonRelease-1>')
        root.update();self.assertEqual(app.profile.get(),6)
        button=app.profile_buttons[2];button.focus_force();root.update()
        button.event_generate('<KeyPress-space>');button.event_generate('<KeyRelease-space>')
        root.update();self.assertEqual(app.profile.get(),2)
        self.assertFalse(any(isinstance(w,tk.Scrollbar) for w in app.content.master.winfo_children()))
