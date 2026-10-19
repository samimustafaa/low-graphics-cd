"""Persistent pin resources must survive bundle cleanup and preserve launch quoting."""
import ctypes
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import shell_identity as shell

class IdentityTests(unittest.TestCase):
    def test_icon_survives_bundle_removal_and_uses_content_version(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'_MEI'/'app.ico';source.parent.mkdir()
            source.write_bytes(b'icon1');target=shell.persistent_icon(source,root/'cache')
            self.assertEqual(shell.persistent_icon(source,root/'cache'),target)
            source.write_bytes(b'icon2');new=shell.persistent_icon(source,root/'cache')
            source.unlink();source.parent.rmdir()
            self.assertNotEqual(target,new)
            self.assertEqual(target.read_bytes(),b'icon1')
            self.assertEqual(new.read_bytes(),b'icon2')
            self.assertFalse(list((root/'cache').glob('*.tmp')))

    def test_frozen_command_excludes_temporary_bundle_and_test_arguments(self):
        with patch.object(sys,'frozen',True,create=True),patch.object(sys,'executable',str(Path('App With Spaces/TextureLab.exe').resolve())),patch.object(sys,'argv',['temporary','--smoke-test','report']):
            self.assertEqual(shell.relaunch_command(),'"'+str(Path(sys.executable).resolve())+'"')
            self.assertNotIn('--smoke-test',shell.relaunch_command())

    def test_property_layout(self):
        self.assertEqual(ctypes.sizeof(shell.GUID),16)
        self.assertEqual(ctypes.sizeof(shell.PropertyKey),20)
        self.assertEqual(shell.PropVariant.value.offset,8)
        self.assertEqual(ctypes.sizeof(shell.PropVariant),24 if ctypes.sizeof(ctypes.c_void_p)==8 else 16)

if __name__=='__main__':unittest.main()
